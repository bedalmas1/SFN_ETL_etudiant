# Ressources LaTeX partagées

Le dossier `common/` contient les éléments communs aux huit présentations :

- `preamble.tex` : dépendances et commandes Beamer minimales ;
- `references.bib` : bibliographie BibTeX commune.

Chaque présentation reste dans le dossier `slides/` de sa séquence. Depuis ce
dossier, le préambule est chargé avec :

```tex
\input{../../../latex/common/preamble}
```

Pour chaque séquence, compiler depuis son dossier `slides/` et conserver le PDF
livrable sous `sXX_nom_sequence.pdf`. Les fichiers intermédiaires produits par
LaTeX (`.aux`, `.log`, `.nav`, `.out`, `.snm`, `.toc`, `.vrb`, `.bbl`, `.blg`,
`.fls`, `.fdb_latexmk`, `.synctex.gz`) restent ignorés par Git. Une vérification
PDF doit contrôler le nombre de pages, la lisibilité, les figures, les références
et l'absence de texte hors cadre.
