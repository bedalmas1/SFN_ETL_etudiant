# Guide de démarrage — Séquence 6bis

Toutes les commandes s'exécutent sous Linux dans Bash, depuis la racine du dépôt.

## Environnement et dépendances

```bash
cd /chemin/vers/course-iot-decision
source .venv/bin/activate
python3 -m pip install -r sessions/s06bis_indicators_visualization_briefing/requirements.txt
export PYTHONPATH=src
python3 -m pytest -q
```

Si `.venv` existe, ne pas la recréer. `which python3` doit pointer vers `.venv/bin/python3`.

## Pas de broker requis

S6bis travaille entièrement sur des fichiers déjà produits ou fournis : `data/processed/batch001_measurements.csv` (séquence 1), `data/raw/batch001_raw.jsonl`, `data/samples/batch003_shift_scenario.jsonl` et `data/samples/batch003_fuel_storage_extended.jsonl`. Docker et MQTT ne sont pas nécessaires.

```bash
test -f data/processed/batch001_measurements.csv && echo "présent"
test -f data/raw/batch001_raw.jsonl && echo "présent"
test -f data/samples/batch003_shift_scenario.jsonl && echo "présent"
test -f data/samples/batch003_fuel_storage_extended.jsonl && echo "présent"
```

## Supports et contrôle à blanc

```bash
mkdir -p /tmp/s06bis
python3 tests/validate_s06bis_artifacts.py
```

Attendu : `moyenne globale: 30.75 °C`, `battery-shelter-01` signalée comme zone masquée ; `battery-shelter-01: score 71/100 -> inspection recommandée` ; `fuel-storage-01: score 62/100 -> aucune action requise` ; `fuel-storage-01: 1/3 mesure(s) >= 28 °C, maximum 28.6 °C` ; puis `S06bis valide`.

## Précautions et matériel

- PDF et guide enseignant ouverts ; guide étudiant, `cas_fil_rouge.md` et le squelette vide de `tp_seance.py` distribués sans corrigé.
- **Ne jamais ouvrir ni projeter `src/iot_decision/risk_score.py` avant la fin de l'étape 3** : c'est le fichier révélé au milieu de la séance, pas un support de cours.
- Binômes « équipe data » / « décideur critique » pour le matin ; échanger les rôles à la pause (2:05).
- Ne jamais qualifier 35 °C, 28 °C ou le seuil de décision 65/100 de norme réelle : ce sont des choix pédagogiques.
- L'étape 5 (deux graphiques, un seul seuil qui change) ne prend son sens qu'après l'étape 3 : ne pas l'anticiper.

## Suivre le code en direct sans vidéoprojecteur (optionnel)

Sans vidéoprojecteur, deux options pour que les étudiants suivent le code écrit en direct dans `tp_seance.py`, de la plus confortable à la plus simple à mettre en place :

1. **JupyterLab en collaboration temps réel.** Si le VPS héberge déjà JupyterLab pour le cours, installer une fois l'extension `jupyter-collaboration` (`pip install jupyter-collaboration`, JupyterLab ≥ 4) et ouvrir `tp_seance.py` (ou une copie `.ipynb`) depuis une URL partagée : chaque étudiant qui ouvre le même document voit les modifications de l'enseignant s'afficher en direct dans son propre navigateur, comme un document collaboratif. À tester une fois avant la séance : la configuration réseau du VPS (port, reverse proxy) peut demander un réglage préalable.
2. **Repli sans installation supplémentaire.** Travailler dans le même espace code-server que les étudiants (fichier `tp_seance.py` sur un chemin partagé du VPS) et leur demander de recharger le fichier (raccourci « revert file » / rafraîchir l'onglet) à chaque fin d'étape annoncée à voix haute. Moins fluide qu'un vrai temps réel, mais ne demande aucune installation ni test préalable.

Cette amélioration reste optionnelle : à défaut, dicter le code à voix haute pendant que les étudiants le tapent dans leur propre `tp_seance.py` fonctionne aussi, comme en s05/s06.

## Plan de repli

- Sans Jupyter ni collaboration temps réel : dicter le code à voix haute, les étudiants tapent dans leur propre `tp_seance.py`. Tous les livrables restent possibles.
- Poste en panne : fournir les sorties de `tests/validate_s06bis_artifacts.py` en consignant leur provenance.
- Retard supérieur à 15 min : fournir directement les deux figures et la note de briefing, maintenir le brief oral et la décision finale.

## Dernière minute

- [ ] environnement activé, `PYTHONPATH=src`, tests réussis ;
- [ ] `batch001_measurements.csv`, `batch001_raw.jsonl`, `batch003_shift_scenario.jsonl` et `batch003_fuel_storage_extended.jsonl` disponibles ;
- [ ] `risk_score.py` fermé, non projeté, non mentionné avant la fin de l'étape 3 ;
- [ ] squelette de `tp_seance.py` et `cas_fil_rouge.md` distribués, PDF lisible, corrigé non distribué ;
- [ ] consigne « décision, confiance, preuves, incertitudes, limites » visible.
