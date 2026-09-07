# Échantillons

Emplacement réservé aux petits jeux de données versionnés utilisés dans les exercices.

`batch001_messages.jsonl` contient 15 enveloppes MQTT reproductibles couvrant cinq zones. Une zone possède des mesures volontairement anciennes pour l’incident pédagogique de la séquence 1.

`batch001_traceability_incident.jsonl` contient deux messages aux champs métier semblables mais dont identifiant, topic, réception et empreinte diffèrent.

`batch002_quality_messages.jsonl` contient 24 messages sur cinq zones autour d'une alerte température, avec cinq erreurs injectées (champ manquant, unité incohérente, valeur hors plage, incohérence temporelle, doublon exact) et un silence réel de vingt minutes sur `battery-shelter-01` juste avant la valeur haute.

`batch003_shift_scenario.jsonl` contient cinq messages d'une zone de stockage carburant jamais vue à la calibration du score de la séquence 5 ; ses valeurs restent sous le seuil pédagogique de 35 °C mais dépassent le seuil de sécurité réel, bien plus bas, propre au carburant.

`batch004_suspect_scenario.jsonl` contient huit messages sur trois zones pour la séquence 7 : un doublon exact et une incohérence temporelle injectée sur `comms-shelter-01`, une mesure de cette même zone republiée sous un nouvel identifiant trente minutes plus tard (candidat de rejeu), et un silence non expliqué de 15 minutes ; aucune valeur mesurée n'est physiquement anormale.
