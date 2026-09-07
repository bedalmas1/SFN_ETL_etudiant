"""Validation intégrée des artefacts reproductibles de la séquence 6."""
import os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ | {"PYTHONPATH": str(ROOT / "src")}
SOURCE = "data/processed/batch002_measurements_clean.csv"


def run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)], cwd=ROOT, env=ENV, check=True,
        capture_output=True, text=True,
    )


def main():
    note = run("-m", "iot_decision.briefing_cli", SOURCE, "battery-shelter-01")
    assert "1/3 mesure(s) >= 35 °C, maximum 36.2 °C" in note.stdout
    assert "Niveau de confiance : faible" in note.stdout

    safe_note = run("-m", "iot_decision.briefing_cli", SOURCE, "comms-shelter-01")
    assert "Niveau de confiance : moyenne" in safe_note.stdout

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        misleading_chart = tmp / "battery_misleading.png"
        honest_chart = tmp / "battery_honest.png"
        run(
            "-m", "iot_decision.visualize_briefing",
            SOURCE, "battery-shelter-01", misleading_chart, honest_chart,
        )
        assert misleading_chart.stat().st_size > 10000
        assert honest_chart.stat().st_size > 10000

        notebook = ROOT / "notebooks/s06_visualization_decision_briefing.ipynb"
        code = (
            "import nbformat; from nbclient import NotebookClient; "
            f"n=nbformat.read(r'{notebook}',as_version=4); "
            "NotebookClient(n,timeout=120,kernel_name='python3').execute()"
        )
        run("-c", code)

    print("S06 valide: note de briefing différenciée par zone, deux mises en forme du même incident, notebook exécutable.")


if __name__ == "__main__":
    main()
