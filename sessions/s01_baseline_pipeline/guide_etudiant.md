# Guide étudiant — Séquence 1

## Mission

Une activité de maintenance drone est prévue à 14 h 00 sur une base aérienne projetée. Un message de supervision signale une possible hausse de température dans le stockage batteries. Des données sont disponibles dans le broker MQTT, mais aucune analyse consolidée n’a encore été réalisée. Une vérification terrain prendrait 30 minutes et reporter l’activité aurait un coût opérationnel.

Vous devez prendre une première décision avec ces seules informations, puis construire une petite chaîne de données et expliquer exactement ce qu’elle permet — ou ne permet pas — de décider.

## Parcours

1. Comprendre la situation et voter.
2. Observer les messages et préserver la preuve brute.
3. Transformer les messages en table comparable.
4. Produire une représentation pour une question précise.
5. Formuler et contester une recommandation.

À chaque étape, conservez une trace : action, confiance, preuve, incertitude, vérification.

## Parcours pédagogique — 4 h

Ce guide est votre support unique. Il alterne compréhension, manipulation, débat et décision ; les TP ne sont pas des recettes techniques isolées.

| Temps | Étape | Trace attendue |
|---|---|---|
| 0:00–0:15 | Situation et vote initial | choix, confiance, information manquante |
| 0:15–0:45 | Lire la chaîne et qualifier l'incertitude | chaîne annotée et mini-décision |
| 0:45–1:55 | Observer puis extraire le brut | fiche observe/conclus et JSONL contrôlé |
| 1:55–2:05 | Pause | — |
| 2:05–2:30 | Distinguer brut, transformé et exploitable | opérations classées |
| 2:30–3:10 | Transformer et contrôler | CSV traçable et revue croisée |
| 3:10–3:35 | Visualiser et critiquer | PNG, observation et limite |
| 3:35–3:55 | Décider, contester et revoter | brief de 120 mots maximum |
| 3:55–4:00 | Exit ticket | trois phrases individuelles |

## Règle d’exécution

Les blocs `bash` ci-dessous sont des commandes à copier-coller dans un terminal. Sauf indication contraire, exécutez-les depuis la racine du dépôt `course-iot-decision`. Les blocs `python` sont de petits contrôles à exécuter dans un notebook ou dans un fichier Python temporaire. Après chaque commande, vérifiez l’absence d’erreur et notez le fichier créé ou modifié.

## Préparer l’environnement

À exécuter par chaque binôme :

```bash
python3 -m pip install -r sessions/s01_baseline_pipeline/requirements.txt
export PYTHONPATH=src
python3 -m pytest -q
```

Si l’enseignant utilise Docker :

```bash
docker compose -f docker/docker-compose.yml up -d --wait
python3 -m iot_decision.mqtt_tools seed data/samples/batch001_messages.jsonl
```

Ne démarrez pas le broker sur un réseau partagé.

## Vote initial

Sans consulter les données, choisissez une seule réponse :

- **A.** Maintenir l’activité.
- **B.** Déclencher une inspection terrain.
- **C.** Mettre temporairement la zone en sécurité.
- **D.** Données insuffisantes pour décider.

Notez une confiance de 0 à 100 %, votre raison principale et l’information qui vous manque le plus. Tenez compte du délai de 30 minutes pour l’inspection et du coût opérationnel d’un report, sans inventer de faits absents du message de supervision.

## Comprendre la chaîne avant de manipuler — 30 min

Représentez la chaîne **capteur → message → donnée structurée → indicateur → décision**. Pour chaque flèche, indiquez une transformation, une erreur plausible, la preuve qui permettrait de la détecter et l'effet possible sur l'action.

Classez ensuite vos affirmations en trois catégories : **observation**, **interprétation**, **hypothèse**. Terminez par une mini-décision : peut-on agir sur la seule présence de messages ? Avec quelle confiance et quelle vérification prioritaire ?

## TP 1 — Extraire le brut

### Observer avant d'extraire

Sur un message montré par l'enseignant ou lu dans l'échantillon, repérez topic, payload, zone, unité, `measured_at`, `received_at` et retained. Complétez deux colonnes « j'observe » / « je peux conclure ». Expliquez pourquoi « reçu maintenant » ne signifie pas « mesuré maintenant ».

### Extraire sans altérer

Mode MQTT, à exécuter :

```bash
python3 -m iot_decision.mqtt_tools extract data/raw/batch001_raw.jsonl
```

Mode échantillon si le broker est indisponible, à exécuter à la place :

```bash
python3 -m iot_decision.baseline_cli extract-sample data/samples/batch001_messages.jsonl data/raw/batch001_raw.jsonl
```

Ensuite, exécutez éventuellement ce contrôle Python :

```python
from pathlib import Path

raw_path = Path("data/raw/batch001_raw.jsonl")
lines = [line for line in raw_path.read_text(encoding="utf-8").splitlines() if line]
print("lignes reçues :", len(lines))
print("première ligne :", lines[0])
print("dernière ligne :", lines[-1])
```

Contrôlez l'effectif, la première et la dernière ligne, puis relevez trois métadonnées de traçabilité. Notez ce que vous observez et ce que vous pouvez en déduire. Ne modifiez jamais le brut. Avant la pause, comparez la fraîcheur des zones et révisez votre décision provisoire sans supprimer une donnée gênante.

## Brut, transformé, exploitable — 25 min

Classez les actions suivantes : conserver le payload ; renommer une zone ; convertir une unité ; calculer un maximum ; supprimer une ligne ; tracer un seuil. Pour chacune, indiquez si elle préserve la preuve, si elle est réversible et ce qu'elle peut changer dans la décision.

Incident : les mesures ont-elles une fraîcheur comparable ? Une donnée ancienne est-elle fausse, inutilisable, ou utilisable avec réserve ? Justifiez sans la « corriger ».

## TP 2 — Transformer en CSV

À exécuter :

```bash
python3 -m iot_decision.baseline_cli transform data/raw/batch001_raw.jsonl data/processed/batch001_measurements.csv
```

Contrôle Python optionnel :

```python
import csv

with open("data/processed/batch001_measurements.csv", encoding="utf-8", newline="") as stream:
    reader = csv.DictReader(stream)
    rows = list(reader)

print("colonnes :", reader.fieldnames)
print("nombre de lignes :", len(rows))
print("première ligne :", rows[0])
```

À faire : vérifier colonnes, zones, unités et temps ; retrouver une ligne CSV dans le JSONL ; noter ce qui est plus lisible et ce qui n’est pas devenu plus vrai.

## TP 3 — Générer et critiquer le graphique

À exécuter :

```bash
python3 -m iot_decision.visualize_baseline data/processed/batch001_measurements.csv sessions/s01_baseline_pipeline/slides/figures/batch001_max_by_zone.png
```

Ouvrez le fichier PNG. Vérifiez titre-question, unité, seuil et lisibilité. Écrivez séparément une observation directement visible, une interprétation prudente et une limite du maximum observé. Proposez un indicateur alternatif pour une autre incertitude. Le graphique doit répondre à une question de décision explicite.

## TP 4 — Rédiger le brief décisionnel

Ce TP se termine par le vote final.

Rédigez une note de 120 mots maximum contenant :

- une action concrète ;
- un niveau de confiance justifié ;
- deux preuves chiffrées retrouvables ;
- deux incertitudes importantes ;
- une vérification prioritaire.

Un membre du binôme joue le contradicteur : quelle hypothèse pourrait renverser votre décision ? Revotez ensuite entre les mêmes options A à D, avec votre niveau de confiance.

## Vérification finale à exécuter

```bash
python3 tests/validate_s01_artifacts.py
```

Cette commande vérifie les artefacts et le notebook ; elle ne rédige pas votre recommandation.

## Aide en cas de blocage

Avant de demander de l’aide, indiquez : l’étape, la commande ou le fichier, le message d’erreur, ce que vous avez vérifié et l’effet possible sur votre décision. Ne demandez pas seulement la réponse : demandez quelle vérification réaliser ensuite.

## Canevas de recommandation

- **Décision :** quelle action proposez-vous ?
- **Confiance :** très faible / faible / moyenne / élevée ; pourquoi ?
- **Preuves :** quelles deux observations pouvez-vous retrouver ?
- **Incertitudes :** qu’est-ce qui pourrait rendre votre conclusion fausse ?
- **Vérification :** que faut-il vérifier avant une action difficilement réversible ?

## Exit ticket

1. « La pipeline permet d’affirmer que… »
2. « Elle ne permet pas d’affirmer que… »
3. « Avant une action irréversible, je vérifierais… »

Les solutions, valeurs de référence et observations attendues sont réservées au guide enseignant et au corrigé.
