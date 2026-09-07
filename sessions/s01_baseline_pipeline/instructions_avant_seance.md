# Guide de démarrage — Séquence 1

Ce guide est destiné à **tous les étudiants**. Exécutez-le sur votre machine Linux au début du cours. Comptez environ 30 à 45 minutes pour une première installation.

Toutes les commandes sont à lancer dans un terminal Bash. Ne continuez pas lorsqu’une commande affiche une erreur : utilisez la section « Dépannage » ou signalez le problème à l’enseignant.

## 1. Vérifier les prérequis

Le cours nécessite :

- Linux avec un terminal Bash ;
- Python 3.10 ou plus récent ;
- le module Python `venv` ;
- Git ;
- Docker Engine avec le plugin Docker Compose.

Vérifiez votre installation :

```bash
python3 --version
git --version
docker --version
docker compose version
```

Python doit afficher une version 3.10 ou plus récente. Chaque autre commande doit afficher un numéro de version.

Si Docker répond « permission denied », ajoutez temporairement `sudo` devant les commandes `docker`. La configuration permanente des droits dépend de votre distribution Linux.

## 2. Se placer à la racine du cours

Ouvrez le dépôt `course-iot-decision`, puis vérifiez votre position :

```bash
cd /chemin/vers/course-iot-decision
pwd
test -f README.md && test -d sessions/s01_baseline_pipeline && echo "Dépôt trouvé"
```

Remplacez `/chemin/vers/course-iot-decision` par le chemin réel sur votre machine. La dernière commande doit afficher `Dépôt trouvé`.

Toutes les commandes suivantes doivent être exécutées depuis cette racine.

## 3. Créer l’environnement Python du cours

Créez un environnement virtuel local, activez-le et installez les dépendances de la séquence 1 :

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r sessions/s01_baseline_pipeline/requirements.txt
export PYTHONPATH=src
```

Une fois l’environnement activé, votre terminal affiche généralement `(.venv)`. Vérifiez l’interpréteur utilisé :

```bash
which python3
python3 --version
```

Le chemin retourné par `which python3` doit se terminer par `.venv/bin/python3`.

À chaque nouveau terminal ouvert pendant le cours, réactivez l’environnement :

```bash
source .venv/bin/activate
export PYTHONPATH=src
```

## 4. Vérifier le code et les supports

Exécutez les tests depuis la racine du dépôt :

```bash
python3 -m pytest -q
python3 tests/validate_s01_artifacts.py
```

Résultat attendu :

- les tests se terminent sans échec ;
- le validateur affiche `S01 valide` ;
- il confirme 15 messages, 15 mesures, une figure et un notebook exécutables.

Un avertissement `zmq` est acceptable si le validateur termine par `S01 valide`.

## 5. Démarrer le broker MQTT local

Le broker du cours reste limité à votre propre machine sur `127.0.0.1`.

Démarrez-le et vérifiez son état :

```bash
docker compose -f docker/docker-compose.yml up -d --wait
docker compose -f docker/docker-compose.yml ps
```

Le service Mosquitto doit être indiqué comme démarré ou sain. Chargez ensuite les messages de la séquence 1 :

```bash
python3 -m iot_decision.mqtt_tools seed data/samples/batch001_messages.jsonl
```

## 6. Tester une extraction MQTT

Extrayez les messages dans un fichier temporaire propre à votre machine :

```bash
rm -f /tmp/s01_student_check.jsonl
python3 -m iot_decision.mqtt_tools extract /tmp/s01_student_check.jsonl
wc -l /tmp/s01_student_check.jsonl
head -n 1 /tmp/s01_student_check.jsonl
```

Résultat attendu :

- `wc -l` affiche `15` ;
- la première ligne est une enveloppe JSON contenant notamment un topic, une date de réception et un payload.

Cette vérification prouve seulement que votre chaîne technique locale fonctionne. Elle ne prouve pas encore que les données suffisent pour décider.

## 7. Préparer votre espace de travail

Vérifiez que les dossiers de sortie sont accessibles :

```bash
test -w data/raw && echo "data/raw accessible"
test -w data/processed && echo "data/processed accessible"
test -f notebooks/s01_baseline_pipeline.ipynb && echo "Notebook trouvé"
test -f sessions/s01_baseline_pipeline/guide_etudiant.md && echo "Guide trouvé"
```

Les quatre confirmations doivent s’afficher. Pendant les activités, notez systématiquement :

- la commande exécutée ;
- le fichier produit ;
- l’observation obtenue ;
- ce que cette observation permet ou non de conclure.

## 8. Plan de secours sans Docker

Si Docker ou MQTT reste indisponible après le dépannage, utilisez l’échantillon fourni :

```bash
python3 -m iot_decision.baseline_cli extract-sample data/samples/batch001_messages.jsonl data/raw/batch001_raw.jsonl
python3 -m iot_decision.baseline_cli transform data/raw/batch001_raw.jsonl data/processed/batch001_measurements.csv
python3 -m iot_decision.visualize_baseline data/processed/batch001_measurements.csv sessions/s01_baseline_pipeline/slides/figures/batch001_max_by_zone.png
python3 tests/validate_s01_artifacts.py
```

Signalez dans votre journal que la source utilisée est un échantillon et non une extraction directe du broker.

## 9. Dépannage

### `python3: command not found`

Installez Python 3 avec le gestionnaire de paquets de votre distribution. Sur Ubuntu ou Debian :

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### L’environnement virtuel ne se crée pas

Vérifiez que `python3-venv` est installé, puis supprimez uniquement l’environnement incomplet avant de recommencer :

```bash
rm -rf .venv
python3 -m venv .venv
```

### `No module named iot_decision`

Vous devez être à la racine du dépôt, avec l’environnement activé :

```bash
pwd
source .venv/bin/activate
export PYTHONPATH=src
```

### Docker ne répond pas

```bash
sudo systemctl start docker
docker info
docker compose -f docker/docker-compose.yml ps
```

Si le problème persiste, passez au plan de secours et prévenez l’enseignant.

### Le port MQTT est déjà utilisé

```bash
sudo ss -ltnp | grep 1883
```

Montrez le résultat à l’enseignant avant d’arrêter ou de modifier un service existant.

## 10. Validation finale

Vous êtes prêt pour la séquence 1 si toutes les affirmations suivantes sont vraies :

- [ ] je suis à la racine de `course-iot-decision` ;
- [ ] `.venv` est activé et `PYTHONPATH=src` est défini ;
- [ ] les tests Python réussissent ;
- [ ] le validateur affiche `S01 valide` ;
- [ ] le broker local fonctionne, ou j’ai identifié que j’utiliserai le plan de secours ;
- [ ] l’extraction MQTT contient 15 lignes, ou l’échantillon local est exploitable ;
- [ ] je peux ouvrir le guide étudiant et le notebook.

À la fin du cours, arrêtez le broker local :

```bash
docker compose -f docker/docker-compose.yml down
```