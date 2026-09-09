# Guide étudiant

## Mission

Une phrase circule ce matin sur le réseau de la base : « la température moyenne de la base est normale. » Le commandant s'appuie sur cette phrase pour décider s'il maintient l'activité prévue. Il vous confie la vérification.

Une sixième zone va entrer en service : `fuel-storage-01`, un dépôt de stockage carburant. Vous allez la suivre jusqu'à la fin de la séance.

**À la fin de la séance, vous serez associé à la recommandation transmise au commandant sur `fuel-storage-01`.**

Ouvrez maintenant `cas_fil_rouge.md` : c'est votre dossier de mission. Il va se compléter au fur et à mesure de la séance. Ouvrez aussi `tp_seance.py` : c'est le seul fichier de code dans lequel vous devez écrire.

## Règle d'exécution

**Règle impérative : n'ouvrez `src/iot_decision/risk_score.py` sous aucun prétexte avant d'avoir terminé l'étape 3.**. Jouez le jeu ;)

## Préparer l'environnement

```bash
python3 -m pip install -r sessions/s06bis_indicators_visualization_briefing/requirements.txt
export PYTHONPATH=src
python3 -m pytest -q
```

## Étape 1 — indicateurs et zone masquée

Complétez `etape1_indicateurs()` : le chargement du CSV est déjà fait (`rows`). Calculez vous-même la moyenne globale, le maximum de chaque zone, puis la ou les zones dont le maximum dépasse 35 °C alors que la moyenne globale reste dessous.

Avant d'exécuter, notez un pronostic : la moyenne globale dépassera-t-elle 30 °C ? Une des cinq zones vous semble-t-elle susceptible de franchir 35 °C malgré tout ?

Vérifiez à la main la moyenne d'une seule zone (l'équipe data pose l'addition, le décideur critique refait le calcul sans regarder l'écran).

**Questions :** La moyenne globale franchit-elle 35 °C ? Quelle zone le franchit malgré tout ? Un indicateur plus simple est-il nécessairement moins fiable ? Votre pronostic était-il juste ?

**Trace dans `cas_fil_rouge.md`, chapitre 1.**

## Débrief — que cache toujours un indicateur ?

La moyenne et le maximum racontent-ils la même histoire ? Que faudrait-il systématiquement faire avant de se fier à un résumé global ?

## Du calcul transparent au calcul opaque

Un **score automatique** transforme des mesures en recommandation, sans que sa logique soit lue au moment de la décision. Notions à maîtriser : biais d'automatisation, calibration, dérive, audit.

**Classez en vrai/faux, avec argument :** un score est plus objectif parce qu'il est automatique ; un modèle calibré une fois reste valable pour toute nouvelle zone ; on peut auditer un score aussi facilement qu'une moyenne.

## Étape 2 — interroger le score sans le lire

Complétez `etape2_score_zones_connues()` : le chargement de `data/raw/batch001_raw.jsonl` est déjà fait (`rows`). Appelez `score_all_zones(rows)` -- la boîte noire fournie, la seule fonction importée de `iot_decision` dans tout ce fichier -- et affichez zone, score et décision pour chacune des cinq zones.

D'après le classement de l'étape 1, quelle zone attendez-vous en tête du score ? Notez-le avant d'exécuter. **N'ouvrez pas `risk_score.py`.**

**Trace dans `cas_fil_rouge.md`, chapitre 2.**

## Étape 3 — une sixième zone

N'exécutez cette étape qu'au signal de l'enseignant, après la pause.

> Une nouvelle zone, `fuel-storage-01`, vient d'être équipée pour une mission de ravitaillement.

Complétez `etape3_nouvelle_zone()` : même démarche que l'étape 2, sur `data/samples/batch003_shift_scenario.jsonl`.

**Questions :** le score de `fuel-storage-01` se distingue-t-il des zones jugées sûres ? Quelle information opérationnelle sur le stockage carburant le score n'a-t-il jamais reçue ? A-t-il un bug, ou applique-t-il correctement une règle hors de son domaine ?

Seulement maintenant, ouvrez `src/iot_decision/risk_score.py` et lisez sa logique.

**Trace dans `cas_fil_rouge.md`, chapitre 3.**

## Échelle, seuil, annotation

Quatre notions pour l'après-midi : échelle (bornes d'un axe), seuil affiché, annotation, incertitude visuelle (un trait continu peut masquer un silence de données).

Complétez ensuite `etape4_extraction_apres_midi()` : le chargement des deux fichiers `fuel-storage-01` est déjà fait (`rows`, triées). Écrivez `rows` dans `data/processed/batch003_measurements.csv` avec `csv.DictWriter`, puis ne gardez que les lignes à partir de `2026-11-02T10:00:00Z` et écrivez-les dans `data/processed/batch003_afternoon_window.csv`.

**Question :** pourquoi isoler cette fenêtre plutôt que garder tout le lot pour la suite ?

## Étape 5 — le même graphique, deux seuils

Complétez `etape5_deux_graphiques()` : écrivez une fonction de tracé (matplotlib : courbe des valeurs, ligne horizontale au seuil, titre, `savefig`) et appelez-la deux fois, en ne changeant que `threshold` : d'abord 35.0, puis 28.0. Attention à ce que le titre utilise bien la variable `threshold`, pas un texte écrit en dur.

**Questions :** les deux graphiques contiennent-ils une valeur différente ? Le titre affiché dit-il la même chose sur les deux figures ? Est-il exact sur les deux ? Si non, le graphique ment-il, ou est-ce autre chose ?

**Trace dans `cas_fil_rouge.md`, chapitre 4.**

## Étape 6-7 — note de briefing et recommandation

Complétez `etape6_note_de_briefing()` : avec `threshold = 28.0`, comptez les mesures au-dessus du seuil, trouvez le maximum, calculez le plus grand écart en minutes entre deux mesures consécutives, déduisez-en une confiance, puis affichez une note (message principal, limite, confiance, vérification).

**Question :** cette note est-elle exacte, contrairement au titre du graphique de l'étape 5 ? Justifiez.

Complétez enfin `etape7_recommandation_finale()` : moins de 100 mots, avec décision, confiance, deux preuves chiffrées (fichier + valeur), et ce que le dossier ne permet toujours pas d'affirmer.

**Trace dans `cas_fil_rouge.md`, chapitre 5.**

## Brief oral et questions contradictoires

Rôles : cellule data, décideur pressé, red team.

- « Si je vous impose l'autre seuil sur le même graphique, votre recommandation change-t-elle ? »
- « Qu'est-ce qui, dans votre dossier, n'est pas une mesure mais un choix de votre part ? »

## Validation finale à exécuter

```bash
python3 tests/validate_s06bis_artifacts.py
```

## Exit ticket

1. « Un indicateur, un score ou un graphique honnête permet d'affirmer que… »
2. « Il ne permet pas d'affirmer que… »
3. « Avant de répéter un texte produit par un outil déjà audité, je vérifierais… »

## Aide en cas de blocage

Avant de demander de l'aide, indiquez : l'étape, la commande ou le fichier, le message d'erreur, ce que vous avez déjà vérifié. Les solutions, valeurs de référence et observations attendues sont réservées au guide enseignant et au corrigé.
