# Tests

Les tests vérifieront les scripts Python et les cas de qualité de données. Ils seront ajoutés avec le code lors de l’étape 4.

`test_baseline_pipeline.py` teste les fonctions de la séquence 1. `validate_s01_artifacts.py` reconstruit le brut, le CSV et la figure dans un dossier temporaire, puis exécute le notebook.

`test_traceability.py` couvre parsing strict, erreurs, empreintes et candidats doublons. `validate_s03_artifacts.py` reconstruit et vérifie le CSV S03.

`test_quality.py` couvre les quatre contrôles de validité, la détection de doublon exact et la distinction silence réel/silence expliqué par un rejet. `validate_s04_artifacts.py` reconstruit `clean.csv`, `rejected.csv`, le rapport et la figure, puis exécute le notebook.

`test_indicators.py` couvre la moyenne globale, les maxima par zone et la détection de zone masquée. `test_risk_score.py` couvre le score automatique sur les zones connues et sa mise en défaut silencieuse sur une zone hors calibration. `validate_s05_artifacts.py` reconstruit les deux figures et exécute le notebook.

`test_briefing.py` couvre le tri chronologique par zone, la confiance faible sur un silence non expliqué suivi d'un franchissement de seuil, la confiance moyenne en l'absence de franchissement, et les quatre champs obligatoires de la note. `validate_s06_artifacts.py` reconstruit les deux mises en forme du même incident et exécute le notebook.

`test_chain_trust.py` couvre la détection des quatre signaux (doublon exact, candidat de rejeu, incohérence temporelle, silence non expliqué) sur le lot suspect, le classement de « suspicion data/cyber » en tête, et l'absence de suspicion sur un lot sans anomalie. `validate_s07_artifacts.py` exécute le diagnostic complet et le notebook.
