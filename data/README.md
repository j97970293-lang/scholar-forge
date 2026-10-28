# data/ — jeu de données unifié

| Fichier | Contenu | Taille |
|---|---|---:|
| `registry.json` | 5 460 entrées dédupliquées (skills, suites, dépôts) avec sources, licences, stades, étoiles, vérification | ~2,4 Mo |
| `registry.csv` | Export plat des mêmes entrées | ~700 Ko |
| `registry-stats.json` | Compteurs par source, type, stade | 1 Ko |
| `rankings-snapshot.json` | Classement étoiles/tendances du 2026-10-27 (114 dépôts) | 180 Ko |
| `scan-summary.json` | Agrégats du scan (15 254 fichiers, 2,39 M lignes, 1 713 hôtes…) | 12 Ko |
| `scan-inventory.json` | Inventaire fichier par fichier des 8 dépôts avec SHA-256 et métadonnées | ~6 Mo |
| `source-skills.json` | 3 244 frontmatters `SKILL.md` extraits | ~1,3 Mo |
| `source-python-clis.json` | 748 scripts Python avec point d'entrée CLI | ~100 Ko |
| `security-summary.json` / `security-findings.json` | Résultats du scan statique (21 règles) | ~470 Ko |

Régénération : `make scan` avec `SF_SOURCES` pointant vers les clones (voir `tools/`).

### Données v2 (2026-10-28)

| Fichier | Contenu |
|---|---|
| `scan-v2-summary.json` | 6 dépôts, 1 440 fichiers, 64,1 Mio, 325 337 lignes, 342 scripts Python analysés, 20 `SKILL.md` officiels |
| `scan-v2-inventory.json` | Inventaire avec SHA-256 des 1 440 fichiers |
| `scan-v2-python.json` | Métadonnées AST (imports, fonctions, classes) par script |
| `scan-v2-skills.json` | 20 frontmatters `SKILL.md` officiels |

Régénération v2 : `python3 tools/v2_pipeline.py --sources /chemin/vers/_scan2`.
