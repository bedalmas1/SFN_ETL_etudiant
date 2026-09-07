import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iot_decision.quality import (
    classify, detect_gaps, diagnose, find_exact_duplicates, flatten, load_raw,
    validate_row, write_csv, write_report,
)

SAMPLE = ROOT / "data/samples/batch002_quality_messages.jsonl"


def _rows():
    return [flatten(envelope) for envelope in load_raw(SAMPLE)]


def test_flatten_preserves_envelope_and_payload_fields():
    rows = _rows()
    assert len(rows) == 24
    first = rows[0]
    assert first["zone"] == "battery-shelter-01"
    assert first["topic"].startswith("airbase/batch002/battery-shelter-01/")
    assert first["retained"] is True


def test_validate_row_detects_each_reason():
    rows = _rows()
    by_id = {row["message_id"]: row for row in rows}
    assert validate_row(by_id["it-room-01-0002"]) == "champ manquant: unit"
    assert validate_row(by_id["maintenance-zone-01-0002"]) == "unité incohérente: fahrenheit"
    assert "valeur hors plage physique" in validate_row(by_id["optronics-shelter-01-0002"])
    assert validate_row(by_id["it-room-01-0003"]) == (
        "incohérence temporelle: measured_at postérieur à received_at"
    )
    assert validate_row(by_id["battery-shelter-01-0000"]) is None


def test_find_exact_duplicates_flags_only_the_retransmission():
    rows = _rows()
    duplicates = find_exact_duplicates(rows)
    assert len(duplicates) == 1
    duplicate_row = rows[list(duplicates)[0]]
    assert duplicate_row["message_id"] == "comms-shelter-01-0001"


def test_classify_matches_the_reference_split():
    clean, rejected = classify(_rows())
    assert len(clean) == 19
    assert len(rejected) == 5
    reasons = {row["rejection_reason"].split(":")[0].strip() for row in rejected}
    assert reasons == {
        "champ manquant", "unité incohérente", "valeur hors plage physique",
        "incohérence temporelle", "doublon exact",
    }


def test_gap_detection_distinguishes_real_silence_from_rejection_artifact():
    clean, rejected = classify(_rows())
    gaps = detect_gaps(clean)
    assert set(gaps) == {
        "battery-shelter-01", "it-room-01", "maintenance-zone-01", "optronics-shelter-01",
    }
    report = diagnose(_rows(), clean, rejected, gaps)
    assert report.gaps_by_zone["battery-shelter-01"][0]["explained_by_rejection"] is False
    assert report.gaps_by_zone["it-room-01"][0]["explained_by_rejection"] is True
    assert report.gaps_by_zone["maintenance-zone-01"][0]["explained_by_rejection"] is True
    assert report.gaps_by_zone["optronics-shelter-01"][0]["explained_by_rejection"] is True
    assert report.confidence == "faible"
    assert "battery-shelter-01" in report.decision


def test_outputs_are_machine_readable(tmp_path):
    clean, rejected = classify(_rows())
    gaps = detect_gaps(clean)
    report = diagnose(_rows(), clean, rejected, gaps)
    clean_csv = tmp_path / "clean.csv"
    rejected_csv = tmp_path / "rejected.csv"
    report_json = tmp_path / "report.json"
    from iot_decision.quality import CSV_FIELDS, REJECTED_FIELDS
    assert write_csv(clean, CSV_FIELDS, clean_csv) == 19
    assert write_csv(rejected, REJECTED_FIELDS, rejected_csv) == 5
    write_report(report, report_json)
    assert clean_csv.read_text(encoding="utf-8").count("\n") == 20
    result = json.loads(report_json.read_text(encoding="utf-8"))
    assert result["raw_count"] == 24 and result["clean_count"] == 19
