# Changelog

## 1.0.0 — 2026-10-27

Création du dépôt unifié à partir de huit dépôts sources.

- **Scan exhaustif** : 8 dépôts, 15 254 fichiers, 136,7 Mo, 2 387 424 lignes ; inventaire
  SHA-256 fichier par fichier, analyse AST de 1 046 scripts Python, extraction de 1 713 hôtes
  réseau et de 1 712 dépôts GitHub référencés (`docs/SCAN_REPORT.md`).
- **Sécurité** : 14 860 fichiers texte passés au crible statique (21 règles), sans exécution
  de code (`docs/SECURITY_SCAN.md`).
- **Fusion des catalogues** : 5 434 entrées dédupliquées issues de 8 jeux de données,
  avec stades du cycle, licences, étoiles, tendances et pertinence académique.
- **Une seule skill** : `SKILL.md` + 22 références progressives + 15 templates + 6 configs.
- **CLI** : 16 commandes, Python 3.9+ stdlib uniquement, 6 API savantes sans clé,
  dégradation gracieuse hors ligne, 30 tests unitaires passants.
- **Qualité** : 10 portes G0–G9, machine à états, `AUDIT.md` PASS/FAIL, 8 cas d'évaluation.
- **Traçabilité** : 8 archives ZIP sans perte (15 314 fichiers, 53,3 Mo), manifeste avec
  commits et SHA-256, `NOTICE.md` et `upstream/LICENSES.md`.
- **Publication** : dépôt GitHub privé + copie sur Google Drive.
