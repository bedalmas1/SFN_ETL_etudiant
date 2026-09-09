"""
Avant d'exécuter ce fichier, pensez à exécuter :

    export PYTHONPATH=src

depuis la racine.

Une seule exception au reste de ce fichier : `score_all_zones`, importé
ci-dessous, est une boîte noire fournie par la supervision. Tout le reste
(lecture des fichiers, calculs, graphiques, note de briefing) se code dans
ce fichier, avec la seule bibliothèque standard de Python (`csv`, `json`,
`datetime`) et `matplotlib`.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from iot_decision.risk_score import score_all_zones  # boîte noire -- ne pas lire avant l'étape 3 terminée

ROOT = Path(__file__).resolve().parents[2]
FIGURES = Path(__file__).resolve().parent / "slides" / "figures"


def etape1_indicateurs() -> None:
    """Chapitre 1 -- une moyenne peut-elle masquer une zone ?

    Le chargement est fait : `rows` est une liste de dictionnaires, un par
    ligne du CSV, avec une clé `"value"` déjà convertie en nombre.

    À vous d'écrire, à partir de `rows` :
    - la moyenne globale (somme des `"value"` divisée par leur nombre) ;
    - le maximum de chaque zone (un dictionnaire zone -> maximum) ;
    - la ou les zones dont le maximum dépasse 35.0 alors que la moyenne
      globale, elle, reste en dessous de 35.0 ;
    - un `print` pour chacun de ces trois résultats.
    """
    with open(ROOT / "data/processed/batch001_measurements.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["value"] = float(row["value"])

    raise NotImplementedError("étape 1 à compléter : moyenne, maxima, zone masquée")


def etape2_score_zones_connues() -> None:
    """Chapitre 2 -- le score confirme-t-il ce que la moyenne a caché ?

    Le chargement est fait : `rows` est une liste de dictionnaires, un par
    mesure, avec `"zone"`, `"value"` (déjà converti en nombre) et
    `"measured_at"`.

    À vous d'appeler `score_all_zones(rows)` -- fourni, à ne pas lire -- et
    d'afficher, pour chaque entrée retournée, la zone, le score et la
    décision affichée. Ne pas ouvrir `risk_score.py` avant le débrief de
    l'étape 3.
    """
    rows = []
    with open(ROOT / "data/raw/batch001_raw.jsonl", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            payload = json.loads(line)["payload"]
            payload["value"] = float(payload["value"])
            rows.append(payload)

    raise NotImplementedError("étape 2 à compléter : score des cinq zones connues")


def etape3_nouvelle_zone() -> None:
    """Chapitre 3 -- une sixième zone, jamais vue à la calibration.

    Le chargement est fait, sur `data/samples/batch003_shift_scenario.jsonl`
    (`fuel-storage-01` uniquement). Même démarche qu'à l'étape 2 : appeler
    `score_all_zones`, afficher le score et la décision, puis répondre par
    écrit dans `cas_fil_rouge.md` : ce score a-t-il déjà vu une zone de
    stockage carburant pendant sa calibration ?
    """
    rows = []
    with open(ROOT / "data/samples/batch003_shift_scenario.jsonl", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            payload = json.loads(line)["payload"]
            payload["value"] = float(payload["value"])
            rows.append(payload)

    raise NotImplementedError("étape 3 à compléter : score de fuel-storage-01")


def etape4_extraction_apres_midi() -> list[dict]:
    """Chapitre 4a -- extraire et assembler le relevé d'après-midi.

    Le chargement des deux fichiers `fuel-storage-01` est fait : `rows`
    contient déjà les huit mesures de la journée (matin + après-midi),
    triées par `"measured_at"`.

    À vous d'écrire :
    - `rows` complet dans `data/processed/batch003_measurements.csv`
      (`csv.DictWriter`, `fieldnames = list(rows[0].keys())`) ;
    - le sous-ensemble des lignes dont `"measured_at"` est supérieur ou égal
      à `"2026-11-02T10:00:00Z"` dans `data/processed/batch003_afternoon_window.csv` ;
    - et retourner ce sous-ensemble : les étapes suivantes le réutilisent.
    """
    rows = []
    for filename in (
        "data/samples/batch003_shift_scenario.jsonl",
        "data/samples/batch003_fuel_storage_extended.jsonl",
    ):
        with open(ROOT / filename, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                payload = json.loads(line)["payload"]
                payload["value"] = float(payload["value"])
                rows.append(payload)
    rows.sort(key=lambda row: row["measured_at"])

    raise NotImplementedError("étape 4 à compléter : extraction et fenêtre d'après-midi")


def etape5_deux_graphiques() -> None:
    """Chapitre 4b -- le même graphique, deux seuils.

    Le chargement est fait : `rows` contient les trois mesures de la fenêtre
    d'après-midi, triées, avec `"value"` déjà en nombre.

    À vous d'écrire une fonction `tracer(threshold, destination)` qui :
    - trace `value` en fonction de `measured_at` (un `ax.plot` ou
      `ax.scatter` suffit, pas besoin d'annotation) ;
    - trace une ligne horizontale au niveau de `threshold` (`ax.axhline`) ;
    - donne un titre qui mentionne `threshold` -- pensez à utiliser la
      variable, pas un texte écrit en dur, sinon le titre du second
      graphique restera celui du premier ;
    - enregistre la figure dans `destination`.

    Appelez cette fonction deux fois : une fois avec `threshold=35.0`
    (seuil pédagogique), une fois avec `threshold=28.0` (seuil réel de
    sécurité carburant), vers deux fichiers différents de `FIGURES`.
    """
    with open(ROOT / "data/processed/batch003_afternoon_window.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["value"] = float(row["value"])
    rows.sort(key=lambda row: row["measured_at"])

    raise NotImplementedError("étape 5 à compléter : graphique à 35 °C puis à 28 °C")


def etape6_note_de_briefing() -> None:
    """Chapitre 5 -- la note de briefing finale.

    Le chargement est fait, comme à l'étape 5.

    Avec `threshold = 28.0`, à vous d'écrire :
    - le nombre de mesures `>= threshold`, sur le nombre total de mesures ;
    - la valeur maximale observée ;
    - le plus grand écart, en minutes, entre deux mesures consécutives
      (`datetime.fromisoformat(valeur.replace("Z", "+00:00"))` sur
      `"measured_at"`, puis la différence des deux dates) ;
    - une confiance : `"faible"` si au moins une mesure dépasse `threshold`
      et que cet écart maximal dépasse 7 minutes, `"moyenne"` sinon ;
    - un `print` avec message principal, limite, confiance et vérification
      recommandée.

    Relisez ensuite votre propre note : correspond-elle exactement à ce que
    montrent vos trois mesures ?
    """
    with open(ROOT / "data/processed/batch003_afternoon_window.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["value"] = float(row["value"])
    rows.sort(key=lambda row: row["measured_at"])

    raise NotImplementedError("étape 6 à compléter : note de briefing sur fuel-storage-01")


def etape7_recommandation_finale() -> str:
    """Chapitre 5 -- votre recommandation, en une fois.

    Rédiger ici, en moins de 100 mots, la recommandation finale sur
    `fuel-storage-01` : décision, confiance, deux preuves chiffrées
    (fichier + valeur), et ce que le dossier ne permet toujours pas
    d'affirmer. Retourner ce texte sous forme de chaîne de caractères.
    """
    raise NotImplementedError("étape 7 à compléter : recommandation finale rédigée")


ETAPES = (
    etape1_indicateurs,
    etape2_score_zones_connues,
    etape3_nouvelle_zone,
    etape4_extraction_apres_midi,
    etape5_deux_graphiques,
    etape6_note_de_briefing,
    etape7_recommandation_finale,
)


def main() -> int:
    for etape in ETAPES:
        print(f"\n--- {etape.__name__} ---")
        try:
            result = etape()
            if isinstance(result, str):
                print(result)
        except NotImplementedError as exc:
            print(f"(pas encore complétée : {exc})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
