"""Validation intégrée des artefacts reproductibles de la séquence 5."""
import os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ | {"PYTHONPATH": str(ROOT / "src")}


def run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)], cwd=ROOT, env=ENV, check=True,
        capture_output=True, text=True,
    )


def main():
    indicators = run(
        "-m", "iot_decision.indicators_cli", "data/processed/batch001_measurements.csv",
    )
    assert "moyenne globale: 30.75" in indicators.stdout
    assert "zone masquée par la moyenne: battery-shelter-01" in indicators.stdout

    known_scores = run("-m", "iot_decision.risk_score_cli", "data/raw/batch001_raw.jsonl")
    assert "battery-shelter-01: score 71/100 -> inspection recommandée" in known_scores.stdout

    shift_scores = run("-m", "iot_decision.risk_score_cli", "data/samples/batch003_shift_scenario.jsonl")
    assert "fuel-storage-01: score 62/100 -> aucune action requise" in shift_scores.stdout

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        masked_chart = tmp / "masked_zone.png"
        score_chart = tmp / "risk_score_shift.png"
        run(
            "-m", "iot_decision.visualize_indicators",
            "data/processed/batch001_measurements.csv", masked_chart,
        )
        run(
            "-m", "iot_decision.visualize_risk_score",
            "data/raw/batch001_raw.jsonl", "data/samples/batch003_shift_scenario.jsonl", score_chart,
        )
        assert masked_chart.stat().st_size > 10000
        assert score_chart.stat().st_size > 10000

        notebook = ROOT / "notebooks/s05_indicators_decision_traps.ipynb"
        code = (
            "import nbformat; from nbclient import NotebookClient; "
            f"n=nbformat.read(r'{notebook}',as_version=4); "
            "NotebookClient(n,timeout=120,kernel_name='python3').execute()"
        )
        run("-c", code)

    print("S05 valide: moyenne trompeuse et score automatique en défaut détectés, figures et notebook exécutables.")


if __name__ == "__main__":
    main()
