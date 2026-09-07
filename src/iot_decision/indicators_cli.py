"""CLI pédagogique des indicateurs transparents pour la séquence 5."""

from __future__ import annotations

import argparse
from pathlib import Path

from .indicators import duration_above_threshold, find_masked_zones, global_mean, load_measurements, zone_maxima


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Calculer des indicateurs transparents et détecter une zone masquée")
    parser.add_argument("source", type=Path)
    parser.add_argument("--threshold", type=float, default=35.0)
    args = parser.parse_args(argv)

    rows = load_measurements(args.source)
    mean_value = global_mean(rows)
    maxima = zone_maxima(rows)

    print(f"moyenne globale: {mean_value:.2f} °C")
    for zone, value in sorted(maxima.items()):
        print(f"  maximum {zone}: {value:.1f} °C")

    masked = find_masked_zones(rows, threshold=args.threshold)
    if masked:
        for entry in masked:
            duration = duration_above_threshold(rows, entry.zone, args.threshold)
            print(
                f"zone masquée par la moyenne: {entry.zone} "
                f"(maximum {entry.zone_max:.1f} °C >= seuil {args.threshold:g} °C, "
                f"moyenne globale {entry.global_mean_value:.2f} °C ; "
                f"durée observée au-dessus du seuil : {duration:.0f} min)"
            )
    else:
        print(f"aucune zone ne franchit {args.threshold:g} °C alors que la moyenne globale reste en dessous")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
