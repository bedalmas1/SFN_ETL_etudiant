"""Deux mises en forme du même incident: une qui exagère, une qui l'expose.

`create_misleading_chart` et `create_honest_chart` partent exactement des
mêmes points mesurés. Seule la mise en forme change: échelle de l'axe,
trait continu ou rompu au niveau d'un silence, seuil affiché ou non,
annotation ou absence d'annotation. Rien n'est recalculé ni corrigé --
l'écart d'impression vient uniquement du graphique, pas de la donnée.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from .briefing import zone_series
from .indicators import load_measurements
from .quality import detect_gaps


def _iso8601(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"horodatage sans fuseau: {value}")
    return parsed.astimezone(timezone.utc)


def create_misleading_chart(source: str | Path, zone: str, destination: str | Path) -> None:
    """Axe tronqué autour des valeurs observées, trait continu sur le silence,
    aucun seuil affiché: la même hausse paraît spectaculaire et ininterrompue."""
    import matplotlib.pyplot as plt

    rows = load_measurements(source)
    series = zone_series(rows, zone)
    times = [_iso8601(row["measured_at"]) for row in series]
    values = [row["value"] for row in series]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(times, values, marker="o", color="#c0392b", linewidth=2.5)
    margin = max(0.3, (max(values) - min(values)) * 0.15)
    ax.set_ylim(min(values) - margin, max(values) + margin)
    ax.set(
        xlabel="Heure de mesure",
        ylabel="Température (°C)",
        title=f"{zone} -- tendance en hausse",
    )
    fig.autofmt_xdate()
    fig.tight_layout()
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_honest_chart(source: str | Path, zone: str, destination: str | Path,
                         threshold: float = 35.0) -> None:
    """Axe démarrant à zéro, seuil annoté, trait rompu et vide de données
    marqué: la même hausse se lit comme une seule mesure incertaine."""
    import matplotlib.pyplot as plt

    rows = load_measurements(source)
    series = zone_series(rows, zone)
    times = [_iso8601(row["measured_at"]) for row in series]
    values = [row["value"] for row in series]
    gaps = detect_gaps(series).get(zone, [])

    fig, ax = plt.subplots(figsize=(9, 5))

    segment_times: list[datetime] = [times[0]]
    segment_values: list[float] = [values[0]]
    gap_bounds = {(_iso8601(gap["from"]), _iso8601(gap["to"])) for gap in gaps}
    for previous_time, time, value in zip(times, times[1:], values[1:]):
        if (previous_time, time) in gap_bounds:
            ax.plot(segment_times, segment_values, marker="o", color="#1b4f72", linewidth=2)
            segment_times, segment_values = [], []
        segment_times.append(time)
        segment_values.append(value)
    ax.plot(segment_times, segment_values, marker="o", color="#1b4f72", linewidth=2)

    for gap in gaps:
        start, end = _iso8601(gap["from"]), _iso8601(gap["to"])
        ax.axvspan(start, end, color="grey", alpha=0.25)
        ax.annotate(
            f"vide de données ({gap['duration_minutes']:.0f} min)\nnon expliqué par un rejet qualité",
            xy=(start, min(values)), xytext=(8, -32), textcoords="offset points",
            fontsize=8, color="#555555",
        )

    ax.axhline(threshold, color="#922b21", linestyle="--", label=f"seuil pédagogique {threshold:g} °C")
    above = [(time, value) for time, value in zip(times, values) if value >= threshold]
    if above:
        ax.annotate(
            "seule mesure >= seuil,\naprès le vide non expliqué",
            xy=above[0], xytext=(-140, 12), textcoords="offset points", fontsize=8, color="#7d0000",
            arrowprops={"arrowstyle": "->", "color": "#7d0000"},
        )

    ax.set_ylim(0, max(threshold + 5, max(values) + 5))
    ax.set(
        xlabel="Heure de mesure",
        ylabel="Température (°C)",
        title=f"{zone} -- une seule mesure franchit le seuil, après un vide non expliqué",
    )
    ax.legend(loc="lower right")
    ax.grid(axis="y", alpha=.2)
    fig.autofmt_xdate()
    fig.tight_layout()
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Produire les deux graphiques du même incident")
    parser.add_argument("source")
    parser.add_argument("zone")
    parser.add_argument("misleading_destination")
    parser.add_argument("honest_destination")
    parser.add_argument("--threshold", type=float, default=35.0)
    args = parser.parse_args(argv)

    create_misleading_chart(args.source, args.zone, args.misleading_destination)
    create_honest_chart(args.source, args.zone, args.honest_destination, threshold=args.threshold)
    print(args.misleading_destination)
    print(args.honest_destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
