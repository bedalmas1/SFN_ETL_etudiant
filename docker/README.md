# Environnement Docker

Ce dossier accueillera Docker Compose et la configuration Mosquitto nécessaires au broker MQTT local.

`docker-compose.yml` lance Mosquitto 2.0.22 en local uniquement. Depuis la racine: `docker compose -f docker/docker-compose.yml up -d --wait`. Précharger ensuite avec `python3 -m iot_decision.mqtt_tools seed data/samples/batch001_messages.jsonl`.

Le service `mosquitto-protected` (séquence 7, port 1884) démarre un second broker avec authentification et ACL obligatoires, pour la démonstration « broker ouvert vs broker protégé » : `docker compose -f docker/docker-compose.yml up -d --wait mosquitto-protected`. Détails et identifiants dans `mosquitto/README.md`.
