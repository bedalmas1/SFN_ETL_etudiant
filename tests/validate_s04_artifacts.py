"""Validation intégrée des artefacts reproductibles de la séquence 4."""
import csv, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ | {"PYTHONPATH": str(ROOT / "src")}


def main():
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        clean, rejected, report = tmp / "clean.csv", tmp / "rejected.csv", tmp / "report.json"
        chart = tmp / "timeline.png"
        subprocess.run([
            sys.executable, "-m", "iot_decision.quality_cli",
            "data/samples/batch002_quality_messages.jsonl", clean, rejected, report,
        ], cwd=ROOT, env=ENV, check=True)
        subprocess.run([
            sys.executable, "-m", "iot_decision.visualize_quality", clean, rejected, chart,
        ], cwd=ROOT, env=ENV, check=True)
        with clean.open(encoding="utf-8", newline="") as stream:
            clean_rows = list(csv.DictReader(stream))
        with rejected.open(encoding="utf-8", newline="") as stream:
            rejected_rows = list(csv.DictReader(stream))
        result = json.loads(report.read_text(encoding="utf-8"))
        assert len(clean_rows) == 19 and len(rejected_rows) == 5
        assert result["raw_count"] == 24 and result["confidence"] == "faible"
        assert result["gaps_by_zone"]["battery-shelter-01"][0]["explained_by_rejection"] is False
        assert chart.stat().st_size > 10000
        notebook = ROOT / "notebooks/s04_data_quality_uncertainty.ipynb"
        code = (
            "import nbformat; from nbclient import NotebookClient; "
            f"n=nbformat.read(r'{notebook}',as_version=4); "
            "NotebookClient(n,timeout=120,kernel_name='python3').execute()"
        )
        subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=ENV, check=True)
    print("S04 valide: séparation propre/rejeté, silence réel détecté, figure et notebook exécutables.")


if __name__ == "__main__":
    main()
