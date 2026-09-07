# Données traitées

Emplacement réservé aux sorties reproductibles de la pipeline pédagogique.

`batch001_measurements.csv` est la table baseline reproductible (15 lignes, cinq zones), obtenue sans correction des valeurs capteur. Elle est réutilisée telle quelle par la séquence 5 pour le calcul des indicateurs transparents.

`batch001_structured.csv` est la projection traçable S03 : 15 lignes, version de schéma, fichier/ligne source et SHA-256 du brut, sans correction de mesure.

`batch002_measurements_clean.csv` (19 lignes) et `batch002_rejected.csv` (5 lignes, avec raison) sont la séparation S04 des messages de `batch002_quality_messages.jsonl`, sans aucune valeur corrigée. `batch002_quality_report.json` documente les rejets par raison et signale, zone par zone, si un silence détecté est réel ou expliqué par un rejet. `batch002_measurements_clean.csv` est réutilisé tel quel par la séquence 6 pour comparer deux mises en forme du même incident (`battery-shelter-01`) sans recalculer aucune valeur.
