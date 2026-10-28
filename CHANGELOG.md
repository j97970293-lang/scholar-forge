# Changelog

## 1.1.0 — 2026-10-28

Recherche documentaire 2026, six dépôts complémentaires et mise en conformité.

- **Conformité Agent Skills** : `description` ramenée à 889 caractères (limite 1024),
  `metadata` en chaînes, `validate` + `tools/validate_skill.py`, playbook 23,
  références maintenues à un seul niveau, `install.sh` produisant un dossier allégé.
- **Intégrité des références** : `sf/integrity.py` croise OpenAlex `is_retracted`, les
  notices `updated-by` de Crossref et les marqueurs de titre ; consensus à 2 signaux,
  verdicts non définitifs, porte `G-integrity` (audit passe à 8 portes), playbook 24.
  Vérifié en ligne sur un DOI réellement rétracté (3 signaux convergents).
- **Recherche reproductible** : filtres `--from-year/--to-year/--min-citations/--oa-only/--type`
  (natif quand l'API le permet + réapplication locale), exports CSV/RIS, journal
  `sources/search-log.{md,json}` conforme PRISMA-S, commande `searchlog`, playbook 27.
- **Directives de rapport** : `config/reporting-guidelines.json` v2 (18 directives) avec
  TRIPOD+AI 2024, STARD-AI 2025 corrigé 2026, TRIPOD-LLM, CONSORT-AI, SPIRIT-AI,
  DECIDE-AI, CLAIM, PRISMA-S ; commande `guideline` (list/recommend/checklist), playbook 25.
- **Déclaration IA** : `config/ai-disclosure.json` (9 catégories de délégation inspirées de
  GAIDeT), `sf/disclosure.py`, `disclosure --check` (5 champs structurels), playbook 26.
- **Six dépôts v2** : agentskills (spec), anthropics/skills, citegate, ASReview, Manubot,
  PaperQA2 — 1 440 fichiers / 325 337 lignes scannés, 6 archives **curées** (4,6 Mio),
  +26 entrées de registre (5 460 au total), playbook 28, `docs/SCAN_REPORT_V2.md`.
- **Recherche consignée** : `docs/RESEARCH_NOTES.md` — sources primaires datées, décisions
  d'implémentation, une affirmation non confirmée explicitement écartée.
- **Qualité** : 28 playbooks, 21 commandes, 7 fichiers de config JSON, 100 tests unitaires,
  18 cas d'évaluation, CI à 11 étapes (dont validation de spec et smoke test des nouveaux
  modules), démonstration FAIL→PASS avec les 8 portes.
- **Publication** : dépôt GitHub privé mis à jour, dossier Drive synchronisé.

### Durcissement avant livraison finale

- Historique Markdown réellement conservé ; requêtes/URL non tronquées, historique
  corrompu jamais effacé, filtres natifs et champs inconnus consignés.
- Cache d'intégrité lié à la bibliographie par SHA-256, durée <24 h ; relations Crossref
  entrantes/sortantes distinguées et références sans DOI non assimilées à un contrôle réussi.
- Sorties `--json` dépourvues de messages parasites ; un auteur par champ RIS `AU`.
- Déclarations vierges refusées, contrôle de contenu intégré à `G-disclosures` ; déclaration
  de non-usage acceptée. Licence de chaque skill v2 distinguée de la licence de la bibliothèque.
- URL primaire CLAIM 2024 corrigée ; notes de recherche restreintes aux constats sourcés.
- **100 tests** dont 30 tests de non-régression supplémentaires ; démo négative FAIL (3/8),
  démo corrigée PASS (7/8). Packaging et empreintes reproduisibles par un outil dédié.

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
