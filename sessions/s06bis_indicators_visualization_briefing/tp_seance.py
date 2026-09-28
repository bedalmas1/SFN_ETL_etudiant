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
from datetime import datetime, timedelta, timezone
from pathlib import Path

from iot_decision.risk_score import score_all_zones  # boîte noire -- ne pas lire avant l'étape 3 terminée

ROOT = Path(__file__).resolve().parents[2]
FIGURES = Path(__file__).resolve().parent / "slides" / "figures"


# ---------------------------------------------------------------------------
# Étape 1 -- indicateurs transparents
# ---------------------------------------------------------------------------


def etape1_indicateurs() -> None:
    """SOCLE -- Chapitre 1 : une moyenne peut-elle masquer une zone ?

    Le chargement est fait : `rows` est une liste de dictionnaires, un par
    ligne du CSV, avec une clé `"value"` déjà convertie en nombre.

    À obtenir et afficher :
    - la moyenne globale ;
    - le maximum, le minimum et l'amplitude (maximum - minimum) de chaque zone ;
    - la ou les zones dont le maximum dépasse 35.0 alors que la moyenne
      globale, elle, reste en dessous ;
    - la zone dont l'amplitude est la plus large.
    """
    with open(ROOT / "data/processed/batch001_measurements.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["value"] = float(row["value"])

    raise NotImplementedError("étape 1 à compléter : moyenne, maxima, minima, amplitudes, zone masquée")


def etape1_approfondissement_classements() -> None:
    """APPROFONDISSEMENT -- le classement des zones dépend de l'indicateur choisi.

    Sur le même fichier, calculez pour chaque zone trois indicateurs de plus :
    - la moyenne de la zone ;
    - la dernière valeur mesurée, **et l'heure à laquelle elle a été mesurée** ;
    - la tendance, en °C par heure (écart entre dernière et première valeur,
      rapporté au temps réellement écoulé entre les deux).

    Affichez ensuite un tableau : une ligne par zone, une colonne par
    indicateur (maximum, amplitude, moyenne de zone, dernière valeur,
    tendance), et le **rang** de la zone pour chaque indicateur.

    À trancher par écrit dans `cas_fil_rouge.md` (chapitre 1) :
    - le classement est-il le même pour tous les indicateurs ? Quelles zones
      échangent leur place, et selon quel indicateur ?
    - les « dernières valeurs » des cinq zones sont-elles comparables entre
      elles ? (regardez les heures)
    - rédigez la **fiche indicateur** demandée au chapitre 1 : l'indicateur
      unique que vous mettriez sur le tableau de bord du commandant, la
      question qu'il sert, sa formule, son seuil, sa fenêtre de temps, et
      ce qu'il ne verra jamais. Vous la défendrez face au binôme voisin.
    """
    raise NotImplementedError("étape 1 -- approfondissement : tableau de classement multi-indicateurs")


def etape1_defi_nouvel_indicateur() -> None:
    """DÉFI (BONUS, non exigé) -- inventer un indicateur qui change encore le classement.

    Inventez un indicateur absent de la liste ci-dessus (par exemple une
    projection, un indicateur de fraîcheur, une combinaison...), codez-le,
    et montrez qu'il produit un classement différent de tous les autres.
    Écrivez en une phrase la question de décision qu'il sert -- et celle
    pour laquelle il serait dangereux.
    """
    raise NotImplementedError("étape 1 -- défi (bonus) : un indicateur inventé")


# ---------------------------------------------------------------------------
# Étape 2 -- interroger le score sans le lire
# ---------------------------------------------------------------------------


def _mesures_synthetiques(
    valeurs: list[float],
    pas_minutes: float = 5,
    zone: str = "sonde-01",
    asset_type: str = "inconnu",
    debut: str = "2026-11-02T12:00:00Z",
) -> list[dict]:
    """Utilitaire déjà écrit : fabrique une série de mesures fictives, une
    toutes les `pas_minutes`, au format attendu par `score_all_zones`.

    Exemple : `_mesures_synthetiques([30, 30, 36], pas_minutes=10)`.
    Pour une série irrégulière, fabriquez deux séries et concaténez-les.
    """
    t0 = datetime.fromisoformat(debut.replace("Z", "+00:00"))
    return [
        {
            "zone": zone,
            "asset_type": asset_type,
            "sensor": "temperature",
            "value": float(valeur),
            "measured_at": (t0 + timedelta(minutes=i * pas_minutes)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        for i, valeur in enumerate(valeurs)
    ]


def etape2_score_zones_connues() -> None:
    """SOCLE -- Chapitre 2 : le score confirme-t-il ce que la moyenne a caché ?

    Le chargement est fait : `rows` est une liste de dictionnaires, un par
    mesure, avec `"zone"`, `"value"` (déjà converti en nombre) et
    `"measured_at"`.

    Appelez `score_all_zones(rows)` -- fourni, mais méthode à ne pas lire -- et affichez,
    pour chaque entrée retournée, la zone, le score et la décision.
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


def etape2_approfondissement_sondes() -> None:
    """APPROFONDISSEMENT -- enquête sur la boîte noire, sans l'ouvrir.

    Vous ne pouvez pas lire `risk_score.py`. Vous pouvez en revanche lui
    soumettre des mesures que **vous** fabriquez avec `_mesures_synthetiques`
    et observer ce qu'il répond : c'est ainsi qu'on audite un système dont
    on n'a pas le code.

    1. Avant de coder, écrivez dans `cas_fil_rouge.md` (chapitre 2) au
       moins quatre hypothèses sur ce qui fait monter le score (la
       moyenne ? le maximum ? la durée ? le type de zone ? le nom ?...).
    2. Concevez au moins **huit sondes**, chacune ne faisant varier
       **qu'un seul facteur** par rapport à une sonde de référence, et
       affichez pour chacune : ce qu'elle teste, le score, la décision.
    3. Concluez : quels facteurs le score prend-il en compte ? lesquels
       ignore-t-il ? Proposez une formule, même approximative, et la valeur
       de température à partir de laquelle une zone bascule en
       « inspection recommandée ».

    Vous confronterez votre formule au vrai code seulement à l'étape 3.
    """
    raise NotImplementedError("étape 2 -- approfondissement : plan de sondes de la boîte noire")


def etape2_defi_bascule_minimale() -> None:
    """DÉFI (BONUS, non exigé) -- la plus petite série qui fait basculer le score.

    Trouvez, uniquement par sondes, la série de mesures la plus « modeste »
    (définissez vous-même ce que « modeste » veut dire) qui fait passer le
    score en « inspection recommandée ». Cherchez aussi une série où la
    zone est **redescendue** sous le seuil mais reste signalée : que dit-elle
    de la façon dont le score compte le temps ?
    """
    raise NotImplementedError("étape 2 -- défi (bonus) : seuil de bascule")


# ---------------------------------------------------------------------------
# Étape 3 -- une sixième zone, hors calibration
# ---------------------------------------------------------------------------


def etape3_nouvelle_zone() -> None:
    """SOCLE -- Chapitre 3 : une sixième zone, jamais vue à la calibration.

    Le chargement est fait, sur `data/samples/batch003_shift_scenario.jsonl`
    (`fuel-storage-01` uniquement). Même démarche qu'à l'étape 2 : appeler
    `score_all_zones`, afficher le score et la décision.

    Ensuite seulement, ouvrez `src/iot_decision/risk_score.py` et comparez
    sa logique à la formule que vous aviez reconstruite par sondes.
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


def etape3_approfondissement_score_v2() -> None:
    """APPROFONDISSEMENT -- réparer le score, et dire ce que la réparation ne répare pas.

    La table `data/samples/batch005_asset_thresholds.csv` donne un seuil par
    couple (type d'installation, capteur). Écrivez ici une fonction
    `score_v2(rows, seuils)` qui reprend la logique de `risk_score.py` mais
    utilise, pour chaque zone, le seuil de température de son `asset_type`.

    Appliquez `score_v2` aux cinq zones connues (`batch001_raw.jsonl`) puis
    à `fuel-storage-01` (matin). Les zones connues changent-elles de
    décision ? Et `fuel-storage-01` ?

    Puis remplissez, dans `cas_fil_rouge.md` (chapitre 3), la **fiche de
    domaine de validité** du score d'origine : données d'entrée, types de
    zones couverts, hypothèses implicites, cas hors domaine connus, qui doit
    réviser le score et quand.
    """
    raise NotImplementedError("étape 3 -- approfondissement : score_v2 à seuil par type d'installation")


def etape3_defi_septieme_zone() -> None:
    """DÉFI (BONUS, non exigé) -- la zone qui casserait aussi `score_v2`.

    En relisant la table des seuils, fabriquez (avec `_mesures_synthetiques`)
    une septième zone plausible sur laquelle `score_v2` se tromperait
    encore -- soit en alertant à tort, soit en restant silencieux. Montrez
    le score obtenu et expliquez l'hypothèse de `score_v2` qu'elle viole.
    """
    raise NotImplementedError("étape 3 -- défi (bonus) : une zone qui casse score_v2")


# ---------------------------------------------------------------------------
# Étape 4 -- extraction, et choix de la fenêtre
# ---------------------------------------------------------------------------


def etape4_extraction_apres_midi() -> list[dict]:
    """SOCLE -- Chapitre 4a : extraire et assembler le relevé.

    Le chargement des deux fichiers `fuel-storage-01` est fait : `rows`
    contient les huit mesures de la journée, triées par `"measured_at"`.

    À écrire :
    - `rows` complet dans `data/processed/batch003_measurements.csv` ;
    - les lignes à partir de `"2026-11-02T10:00:00Z"` dans
      `data/processed/batch003_afternoon_window.csv` ;
    - retourner ce sous-ensemble.
    """
    rows = _lire_journee_jsonl()

    raise NotImplementedError("étape 4 à compléter : extraction et fenêtre d'après-midi")


def _lire_journee_jsonl() -> list[dict]:
    """Utilitaire déjà écrit : les huit mesures `fuel-storage-01` de la
    journée (matin + après-midi), valeurs converties, triées par heure."""
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
    return rows


def _lire_fenetre_apres_midi() -> list[dict]:
    """Utilitaire déjà écrit : recharge `batch003_afternoon_window.csv`,
    valeurs converties en nombre, trié par `measured_at`."""
    with open(ROOT / "data/processed/batch003_afternoon_window.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["value"] = float(row["value"])
    rows.sort(key=lambda row: row["measured_at"])
    return rows


def etape4_approfondissement_fenetres() -> None:
    """APPROFONDISSEMENT -- le choix de la fenêtre est un levier comme un autre.

    Sur les huit mesures de la journée (`_lire_journee_jsonl()`), comparez
    trois fenêtres : le matin (avant 10:00), l'après-midi (à partir de
    10:00), la journée entière. Pour chacune, affichez : nombre de mesures,
    nombre et proportion de mesures >= 28 °C, minimum, maximum, moyenne,
    plus grand écart entre deux mesures consécutives (en minutes).

    Affichez aussi, pour chaque mesure, son numéro `sequence`.

    À trancher par écrit dans `cas_fil_rouge.md` (chapitre 4) :
    - la conclusion « 1 mesure sur 3 au-dessus du seuil réel » est-elle
      vraie ? est-elle représentative de la journée ?
    - que s'est-il passé entre la dernière mesure du matin et la première
      de l'après-midi ? Listez au moins **quatre hypothèses** physiques ou
      techniques, et pour chacune la vérification qui la confirmerait.
    - les numéros de séquence permettent-ils de dire si les silences
      viennent du réseau (messages perdus) ou du capteur (messages jamais
      émis) ?
    - qui a choisi, dans ce TP, de ne tracer que l'après-midi ? Ce choix
      est-il écrit quelque part dans le dossier transmis au commandant ?
    """
    raise NotImplementedError("étape 4 -- approfondissement : comparaison de trois fenêtres")


def etape4_defi_fenetre_inverse() -> None:
    """DÉFI (BONUS, non exigé) -- deux fenêtres plausibles, deux conclusions opposées.

    Trouvez deux fenêtres de temps, chacune justifiable par une phrase
    d'apparence neutre (« depuis la reprise », « la dernière demi-heure »...),
    qui mènent à des conclusions opposées sur `fuel-storage-01`. Affichez
    les deux phrases et les chiffres qui les accompagnent.
    """
    raise NotImplementedError("étape 4 -- défi (bonus) : fenêtres contradictoires")


# ---------------------------------------------------------------------------
# Étape 5 -- graphiques trompeurs
# ---------------------------------------------------------------------------


def etape5_graphique_trompeur() -> None:
    """SOCLE -- Chapitre 4b : un graphique trompeur, honnêtement obtenu.

    À partir des trois mesures de `_lire_fenetre_apres_midi()`, construisez
    un graphique qui cumule, sans modifier aucune valeur :
    - un axe du temps où les trois points sont régulièrement espacés,
      quelle que soit la durée réelle entre eux ;
    - un axe des ordonnées resserré autour des valeurs observées ;
    - aucun seuil affiché, un trait continu sur tout le relevé.

    Enregistrez vers `FIGURES / "fuel_storage_misleading_scale.png"` et
    affichez un `print` décrivant chacun des choix effectués.
    Ne corrigez rien à ce stade.
    """
    rows = _lire_fenetre_apres_midi()

    raise NotImplementedError("étape 5 à compléter : graphique trompeur, honnêtement obtenu")


def etape5_approfondissement_commande(lettre: str = "A") -> None:
    """APPROFONDISSEMENT -- atelier « commande cachée ».

    L'enseignant vous remet une carte de `cartes_commande.md` (lettre A à F).
    Ne la montrez pas au binôme voisin.

    Produisez la figure qui remplit cette commande, avec **toutes** les
    mesures disponibles de la journée si vous le souhaitez, sans modifier ni
    supprimer aucune valeur à l'intérieur de la fenêtre que vous choisissez.
    Tous les leviers sont permis : fenêtre, échelle, espacement du temps,
    seuil (choisi ou omis), titre, couleurs, annotations.

    Enregistrez vers `FIGURES / f"fuel_storage_commande_{lettre}.png"` et
    listez par `print` chaque levier actionné.

    Ensuite, échangez **uniquement la figure** avec un autre binôme : il
    doit deviner votre commande et nommer vos leviers, à l'aide de la grille
    de détection du chapitre 4 de `cas_fil_rouge.md`.
    """
    raise NotImplementedError("étape 5 -- approfondissement : figure de commande cachée")


def etape5_defi_double_commande() -> None:
    """DÉFI (BONUS, non exigé) -- une seule figure, deux lectures.

    Produisez une figure unique qui semble rassurante à un lecteur qui ne
    lit que le titre, et alarmante à un lecteur qui lit les axes et la
    légende -- ou l'inverse. Enregistrez vers
    `FIGURES / "fuel_storage_double_lecture.png"`.
    """
    raise NotImplementedError("étape 5 -- défi (bonus) : figure à double lecture")


# ---------------------------------------------------------------------------
# Étape 6 -- graphiques honnêtes
# ---------------------------------------------------------------------------


def etape6_deux_graphiques_honnetes() -> None:
    """SOCLE -- Chapitre 4c : le même relevé, deux seuils, mise en forme honnête.

    **Avant de coder : 5 minutes de maquette papier** (croquis dans
    `cas_fil_rouge.md` ou sur feuille). Contrainte : le commandant regarde
    la figure 5 secondes sur une tablette, sans légende orale.

    Écrivez une fonction `tracer_honnete(threshold, destination)` qui
    corrige, un par un, les choix de l'étape 5 :
    - le temps est représenté à l'échelle réelle ;
    - un silence de plus de 7 minutes entre deux mesures n'est pas relié par
      un trait, et il est rendu visible et annoté avec sa durée ;
    - le seuil est tracé et légendé ;
    - l'axe des ordonnées démarre à 0 ;
    - le titre dépend du seuil tracé.

    Appelez-la deux fois, en ne changeant que `threshold` : 35.0 vers
    `FIGURES / "fuel_storage_pedagogical_threshold.png"`, puis 28.0 vers
    `FIGURES / "fuel_storage_real_threshold.png"`.
    """
    rows = _lire_fenetre_apres_midi()

    raise NotImplementedError("étape 6 à compléter : graphique à 35 °C puis à 28 °C, mise en forme honnête")


def etape6_approfondissement_titre_message() -> None:
    """APPROFONDISSEMENT -- titre descriptif ou titre-message ?

    Un titre descriptif dit ce qui est tracé (« fuel-storage-01 -- seuil à
    28 °C »). Un titre-message dit ce qu'il faut en retenir (« dernière
    mesure au-dessus du seuil réel, après 25 min sans données »).

    Produisez une troisième version de la figure à 28 °C dont le titre est
    un titre-message **calculé à partir des données** (nombre de mesures au
    seuil, durée du plus long silence) -- jamais écrit à la main --, vers
    `FIGURES / "fuel_storage_real_threshold_message.png"`.

    À trancher par écrit : un titre-message est-il plus honnête ou moins
    honnête qu'un titre descriptif ? Qu'est-ce qui le rend acceptable ?
    Que devient-il si quelqu'un réutilise la figure avec un autre fichier ?
    """
    raise NotImplementedError("étape 6 -- approfondissement : titre-message calculé")


def etape6_defi_journee_complete() -> None:
    """DÉFI (BONUS, non exigé) -- toute la journée, deux seuils, lisible en 5 secondes.

    Une seule figure, sur les huit mesures de la journée, avec les deux
    seuils (35 et 28 °C) distingués sans ambiguïté et les deux silences
    annotés. Vers `FIGURES / "fuel_storage_journee.png"`. Faites-la lire
    5 secondes à quelqu'un d'un autre binôme, puis demandez-lui ce qu'il a
    retenu : notez sa réponse dans `cas_fil_rouge.md`.
    """
    raise NotImplementedError("étape 6 -- défi (bonus) : figure journée complète")


# ---------------------------------------------------------------------------
# Étape 7 -- note de briefing
# ---------------------------------------------------------------------------


def regle_confiance(rows: list[dict], threshold: float) -> str:
    """À CONCEVOIR (socle de l'étape 7) -- votre règle de confiance.

    Aucune règle n'est fournie. En binôme, listez dans `cas_fil_rouge.md`
    (chapitre 5) au moins **quatre critères** qui devraient, selon vous,
    faire baisser ou monter la confiance dans une conclusion tirée de ces
    mesures (pensez à : nombre de mesures, silences, marge au seuil,
    provenance du seuil, cohérence avec le reste de la journée...).

    Retenez-en au moins deux, codez ici une règle qui retourne `"faible"`,
    `"moyenne"` ou `"élevée"`, et justifiez chaque borne chiffrée que vous
    choisissez. La classe comparera les règles au débrief.
    """
    raise NotImplementedError("étape 7 -- règle de confiance à concevoir")


def etape7_note_de_briefing() -> None:
    """SOCLE -- Chapitre 5 : la note de briefing.

    Sur la fenêtre d'après-midi, avec `threshold = 28.0`, calculez : le
    nombre de mesures au seuil sur le total, la valeur maximale, le plus
    long silence entre deux mesures (en minutes), et la confiance donnée
    par **votre** `regle_confiance`.

    Affichez une note au format imposé, en quatre lignes : message
    principal, limite, niveau de confiance, vérification recommandée.
    Chaque chiffre de la note doit venir d'une variable, jamais d'un texte
    tapé à la main.
    """
    rows = _lire_fenetre_apres_midi()

    raise NotImplementedError("étape 7 à compléter : note de briefing sur fuel-storage-01")


def etape7_approfondissement_audit_note_ia() -> None:
    """APPROFONDISSEMENT -- auditer une note rédigée par un assistant IA.

    Le fichier `note_ia_a_auditer.md` contient une note de briefing sur
    `fuel-storage-01`, produite par un assistant IA à partir des mêmes
    données. Elle est bien écrite, sûre d'elle -- et fausse par endroits.

    1. Relevez dans `cas_fil_rouge.md` (chapitre 5) chaque affirmation de
       la note, et classez-la : vérifiable et exacte / vérifiable et
       fausse / exacte mais trompeuse / invérifiable avec ce dossier.
    2. Codez ici la vérification de chaque affirmation chiffrée : un
       `print` par affirmation, avec la valeur annoncée par la note et la
       valeur que vous recalculez.

    Question à garder pour l'exit ticket : qu'est-ce que vous auriez dû
    vérifier si vous aviez vous-mêmes demandé cette note à une IA ?
    """
    raise NotImplementedError("étape 7 -- approfondissement : audit de la note IA")


def etape7_defi_trois_destinataires() -> None:
    """DÉFI (BONUS, non exigé) -- une même situation, trois notes BLUF.

    Réécrivez la note pour trois destinataires : le commandant de base, le
    chef du dépôt carburant, la cellule technique capteurs. Format BLUF
    (conclusion en première ligne), quatre lignes maximum chacune. Les
    chiffres doivent être identiques dans les trois ; seuls l'ordre, le
    vocabulaire et la vérification demandée changent. Affichez les trois.
    """
    raise NotImplementedError("étape 7 -- défi (bonus) : trois destinataires")


# ---------------------------------------------------------------------------
# Étape 8 -- recommandation finale
# ---------------------------------------------------------------------------


def etape8_recommandation_finale() -> str:
    """SOCLE -- Chapitre 5 : votre recommandation, et le choix de la pièce jointe.

    Plusieurs figures existent maintenant dans `slides/figures/`. Ajoutez
    un `print` indiquant laquelle accompagne le dossier transmis au
    commandant, et pourquoi pas chacune des autres.

    Rédigez ensuite, en moins de 100 mots, la recommandation finale sur
    `fuel-storage-01` : décision, confiance, deux preuves chiffrées
    (fichier + valeur), et ce que le dossier ne permet toujours pas
    d'affirmer. Retournez ce texte.
    """
    raise NotImplementedError("étape 8 à compléter : choix de la figure jointe puis recommandation finale rédigée")


def etape8_approfondissement_premortem() -> str:
    """APPROFONDISSEMENT -- pré-mortem et plan de collecte.

    Nous sommes demain matin. Votre recommandation s'est révélée fausse.

    Retournez un texte qui contient :
    - trois scénarios, distincts et plausibles, expliquant pourquoi elle
      était fausse (au moins un où vous avez alerté à tort, au moins un où
      vous auriez dû alerter plus fort) ;
    - pour chaque scénario, l'indice présent **aujourd'hui** dans le
      dossier qui aurait pu vous mettre en garde ;
    - un plan de collecte : quelle donnée supplémentaire (capteur, fréquence,
      information humaine) ferait changer votre décision, et dans quel sens.
    """
    raise NotImplementedError("étape 8 -- approfondissement : pré-mortem et plan de collecte")


def etape8_defi_cout_de_l_erreur() -> str:
    """DÉFI (BONUS, non exigé) -- chiffrer le coût de l'erreur.

    Comparez, dans un tableau court, les deux erreurs possibles : envoyer
    une équipe pour rien, ou ne pas l'envoyer alors qu'il le fallait.
    Pour chacune : conséquence, ordre de grandeur de coût (temps, moyens,
    risque), réversibilité. Concluez sur le seuil de confiance à partir
    duquel vous renonceriez à la vérification terrain -- et dites si ce
    seuil peut seulement être atteint avec les données actuelles.
    """
    raise NotImplementedError("étape 8 -- défi (bonus) : coût comparé des deux erreurs")


ETAPES = (
    etape1_indicateurs,
    etape1_approfondissement_classements,
    etape1_defi_nouvel_indicateur,
    etape2_score_zones_connues,
    etape2_approfondissement_sondes,
    etape2_defi_bascule_minimale,
    etape3_nouvelle_zone,
    etape3_approfondissement_score_v2,
    etape3_defi_septieme_zone,
    etape4_extraction_apres_midi,
    etape4_approfondissement_fenetres,
    etape4_defi_fenetre_inverse,
    etape5_graphique_trompeur,
    etape5_approfondissement_commande,
    etape5_defi_double_commande,
    etape6_deux_graphiques_honnetes,
    etape6_approfondissement_titre_message,
    etape6_defi_journee_complete,
    etape7_note_de_briefing,
    etape7_approfondissement_audit_note_ia,
    etape7_defi_trois_destinataires,
    etape8_recommandation_finale,
    etape8_approfondissement_premortem,
    etape8_defi_cout_de_l_erreur,
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
