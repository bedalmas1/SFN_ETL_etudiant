"""Validation intégrée des artefacts reproductibles de la séquence 6bis."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ | {"PYTHONPATH": str(ROOT / "src")}


def run(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)], cwd=ROOT, env=ENV, check=True,
        capture_output=True, text=True,
    )


def main():
    # Étape 1 : indicateurs du matin, zone masquée par la moyenne.
    indicators = run(
        "-m", "iot_decision.indicators_cli", "data/processed/batch001_measurements.csv",
    )
    assert "moyenne globale: 30.75" in indicators.stdout
    assert "zone masquée par la moyenne: battery-shelter-01" in indicators.stdout

    # Étape 2 : score sur les cinq zones connues.
    known_scores = run("-m", "iot_decision.risk_score_cli", "data/raw/batch001_raw.jsonl")
    assert "battery-shelter-01: score 71/100 -> inspection recommandée" in known_scores.stdout

    # Étape 3 : bascule sur fuel-storage-01, angle mort de calibration.
    shift_scores = run("-m", "iot_decision.risk_score_cli", "data/samples/batch003_shift_scenario.jsonl")
    assert "fuel-storage-01: score 62/100 -> aucune action requise" in shift_scores.stdout

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)

        # Étape 4 : extraction et fenêtre d'après-midi.
        extraction_code = (
            "from pathlib import Path;"
            "from iot_decision.baseline import load_raw, transform_raw, write_csv;"
            "records = load_raw('data/samples/batch003_shift_scenario.jsonl')"
            " + load_raw('data/samples/batch003_fuel_storage_extended.jsonl');"
            "rows = transform_raw(records);"
            f"write_csv(rows, Path(r'{tmp}') / 'batch003_measurements.csv');"
            "afternoon = [r for r in rows if r['measured_at'] >= '2026-11-02T10:00:00Z'];"
            f"n = write_csv(afternoon, Path(r'{tmp}') / 'batch003_afternoon_window.csv');"
            "print('fenetre apres-midi:', n, 'lignes')"
        )
        extraction = run("-c", extraction_code)
        assert "fenetre apres-midi: 3 lignes" in extraction.stdout
        combined_csv = tmp / "batch003_measurements.csv"
        afternoon_csv = tmp / "batch003_afternoon_window.csv"
        assert combined_csv.exists() and afternoon_csv.exists()

        # Étape 5 : le même graphique, deux seuils.
        misleading_chart = tmp / "fuel_storage_misleading_scale.png"
        pedagogical_chart = tmp / "fuel_storage_pedagogical_threshold.png"
        real_chart = tmp / "fuel_storage_real_threshold.png"
        chart_code = (
            "from iot_decision.visualize_briefing import create_misleading_chart, create_honest_chart;"
            f"create_misleading_chart(r'{afternoon_csv}', 'fuel-storage-01', r'{misleading_chart}');"
            f"create_honest_chart(r'{afternoon_csv}', 'fuel-storage-01', r'{pedagogical_chart}', threshold=35.0);"
            f"create_honest_chart(r'{afternoon_csv}', 'fuel-storage-01', r'{real_chart}', threshold=28.0)"
        )
        run("-c", chart_code)
        assert misleading_chart.stat().st_size > 10000
        assert pedagogical_chart.stat().st_size > 10000
        assert real_chart.stat().st_size > 10000

        # Étape 6 : note de briefing exacte sur le seuil réel.
        briefing_code = (
            "from iot_decision.indicators import load_measurements;"
            "from iot_decision.briefing import summarize_zone, briefing_note;"
            f"rows = load_measurements(r'{afternoon_csv}');"
            "summary = summarize_zone(rows, 'fuel-storage-01', threshold=28.0);"
            "print(briefing_note(summary))"
        )
        briefing = run("-c", briefing_code)
        assert "fuel-storage-01: 1/3 mesure(s) >= 28 °C, maximum 28.6 °C" in briefing.stdout
        assert "Niveau de confiance : faible" in briefing.stdout

    print(
        "S06bis valide: moyenne trompeuse, score hors calibration et graphique "
        "à texte figé détectés sur un seul cas fil rouge (fuel-storage-01)."
    )


if __name__ == "__main__":
    main()
