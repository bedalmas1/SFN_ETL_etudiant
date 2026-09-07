import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iot_decision.indicators import (
    duration_above_threshold, find_masked_zones, global_mean, load_measurements, zone_maxima,
)

SAMPLE = ROOT / "data/processed/batch001_measurements.csv"


def test_global_mean_looks_normal():
    rows = load_measurements(SAMPLE)
    assert round(global_mean(rows), 2) == 30.75


def test_zone_maxima_matches_reference():
    rows = load_measurements(SAMPLE)
    maxima = zone_maxima(rows)
    assert maxima["battery-shelter-01"] == 35.4
    assert maxima["optronics-shelter-01"] == 28.1


def test_find_masked_zones_flags_only_battery():
    rows = load_measurements(SAMPLE)
    masked = find_masked_zones(rows, threshold=35.0)
    assert len(masked) == 1
    assert masked[0].zone == "battery-shelter-01"
    assert masked[0].global_mean_value < 35.0 <= masked[0].zone_max


def test_duration_above_threshold_does_not_overclaim():
    rows = load_measurements(SAMPLE)
    duration = duration_above_threshold(rows, "battery-shelter-01", threshold=35.0)
    assert duration == 0.0


def test_no_masked_zone_when_threshold_too_high():
    rows = load_measurements(SAMPLE)
    assert find_masked_zones(rows, threshold=50.0) == []
