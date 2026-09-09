# Séquence 9 — Construire des indicateurs sous Excel

Séance de 4 h qui applique, avec Excel plutôt qu'avec Python, les réflexes déjà installés en séquence 5 : un indicateur compresse toujours la réalité, et l'outil exécute exactement ce qu'on lui demande, jamais ce qu'on voulait dire. Le jeu de données est volontairement plus riche que celui des séquences précédentes : sept zones, quatre grandeurs physiques (température, humidité, tension batterie, qualité de signal LoRa), trois jours de mesures.

Cette séquence ne touche ni le broker MQTT ni Python en séance : les étudiants travaillent entièrement dans le classeur `classeur_s09_depart.xlsx`, préparé en amont à partir de `data/processed/batch005_measurements.csv`.

## Question directrice

**À la fin, les étudiants doivent décider quelles zones de la base méritent une vérification prioritaire une fois les indicateurs correctement construits sous Excel, et lesquelles un simple filtre unique à 35 °C aurait manquées.**

## Démarrage rapide (préparation enseignant)

```bash
python3 -m pip install -r sessions/s09_excel_pivot_indicators/requirements.txt
export PYTHONPATH=src
python3 -m iot_decision.excel_dataset_cli
python3 -m iot_decision.excel_workbook_cli sessions/s09_excel_pivot_indicators/classeur_s09_depart.xlsx
python3 -m iot_decision.excel_workbook_corrige_cli sessions/s09_excel_pivot_indicators/classeur_s09_corrige.xlsx
python3 -m iot_decision.visualize_excel_indicators sessions/s09_excel_pivot_indicators/slides/figures/battery_divergence.png sessions/s09_excel_pivot_indicators/slides/figures/threshold_comparison.png
python3 -m pytest -q tests/test_excel_dataset.py
python3 tests/validate_s09_artifacts.py
```

Livrables étudiants : classeur Excel avec table structurée, TCD par zone et par capteur, colonne de seuil obtenue par RECHERCHEX, indicateur trompeur (moyenne mélangeant plusieurs grandeurs) identifié, note de décision. Le PDF projetable est `slides/s09_excel_pivot_indicators.pdf`.

Le classeur de départ `classeur_s09_depart.xlsx` contient quatre feuilles : `Mesures` (table structurée, 144 lignes), `Seuils` (table structurée, 12 seuils), `Indicateurs` et `Note de décision` (vides, à construire en séance). Il ne contient aucune solution.

**`classeur_s09_corrige.xlsx` est réservé à l'enseignant, à ne jamais distribuer aux étudiants.** Il reproduit le résultat attendu en fin de séance avec de vraies formules Excel (clé, `RECHERCHEX`, alerte, mise en forme conditionnelle), les indicateurs de référence, le graphique combiné température/tension et la note de décision remplie.
