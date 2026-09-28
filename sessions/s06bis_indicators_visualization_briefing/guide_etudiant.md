# Guide étudiant — Séquence 6bis

## Mission

Une phrase circule ce matin sur le réseau de la base : « la température moyenne de la base est normale. » Le commandant s'appuie sur cette phrase pour décider s'il maintient l'activité prévue. Il vous confie la vérification.

En fin de matinée, une sixième zone entre en service : `fuel-storage-01`, un dépôt de stockage carburant. Vous allez la suivre jusqu'à la fin de la séance.

## Documents à votre dispisition : 
- `cas_fil_rouge.md` : c'est votre dossier de mission. Il se complète chapitre par chapitre, au même rythme que ce guide. 
- `tp_seance.py` : c'est votre seul fichier de code pour toute la séance — vous le complétez étape par étape.

>**Ce guide se suffit à lui-même.** Chaque étape commence par un encadré **« À savoir »** qui contient le contenu théorique nécessaire. Les slides du cours reprennent le même contenu.

## L'idée qui traverse toute la séance

Un indicateur transparent, un score automatique fiable sur son périmètre de calibration et un graphique honnête dans sa mise en forme peuvent chacun, à leur manière, laisser passer un risque. Aucun des trois n'est pour autant « faux ». Ils sont trois formes successives du même geste, **compresser des mesures pour décider** :

- une moyenne ;
- un score dont on ne lit pas la logique ;
- un graphique dont on ne relit pas toujours le texte.

Chaque compression porte des choix. Le travail de la séance consiste à les retrouver et à les nommer.


**Question qui guide la séance :** `fuel-storage-01` mérite-t-elle une vérification terrain avant la fin du service ? Aucun outil de la séance ne répondra seul à cette question, et chacun peut vous laisser croire que la réponse est non, pour une raison différente. Le raisonnement compte autant que la conclusion.

## Trois paliers par étape

Chaque étape de `tp_seance.py` comporte trois phases : une question socle, une question d'approfondissement et un défi.

> **Les défis sont un bonus.** Ils sont réservés aux binômes qui ont terminé le socle et l'approfondissement avant la fin du temps recommandé. Ne commencez jamais un défi tant que l'approfondissement de la même étape n'est pas terminé.

## Deux règles de méthode

1. **Pronostic d'abord.** Avant chaque exécution, écrivez votre pronostic dans la rubrique prévue de `cas_fil_rouge.md`. Il ne se corrige plus ensuite. Un pronostic faux, honnêtement noté puis expliqué, est valorisé.
2. **L'IA générative est autorisée, mais elle ne rédige pas votre dossier.** Vous pouvez vous faire aider pour la syntaxe Python ou matplotlib. En revanche, les hypothèses, les fiches, les choix de fenêtre, de seuil et de règle de confiance, les audits et la recommandation seraient notés sur votre capacité à les **défendre à l'oral** avec un fichier et un chiffre. Une réponse que vous ne savez pas justifier est inutile.

## Règle d'exécution

**Règle impérative : n'ouvrez `src/iot_decision/risk_score.py` sous aucun prétexte avant d'avoir terminé le socle de l'étape 3.** L'enquête de l'étape 2 n'a de sens que si vous ne connaissez pas sa logique.

## Préparer l'environnement

```bash
python3 -m pip install -r sessions/s06bis_indicators_visualization_briefing/requirements.txt
export PYTHONPATH=src
python3 -m pytest -q
```

Cette séquence ne nécessite pas Docker ni de broker MQTT.

## Étape 1 — indicateurs, classements, fiche indicateur — 40 min

> ### À savoir — un indicateur est un choix de compression
>
> Un **indicateur** résume plusieurs mesures en un chiffre. Chaque résumé conserve une information et en jette d'autres. La question n'est jamais « cet indicateur est-il juste ? », mais « à quelle question répond-il, et qu'a-t-il jeté ? ».
>
> | Notion | Définition | Piège fréquent |
> |---|---|---|
> | **Moyenne** | somme des valeurs divisée par leur nombre ; un résumé unique de toutes les mesures | la croire représentative de chaque zone ; une zone très chaude peut disparaître dans la masse des autres |
> | **Maximum / minimum** | valeur la plus haute / la plus basse observée, par zone | interpréter un pic comme une tendance ; le maximum ne dit rien de la durée |
> | **Amplitude** | maximum − minimum d'une zone ; mesure la variabilité | la confondre avec un niveau de danger ; elle signale une instabilité, pas un dépassement |
> | **Tendance** | variation rapportée au temps réellement écoulé (°C par heure) | la calculer sur trop peu de points, ou la prolonger sans cause physique |
> | **Dernière valeur** | la mesure la plus récente d'une zone | oublier son heure : deux « dernières valeurs » ne sont comparables que si elles ont été mesurées au même moment |
> | **Seuil** | valeur de référence à partir de laquelle on discute d'une action | le prendre pour une norme officielle ; dans ce cours, 35 °C est un **seuil pédagogique** |
> | **Rang** | position d'une zone dans un classement selon un indicateur | croire que le classement est une propriété des zones ; il dépend de l'indicateur choisi |
>
> **Zone masquée.** C'est une zone dont un indicateur local (son maximum) franchit un seuil, alors que le résumé global (la moyenne de toutes les zones) reste dessous. La moyenne n'est pas fausse : elle répond à « la base est-elle globalement chaude ? », pas à « une zone est-elle en danger ? ».
>
> **Fiche indicateur.** Proposer un indicateur, c'est prendre une décision de conception. Une fiche indicateur rend cette décision explicite en sept rubriques :
>
> 1. la question de décision servie ;
> 2. la formule exacte ;
> 3. le seuil d'alerte et sa provenance ;
> 4. la fenêtre de temps ;
> 5. ce que l'indicateur ne verra jamais (son angle mort) ;
> 6. l'objection d'un tiers ;
> 7. votre réponse à cette objection.
>
> Une fiche sans angle mort est une fiche incomplète.
>
> **Règle pratique.** Avant de se fier à un résumé global, le décomposer par zone, et vérifier à la main au moins un calcul.

**Socle.** Complétez `etape1_indicateurs()` : moyenne globale, maximum, minimum et amplitude par zone, zone masquée par la moyenne, zone la plus instable. Vérifiez à la main la moyenne d'une zone (l'équipe data pose l'addition, le décideur critique refait le calcul sans regarder l'écran).

**Approfondissement.** Complétez `etape1_approfondissement_classements()` : ajoutez moyenne de zone, dernière valeur (avec son heure) et tendance en °C/h, puis affichez un tableau de rangs. Le classement des zones est-il le même pour tous les indicateurs ? Les dernières valeurs sont-elles comparables entre elles ? Rédigez la **fiche indicateur** du chapitre 1 : vous la défendrez face au binôme voisin au débrief.

**[DÉFI — BONUS]** `etape1_defi_nouvel_indicateur()` : inventez un indicateur qui produit encore un autre classement.

## Étape 2 — Du calcul transparent au calcul opaque — 50 min

> ### À savoir — score automatique, calibration, audit
>
> | Notion | Définition | Piège fréquent |
> |---|---|---|
> | **Score automatique** | fonction qui transforme des mesures en une note puis en recommandation (« inspection recommandée » / « aucune action requise »), sans que sa logique soit lue au moment de la décision | le croire plus objectif parce qu'il est automatique : il reproduit et cache les choix de son concepteur, comme une moyenne cache une dispersion |
> | **Boîte noire** | système dont on voit les entrées et les sorties, mais pas la logique interne | conclure qu'on ne peut rien en savoir |
> | **Calibration** | réglage des paramètres d'un score (seuils, poids) sur un ensemble de cas connus | oublier sur quels cas il a été calibré |
> | **Domaine de validité** | l'ensemble des situations semblables à celles de la calibration, pour lesquelles le score est fiable | l'appliquer hors de ce domaine sans le savoir |
> | **Dérive / hors calibration** | écart entre la situation actuelle et celles de la calibration (nouveau type de zone, nouveau capteur, nouvelles conditions) | ne la remarquer qu'après l'incident |
> | **Biais d'automatisation** | tendance à faire davantage confiance à une machine qu'à un calcul qu'on pourrait vérifier soi-même | ne plus remettre en cause un score qui « a toujours eu raison » |
> | **Audit** | vérification indépendante de ce que fait un système, et de ses limites | le réduire à la lecture du code ; en opération, on dispose rarement du code d'un outil fourni |
>
> **Auditer une boîte noire par sondes.** On lui soumet des entrées fabriquées exprès, et on observe ses sorties. C'est une démarche expérimentale en quatre temps :
>
> 1. **Hypothèses d'abord.** Écrire ce que l'on croit avant de tester (« le score dépend de la moyenne », « le score dépend du type de zone »…). Une hypothèse écrite après coup ne prouve rien.
> 2. **Une référence.** Définir une série de mesures simple, dont on note le score.
> 3. **Un seul facteur à la fois.** Chaque sonde ne diffère de la référence que par un seul élément : la valeur maximale, le nombre de mesures, la durée, l'ordre, le nom de zone, le type d'installation… Si deux facteurs changent en même temps, on ne sait pas lequel a produit l'effet.
> 4. **Conclure.** Lister les facteurs qui font bouger le score et ceux qui le laissent identique. En déduire une formule approchée, et chercher le point de bascule de la décision.
>
> Un facteur qui ne change jamais le score est un facteur **ignoré** par le score. C'est souvent là que se cache son angle mort.

**Socle.** Complétez `etape2_score_zones_connues()` : appelez `score_all_zones(rows)` — la boîte noire fournie — et affichez zone, score et décision. Pronostic d'abord : quelle zone attendez-vous en tête ?

**Approfondissement.** Complétez `etape2_approfondissement_sondes()`. Vous ne pouvez pas lire le code, mais vous pouvez fabriquer vos propres mesures avec l'utilitaire `_mesures_synthetiques()` et observer ce que répond le score — c'est ainsi qu'on audite un système fermé.

1. Écrivez au moins quatre hypothèses au chapitre 2 **avant** la première sonde.
2. Concevez au moins cinq sondes, chacune ne changeant **qu'un seul facteur** par rapport à une référence.
3. Concluez : facteurs pris en compte, facteurs ignorés, formule reconstruite, température de bascule.

**[DÉFI — BONUS]** `etape2_defi_bascule_minimale()` : la plus petite série qui fait basculer le score, et une zone redescendue sous le seuil qui reste pourtant signalée.

## Étape 3 — une sixième zone — 35 min

> Une nouvelle zone, `fuel-storage-01`, vient d'être équipée pour une mission de ravitaillement.

> ### À savoir — bug, défaut de conception, réparation
>
> **Bug ou défaut de conception ?**
>
> - Un **bug** : le code ne fait pas ce que son auteur voulait.
> - Un **défaut de conception** : le code fait exactement ce que son auteur voulait, mais cette intention ne couvre pas la situation présente.
>
> Un score appliqué hors de son domaine de validité n'a généralement pas de bug. Il applique correctement une règle qui n'a pas été pensée pour ce cas.
>
> **Un seuil appartient à un type d'installation.** Une température acceptable dans un local informatique ne l'est pas forcément pour un stockage de batteries, un poste médical ou un dépôt de carburant. Les seuils réels viennent de la nature de ce qu'on protège, pas des données du capteur. Dans ce cours, la table `data/samples/batch005_asset_thresholds.csv` donne un seuil par couple (type d'installation, capteur). Elle indique aussi le sens du seuil : `>=` pour un plafond, `<=` pour un plancher.
>
> **Réparer un score déplace souvent l'angle mort sans le supprimer.** Une réparation corrige l'hypothèse qui a échoué, et garde toutes les autres. Il faut donc toujours se demander : « quelle est la prochaine situation que cette version ne couvrira pas ? ».
>
> **Fiche de domaine de validité.** Inspirée des *model cards* utilisées pour documenter les modèles d'apprentissage automatique, elle accompagne un score et rend explicites :
>
> - ses données d'entrée utilisées, et celles qu'il ignore ;
> - les cas sur lesquels il a été calibré ;
> - ses hypothèses implicites ;
> - les cas hors domaine déjà connus ;
> - qui doit le réviser, et à quel déclencheur.

**Socle.** Pronostic d'abord, **à partir de la formule que vous avez reconstruite** : quel score pour `fuel-storage-01` ? Complétez `etape3_nouvelle_zone()`. Le score de `fuel-storage-01` se distingue-t-il des zones jugées sûres ? A-t-il un bug, ou applique-t-il correctement une règle hors de son domaine ? Seulement maintenant, ouvrez `src/iot_decision/risk_score.py` : qu'est-ce que votre enquête avait trouvé, qu'est-ce qu'elle avait manqué ?

**Approfondissement.** Complétez `etape3_approfondissement_score_v2()` : un score qui prend le seuil de chaque zone dans `data/samples/batch005_asset_thresholds.csv`. Puis remplissez la **fiche de domaine de validité** du score d'origine au chapitre 3.

**[DÉFI — BONUS]** `etape3_defi_septieme_zone()` : fabriquez une septième zone plausible sur laquelle `score_v2` se tromperait encore.

## Étape 4 — extraction, et choix de la fenêtre — 25 min

> ### À savoir — fenêtre de temps, silences, traçabilité
>
> **Fenêtre de temps.** C'est la période retenue pour calculer un indicateur ou tracer un graphique. Choisir une fenêtre est une décision : elle peut suffire à inverser une conclusion sans modifier une seule valeur. Elle doit donc être écrite dans le dossier, avec la raison de son choix et le nom de celui qui l'a choisie.
>
> **Exact n'est pas représentatif.** Une affirmation est **exacte** si elle est vraie sur les données sur lesquelles elle a été calculée. Elle est **représentative** si elle reste vraie quand on élargit ou déplace la fenêtre. Une phrase peut être exacte et non représentative : c'est l'un des pièges les plus fréquents d'un briefing.
>
> **Silence de données.** C'est un intervalle anormalement long entre deux mesures consécutives, par rapport à la fréquence attendue du capteur. Dans cette séquence, on parle de silence au-delà de 7 minutes : 5 minutes de fréquence nominale, plus 2 minutes de tolérance. Pendant un silence, on ne sait rien. La valeur a pu rester stable, monter ou descendre.
>
> **Réseau ou capteur ?** 
>
> - Chaque message porte un **numéro de séquence** incrémenté par le capteur à chaque émission, une heure de mesure (`measured_at`) et une heure de réception (`received_at`).
> - **Un numéro manquant** signifie qu'un message émis n'est jamais arrivé : c'est une perte en route.
> - **Des numéros consécutifs** séparés par un long silence signifient que le capteur n'a rien émis pendant ce temps.
> - Les deux cas n'appellent pas la même vérification.
>
> **Formuler une hypothèse utile.** Une hypothèse sur ce qui s'est passé n'a de valeur que si on peut dire comment la vérifier : un journal d'intervention, un relevé manuel, une question à la personne présente sur place, une comparaison de deux horodatages…

**Socle.** Complétez `etape4_extraction_apres_midi()` : écrivez les huit mesures de la journée dans `data/processed/batch003_measurements.csv`, puis la fenêtre à partir de `2026-11-02T10:00:00Z` dans `data/processed/batch003_afternoon_window.csv`.

**Approfondissement.** Complétez `etape4_approfondissement_fenetres()` : comparez matin, après-midi et journée entière (proportion au-dessus de 28 °C, min, max, moyenne, plus long silence), et affichez les numéros de séquence. Au chapitre 4a : la phrase « 1 mesure sur 3 au-dessus du seuil réel » est-elle représentative ? Que s'est-il passé entre 09:20 et 10:00 (au moins quatre hypothèses, chacune avec sa vérification) ? Les silences viennent-ils du réseau ou du capteur ?

**[DÉFI — BONUS]** `etape4_defi_fenetre_inverse()` : deux fenêtres plausibles, deux conclusions opposées.

## Six leviers de mise en forme — 10 min

> ### À savoir — les leviers de mise en forme
>
> Un graphique ne montre jamais « les données » : il montre des données **mises en forme**. Chacun des six leviers ci-dessous est, pris isolément, un choix de présentation légitime. Combinés sans être nommés, ils peuvent changer complètement l'impression produite sans modifier une seule valeur.
>
> | Levier | Définition | Piège fréquent | Effet sur la décision |
> |---|---|---|---|
> | **Fenêtre de temps** | période retenue pour tracer | ne pas écrire qui l'a choisie, ni pourquoi | peut inverser la conclusion |
> | **Échelle** | bornes de l'axe des ordonnées | tronquer l'axe autour des valeurs observées | amplifie toute variation, même faible ; à l'inverse, un axe très large écrase tout |
> | **Espacement du temps** | points placés à intervalles réguliers (libellés), ou selon le temps réellement écoulé | faire occuper à 25 minutes la même largeur qu'à 5 minutes | rend un silence invisible |
> | **Seuil affiché** | valeur de référence tracée sur la figure | l'omettre, ou afficher un seuil non pertinent pour la zone | prive le lecteur de repère, ou le rassure à tort |
> | **Annotation** | texte, flèche, zone surlignée qui désigne ce que les données seules ne montrent pas | croire qu'une figure sans annotation est plus objective | sans elle, un doute devient une fausse évidence |
> | **Incertitude visuelle** | représentation explicite d'un silence ou d'une zone non mesurée | relier deux points par un trait continu malgré un vide entre eux | fait paraître régulière une évolution jamais observée |
>
> S'y ajoutent des leviers plus discrets : le **titre** (descriptif ou affirmatif), les **couleurs** (vert rassure, rouge alarme), l'épaisseur des traits, l'ordre et la taille des légendes.
>
> **Trompeur n'est pas faux.**
>
> - Une figure **fausse** contient une valeur inexacte.
> - Une figure **trompeuse** ne contient que des valeurs exactes, mais produit une impression que les données ne justifient pas.
> - Une figure **grave** n'est pas forcément trompeuse : elle peut être alarmante et entièrement justifiable.
>
> Modifier, inventer ou supprimer une valeur n'est plus de la mise en forme : c'est de la **falsification**.

## Étape 5 — graphiques trompeurs — 30 min + 10 min d'échange

> ### À savoir — pourquoi construire soi-même une figure trompeuse
>
> Il est plus facile de nommer après coup les leviers d'une figure faite par un autre que de les repérer dans la sienne, sous contrainte de temps. Actionner soi-même, volontairement, chaque levier du tableau ci-dessus permet ensuite de les reconnaître quand on les actionne sans le vouloir.
>
> **Red team.** Une équipe adverse examine un produit sans connaître l'intention de son auteur, et cherche ce qui cloche. Ici, l'autre binôme reçoit votre figure sans votre carte. Il doit deviner votre commande et nommer chaque levier. S'il n'y arrive pas, votre figure tromperait aussi un vrai lecteur.
>
> **Grille de détection.** Face à n'importe quelle figure, passer en revue chaque levier :
>
> - Quelle fenêtre ?
> - Quelle échelle ?
> - Quel espacement du temps ?
> - Quel seuil, et pourquoi celui-là ?
> - Comment les silences sont-ils traités ?
> - Que dit le titre ?
> - Que suggèrent les couleurs ?
>
> Le levier le plus dangereux est celui qu'on ne pense pas à vérifier.

**Socle.** Complétez `etape5_graphique_trompeur()` sur les trois points de l'après-midi : temps régulièrement espacé quelle que soit la durée réelle, axe des ordonnées resserré, aucun seuil, trait continu. Enregistrez vers `fuel_storage_misleading_scale.png`. Ce graphique contient-il une seule valeur inexacte ?

**Approfondissement — commande cachée.** L'enseignant vous remet une carte de `cartes_commande.md`. Sans la montrer, complétez `etape5_approfondissement_commande(lettre)` : produisez la figure qui remplit la commande, sans modifier aucune valeur à l'intérieur de la fenêtre choisie. Puis **échangez uniquement la figure** avec un autre binôme : chacun devine la commande de l'autre et remplit la grille de détection du chapitre 4b.

**[DÉFI — BONUS]** `etape5_defi_double_commande()` : une figure rassurante pour qui ne lit que le titre, alarmante pour qui lit tout — ou l'inverse.

## Étape 6 — graphiques honnêtes — 30 min

> ### À savoir — ce qui rend une figure honnête
>
> Une figure honnête n'est pas une figure neutre : c'est une figure dont chaque choix de mise en forme est **justifiable indépendamment**. Principes pour une série temporelle :
>
> - **Le temps à l'échelle réelle.** L'écart horizontal entre deux points est proportionnel au temps écoulé.
> - **Les silences visibles.** On ne relie pas par un trait deux mesures séparées par un silence. On le rend visible (zone grisée) et on l'annote avec sa durée.
> - **Un seuil pertinent, tracé et légendé.** Le lecteur doit savoir à quoi comparer, et d'où vient ce seuil.
> - **Une échelle qui ne dramatise pas.** Pour une température comparée à un seuil, un axe partant de 0 évite d'amplifier artificiellement une variation. On peut s'en écarter, mais il faut le dire.
> - **Un paramètre plutôt qu'une copie.** Si l'on trace la même figure pour plusieurs seuils, on écrit une seule fonction avec le seuil en paramètre, sans dupliquer le code. Tout texte qui dépend du seuil (titre, légende) doit être construit à partir de ce paramètre. Un texte recopié à la main reste figé sur le premier cas.
>
> **Titre descriptif ou titre-message ?**
>
> - Un **titre descriptif** dit ce qui est tracé (« fuel-storage-01 — seuil à 28 °C »).
> - Un **titre-message** dit ce qu'il faut retenir (« dernière mesure au-dessus du seuil, après un silence »). Il aide le lecteur pressé, mais il *affirme*.
> - Un titre-message n'est acceptable que s'il est **calculé à partir des données tracées**, jamais écrit à la main.
>
> **Maquette papier.** Dessiner la figure avant de la coder oblige à décider de ce que le lecteur doit voir en premier. Sinon, les réglages par défaut de la bibliothèque décident à votre place. Contrainte de l'exercice : le commandant regarde la figure 5 secondes, sur une tablette, sans commentaire oral.

**Socle.** D'abord **5 minutes de maquette papier**, sans écran : le commandant verra la figure 5 secondes sur une tablette. Puis complétez `etape6_deux_graphiques_honnetes()` : une fonction `tracer_honnete(threshold, destination)` qui corrige un par un les choix de l'étape 5, appelée deux fois en ne changeant que `threshold` (35.0 puis 28.0). Les deux graphiques contiennent-ils une valeur différente ? Le titre dit-il la même chose sur les deux ? Est-il exact sur les deux ?

**Approfondissement.** Complétez `etape6_approfondissement_titre_message()` : une version de la figure à 28 °C dont le titre dit ce qu'il faut retenir, **calculé à partir des données**. Un titre-message est-il plus ou moins honnête qu'un titre descriptif ?

**[DÉFI — BONUS]** `etape6_defi_journee_complete()` : toute la journée, deux seuils, deux silences, lisible en 5 secondes — testée sur un lecteur d'un autre binôme.

## Débrief design — 10 min

Laquelle de toutes les figures produites donne l'impression la plus grave ? Est-ce la plus exacte ? Qu'est-ce qui différencie, précisément, « trompeur » de « grave » ? Quels leviers la classe ajoute-t-elle à la grille de détection ?

## Étape 7 — confiance, note, audit — 25 min

> ### À savoir — note de briefing, règle de confiance, audit d'un texte généré
>
> **Format de la note de briefing** (quatre lignes) :
>
> - **Message principal** : ce que l'observation permet d'affirmer, avec ses chiffres.
> - **Limite** : ce que l'observation ne permet pas encore de conclure.
> - **Niveau de confiance** : faible, moyenne ou élevée, déduit d'une règle.
> - **Vérification recommandée** : l'action qui lèverait le doute.
>
> **Format BLUF** (*Bottom Line Up Front*) : la conclusion en première ligne, les justifications ensuite. Le lecteur pressé qui s'arrête à la première ligne a l'essentiel.
>
> **Une bonne règle de confiance :**
>
> - elle est **explicite** : écrite avant d'être appliquée ;
> - elle est **systématique** : appliquée de la même façon à tous les cas, jamais ajustée au cas par cas pour obtenir le résultat souhaité ;
> - elle est **justifiée** : chaque borne chiffrée a une raison ;
> - elle est **attribuée** : on sait qui l'a validée.
>
> Critères couramment utilisés : nombre de mesures, présence et durée des silences, marge entre la valeur observée et le seuil, provenance du seuil, cohérence avec le reste de la journée, fraîcheur de la dernière mesure. Une confiance « choisie à la main » n'est pas une confiance : c'est une opinion.
>
> **Auditer un texte produit automatiquement** (par un script, un score ou une IA générative). Chaque affirmation se range dans l'une de quatre catégories :
>
> | Catégorie | Signification |
> |---|---|
> | **Exacte** | vérifiable, et vérifiée |
> | **Fausse** | vérifiable, et contredite par le recalcul |
> | **Exacte mais trompeuse** | vraie à la lettre, mais suggère une conclusion que les données ne justifient pas (mauvais seuil, extrapolation, mot comme « conforme ») |
> | **Invérifiable** | ne peut pas être établie à partir des données fournies ; une IA générative peut produire des affirmations plausibles et précises sans base réelle |
>
> Trois réflexes :
>
> 1. recalculer chaque chiffre ;
> 2. vérifier quel seuil et quelle fenêtre ont été utilisés ;
> 3. vérifier sur quelles données le texte a réellement été produit.
>
> Un texte bien écrit et sûr de lui n'est pas un texte vérifié. L'erreur la plus dangereuse n'est pas toujours la plus visible : c'est celle qui porte la décision.

**Socle.** Aucune règle de confiance ne vous est donnée. Au chapitre 5a, listez au moins quatre critères candidats, retenez-en au moins deux, justifiez chaque borne chiffrée, puis codez `regle_confiance(rows, threshold)`. Complétez ensuite `etape7_note_de_briefing()` : note en quatre lignes (message principal, limite, confiance, vérification), chaque chiffre venant d'une variable.

**Approfondissement.** Ouvrez `note_ia_a_auditer.md` : une note produite par un assistant IA sur les mêmes données. Classez chacune de ses affirmations (exacte / fausse / exacte mais trompeuse / invérifiable) au chapitre 5b, et codez dans `etape7_approfondissement_audit_note_ia()` le recalcul de chaque chiffre qu'elle annonce.

**[DÉFI — BONUS]** `etape7_defi_trois_destinataires()` : la même note pour le commandant, le chef de dépôt et la cellule capteurs, au format BLUF.

## Étape 8 — recommandation, pré-mortem — 20 min

> ### À savoir — recommander, et anticiper son erreur
>
> **Une recommandation opérationnelle contient toujours :**
>
> - une **décision** claire ;
> - un **niveau de confiance** ;
> - des **preuves**, chacune citée par son fichier et sa valeur ;
> - une **limite** : ce que le dossier ne permet pas d'affirmer.
>
> La pièce jointe (la figure) fait partie de la recommandation. Un lecteur pressé ne lira souvent qu'elle. Joindre une figure trompeuse, même accompagnée d'un commentaire, c'est laisser l'image décider à votre place.
>
> **Pré-mortem.** Technique de décision proposée par le psychologue Gary Klein. Avant d'agir, on imagine que la décision a déjà échoué, et on se demande pourquoi. Cela contourne l'excès de confiance : il est plus facile d'expliquer un échec présenté comme certain que d'imaginer un échec possible. Deux types d'erreurs à envisager :
>
> - l'**alerte à tort** : on a mobilisé des moyens pour rien ;
> - l'**alerte trop faible** : on a laissé passer un vrai problème.
>
> Pour chaque scénario, on cherche l'indice **déjà présent aujourd'hui** dans le dossier.
>
> **Asymétrie des coûts.** Les deux erreurs n'ont pas le même prix :
>
> - une vérification inutile coûte du temps et se rattrape ;
> - un défaut non détecté peut être grave et irréversible.
>
> Le niveau de confiance exigé pour renoncer à agir dépend de cette asymétrie, pas seulement des données.
>
> **Plan de collecte.** Si la confiance est insuffisante, la bonne réponse est souvent de dire quelle donnée supplémentaire changerait la décision, et dans quel sens : relevé manuel, capteur redondant, fréquence de mesure, information humaine.

**Socle.** Dans `etape8_recommandation_finale()`, indiquez par un `print` quelle figure accompagne le dossier, et pourquoi pas chacune des autres. Rédigez ensuite, en moins de 100 mots, la recommandation : décision, confiance, deux preuves chiffrées (fichier + valeur), et ce que le dossier ne permet toujours pas d'affirmer.

**Approfondissement.** `etape8_approfondissement_premortem()` : nous sommes demain, votre recommandation s'est révélée fausse. Trois scénarios (au moins une alerte à tort, au moins une alerte trop faible), l'indice présent aujourd'hui pour chacun, et un plan de collecte.

**[DÉFI — BONUS]** `etape8_defi_cout_de_l_erreur()` : coût comparé des deux erreurs possibles.

## Brief oral et questions contradictoires — 15 min

Chaque binôme dispose de 3 minutes pour défendre sa recommandation sur `fuel-storage-01`. Les rôles permutent à chaque passage :

- **cellule data** : présente la recommandation et ses preuves ;
- **décideur pressé** : veut une réponse en une phrase et coupe les détails ;
- **red team** : cherche le choix non assumé, le chiffre non sourcé, la figure qui trompe.

Questions types :

- « Si je vous impose l'autre seuil sur le même graphique, votre recommandation change-t-elle ? »
- « Qu'est-ce qui, dans votre dossier, n'est pas une mesure mais un choix de votre part ? »
- « Pourquoi n'avoir tracé que l'après-midi ? »
- « Votre règle de confiance, qui l'a validée ? »

## Validation finale à exécuter

```bash
python3 tests/validate_s06bis_artifacts.py
```

## Exit ticket

1. « Un indicateur, un score ou un graphique honnête permet d'affirmer que… »
2. « Il ne permet pas d'affirmer que… »
3. « Avant de répéter un texte ou une figure produits par un outil — score, graphique ou IA —, je vérifierais… »

## Aide en cas de blocage

Avant de demander de l'aide, indiquez : l'étape, la commande ou le fichier, le message d'erreur, ce que vous avez déjà vérifié. Les solutions, valeurs de référence et observations attendues sont réservées au guide enseignant et au corrigé.
