"""Indicateurs transparents: un calcul auditable à la main, ligne par ligne.

Un indicateur est un choix de compression: il rend une question lisible en
résumant beaucoup de valeurs en une seule. Ce module ne cache rien du calcul
lui-même; c'est le résultat du calcul, une fois résumé, qui peut encore
masquer un risque. Comparer à `risk_score.py`, dont la logique n'est
volontairement pas lue avant le débrief.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def _iso8601(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"horodatage sans fuseau: {value}")
    return parsed.astimezone(timezone.utc)


def load_measurements(path: str | Path) -> list[dict]:
    """Charge une table de mesures au format de sortie de la séquence 1."""
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        row["value"] = float(row["value"])
        row["retained"] = str(row["retained"]).lower() == "true"
    return rows


def global_mean(rows: Iterable[dict]) -> float:
    """Moyenne unique sur toutes les lignes, tous zones confondues."""
    materialized = list(rows)
    if not materialized:
        raise ValueError("aucune mesure disponible")
    return sum(row["value"] for row in materialized) / len(materialized)


def zone_maxima(rows: Iterable[dict]) -> dict[str, float]:
    """Maximum observé par zone."""
    maxima: dict[str, float] = {}
    for row in rows:
        zone = str(row["zone"])
        maxima[zone] = max(maxima.get(zone, float("-inf")), row["value"])
    return maxima


def zone_means(rows: Iterable[dict]) -> dict[str, float]:
    """Moyenne par zone, pour comparer à la moyenne globale."""
    totals: dict[str, list[float]] = {}
    for row in rows:
        totals.setdefault(str(row["zone"]), []).append(row["value"])
    return {zone: sum(values) / len(values) for zone, values in totals.items()}


def duration_above_threshold(rows: Iterable[dict], zone: str, threshold: float) -> float:
    """Minutes observées entre la première et la dernière mesure de la zone
    au-dessus du seuil. Ne suppose rien au-delà de la dernière mesure connue:
    si une seule mesure franchit le seuil, la durée observée est nulle."""
    zone_rows = sorted((row for row in rows if row["zone"] == zone), key=lambda row: row["measured_at"])
    above = [row for row in zone_rows if row["value"] >= threshold]
    if not above or not zone_rows:
        return 0.0
    first_above = _iso8601(str(above[0]["measured_at"]))
    last = _iso8601(str(zone_rows[-1]["measured_at"]))
    return max(0.0, (last - first_above).total_seconds() / 60)


@dataclass(frozen=True)
class MaskedZone:
    zone: str
    zone_max: float
    global_mean_value: float


def find_masked_zones(rows: Iterable[dict], threshold: float = 35.0) -> list[MaskedZone]:
    """Zones dont le maximum franchit le seuil alors que la moyenne globale
    reste en dessous: exactement ce que la moyenne seule ne montre pas."""
    materialized = list(rows)
    mean_value = global_mean(materialized)
    maxima = zone_maxima(materialized)
    if mean_value >= threshold:
        return []
    return [
        MaskedZone(zone, value, mean_value)
        for zone, value in sorted(maxima.items())
        if value >= threshold
    ]
