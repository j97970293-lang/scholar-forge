# config/ — règles éditables

Six fichiers JSON (JSON est un sous-ensemble valide de YAML 1.2, lisible partout) pilotent le
comportement de la skill. Les modifier ne nécessite aucun changement de code.

| Fichier | Rôle | Consommé par |
|---|---|---|
| `rules.json` | Expressions « AI slop », placeholders, termes de nuance, seuil de score, pénalités | `sf/lint.py` |
| `sources.json` | 7 API, endpoints, clés optionnelles, limites, champs obligatoires du journal de recherche, pratiques interdites | `sf/sources.py`, `references/04` |
| `venues.json` | 8 profils de venue (IEEE Access, Nature, LNCS, APA7, NeurIPS, ICLR, ACM, arXiv) avec la règle de vérification obligatoire | `references/15` |
| `styles.json` | APA/IEEE/Vancouver/Chicago/Nature + règles d'interopérabilité BibTeX/CSL | `sf/bib.py`, `references/08` |
| `gates.json` | Portes G0–G9, seuils, limites de l'audit | `sf/pipeline.py`, `sf/audit.py` |
| `reporting-guidelines.json` | CONSORT/STROBE/PRISMA/STARD/TRIPOD+AI/COREQ/ARRIVE/SPIRIT/CARE/CHEERS + outils RoB + GRADE | `references/06`, `09`, `13` |

Validation rapide :
```bash
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('config/*.json')]; print('config OK')"
```
