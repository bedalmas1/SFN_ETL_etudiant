"""CLI pédagogique pour la séquence 2."""

from __future__ import annotations

import argparse
from pathlib import Path

from .source_inventory import diagnose, inventory, load_expected, load_jsonl, write_inventory, write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inventorier un instantané MQTT et tester sa complétude")
    parser.add_argument("sample", type=Path)
    parser.add_argument("expected", type=Path)
    parser.add_argument("inventory_csv", type=Path)
    parser.add_argument("report_json", type=Path)
    args = parser.parse_args(argv)
    rows = inventory(load_jsonl(args.sample))
    report = diagnose(rows, load_expected(args.expected))
    write_inventory(rows, args.inventory_csv)
    write_report(report, args.report_json)
    print(f"{report.observed_count}/{report.expected_count} topics attendus observés")
    print(f"lot complet: {'oui' if report.complete else 'non'}; confiance: {report.confidence}")
    for topic in report.missing_topics:
        print(f"absent: {topic}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
