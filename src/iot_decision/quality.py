"""Contrôles qualité minimaux sur une fenêtre de messages MQTT retained.

Le module ne corrige jamais une mesure: il classe chaque ligne comme propre
ou rejetée, avec une raison explicite, puis signale séparément les périodes
sans message reçu. La correction et la quarantaine restent des décisions
humaines, tracées dans le rapport qualité et le brief, pas des opérations
automatiques.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REQUIRED_FIELDS = ("message_id", "zone", "sensor", "measured_at", "value", "unit")
ALLOWED_UNITS = ("celsius",)
VALUE_RANGE = (-10.0, 60.0)  # bornes pédagogiques, pas une spécification capteur réelle
CSV_FIELDS = (
    "message_id", "site_id", "zone", "asset_type", "sensor", "measured_at",
    "value", "unit", "sequence", "topic", "received_at", "retained",
)
REJECTED_FIELDS = CSV_FIELDS + ("rejection_reason",)


def _iso8601(value: str) -> datetime:
    """Parse un horodatage ISO 8601; exige un fuseau explicite."""
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"horodatage sans fuseau: {value}")
    return parsed.astimezone(timezone.utc)


def load_raw(path: str | Path) -> list[dict]:
    """Charge des enveloppes JSONL, une par ligne non vide, sans validation."""
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


def flatten(envelope: dict) -> dict:
    """Aplatit une enveloppe sans exiger la présence des champs obligatoires.

    Un champ manquant devient une chaîne vide: c'est un cas à qualifier par
    ``validate_row``, pas une erreur de lecture.
    """
    payload = envelope.get("payload") or {}
    row = {field: payload.get(field, "") for field in CSV_FIELDS}
    row.update({
        "topic": envelope.get("topic", ""),
        "received_at": envelope.get("received_at", ""),
        "retained": bool(envelope.get("retained", False)),
    })
    return row


def missing_fields(row: dict) -> list[str]:
    """Retourne les champs obligatoires absents ou vides sur cette ligne."""
    return [field for field in REQUIRED_FIELDS if row.get(field, "") in ("", None)]


def validate_row(row: dict) -> str | None:
    """Retourne une raison de rejet, ou ``None`` si la ligne est propre.

    Les contrôles sont appliqués dans un ordre fixe: un champ manquant
    masque toute autre anomalie tant qu'il n'est pas résolu.
    """
    missing = missing_fields(row)
    if missing:
        return f"champ manquant: {', '.join(missing)}"
    unit = str(row["unit"])
    if unit not in ALLOWED_UNITS:
        return f"unité incohérente: {unit}"
    try:
        value = float(row["value"])
    except (TypeError, ValueError):
        return f"valeur non numérique: {row['value']}"
    low, high = VALUE_RANGE
    if not (low <= value <= high):
        return f"valeur hors plage physique: {value:g} (bornes {low:g}..{high:g})"
    try:
        measured = _iso8601(str(row["measured_at"]))
        received = _iso8601(str(row["received_at"]))
    except ValueError:
        return "horodatage invalide"
    if measured > received:
        return "incohérence temporelle: measured_at postérieur à received_at"
    return None


def find_exact_duplicates(rows: list[dict]) -> set[int]:
    """Retourne les index des occurrences répétées d'un même événement déclaré.

    La clé (topic, message_id, measured_at, value, unit) identifie un même
    événement publié plusieurs fois, par exemple à la suite d'une
    retransmission MQTT. ``received_at`` est volontairement exclu: son
    léger décalage ne change pas l'identité de l'événement.
    """
    seen: dict[tuple, int] = {}
    duplicates: set[int] = set()
    for index, row in enumerate(rows):
        key = (row["topic"], row["message_id"], row["measured_at"], str(row["value"]), row["unit"])
        if key in seen:
            duplicates.add(index)
        else:
            seen[key] = index
    return duplicates


def classify(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Sépare les lignes propres des lignes rejetées, chacune avec sa raison.

    Les doublons exacts sont détectés avant la validation ligne à ligne:
    une retransmission parfaitement valide doit être écartée pour son
    identité, pas requalifiée par un autre contrôle.
    """
    duplicate_indices = find_exact_duplicates(rows)
    clean: list[dict] = []
    rejected: list[dict] = []
    for index, row in enumerate(rows):
        if index in duplicate_indices:
            rejected.append({**row, "rejection_reason": "doublon exact"})
            continue
        reason = validate_row(row)
        if reason:
            rejected.append({**row, "rejection_reason": reason})
        else:
            clean.append(row)
    return clean, rejected


def detect_gaps(clean_rows: Iterable[dict], *, expected_minutes: float = 5.0,
                 tolerance_minutes: float = 2.0) -> dict[str, list[dict]]:
    """Signale, par zone, les écarts entre mesures propres consécutives.

    Ne couvre que les lignes propres: un rejet n'est pas un silence, et un
    silence n'est jamais comblé par une valeur inventée.
    """
    by_zone: dict[str, list[dict]] = {}
    for row in clean_rows:
        by_zone.setdefault(str(row["zone"]), []).append(row)
    gaps: dict[str, list[dict]] = {}
    threshold = expected_minutes + tolerance_minutes
    for zone, zone_rows in by_zone.items():
        ordered = sorted(zone_rows, key=lambda row: row["measured_at"])
        zone_gaps = []
        for previous, current in zip(ordered, ordered[1:]):
            delta = (_iso8601(current["measured_at"]) - _iso8601(previous["measured_at"]))
            minutes = delta.total_seconds() / 60
            if minutes > threshold:
                zone_gaps.append({
                    "from": previous["measured_at"],
                    "to": current["measured_at"],
                    "duration_minutes": round(minutes, 1),
                })
        if zone_gaps:
            gaps[zone] = zone_gaps
    return gaps


@dataclass(frozen=True)
class QualityReport:
    raw_count: int
    clean_count: int
    rejected_count: int
    rejected_by_reason: dict[str, int]
    counts_by_zone: dict[str, dict[str, int]]
    gaps_by_zone: dict[str, list[dict]]
    confidence: str
    decision: str


def _counts_by_zone(raw_rows: list[dict], clean_rows: list[dict],
                     rejected_rows: list[dict]) -> dict[str, dict[str, int]]:
    """Compte brut/propre/rejeté par zone, pour l'audit du rapport."""
    zones = sorted({str(row["zone"]) for row in raw_rows if row.get("zone")})
    counts = {zone: {"raw": 0, "clean": 0, "rejected": 0} for zone in zones}
    for row in raw_rows:
        zone = str(row.get("zone", ""))
        if zone in counts:
            counts[zone]["raw"] += 1
    for row in clean_rows:
        counts[str(row["zone"])]["clean"] += 1
    for row in rejected_rows:
        zone = str(row.get("zone", ""))
        if zone in counts:
            counts[zone]["rejected"] += 1
    return counts


def _explain_gaps(gaps: dict[str, list[dict]], rejected_rows: list[dict]) -> dict[str, list[dict]]:
    """Annote chaque silence: une ligne rejetée dans la fenêtre du silence
    explique un simple effet du filtrage; son absence signale un silence
    réel, sans message reçu ni rejeté pour cette période."""
    rejected_by_zone: dict[str, list[dict]] = {}
    for row in rejected_rows:
        rejected_by_zone.setdefault(str(row["zone"]), []).append(row)
    annotated: dict[str, list[dict]] = {}
    for zone, zone_gaps in gaps.items():
        zone_rejected = rejected_by_zone.get(zone, [])
        annotated[zone] = []
        for gap in zone_gaps:
            start, end = _iso8601(gap["from"]), _iso8601(gap["to"])
            explained = any(start < _iso8601(str(row["measured_at"])) < end for row in zone_rejected)
            annotated[zone].append({**gap, "explained_by_rejection": explained})
    return annotated


def diagnose(raw_rows: list[dict], clean_rows: list[dict], rejected_rows: list[dict],
             gaps: dict[str, list[dict]], *, alert_zone: str = "battery-shelter-01") -> QualityReport:
    """Produit un diagnostic déterministe: ni correction, ni note chiffrée."""
    reason_counts = Counter(row["rejection_reason"].split(":")[0].strip() for row in rejected_rows)
    counts_by_zone = _counts_by_zone(raw_rows, clean_rows, rejected_rows)
    gaps = _explain_gaps(gaps, rejected_rows)
    real_silence_zones = [zone for zone, zone_gaps in gaps.items()
                          if any(not gap["explained_by_rejection"] for gap in zone_gaps)]
    if alert_zone in real_silence_zones:
        confidence = "faible"
        decision = (
            f"ne pas conclure seul sur l'alerte de {alert_zone}; "
            "la période sans message précédant la valeur haute exige une vérification terrain"
        )
    elif rejected_rows:
        confidence = "moyenne"
        decision = "poursuivre l'analyse sur les lignes propres; documenter et surveiller les rejets"
    else:
        confidence = "moyenne"
        decision = "poursuivre l'analyse avec les réserves habituelles du cours"
    return QualityReport(
        raw_count=len(raw_rows),
        clean_count=len(clean_rows),
        rejected_count=len(rejected_rows),
        rejected_by_reason=dict(sorted(reason_counts.items())),
        counts_by_zone=counts_by_zone,
        gaps_by_zone=gaps,
        confidence=confidence,
        decision=decision,
    )


def write_csv(rows: Iterable[dict], fields: tuple[str, ...], destination: str | Path) -> int:
    """Écrit un CSV avec un ordre de colonnes stable."""
    import csv

    materialized = list(rows)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(materialized)
    return len(materialized)


def write_report(report: QualityReport, destination: str | Path) -> None:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
