"""Graphique de débrief: le score automatique traite toutes les zones avec
la même règle, y compris une zone jamais vue à sa calibration."""

from __future__ import annotations

import argparse
from pathlib import Path

from .quality import flatten, load_raw
from .risk_score import DECISION_CUTOFF, score_all_zones


def create_chart(known_source: str | Path, shift_source: str | Path, destination: str | Path,
                  *, shifted_zone: str = "fuel-storage-01") -> None:
    import matplotlib.pyplot as plt

    rows = []
    for source in (known_source, shift_source):
        for envelope in load_raw(source):
            row = flatten(envelope)
            row["value"] = float(row["value"])
            rows.append(row)

    entries = score_all_zones(rows)
    labels = [entry.zone for entry in entries]
    values = [entry.score for entry in entries]
    colors = ["#b7950b" if zone == shifted_zone else
              ("#c0392b" if score >= DECISION_CUTOFF else "#2874a6")
              for zone, score in zip(labels, values)]

    fig, ax = plt.subplots(figsize=(10, 5.4))
    bars = ax.barh(labels, values, color=colors)
    ax.axvline(DECISION_CUTOFF, color="#922b21", linestyle="--",
               label=f"seuil de décision du score {DECISION_CUTOFF:g}/100")
    ax.bar_label(bars, fmt="%.0f/100", padding=3)
    ax.set(xlabel="Score automatique (0-100)",
           title="Score automatique par zone -- une règle unique, cinq zones connues et une nouvelle")
    ax.set_xlim(0, 100)
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=.2)
    if shifted_zone in labels:
        ax.annotate(
            f"{shifted_zone} : jamais vue à la calibration du score\n"
            "(seuil de sécurité réel du carburant plus bas que 35 °C)",
            xy=(values[labels.index(shifted_zone)], labels.index(shifted_zone)),
            xytext=(12, -28), textcoords="offset points", fontsize=8, color="#7d5b00",
        )
    fig.tight_layout()
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=160)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("known_source")
    parser.add_argument("shift_source")
    parser.add_argument("destination")
    args = parser.parse_args(argv)
    create_chart(args.known_source, args.shift_source, args.destination)
    print(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
