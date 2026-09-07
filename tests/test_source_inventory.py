import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iot_decision.source_inventory import diagnose, inventory, load_expected, load_jsonl, write_inventory, write_report

SAMPLE = ROOT / "data/samples/batch002_retained_messages.jsonl"
EXPECTED = ROOT / "data/samples/batch002_expected_sensors.csv"


def test_inventory_preserves_source_metadata():
    rows = inventory(load_jsonl(SAMPLE))
    assert len(rows) == 4
    assert all(row["retained"] for row in rows)
    assert {row["zone"] for row in rows} == {
        "battery-shelter-01", "comms-shelter-01", "it-room-01", "maintenance-zone-01"
    }


def test_completeness_detects_expected_missing_sensor():
    report = diagnose(inventory(load_jsonl(SAMPLE)), load_expected(EXPECTED))
    assert report.complete is False
    assert report.observed_count == 4 and report.expected_count == 5
    assert report.missing_topics == ("airbase/batch002/optronics-shelter-01/temperature",)
    assert report.confidence == "faible"


def test_outputs_are_machine_readable(tmp_path):
    rows = inventory(load_jsonl(SAMPLE))
    report = diagnose(rows, load_expected(EXPECTED))
    table = tmp_path / "inventory.csv"
    diagnostic = tmp_path / "report.json"
    assert write_inventory(rows, table) == 4
    write_report(report, diagnostic)
    assert table.read_text(encoding="utf-8").count("\n") == 5
    assert json.loads(diagnostic.read_text(encoding="utf-8"))["complete"] is False
