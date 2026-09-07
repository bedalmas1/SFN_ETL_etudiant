"""Validation intégrée des artefacts reproductibles de la séquence 7."""
import os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ | {"PYTHONPATH": str(ROOT / "src")}
SOURCE = "data/samples/batch004_suspect_scenario.jsonl"


def run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)], cwd=ROOT, env=ENV, check=True,
        capture_output=True, text=True,
    )


def main():
    diagnostic = run("-m", "iot_decision.chain_trust_cli", SOURCE)
    assert "1 doublon(s) exact(s)" in diagnostic.stdout
    assert "1 candidat(s) de rejeu" in diagnostic.stdout
    assert "1 incohérence(s) temporelle(s)" in diagnostic.stdout
    assert "silence non expliqué maximal 15 min" in diagnostic.stdout
    assert "suspicion data/cyber: probabilité forte, impact élevé" in diagnostic.stdout
    assert "recommandation: ne pas agir directement sur ces données" in diagnostic.stdout

    notebook = ROOT / "notebooks/s07_security_trust_robustness.ipynb"
    code = (
        "import nbformat; from nbclient import NotebookClient; "
        f"n=nbformat.read(r'{notebook}',as_version=4); "
        "NotebookClient(n,timeout=120,kernel_name='python3').execute()"
    )
    run("-c", code)

    print("S07 valide: signaux de confiance détectés sans recalcul, suspicion data/cyber priorisée, notebook exécutable.")


if __name__ == "__main__":
    main()
