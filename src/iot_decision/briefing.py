"""Note de briefing: exposer l'incertitude au lieu de la dissimuler dans un graphique.

Une visualisation résume, tout comme un indicateur (voir `indicators.py`): un
choix d'échelle, l'absence d'annotation ou un trait qui relie deux points de
part et d'autre d'un silence peuvent faire disparaître un vide de données
aussi sûrement qu'une moyenne masque une zone. Ce module ne trace rien: il
calcule ce qu'un graphique honnête doit dire et taire, pour que la mise en
forme reste une décision explicite plutôt qu'un hasard esthétique.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .quality import detect_gaps


def zone_series(rows: Iterable[dict], zone: str) -> list[dict]:
    """Mesures d'une seule zone, triées par horodatage de mesure."""
    return sorted((row for row in rows if row["zone"] == zone), key=lambda row: row["measured_at"])


@dataclass(frozen=True)
class ZoneBriefing:
    zone: str
    point_count: int
    above_threshold_count: int
    threshold: float
    max_value: float
    unexplained_gap_minutes: float
    confidence: str
    headline: str
    caveat: str
    verification: str


def summarize_zone(rows: Iterable[dict], zone: str, threshold: float = 35.0) -> ZoneBriefing:
    """Résume une zone pour un briefing: ce que la série montre, ce qu'elle
    ne permet pas d'affirmer, et le niveau de confiance qui en découle.

    Un vide de données qui précède directement la seule mesure haute abaisse
    la confiance, même si le calcul du maximum lui-même reste exact.
    """
    series = zone_series(rows, zone)
    if not series:
        raise ValueError(f"aucune mesure pour la zone {zone}")

    gaps = detect_gaps(series).get(zone, [])
    unexplained_gap_minutes = max((gap["duration_minutes"] for gap in gaps), default=0.0)
    above = [row for row in series if row["value"] >= threshold]
    max_value = max(row["value"] for row in series)

    if unexplained_gap_minutes > 0 and above:
        confidence = "faible"
        caveat = (
            f"la seule mesure au-dessus du seuil suit un vide de "
            f"{unexplained_gap_minutes:.0f} min, non expliqué par un rejet qualité"
        )
        verification = "vérification terrain avant toute conclusion sur cette zone"
    elif above:
        confidence = "moyenne"
        caveat = "aucun vide non expliqué ne précède la mesure haute"
        verification = "confirmer par une deuxième lecture avant action"
    else:
        confidence = "moyenne"
        caveat = f"aucune mesure ne franchit {threshold:g} °C sur la fenêtre observée"
        verification = "surveiller la zone sans action immédiate"

    headline = f"{zone}: {len(above)}/{len(series)} mesure(s) >= {threshold:g} °C, maximum {max_value:.1f} °C"
    return ZoneBriefing(
        zone=zone,
        point_count=len(series),
        above_threshold_count=len(above),
        threshold=threshold,
        max_value=max_value,
        unexplained_gap_minutes=unexplained_gap_minutes,
        confidence=confidence,
        headline=headline,
        caveat=caveat,
        verification=verification,
    )


def briefing_note(summary: ZoneBriefing) -> str:
    """Mini-note au format imposé: message principal, limite, confiance, vérification."""
    return "\n".join((
        f"Message principal : {summary.headline}.",
        f"Limite : {summary.caveat}.",
        f"Niveau de confiance : {summary.confidence}.",
        f"Vérification recommandée : {summary.verification}.",
    ))
