"""CLI d'interrogation du score automatique pour la séquence 5.

Volontairement minimal: cette commande n'affiche que zone, score et
décision -- jamais la formule. Consulter `risk_score.py` avant le débrief
retire tout l'intérêt de l'activité.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .quality import flatten, load_raw
from .risk_score import score_all_zones


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Interroger le score automatique sur une fenêtre de messages")
    parser.add_argument("source", type=Path, help="fenêtre de messages MQTT bruts (JSONL)")
    args = parser.parse_args(argv)

    rows = [flatten(envelope) for envelope in load_raw(args.source)]
    for row in rows:
        row["value"] = float(row["value"])

    for entry in score_all_zones(rows):
        print(f"{entry.zone}: score {entry.score:.0f}/100 -> {entry.decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
