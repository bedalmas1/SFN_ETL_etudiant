"""CLI de briefing pour la séquence 6: la note, jamais le graphique.

Affiche le message principal, la limite, le niveau de confiance et la
vérification recommandée pour une zone -- sans dépendre d'un rendu visuel,
pour dissocier ce qu'une décision peut affirmer de la façon dont elle est
présentée à l'écran.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .briefing import briefing_note, summarize_zone
from .indicators import load_measurements


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Produire la note de briefing d'une zone")
    parser.add_argument("source", type=Path, help="table de mesures nettoyée (CSV)")
    parser.add_argument("zone")
    parser.add_argument("--threshold", type=float, default=35.0)
    args = parser.parse_args(argv)

    rows = load_measurements(args.source)
    summary = summarize_zone(rows, args.zone, threshold=args.threshold)
    print(briefing_note(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
