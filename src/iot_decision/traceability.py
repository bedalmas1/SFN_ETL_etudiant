"""Parsing traçable d'enveloppes MQTT JSONL vers une table structurée."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = "s03-v1"
REQUIRED_ENVELOPE = ("topic", "received_at", "retained", "payload")
REQUIRED_PAYLOAD = (
    "batch_id", "message_id", "site_id", "zone", "asset_type", "sensor",
    "measured_at", "value", "unit", "sequence",
)
CSV_FIELDS = (
    "schema_version", "source_file", "source_line", "raw_sha256", "topic",
    "received_at", "retained", "batch_id", "message_id", "site_id", "zone",
    "asset_type", "sensor", "measured_at", "value", "unit", "sequence",
)


@dataclass(frozen=True)
class ParseIssue:
    source_line: int
    code: str
    detail: str


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"clé JSON dupliquée: {key}")
        result[key] = value
    return result


def parse_line(raw_line: str, source_file: str, source_line: int) -> dict:
    """Parse une ligne sans perdre son adresse ni son empreinte brute."""
    try:
        envelope = json.loads(raw_line, object_pairs_hook=_object_without_duplicate_keys)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"ligne {source_line}: JSON invalide ({exc})") from exc
    if not isinstance(envelope, dict):
        raise ValueError(f"ligne {source_line}: enveloppe objet attendue")
    missing_envelope = [field for field in REQUIRED_ENVELOPE if field not in envelope]
    if missing_envelope:
        raise ValueError(f"ligne {source_line}: enveloppe incomplète: {', '.join(missing_envelope)}")
    payload = envelope["payload"]
    if not isinstance(payload, dict):
        raise ValueError(f"ligne {source_line}: payload objet attendu")
    missing_payload = [field for field in REQUIRED_PAYLOAD if field not in payload]
    if missing_payload:
        raise ValueError(f"ligne {source_line}: payload incomplet: {', '.join(missing_payload)}")
    value = payload["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"ligne {source_line}: value doit être numérique")
    if not isinstance(envelope["retained"], bool):
        raise ValueError(f"ligne {source_line}: retained doit être booléen")
    return {
        "schema_version": SCHEMA_VERSION,
        "source_file": source_file,
        "source_line": source_line,
        "raw_sha256": hashlib.sha256(raw_line.encode("utf-8")).hexdigest(),
        "topic": envelope["topic"],
        "received_at": envelope["received_at"],
        "retained": envelope["retained"],
        **{field: payload[field] for field in REQUIRED_PAYLOAD},
    }


def parse_jsonl(path: str | Path, *, strict: bool = True) -> tuple[list[dict], list[ParseIssue]]:
    """Parse un JSONL. En mode strict, la première anomalie interrompt le lot."""
    source = Path(path)
    rows: list[dict] = []
    issues: list[ParseIssue] = []
    for number, raw_line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            rows.append(parse_line(raw_line, source.as_posix(), number))
        except ValueError as exc:
            issue = ParseIssue(number, "parse_error", str(exc))
            issues.append(issue)
            if strict:
                raise
    return rows, issues


def write_structured_csv(rows: Iterable[dict], destination: str | Path) -> int:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(materialized)
    return len(materialized)


def verify_traceability(rows: Iterable[dict], raw_path: str | Path) -> list[str]:
    """Retourne les écarts entre chaque ligne structurée et sa ligne brute."""
    raw_lines = Path(raw_path).read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    for row in rows:
        line_number = int(row["source_line"])
        if line_number < 1 or line_number > len(raw_lines):
            errors.append(f"ligne source hors limites: {line_number}")
            continue
        digest = hashlib.sha256(raw_lines[line_number - 1].encode("utf-8")).hexdigest()
        if digest != row["raw_sha256"]:
            errors.append(f"empreinte différente pour source_line={line_number}")
    return errors


def duplicate_candidates(rows: Iterable[dict]) -> list[list[dict]]:
    """Regroupe les mesures métier semblables sans décider de les supprimer."""
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        key = (row["site_id"], row["zone"], row["sensor"], row["measured_at"],
               str(row["value"]), row["unit"])
        groups.setdefault(key, []).append(row)
    return [group for group in groups.values() if len(group) > 1]
