"""Score de risque automatique -- volontairement non documenté aux étudiants
avant le débrief de la séquence 5.

Ce module simule un modèle de décision: une fonction déterministe qui
transforme des mesures en un score, sans que sa logique interne soit
consultée pendant le TP. Sa règle est simple, mais elle encode une
hypothèse cachée: le seuil de 35 °C, calibré une fois sur les cinq zones
d'origine du cours, n'a jamais été revu pour un nouveau type de zone. Sur
une zone de stockage carburant, dont le seuil de sécurité réel est bien
plus bas, ce score reste silencieusement rassurant.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .indicators import duration_above_threshold, zone_maxima

FIXED_THRESHOLD = 35.0  # calibré une fois sur les cinq zones d'origine, jamais révisé
DECISION_CUTOFF = 65.0
MAX_RATIO_CAP = 1.3
DURATION_NORMALIZATION_MINUTES = 30.0


def black_box_score(rows: Iterable[dict], zone: str) -> float:
    """Retourne un score 0-100, en fonction du seul maximum et de la seule
    durée au-dessus d'un seuil fixe de 35 °C -- quelle que soit la zone."""
    materialized = list(rows)
    maxima = zone_maxima(materialized)
    if zone not in maxima:
        raise ValueError(f"zone inconnue: {zone}")
    max_ratio = min(maxima[zone] / FIXED_THRESHOLD, MAX_RATIO_CAP)
    duration = duration_above_threshold(materialized, zone, FIXED_THRESHOLD)
    duration_ratio = min(duration / DURATION_NORMALIZATION_MINUTES, 1.0)
    score = 100 * (0.7 * max_ratio + 0.3 * duration_ratio)
    return max(0.0, min(100.0, score))


def decide(score: float) -> str:
    return "inspection recommandée" if score >= DECISION_CUTOFF else "aucune action requise"


@dataclass(frozen=True)
class ScoreEntry:
    zone: str
    score: float
    decision: str


def score_all_zones(rows: Iterable[dict]) -> list[ScoreEntry]:
    materialized = list(rows)
    zones = sorted(zone_maxima(materialized))
    entries = []
    for zone in zones:
        score = black_box_score(materialized, zone)
        entries.append(ScoreEntry(zone, score, decide(score)))
    return entries
