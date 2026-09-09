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

## Vérifications

```bash
mkdir -p /tmp/s06bis
python3 tests/validate_s06bis_artifacts.py
```

Attendu : `moyenne globale: 30.75 °C`, `battery-shelter-01` signalée comme zone masquée ; `battery-shelter-01: score 71/100 -> inspection recommandée` ; `fuel-storage-01: score 62/100 -> aucune action requise` ; `fuel-storage-01: 1/3 mesure(s) >= 28 °C, maximum 28.6 °C` ; puis `S06bis valide`.

## Dernière minute

- [ ] environnement activé, `PYTHONPATH=src`, tests réussis ;
- [ ] `batch001_measurements.csv`, `batch001_raw.jsonl`, `batch003_shift_scenario.jsonl` et `batch003_fuel_storage_extended.jsonl` disponibles ;
- [ ] `risk_score.py` fermé, non projeté, non mentionné avant la fin de l'étape 3 ;
- [ ] squelette de `tp_seance.py` et `cas_fil_rouge.md` distribués, PDF lisible, corrigé non distribué ;
- [ ] consigne « décision, confiance, preuves, incertitudes, limites » visible.
