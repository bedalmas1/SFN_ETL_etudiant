import csv
from pathlib import Path

import pytest

from iot_decision.traceability import (
    duplicate_candidates, parse_jsonl, parse_line, verify_traceability, write_structured_csv,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data/samples/batch001_messages.jsonl"


def test_parse_reference_batch_and_verify_hashes(tmp_path):
    rows, issues = parse_jsonl(SAMPLE)
    assert len(rows) == 15
    assert not issues
    assert rows[0]["source_line"] == 1
    assert len(rows[0]["raw_sha256"]) == 64
    target = tmp_path / "structured.csv"
    assert write_structured_csv(rows, target) == 15
    with target.open(encoding="utf-8", newline="") as stream:
        restored = list(csv.DictReader(stream))
    assert verify_traceability(restored, SAMPLE) == []


def test_duplicate_json_keys_are_rejected():
    raw = '{"topic":"a","topic":"b","received_at":"x","retained":true,"payload":{}}'
    with pytest.raises(ValueError, match="clé JSON dupliquée"):
        parse_line(raw, "sample.jsonl", 1)


def test_missing_required_field_is_rejected():
    raw = '{"topic":"a","received_at":"x","retained":true,"payload":{}}'
    with pytest.raises(ValueError, match="payload incomplet"):
        parse_line(raw, "sample.jsonl", 1)


def test_lenient_mode_isolates_invalid_line(tmp_path):
    source = tmp_path / "mixed.jsonl"
    first = SAMPLE.read_text(encoding="utf-8").splitlines()[0]
    source.write_text(first + "\n{broken}\n", encoding="utf-8")
    rows, issues = parse_jsonl(source, strict=False)
    assert len(rows) == 1
    assert len(issues) == 1 and issues[0].source_line == 2


def test_similar_measurements_are_candidates_not_deleted():
    rows, _ = parse_jsonl(ROOT / "data/samples/batch001_traceability_incident.jsonl")
    groups = duplicate_candidates(rows)
    assert len(rows) == 2
    assert len(groups) == 1
    assert {row["message_id"] for row in groups[0]} == {
        "battery-shelter-01-0002", "battery-shelter-01-replay-a",
    }
