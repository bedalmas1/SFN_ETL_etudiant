# De la donnée capteur à la décision opérationnelle

Support pédagogique destiné aux officiers et élèves officiers de l’École de l’air et de l’espace.

Le cours étudie comment des données de capteurs imparfaites traversent une pipeline IoT et deviennent des indicateurs utilisés pour décider. Le fil rouge relie systématiquement qualité des données, confiance, incertitude, risques et décision opérationnelle.

## État du dépôt

Cette première étape installe uniquement l’arborescence. Les contenus seront ajoutés progressivement : syllabus, puis une séquence complète à la fois, scripts testés et vérification finale.

## Environnement d’exécution

L’ensemble du cours s’exécute sous Linux dans un terminal Bash. Les commandes utilisent `python3`, `python3 -m pip`, des chemins POSIX et Docker Engine avec le plugin Compose. PowerShell, les chemins Windows et le lanceur `python.exe` ne font pas partie de l’environnement pédagogique.
## Organisation

- `syllabus/` : syllabus général et bibliographie ;
- `sessions/` : huit séquences de quatre heures, précédées d'une séquence 0 optionnelle de 3 h sans écran (`sessions/s00_pipeline_detective/`), utilisable en ouverture même sans accès informatique ;
- `latex/common/` : préambule Beamer et bibliographie partagés ;
- `src/` : code Python pédagogique ;
- `data/` : données brutes, traitées et échantillons ;
- `notebooks/` : notebooks Jupyter ;
- `docker/` : environnement MQTT local ;
- `tests/` : tests automatisés ;
- `prompts/` : grilles et prompts d’évaluation assistée par IA.

Chaque séquence conserve ses slides dans `sessions/<séquence>/slides/`. Le fichier
`.tex` principal et les figures associées restent ainsi proches des exercices et
des guides de la séquence. Les fichiers générés par LaTeX ne sont pas versionnés.

## Principe de progression

Chaque étape importante fait l’objet d’une validation avant modification. Le dépôt privilégie de petits changements et des commits explicites.
