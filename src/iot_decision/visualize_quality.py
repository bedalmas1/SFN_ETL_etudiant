"""Chronologie décisionnelle: valeurs propres, rejets et silences par zone."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _read_rows(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def create_chart(clean_csv: str | Path, rejected_csv: str | Path, destination: str | Path,
                  *, threshold: float = 35.0, alert_zone: str = "battery-shelter-01",
                  y_range: tuple[float, float] = (24.0, 40.0)) -> None:
    import matplotlib.pyplot as plt

    clean_rows = _read_rows(clean_csv)
    rejected_rows = _read_rows(rejected_csv)
    zones = sorted({row["zone"] for row in clean_rows} | {row["zone"] for row in rejected_rows})
    colors = plt.cm.tab10.colors
    y_low, y_high = y_range

    fig, ax = plt.subplots(figsize=(11, 5.8))
    for index, zone in enumerate(zones):
        points = sorted(
            ((_parse(row["measured_at"]), float(row["value"])) for row in clean_rows if row["zone"] == zone),
            key=lambda point: point[0],
        )
        if points:
            times, values = zip(*points)
            ax.plot(times, values, marker="o", linewidth=1.6, color=colors[index % 10], label=zone)

    rejected_plotted = False
    offscale_plotted = False
    offscale_count = 0
    for row in rejected_rows:
        try:
            value = float(row["value"])
        except (TypeError, ValueError):
            continue
        moment = _parse(row["measured_at"])
        if y_low <= value <= y_high:
            ax.scatter(
                moment, value, marker="x", s=90, linewidths=2.2, color="#7d0a0a", zorder=5,
                label=None if rejected_plotted else "rejeté, dans l'échelle (voir raison)",
            )
            rejected_plotted = True
        else:
            unit = row.get("unit") or "?"
            marker_y = y_high - 0.4 - 0.9 * offscale_count
            ax.scatter(
                moment, marker_y, marker="^", s=110, linewidths=1.5,
                edgecolors="#7d0a0a", facecolors="none", zorder=5,
                label=None if offscale_plotted else "rejeté, hors échelle (valeur annotée)",
            )
            ax.annotate(
                f"{value:g} {unit}", xy=(moment, marker_y), xytext=(10, 0),
                textcoords="offset points", ha="left", va="center", fontsize=8, color="#7d0a0a",
            )
            offscale_plotted = True
            offscale_count += 1

    alert_points = sorted(
        (_parse(row["measured_at"]) for row in clean_rows if row["zone"] == alert_zone)
    )
    if len(alert_points) >= 2:
        gaps = [(a, b) for a, b in zip(alert_points, alert_points[1:]) if (b - a).total_seconds() > 7 * 60]
        for start, end in gaps:
            ax.axvspan(start, end, color="#7d0a0a", alpha=.08)
            ax.annotate(
                "silence réel\n(aucun message reçu)", xy=(start + (end - start) / 2, y_low),
                xytext=(0, 6), textcoords="offset points", ha="center", fontsize=8, color="#7d0a0a",
            )

    ax.axhline(threshold, color="#922b21", linestyle="--", linewidth=1, label=f"seuil pédagogique {threshold:g} °C")
    ax.set_ylim(y_low, y_high)
    ax.set(xlabel="Heure de mesure déclarée (measured_at, UTC)", ylabel="Valeur (°C)",
           title="Batch 002 — fenêtre d'alerte : mesures propres, rejets et silences")
    ax.grid(alpha=.2)
    fig.autofmt_xdate()
    ax.legend(loc="lower right", fontsize=7.5, ncol=2)
    fig.tight_layout()
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=160)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chronologie qualité pour la séquence 4")
    parser.add_argument("clean_csv")
    parser.add_argument("rejected_csv")
    parser.add_argument("destination")
    parser.add_argument("--threshold", type=float, default=35.0)
    parser.add_argument("--alert-zone", default="battery-shelter-01")
    args = parser.parse_args(argv)
    create_chart(args.clean_csv, args.rejected_csv, args.destination,
                 threshold=args.threshold, alert_zone=args.alert_zone)
    print(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
