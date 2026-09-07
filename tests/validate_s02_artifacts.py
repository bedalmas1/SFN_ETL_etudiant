"""Validation intégrée des artefacts reproductibles de la séquence 2."""
import csv, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ | {"PYTHONPATH": str(ROOT / "src")}


def main():
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        table, report = tmp / "inventory.csv", tmp / "report.json"
        subprocess.run([
            sys.executable, "-m", "iot_decision.source_inventory_cli",
            "data/samples/batch002_retained_messages.jsonl",
            "data/samples/batch002_expected_sensors.csv", table, report,
        ], cwd=ROOT, env=ENV, check=True)
        with table.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        result = json.loads(report.read_text(encoding="utf-8"))
        assert len(rows) == 4 and result["expected_count"] == 5
        assert result["missing_topics"] == ["airbase/batch002/optronics-shelter-01/temperature"]
        assert result["complete"] is False
    print("S02 valide: inventaire reproductible et capteur optronique absent détecté.")


if __name__ == "__main__":
    main()
