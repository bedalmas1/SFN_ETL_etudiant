"""Diagnostic de confiance dans la chaîne, pas dans la seule valeur mesurée.

Ce module ne recalcule rien de nouveau: il relit des signaux déjà détectés
par les séquences précédentes (doublon exact, candidat de rejeu, incohérence
temporelle, silence) et les relie à des hypothèses opérationnelles
concurrentes -- incident réel, panne capteur, problème réseau, suspicion
data/cyber -- chacune avec sa probabilité et son impact déclarés, jamais un
verdict unique. Un candidat de rejeu (même mesure, identité de message
différente) peut passer chaque contrôle de qualité ligne à ligne sans être
détecté: seul le rapprochement entre plusieurs messages le révèle.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from .quality import classify, detect_gaps
from .traceability import duplicate_candidates

_LIKELIHOOD_ORDER = {"faible": 0, "moyenne": 1, "forte": 2}
_IMPACT_ORDER = {"faible": 0, "moyen": 1, "élevé": 2}


def _iso8601(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"horodatage sans fuseau: {value}")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class ChainSignals:
    exact_duplicates: int
    replay_candidates: int
    temporal_incoherences: int
    unexplained_gap_minutes: float


def collect_signals(rows: list[dict]) -> ChainSignals:
    """Rassemble, sans les recalculer, les signaux déjà détectables par
    `quality.classify` et `traceability.duplicate_candidates`."""
    clean_rows, rejected_rows = classify(rows)

    replay_groups = [
        group for group in duplicate_candidates(rows)
        if len({row["message_id"] for row in group}) > 1
    ]

    temporal_incoherences = sum(
        1 for row in rejected_rows
        if str(row["rejection_reason"]).startswith("incohérence temporelle")
    )
    exact_duplicates = sum(
        1 for row in rejected_rows if row["rejection_reason"] == "doublon exact"
    )

    gaps_by_zone = detect_gaps(clean_rows)
    unexplained_gap_minutes = 0.0
    for zone, gaps in gaps_by_zone.items():
        zone_rejected = [row for row in rejected_rows if row["zone"] == zone]
        for gap in gaps:
            start, end = _iso8601(gap["from"]), _iso8601(gap["to"])
            explained = any(start < _iso8601(str(row["measured_at"])) < end for row in zone_rejected)
            if not explained:
                unexplained_gap_minutes = max(unexplained_gap_minutes, gap["duration_minutes"])

    return ChainSignals(
        exact_duplicates=exact_duplicates,
        replay_candidates=len(replay_groups),
        temporal_incoherences=temporal_incoherences,
        unexplained_gap_minutes=unexplained_gap_minutes,
    )


@dataclass(frozen=True)
class Hypothesis:
    name: str
    likelihood: str
    impact: str
    rationale: str


def rank_hypotheses(signals: ChainSignals) -> list[Hypothesis]:
    """Classe quatre hypothèses concurrentes par probabilité puis impact.

    Chaque règle est fixe et documentée ici: aucune ne "sait" quoi que ce
    soit sur l'intention derrière les messages, elle relie seulement un
    signal observable à une hypothèse candidate.
    """
    hypotheses = [
        Hypothesis(
            "suspicion data/cyber",
            likelihood=(
                "forte" if signals.replay_candidates else
                "moyenne" if signals.temporal_incoherences else "faible"
            ),
            impact="élevé" if (signals.replay_candidates or signals.temporal_incoherences) else "faible",
            rationale=(
                f"{signals.replay_candidates} candidat(s) de rejeu (même mesure, identité différente) et "
                f"{signals.temporal_incoherences} incohérence(s) temporelle(s) détectée(s)"
            ),
        ),
        Hypothesis(
            "problème réseau",
            likelihood="forte" if signals.unexplained_gap_minutes > 0 else "faible",
            impact="moyen",
            rationale=(
                f"silence non expliqué de {signals.unexplained_gap_minutes:.0f} min"
                if signals.unexplained_gap_minutes else "aucun silence non expliqué"
            ),
        ),
        Hypothesis(
            "panne capteur",
            likelihood="moyenne" if signals.exact_duplicates else "faible",
            impact="moyen",
            rationale=(
                f"{signals.exact_duplicates} retransmission(s) exacte(s) détectée(s)"
                if signals.exact_duplicates else "aucune retransmission détectée"
            ),
        ),
        Hypothesis(
            "incident réel",
            likelihood="faible",
            impact="élevé",
            rationale=(
                "aucun franchissement de seuil observé sur ce lot; les signaux détectés "
                "concernent l'identité et la régularité des messages, pas leur valeur physique"
            ),
        ),
    ]
    return sorted(
        hypotheses,
        key=lambda h: (_LIKELIHOOD_ORDER[h.likelihood], _IMPACT_ORDER[h.impact]),
        reverse=True,
    )


def recommend(hypotheses: Iterable[Hypothesis]) -> str:
    """Réponse à la question directrice: peut-on agir sur ces données ?"""
    top = next(iter(hypotheses))
    if top.name == "suspicion data/cyber" and top.likelihood in ("forte", "moyenne"):
        return (
            "ne pas agir directement sur ces données: isoler le lot, vérifier l'identité et "
            "la source des messages suspects avant toute décision opérationnelle"
        )
    if top.name == "problème réseau" and top.likelihood == "forte":
        return "ne pas conclure sur les zones touchées par le silence: vérifier la connectivité avant toute décision"
    return "poursuivre l'analyse avec les réserves habituelles du cours"
