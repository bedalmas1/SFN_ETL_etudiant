"""CLI pédagogique de contrôle qualité pour la séquence 4."""

from __future__ import annotations

import argparse
from pathlib import Path

from .quality import (
    CSV_FIELDS, REJECTED_FIELDS, classify, detect_gaps, diagnose, flatten, load_raw,
    write_csv, write_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Séparer les messages propres des messages rejetés et signaler les silences"
    )
    parser.add_argument("source", type=Path, help="fenêtre de messages MQTT bruts (JSONL)")
    parser.add_argument("clean_csv", type=Path)
    parser.add_argument("rejected_csv", type=Path)
    parser.add_argument("report_json", type=Path)
    parser.add_argument("--alert-zone", default="battery-shelter-01")
    args = parser.parse_args(argv)

    envelopes = load_raw(args.source)
    rows = [flatten(envelope) for envelope in envelopes]
    clean, rejected = classify(rows)
    gaps = detect_gaps(clean)
    report = diagnose(rows, clean, rejected, gaps, alert_zone=args.alert_zone)

    write_csv(clean, CSV_FIELDS, args.clean_csv)
    write_csv(rejected, REJECTED_FIELDS, args.rejected_csv)
    write_report(report, args.report_json)

    print(f"{report.clean_count} lignes propres; {report.rejected_count} lignes rejetées")
    for reason, count in report.rejected_by_reason.items():
        print(f"  - {reason}: {count}")
    if report.gaps_by_zone:
        for zone, zone_gaps in report.gaps_by_zone.items():
            for gap in zone_gaps:
                nature = "silence apparent: expliqué par une ligne rejetée dans cette fenêtre" \
                    if gap["explained_by_rejection"] \
                    else "silence réel: aucune ligne rejetée ne l'explique, un message manque en amont"
                print(f"{zone}: {gap['from']} -> {gap['to']} ({gap['duration_minutes']} min) -- {nature}")
    else:
        print("aucun silence détecté au-delà du seuil de tolérance")
    print(f"confiance: {report.confidence}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
