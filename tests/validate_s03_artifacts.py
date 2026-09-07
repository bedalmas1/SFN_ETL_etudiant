"""Validation intégrée des artefacts reproductibles de la séquence 3."""
import csv
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ | {"PYTHONPATH": str(ROOT / "src")}


def main():
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "batch001_structured.csv"
        subprocess.run([
            sys.executable, "-m", "iot_decision.traceability_cli", "parse",
            "data/samples/batch001_messages.jsonl", output,
        ], cwd=ROOT, env=ENV, check=True)
        subprocess.run([
            sys.executable, "-m", "iot_decision.traceability_cli", "verify",
            "data/samples/batch001_messages.jsonl", output,
        ], cwd=ROOT, env=ENV, check=True)
        with output.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 15
        assert len({row["message_id"] for row in rows}) == 15
        assert len({row["raw_sha256"] for row in rows}) == 15
        assert all(row["schema_version"] == "s03-v1" for row in rows)
    print("S03 valide: 15 lignes structurées, reliées et vérifiables depuis le brut.")


if __name__ == "__main__":
    main()
