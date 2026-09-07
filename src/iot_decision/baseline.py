"""Pipeline baseline: conserver le brut, structurer, visualiser, décider.

Le module privilégie la lisibilité et la traçabilité. Il ne corrige aucune mesure:
les limites observées deviennent des éléments explicites de la recommandation.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REQUIRED = ("message_id", "zone", "sensor", "measured_at", "value", "unit")
CSV_FIELDS = (
    "message_id", "site_id", "zone", "asset_type", "sensor", "measured_at",
    "value", "unit", "sequence", "topic", "received_at", "retained",
)


def _iso8601(value: str) -> datetime:
    """Parse un horodatage ISO 8601; exige un fuseau explicite."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"horodatage sans fuseau: {value}")
    return parsed.astimezone(timezone.utc)


def load_raw(path: str | Path) -> list[dict]:
    """Charge des enveloppes JSONL, une par ligne non vide."""
    records: list[dict] = []
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON invalide ligne {line_number}: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"ligne {line_number}: objet JSON attendu")
            records.append(record)
    return records


def extract_sample(source: str | Path, destination: str | Path) -> int:
    """Copie exactement un échantillon vers le brut et retourne son effectif."""
    source = Path(source)
    target = Path(destination)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())

    return len(load_raw(source))


def transform_raw(records: Iterable[dict]) -> list[dict]:
    """Aplatit les enveloppes valides sans modifier les valeurs capteur."""
    rows: list[dict] = []
    for index, envelope in enumerate(records, 1):
        payload = envelope.get("payload")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError(f"enregistrement {index}: payload JSON invalide") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"enregistrement {index}: payload objet attendu")
        missing = [field for field in REQUIRED if field not in payload]
        if missing:
            raise ValueError(f"enregistrement {index}: champs manquants {missing}")
        _iso8601(str(payload["measured_at"]))
        _iso8601(str(envelope["received_at"]))
        value = payload["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"enregistrement {index}: valeur numérique attendue")
        row = {field: payload.get(field, "") for field in CSV_FIELDS}
        row.update({
            "topic": envelope.get("topic", ""),
            "received_at": envelope["received_at"],
            "retained": bool(envelope.get("retained", False)),
        })
        rows.append(row)
    return sorted(rows, key=lambda row: (row["zone"], row["measured_at"], row["message_id"]))


def write_csv(rows: Iterable[dict], destination: str | Path) -> int:
    """Écrit le CSV avec ordre de colonnes stable."""
    materialized = list(rows)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(materialized)
    return len(materialized)


@dataclass(frozen=True)
class DecisionBrief:
    decision: str
    confidence: str
    evidence: tuple[str, ...]
    uncertainties: tuple[str, ...]
    verification: str


def recommend(rows: Iterable[dict], *, threshold: float = 35.0,
              reference_time: str = "2026-10-12T10:05:00Z",
              stale_minutes: int = 30) -> DecisionBrief:
    """Produit une recommandation prudente, transparente et déterministe."""
    data = list(rows)
    if not data:
        return DecisionBrief("demander une vérification terrain", "très faible", (),
                             ("aucune donnée exploitable",), "relever les cinq zones")
    reference = _iso8601(reference_time)
    maxima: dict[str, float] = {}
    stale_zones: set[str] = set()
    for row in data:
        zone = str(row["zone"])
        maxima[zone] = max(maxima.get(zone, float("-inf")), float(row["value"]))
        age = (reference - _iso8601(str(row["measured_at"]))).total_seconds() / 60
        if age > stale_minutes:
            stale_zones.add(zone)
    over = {zone: value for zone, value in maxima.items() if value >= threshold}
    evidence = tuple(f"{zone}: maximum {value:.1f} °C" for zone, value in sorted(maxima.items()))
    uncertainties = []
    if stale_zones:
        uncertainties.append("fraîcheur insuffisante: " + ", ".join(sorted(stale_zones)))
    uncertainties.append("baseline: absence de preuve sur calibration, exhaustivité et intégrité")
    if over:
        decision = "déclencher une inspection des zones au seuil avant maintien sans réserve"
        confidence = "moyen" if not stale_zones else "faible"
    else:
        decision = "maintenir sous réserve d'une vérification ciblée des données anciennes"
        confidence = "moyen" if not stale_zones else "faible"
    return DecisionBrief(decision, confidence, evidence, tuple(uncertainties),
                         "confirmer sur le terrain les zones au seuil ou dont la mesure est ancienne")
