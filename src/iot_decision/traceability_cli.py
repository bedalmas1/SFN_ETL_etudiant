"""CLI pédagogique de parsing traçable pour la séquence 3."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .traceability import duplicate_candidates, parse_jsonl, verify_traceability, write_structured_csv


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Structurer un JSONL en conservant le lien vers chaque message brut")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parse = subparsers.add_parser("parse", help="produire le CSV structuré")
    parse.add_argument("source", type=Path)
    parse.add_argument("destination", type=Path)
    parse.add_argument("--lenient", action="store_true", help="isoler les lignes invalides au lieu d'arrêter")
    verify = subparsers.add_parser("verify", help="rejouer les empreintes brut/structuré")
    verify.add_argument("source", type=Path)
    verify.add_argument("structured", type=Path)
    duplicate = subparsers.add_parser("candidates", help="signaler les mesures métier qui se ressemblent")
    duplicate.add_argument("structured", type=Path)
    args = parser.parse_args(argv)

    if args.command == "parse":
        rows, issues = parse_jsonl(args.source, strict=not args.lenient)
        count = write_structured_csv(rows, args.destination)
        print(f"{count} lignes structurées; {len(issues)} anomalie(s) isolée(s)")
        return 0 if not issues else 2
    rows = _read_csv(args.structured)
    if args.command == "verify":
        errors = verify_traceability(rows, args.source)
        print("traçabilité vérifiée" if not errors else "\n".join(errors))
        return 0 if not errors else 1
    groups = duplicate_candidates(rows)
    print(f"{len(groups)} groupe(s) candidat(s); aucune suppression automatique")
    for group in groups:
        print(" | ".join(f"{row['message_id']}@L{row['source_line']}" for row in group))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
