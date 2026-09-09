# Cas fil rouge — Séquence 6bis

> Ce document est le vôtre pour toute la séance. Il se complète par chapitres, dans l'ordre où ils se débloquent en cours. Ne lisez pas un chapitre avant que l'enseignant ne l'annonce : chacun est construit pour être découvert au bon moment, pas relu à l'avance.

## Situation initiale

Base aérienne projetée alpha. Cinq zones critiques sont déjà équipées de capteurs de température : `battery-shelter-01`, `comms-shelter-01`, `it-room-01`, `maintenance-zone-01`, `optronics-shelter-01`. Une sixième zone vient d'être mise en service ce matin pour une mission de ravitaillement : `fuel-storage-01`, un dépôt de stockage carburant.

Vous êtes la cellule data de service. Votre dossier sur `fuel-storage-01` est vide au début de la séance. Il s'épaissit à chaque chapitre, avec le même fichier `tp_seance.py` que vous complétez au fur et à mesure — jamais un nouveau fichier, jamais un nouvel outil.

**Question qui reste ouverte toute la journée : `fuel-storage-01` mérite-t-elle une vérification terrain avant la fin de votre service ?**

---

## Chapitre 1 — Indicateurs (matin)

*Débloqué à l'ouverture de la séance.*

> « La température moyenne de la base est normale. »

Vous disposez du relevé du matin sur les cinq zones déjà connues (`data/processed/batch001_measurements.csv`). `fuel-storage-01` n'apparaît pas encore dans ce lot.

Notes de chapitre (à remplir en séance) :

- Moyenne globale calculée : ______
- Zone dont le maximum dépasse pourtant le seuil pédagogique (35 °C) : ______
- Ce que cette moyenne ne permet pas d'affirmer : ______

## Chapitre 2 — Score automatique (matin)

*Débloqué après le débrief du chapitre 1.*

Un score automatique existe déjà pour les cinq zones connues. Vous l'utilisez sans lire sa logique interne.

- Zone signalée « inspection recommandée » par le score : ______
- Ce score confirme-t-il ou contredit-il le chapitre 1 ? ______

## Chapitre 3 — Une nouvelle zone (bascule)

*Débloqué en fin de matinée.*

`fuel-storage-01` vient d'envoyer ses cinq premières mesures. Vous appliquez le même score automatique, sans le modifier.

- Score obtenu pour `fuel-storage-01` : ______
- Décision affichée par le score : ______
- Ce score a-t-il déjà vu une zone de stockage carburant pendant sa calibration ? ______

Question à garder en tête pour l'après-midi : **un score qui n'a jamais été calibré sur ce type de zone peut-il seulement se tromper « fort », ou peut-il aussi se tromper en restant silencieux ?**

## Chapitre 4 — Un nouveau relevé (après-midi)

*Débloqué après la pause.*

Un nouveau relevé de `fuel-storage-01` arrive en tout début d'après-midi : trois mesures, avec un vide de vingt-cinq minutes au milieu. Vous produisez deux graphiques honnêtes à partir des trois mêmes points — rien n'est recalculé, seul un paramètre change entre les deux appels.

- Seuil pédagogique utilisé pour le premier graphique : ______ °C — une mesure le franchit-elle ? ______
- Seuil réel de sécurité carburant utilisé pour le second graphique : ______ °C — une mesure le franchit-elle ? ______
- Un élément affiché sur le graphique (titre, légende, texte) reste-t-il identique aux deux seuils, alors qu'il ne devrait plus l'être ? Lequel ? ______

## Chapitre 5 — Briefing et décision finale

*Débloqué en fin de séance.*

Vous rédigez la note de briefing finale sur `fuel-storage-01`, au format imposé : message principal, limite, niveau de confiance, vérification recommandée.

- Recommandation retenue : ______
- Confiance : ______
- Preuve n°1 citée (fichier + chiffre) : ______
- Preuve n°2 citée (fichier + chiffre) : ______
- Ce que votre dossier ne permet toujours pas d'affirmer avec certitude : ______

---

## À retenir en sortant de la séance

Un indicateur transparent (la moyenne), un score automatique fiable sur son périmètre de calibration, et un graphique honnête dans sa mise en forme peuvent chacun, à leur manière, laisser passer `fuel-storage-01` sans alerte — pas parce qu'ils mentent, mais parce que chacun porte une hypothèse qu'on cesse de remettre en cause dès qu'on lui fait confiance. Relire ce que chaque sortie affirme réellement reste le geste qui ne se délègue jamais.
