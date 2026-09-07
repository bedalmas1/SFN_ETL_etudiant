"""Graphique décisionnel: maximum par zone contre la moyenne globale."""

from __future__ import annotations

import argparse
from pathlib import Path

from .indicators import global_mean, load_measurements, zone_maxima


def create_chart(source: str | Path, destination: str | Path, threshold: float = 35.0) -> None:
    import matplotlib.pyplot as plt

    rows = load_measurements(source)
    maxima = zone_maxima(rows)
    mean_value = global_mean(rows)
    labels = sorted(maxima)
    values = [maxima[label] for label in labels]
    colors = ["#c0392b" if value >= threshold else "#2874a6" for value in values]

    fig, ax = plt.subplots(figsize=(10, 5.2))
    bars = ax.barh(labels, values, color=colors)
    ax.axvline(threshold, color="#922b21", linestyle="--", label=f"seuil pédagogique {threshold:g} °C")
    ax.axvline(mean_value, color="#1b4f72", linestyle=":", label=f"moyenne globale {mean_value:.1f} °C")
    ax.bar_label(bars, fmt="%.1f °C", padding=3)
    ax.set(xlabel="Maximum observé (°C)", title="Batch 001 -- maximum par zone contre la moyenne globale")
    ax.set_xlim(0, max(threshold + 5, max(values) + 5))
    ax.legend(loc="lower center", bbox_to_anchor=(.5, 1.14), ncol=2)
    ax.grid(axis="x", alpha=.2)
    fig.tight_layout()
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--threshold", type=float, default=35.0)
    args = parser.parse_args(argv)
    create_chart(args.source, args.destination, args.threshold)
    print(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
