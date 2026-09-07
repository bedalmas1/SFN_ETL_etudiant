import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iot_decision.baseline import extract_sample, load_raw, recommend, transform_raw, write_csv

SAMPLE = ROOT / "data" / "samples" / "batch001_messages.jsonl"


def test_sample_is_representative_and_reproducible():
    records = load_raw(SAMPLE)
    rows = transform_raw(records)
    assert len(rows) == 15
    assert len({row["message_id"] for row in rows}) == 15
    assert len({row["zone"] for row in rows}) == 5
    assert all(row["unit"] == "celsius" for row in rows)
    assert all(row["retained"] is True for row in rows)


def test_extract_preserves_semantics(tmp_path):
    target = tmp_path / "raw.jsonl"
    assert extract_sample(SAMPLE, target) == 15
    assert load_raw(target) == load_raw(SAMPLE)


def test_transform_writes_stable_csv(tmp_path):
    rows = transform_raw(load_raw(SAMPLE))
    target = tmp_path / "measurements.csv"
    assert write_csv(rows, target) == 15
    with target.open(encoding="utf-8", newline="") as stream:
        parsed = list(csv.DictReader(stream))
    assert parsed[0]["zone"] == "battery-shelter-01"
    assert parsed[-1]["zone"] == "optronics-shelter-01"


def test_invalid_payload_is_rejected_explicitly():
    record = load_raw(SAMPLE)[0]
    record["payload"] = json.dumps({"zone": "x"})
    with pytest.raises(ValueError, match="champs manquants"):
        transform_raw([record])


def test_recommendation_exposes_threshold_and_staleness():
    brief = recommend(transform_raw(load_raw(SAMPLE)))
    assert "inspection" in brief.decision
    assert brief.confidence == "faible"
    assert any("optronics-shelter-01" in item for item in brief.uncertainties)
    assert any("35.4" in item for item in brief.evidence)
