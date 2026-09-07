import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iot_decision.quality import flatten, load_raw
from iot_decision.risk_score import DECISION_CUTOFF, black_box_score, decide, score_all_zones

KNOWN = ROOT / "data/raw/batch001_raw.jsonl"
SHIFT = ROOT / "data/samples/batch003_shift_scenario.jsonl"


def _rows(path):
    rows = [flatten(envelope) for envelope in load_raw(path)]
    for row in rows:
        row["value"] = float(row["value"])
    return rows


def test_battery_zone_crosses_the_decision_cutoff():
    rows = _rows(KNOWN)
    score = black_box_score(rows, "battery-shelter-01")
    assert score >= DECISION_CUTOFF
    assert decide(score) == "inspection recommandée"


def test_other_known_zones_stay_below_cutoff():
    rows = _rows(KNOWN)
    for zone in ("comms-shelter-01", "it-room-01", "maintenance-zone-01", "optronics-shelter-01"):
        assert black_box_score(rows, zone) < DECISION_CUTOFF


def test_shifted_zone_silently_matches_the_safe_zones():
    """The model has no notion of fuel-storage's own, lower safety ceiling:
    its score for fuel-storage-01 lands in the same range as genuinely safe
    zones instead of standing out, and the decision reads 'no action'."""
    known_rows = _rows(KNOWN)
    shift_rows = _rows(SHIFT)
    safe_scores = [
        black_box_score(known_rows, zone)
        for zone in ("comms-shelter-01", "it-room-01", "maintenance-zone-01", "optronics-shelter-01")
    ]
    shifted_score = black_box_score(shift_rows, "fuel-storage-01")
    assert min(safe_scores) <= shifted_score <= max(safe_scores)
    assert decide(shifted_score) == "aucune action requise"


def test_score_all_zones_is_sorted_and_complete():
    rows = _rows(KNOWN)
    entries = score_all_zones(rows)
    assert [entry.zone for entry in entries] == sorted(entry.zone for entry in entries)
    assert len(entries) == 5
