import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iot_decision.briefing import briefing_note, summarize_zone, zone_series
from iot_decision.indicators import load_measurements

SAMPLE = ROOT / "data/processed/batch002_measurements_clean.csv"


def test_zone_series_is_sorted_by_measured_at():
    rows = load_measurements(SAMPLE)
    series = zone_series(rows, "battery-shelter-01")
    assert [row["measured_at"] for row in series] == sorted(row["measured_at"] for row in series)


def test_summarize_zone_flags_low_confidence_on_unexplained_gap():
    rows = load_measurements(SAMPLE)
    summary = summarize_zone(rows, "battery-shelter-01", threshold=35.0)
    assert summary.point_count == 3
    assert summary.above_threshold_count == 1
    assert summary.max_value == 36.2
    assert summary.unexplained_gap_minutes == 20.0
    assert summary.confidence == "faible"


def test_summarize_zone_without_gap_keeps_medium_confidence():
    rows = load_measurements(SAMPLE)
    summary = summarize_zone(rows, "comms-shelter-01", threshold=35.0)
    assert summary.above_threshold_count == 0
    assert summary.unexplained_gap_minutes == 0.0
    assert summary.confidence == "moyenne"


def test_briefing_note_contains_the_four_required_lines():
    rows = load_measurements(SAMPLE)
    summary = summarize_zone(rows, "battery-shelter-01", threshold=35.0)
    note = briefing_note(summary)
    assert note.startswith("Message principal :")
    assert "Limite :" in note
    assert "Niveau de confiance : faible" in note
    assert "Vérification recommandée :" in note


def test_summarize_zone_rejects_unknown_zone():
    rows = load_measurements(SAMPLE)
    try:
        summarize_zone(rows, "zone-inexistante")
    except ValueError:
        pass
    else:
        raise AssertionError("une zone absente doit lever une erreur explicite")
