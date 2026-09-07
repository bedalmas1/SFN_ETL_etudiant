import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iot_decision.chain_trust import collect_signals, rank_hypotheses, recommend
from iot_decision.quality import flatten, load_raw

SAMPLE = ROOT / "data/samples/batch004_suspect_scenario.jsonl"


def _rows():
    rows = [flatten(envelope) for envelope in load_raw(SAMPLE)]
    for row in rows:
        row["value"] = float(row["value"])
    return rows


def test_collect_signals_matches_the_injected_anomalies():
    signals = collect_signals(_rows())
    assert signals.exact_duplicates == 1
    assert signals.replay_candidates == 1
    assert signals.temporal_incoherences == 1
    assert signals.unexplained_gap_minutes == 15.0


def test_rank_hypotheses_puts_cyber_suspicion_first():
    signals = collect_signals(_rows())
    hypotheses = rank_hypotheses(signals)
    assert hypotheses[0].name == "suspicion data/cyber"
    assert hypotheses[0].likelihood == "forte"
    assert hypotheses[0].impact == "élevé"


def test_rank_hypotheses_keeps_real_incident_least_likely():
    signals = collect_signals(_rows())
    hypotheses = rank_hypotheses(signals)
    real_incident = next(h for h in hypotheses if h.name == "incident réel")
    assert real_incident.likelihood == "faible"


def test_recommend_calls_for_isolation_on_this_batch():
    signals = collect_signals(_rows())
    assert "isoler" in recommend(rank_hypotheses(signals))


def test_clean_batch_without_anomalies_does_not_trigger_suspicion():
    clean_rows = [row for row in _rows() if row["zone"] != "comms-shelter-01"]
    signals = collect_signals(clean_rows)
    assert signals.exact_duplicates == 0
    assert signals.replay_candidates == 0
    assert signals.temporal_incoherences == 0
    top = rank_hypotheses(signals)[0]
    assert top.likelihood in ("faible", "moyenne")
