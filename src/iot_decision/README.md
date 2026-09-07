# Paquet `iot_decision`

Modules prévus : générateur MQTT, extracteur, transformations, contrôles qualité et indicateurs.

Séquence 1: `baseline.py` porte les transformations et la recommandation déterministe; `baseline_cli.py` expose le parcours hors broker; `mqtt_tools.py` précharge et extrait Mosquitto; `visualize_baseline.py` produit le graphique décisionnel.

Séquence 2 : `source_inventory.py` et sa CLI comparent l'observé à l'attendu.

Séquence 3 : `traceability.py` parse strictement le JSONL, conserve adresse et empreinte de chaque ligne, vérifie le retour à la source et signale les candidats doublons sans suppression automatique.

Séquence 4 : `quality.py` sépare les messages propres des messages rejetés (champ manquant, unité incohérente, valeur hors plage, incohérence temporelle, doublon exact) sans jamais corriger une valeur, puis distingue un silence réel d'un silence expliqué par un rejet ; `quality_cli.py` produit `clean.csv`, `rejected.csv` et le rapport JSON en un seul appel ; `visualize_quality.py` trace la chronologie décisionnelle.

Séquence 5 : `indicators.py` calcule des indicateurs transparents (moyenne, maximum, durée au-dessus d'un seuil) et détecte une zone masquée par la moyenne globale ; `risk_score.py` simule un score automatique déterministe, volontairement non documenté aux étudiants avant le débrief, calibré une fois sur cinq zones et mis en défaut sur une zone nouvelle ; `visualize_indicators.py` et `visualize_risk_score.py` produisent les deux graphiques de la séance.

Séquence 6 : `briefing.py` résume une zone (message principal, limite, niveau de confiance, vérification) à partir d'un franchissement de seuil et d'un silence non expliqué, sans jamais choisir la confiance à la main ; `briefing_cli.py` affiche cette note ; `visualize_briefing.py` produit, à partir des mêmes mesures, une mise en forme trompeuse (échelle tronquée, trait continu sur le silence) et une mise en forme honnête (échelle complète, seuil et silence annotés).

Séquence 7 : `chain_trust.py` ne recalcule rien de nouveau -- il relit les signaux déjà détectables par `quality.classify` (doublon exact, incohérence temporelle) et `traceability.duplicate_candidates` (candidat de rejeu, même mesure sous une identité différente), les relie à quatre hypothèses concurrentes (incident réel, panne capteur, problème réseau, suspicion data/cyber) classées par probabilité puis impact, et recommande d'agir ou d'isoler ; `chain_trust_cli.py` affiche ce diagnostic. `mqtt_tools.py` accepte désormais `--username`/`--password` pour la démonstration du broker protégé.
