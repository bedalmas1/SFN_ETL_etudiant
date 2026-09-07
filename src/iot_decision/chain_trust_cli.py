"""CLI de diagnostic de confiance pour la séquence 7."""

from __future__ import annotations

import argparse
from pathlib import Path

from .chain_trust import collect_signals, rank_hypotheses, recommend
from .quality import flatten, load_raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnostiquer la confiance dans un lot de messages MQTT bruts")
    parser.add_argument("source", type=Path)
    args = parser.parse_args(argv)

    rows = [flatten(envelope) for envelope in load_raw(args.source)]
    for row in rows:
        row["value"] = float(row["value"])

    signals = collect_signals(rows)
    print(
        f"signaux: {signals.exact_duplicates} doublon(s) exact(s), "
        f"{signals.replay_candidates} candidat(s) de rejeu, "
        f"{signals.temporal_incoherences} incohérence(s) temporelle(s), "
        f"silence non expliqué maximal {signals.unexplained_gap_minutes:.0f} min"
    )
    for hypothesis in rank_hypotheses(signals):
        print(f"  {hypothesis.name}: probabilité {hypothesis.likelihood}, impact {hypothesis.impact} -- {hypothesis.rationale}")
    print(f"recommandation: {recommend(rank_hypotheses(signals))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
