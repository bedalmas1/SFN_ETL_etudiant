"""Inventaire et diagnostic de complétude d'un instantané MQTT retained."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CompletenessReport:
    expected_count: int
    observed_count: int
    missing_topics: tuple[str, ...]
    unexpected_topics: tuple[str, ...]
    complete: bool
    confidence: str
    decision: str


def load_jsonl(path: str | Path) -> list[dict]:
    records = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON invalide ligne {number}: {exc.msg}") from exc
        if not isinstance(record, dict) or not isinstance(record.get("payload"), dict):
            raise ValueError(f"ligne {number}: enveloppe et payload objets attendus")
        records.append(record)
    return records


def inventory(records: list[dict]) -> list[dict]:
    rows = []
    for number, envelope in enumerate(records, 1):
        payload = envelope["payload"]
        topic = str(envelope.get("topic", ""))
        if not topic:
            raise ValueError(f"enregistrement {number}: topic absent")
        rows.append({
            "topic": topic,
            "site_id": payload.get("site_id", ""),
            "zone": payload.get("zone", ""),
            "sensor": payload.get("sensor", ""),
            "message_id": payload.get("message_id", ""),
            "measured_at": payload.get("measured_at", ""),
            "received_at": envelope.get("received_at", ""),
            "retained": bool(envelope.get("retained", False)),
            "payload_fields": len(payload),
        })
    return sorted(rows, key=lambda row: row["topic"])


def load_expected(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    required = {"topic", "zone", "sensor", "criticality"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("référentiel attendu vide ou colonnes manquantes")
    return rows


def diagnose(rows: list[dict], expected: list[dict]) -> CompletenessReport:
    observed_topics = {row["topic"] for row in rows}
    expected_topics = {row["topic"] for row in expected}
    missing = tuple(sorted(expected_topics - observed_topics))
    unexpected = tuple(sorted(observed_topics - expected_topics))
    complete = not missing and not unexpected and len(rows) == len(observed_topics)
    if complete:
        confidence = "moyenne"
        decision = "lot conforme au référentiel déclaré; poursuivre l'analyse avec réserves"
    else:
        confidence = "faible"
        decision = "ne pas conclure pour les zones non couvertes; vérifier la source et le terrain"
    return CompletenessReport(len(expected_topics), len(observed_topics), missing,
                              unexpected, complete, confidence, decision)


def write_inventory(rows: list[dict], destination: str | Path) -> int:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fields = ("topic", "site_id", "zone", "sensor", "message_id", "measured_at",
              "received_at", "retained", "payload_fields")
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_report(report: CompletenessReport, destination: str | Path) -> None:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
