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

À chaque étape, conservez une trace : action, confiance, preuve, incertitude, vérification. Dans chaque TP, quelques lignes de Python complètent les commandes toutes faites : elles servent à répondre vous-même à une question précise sur la donnée, avec un résultat que vous pourrez citer comme preuve chiffrée.


## Règle d’exécution

Les blocs `bash` ci-dessous sont des commandes à copier-coller dans un terminal. Sauf indication contraire, exécutez-les depuis la racine du dépôt `course-iot-decision`. Les blocs `python` marqués **« À coder »** contiennent des `# TODO` : complétez-les vous-même dans un notebook ou un fichier Python temporaire, ils ne fonctionnent pas tels quels. Gardez le même notebook ou le même fichier d'un TP à l'autre : les variables calculées au TP 1 servent au TP 4. Après chaque commande ou chaque cellule, vérifiez l’absence d’erreur et notez le résultat obtenu.

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

### À coder — combien de messages par zone, et quelle zone est la plus ancienne ?

Le CLI vous dit combien de lignes il a écrites, mais pas comment elles se répartissent ni si elles datent toutes du même moment. Complétez les `# TODO` :

```python
import json
from datetime import datetime

raw_path = "data/raw/batch001_raw.jsonl"
messages = []
with open(raw_path, encoding="utf-8") as flux:
    for ligne in flux:
        if ligne.strip():
            messages.append(json.loads(ligne))

print("messages chargés :", len(messages))

# Question 1 : quelles sont la première et la dernière ligne du fichier ?
# TODO : afficher messages[0] et messages[-1]

# Question 2 : combien de messages par zone ?
compte_par_zone = {}
for message in messages:
    zone = message["payload"]["zone"]
    # TODO : incrémenter compte_par_zone[zone] de 1 (utilisez .get(zone, 0))

print("messages par zone :", compte_par_zone)


def horodatage(valeur: str) -> datetime:
    return datetime.fromisoformat(valeur.replace("Z", "+00:00"))


# Question 3 : quel est l'écart, en minutes, entre measured_at et received_at ?
ecarts_par_zone = {}
for message in messages:
    zone = message["payload"]["zone"]
    mesure = horodatage(message["payload"]["measured_at"])
    reception = horodatage(message["received_at"])
    # TODO : calculer l'écart en minutes entre reception et mesure
    ecart_minutes = None
    ecarts_par_zone.setdefault(zone, []).append(ecart_minutes)

for zone, ecarts in sorted(ecarts_par_zone.items()):
    print(zone, "écart maximum (min) :", max(ecarts))
```

Notez le résultat des trois questions : la première et la dernière ligne du fichier, combien de messages par zone, et quelle zone a l'écart mesure/réception le plus grand. Relevez aussi trois métadonnées de traçabilité sur la première ligne affichée. Ne modifiez jamais le brut. Avant la pause, comparez la fraîcheur des zones grâce à vos écarts calculés et révisez votre décision provisoire sans supprimer une donnée gênante.

## Brut, transformé, exploitable — 25 min

Classez les actions suivantes : conserver le payload ; renommer une zone ; convertir une unité ; calculer un maximum ; supprimer une ligne ; tracer un seuil. Pour chacune, indiquez si elle préserve la preuve, si elle est réversible et ce qu'elle peut changer dans la décision.

Incident : les mesures ont-elles une fraîcheur comparable ? Une donnée ancienne est-elle fausse, inutilisable, ou utilisable avec réserve ? Justifiez sans la « corriger ».

## TP 2 — Transformer en CSV

À exécuter :

```bash
python3 -m iot_decision.baseline_cli transform data/raw/batch001_raw.jsonl data/processed/batch001_measurements.csv
```

### À coder — quelles zones dépassent le seuil de 35 °C ?

Le CSV rend les valeurs comparables, mais rien ne signale encore un dépassement. Complétez les `# TODO` :

```python
import csv

SEUIL = 35.0

with open("data/processed/batch001_measurements.csv", encoding="utf-8", newline="") as flux:
    lignes = list(csv.DictReader(flux))

print("colonnes :", lignes[0].keys())
print("nombre de lignes :", len(lignes))

# Question : quel est le maximum observé par zone, et dépasse-t-il le seuil ?
maxima_par_zone = {}
for ligne in lignes:
    zone = ligne["zone"]
    valeur = float(ligne["value"])
    # TODO : mettre à jour maxima_par_zone[zone] avec le maximum entre
    #        la valeur déjà stockée (ou float("-inf") si absente) et `valeur`

for zone, maximum in sorted(maxima_par_zone.items()):
    alerte = "AU-DESSUS DU SEUIL" if maximum >= SEUIL else "en dessous"
    print(f"{zone}: {maximum:.1f} °C ({alerte})")
```

Notez combien de zones dépassent le seuil et leur valeur exacte. Retrouvez ensuite une ligne CSV correspondante dans le JSONL brut : vérifiez que `message_id` et `measured_at` correspondent bien. Ce que le CSV a gagné en lisibilité ne l'a pas rendu plus vrai — dites pourquoi en une phrase.

## TP 3 — Générer et critiquer le graphique

À exécuter :

```bash
python3 -m iot_decision.visualize_baseline data/processed/batch001_measurements.csv sessions/s01_baseline_pipeline/slides/figures/batch001_max_by_zone.png
```

Ouvrez le fichier PNG. Vérifiez titre-question, unité, seuil et lisibilité. Écrivez séparément une observation directement visible, une interprétation prudente et une limite du maximum observé.

### À coder — un indicateur que le graphique ne montre pas

Le graphique n'affiche que le maximum par zone : il masque la dispersion des mesures et le nombre de dépassements. Complétez les `# TODO` pour calculer un indicateur alternatif à partir des mêmes lignes CSV que le TP 2 (`lignes`) :

```python
valeurs_par_zone = {}
for ligne in lignes:
    zone = ligne["zone"]
    valeur = float(ligne["value"])
    valeurs_par_zone.setdefault(zone, []).append(valeur)

for zone, valeurs in sorted(valeurs_par_zone.items()):
    minimum = min(valeurs)
    maximum = max(valeurs)
    # TODO : calculer la dispersion (maximum - minimum)
    dispersion = None
    # TODO : compter combien de valeurs de la zone sont >= SEUIL
    nb_au_dessus = None
    print(f"{zone}: min={minimum:.1f} max={maximum:.1f} dispersion={dispersion:.1f} "
          f"mesures au-dessus du seuil={nb_au_dessus}")
```

Comparez ce que cet indicateur montre et ce que le graphique du maximum masquait (durée, fréquence, dispersion). Le graphique doit répondre à une question de décision explicite : la dispersion ou le compte de dépassements y répond-il mieux, moins bien, ou différemment ?

## TP 4 — Rédiger le brief décisionnel

Ce TP se termine par le vote final.

### À coder — rassembler vos preuves chiffrées

Réutilisez les variables déjà calculées (`maxima_par_zone` du TP 2, `ecarts_par_zone` du TP 1) pour préparer les deux preuves chiffrées de votre brief. Complétez les `# TODO` :

```python
# Preuve 1 : la zone et la valeur du maximum le plus élevé sur l'ensemble du lot
zone_max, valeur_max = None, float("-inf")
for zone, maximum in maxima_par_zone.items():
    # TODO : si `maximum` dépasse `valeur_max`, mettre à jour zone_max et valeur_max
    pass
print(f"Preuve 1 : {zone_max} a atteint {valeur_max:.1f} °C")

# Preuve 2 : la zone dont l'écart mesure/réception est le plus grand
zone_ancienne, ecart_max = None, float("-inf")
for zone, ecarts in ecarts_par_zone.items():
    pire = max(ecarts)
    # TODO : si `pire` dépasse `ecart_max`, mettre à jour zone_ancienne et ecart_max
    pass
print(f"Preuve 2 : {zone_ancienne} a une mesure vieille de {ecart_max:.0f} minutes")
```

Rédigez une note de 120 mots maximum contenant :

- une action concrète ;
- un niveau de confiance justifié ;
- les deux preuves chiffrées imprimées ci-dessus, retrouvables dans le CSV ou le JSONL ;
- deux incertitudes importantes ;
- une vérification prioritaire.

Un membre du binôme joue le contradicteur : quelle hypothèse pourrait renverser votre décision ? Revotez ensuite entre les mêmes options A à D, avec votre niveau de confiance.

## Vérification finale à exécuter

```bash
python3 tests/validate_s01_artifacts.py
```

Cette commande vérifie les artefacts et le notebook ; elle ne rédige pas votre recommandation et ne remplace pas vos réponses aux questions codées.

## Aide en cas de blocage

Avant de demander de l’aide, indiquez : l’étape, la commande, le fichier ou la cellule `# TODO`, le message d’erreur, ce que vous avez vérifié et l’effet possible sur votre décision. Ne demandez pas seulement la réponse : demandez quelle vérification réaliser ensuite.

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
