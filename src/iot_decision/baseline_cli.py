"""Interface en ligne de commande de la séquence 1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .baseline import extract_sample, load_raw, recommend, transform_raw, write_csv


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline baseline IoT")
    sub = parser.add_subparsers(dest="command", required=True)
    extract = sub.add_parser("extract-sample", help="copier un échantillon comme brut")
    extract.add_argument("source")
    extract.add_argument("destination")
    transform = sub.add_parser("transform", help="aplatir le JSONL en CSV")
    transform.add_argument("source")
    transform.add_argument("destination")
    decide = sub.add_parser("decide", help="produire la note décisionnelle")
    decide.add_argument("source")
    decide.add_argument("--threshold", type=float, default=35.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "extract-sample":
        print(f"{extract_sample(args.source, args.destination)} messages conservés")
    elif args.command == "transform":
        rows = transform_raw(load_raw(args.source))
        print(f"{write_csv(rows, args.destination)} mesures écrites")
    else:
        rows = transform_raw(load_raw(args.source))
        brief = recommend(rows, threshold=args.threshold)
        print(json.dumps(brief.__dict__, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
