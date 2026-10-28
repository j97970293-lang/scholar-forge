# config/ — règles éditables

Sept fichiers JSON (JSON est un sous-ensemble valide de YAML 1.2, lisible partout) pilotent le
comportement de la skill. Les modifier ne nécessite aucun changement de code.

| Fichier | Rôle | Consommé par |
|---|---|---|
| `rules.json` | Expressions « AI slop », placeholders, termes de nuance, seuil de score, pénalités | `sf/lint.py` |
| `sources.json` | 7 API, endpoints, clés optionnelles, limites, champs obligatoires du journal de recherche, pratiques interdites | `sf/sources.py`, `references/04` |
| `venues.json` | 8 profils de venue (IEEE Access, Nature, LNCS, APA7, NeurIPS, ICLR, ACM, arXiv) avec la règle de vérification obligatoire | `references/15` |
| `styles.json` | APA/IEEE/Vancouver/Chicago/Nature + règles d'interopérabilité BibTeX/CSL | `sf/bib.py`, `references/08` |
| `gates.json` | Portes G0–G9, seuils, limites de l'audit | `sf/pipeline.py`, `sf/audit.py` |
| `reporting-guidelines.json` | **18 directives** datées avec URL officielle et checklist de travail : CONSORT 2025, SPIRIT 2025, CONSORT-AI, SPIRIT-AI, TRIPOD+AI, TRIPOD-LLM, STARD-AI, DECIDE-AI, CLAIM, PRISMA 2020, PRISMA-S, STROBE, COREQ, ARRIVE 2.0, CARE, ENTREQ, CHEERS 2022, checklists ML + outils RoB + GRADE | `sf/guidelines.py`, playbooks 09, 25 |
| `ai-disclosure.json` | 9 catégories de délégation IA (GAIDeT), règles COPE/ICMJE, rôles CRediT humains, sources primaires | `sf/disclosure.py`, playbook 26 |

Validation rapide :
```bash
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('config/*.json')]; print('config OK')"
```
