"""Graphique décisionnel minimal: maximum observé par zone et seuil pédagogique."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def create_chart(source: str | Path, destination: str | Path, threshold: float = 35.0) -> None:
    import matplotlib.pyplot as plt

    maxima: dict[str, float] = {}
    with Path(source).open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            maxima[row["zone"]] = max(maxima.get(row["zone"], float("-inf")), float(row["value"]))
    labels = list(sorted(maxima))
    values = [maxima[label] for label in labels]
    colors = ["#c0392b" if value >= threshold else "#2874a6" for value in values]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    bars = ax.barh(labels, values, color=colors)
    ax.axvline(threshold, color="#922b21", linestyle="--", label=f"seuil pédagogique {threshold:g} °C")
    ax.bar_label(bars, fmt="%.1f °C", padding=3)
    ax.set(xlabel="Maximum observé (°C)", title="Batch 001 — maximum observé par zone")
    ax.set_xlim(0, max(threshold + 5, max(values) + 5))
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=.2)
    fig.tight_layout()
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=160)
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
