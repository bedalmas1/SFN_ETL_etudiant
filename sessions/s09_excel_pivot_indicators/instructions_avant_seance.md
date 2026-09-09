# Guide de démarrage — Séquence 9

Cette séquence ne s'exécute pas en Bash côté étudiant : elle se prépare une fois en Bash (génération des données et du classeur), puis se déroule entièrement dans Excel en séance.

## Préparation (une fois, avant la séance)

```bash
cd /chemin/vers/course-iot-decision
source .venv/bin/activate
python3 -m pip install -r sessions/s09_excel_pivot_indicators/requirements.txt
export PYTHONPATH=src
python3 -m pytest -q tests/test_excel_dataset.py
```

Si `.venv` existe, ne pas la recréer. `which python3` doit pointer vers `.venv/bin/python3`.

## Pas de broker requis

S9 ne nécessite ni Docker ni MQTT : elle part de `data/processed/batch005_measurements.csv`, déjà généré. Vérifier sa présence et régénérer si besoin :

```bash
test -f data/processed/batch005_measurements.csv && echo "présent"
test -f data/samples/batch005_asset_thresholds.csv && echo "présent"
python3 -m iot_decision.excel_dataset_cli
```

## Construire et vérifier le classeur de départ

```bash
python3 -m iot_decision.excel_workbook_cli sessions/s09_excel_pivot_indicators/classeur_s09_depart.xlsx
python3 -m iot_decision.excel_workbook_corrige_cli sessions/s09_excel_pivot_indicators/classeur_s09_corrige.xlsx
python3 -m iot_decision.visualize_excel_indicators sessions/s09_excel_pivot_indicators/slides/figures/battery_divergence.png sessions/s09_excel_pivot_indicators/slides/figures/threshold_comparison.png
python3 tests/validate_s09_artifacts.py
```

Attendu : `moyenne naïve toutes grandeurs confondues: 24.05`, `battery-shelter-01: 33.62 °C`, `fuel-storage-01` listée comme zone systématiquement au-dessus de son seuil, puis `S09 valide`.

Ouvrir ensuite `classeur_s09_depart.xlsx` et vérifier à l'œil : quatre feuilles (`Mesures`, `Seuils`, `Indicateurs`, `Note de décision`), 144 lignes de données, tables structurées actives (nom visible dans l'onglet Création de tableau).

**`classeur_s09_corrige.xlsx` reste sur le poste enseignant, jamais sur un poste étudiant ni sur un partage accessible en séance.** Il sert uniquement de référence pour projeter le résultat attendu au débrief (colonnes de recherche, graphique combiné, note de décision remplie).

## Matériel et précautions

- Chaque binôme a besoin d'un poste avec Excel (ou un tableur compatible RECHERCHEX/XLOOKUP) et sa propre copie modifiable du classeur — jamais un fichier partagé en lecture seule.
- PDF et guide enseignant ouverts ; guide étudiant distribué sans corrigé.
- Vérifier la disponibilité de `RECHERCHEX` sur les postes ; à défaut, le repli `INDEX`/`EQUIV` documenté dans le guide enseignant fonctionne à l'identique.
- Ne jamais qualifier 35 °C, 28 °C ou 11,5 V de normes officielles réelles : ce sont des choix pédagogiques, comme en séquence 5.
- Binômes stables sur toute la séance ; pas de redistribution de rôles nécessaire, contrairement à la séquence 5.

## Plan de repli

- Poste sans Excel de bureau : Excel en ligne ou Google Sheets conviennent pour les TCD et RECHERCHEX ; vérifier `XLOOKUP` sous Google Sheets (nom identique).
- Poste en panne : redistribuer une copie fraîche de `classeur_s09_depart.xlsx` depuis une clé USB ou un partage local, jamais depuis un lien nécessitant une connexion incertaine.
- Retard supérieur à 15 min : fournir directement les deux TCD de référence (moyenne filtrée, maxima par jour) en projection, maintenir le TP 2 et la décision finale.

## Dernière minute

- [ ] environnement Python activé pour la préparation, `PYTHONPATH=src`, tests réussis ;
- [ ] `batch005_measurements.csv` et `batch005_asset_thresholds.csv` disponibles ;
- [ ] `classeur_s09_depart.xlsx` régénéré, ouvert et vérifié (4 feuilles, 144 lignes) ;
- [ ] `classeur_s09_corrige.xlsx` régénéré côté enseignant uniquement, absent de tout poste ou partage étudiant ;
- [ ] une copie modifiable du classeur de départ par binôme, PDF lisible, corrigé non distribué ;
- [ ] consigne « toujours filtrer par capteur avant un agrégat » visible en fond de salle.
