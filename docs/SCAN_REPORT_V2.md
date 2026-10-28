# Scan report — v2 sources (2026-10-28)

Curated scan of six v2 repositories (VCS internals excluded). Read-only; no upstream code was executed.

- **6** dépôts | **1,440** fichiers | **64.1 Mio** | **325,337** lignes de texte
- **342** scripts Python analysés par AST | **20** `SKILL.md` officiels lus
- **1734** hôtes HTTP distincts | **188** dépôts GitHub référencés

| Dépôt | Fichiers | Taille | Lignes | `.py` | `SKILL.md` | Commit | Rôle |
|---|---:|---:|---:|---:|---:|---|---|
| `agentskills_agentskills` | 138 | 1.6 Mio | 3,487 | 11 | 0 | `69ef37e9` | official Agent Skills open specification + skills-ref validation libra |
| `anthropics_skills` | 445 | 11.3 Mio | 57,406 | 72 | 20 | `dbd4588f` | official skill library: 20 SKILL.md examples of progressive disclosure |
| `chrisyangsong_citegate` | 19 | 65.0 Kio | 1,880 | 8 | 0 | `94cc0a02` | citation-integrity CI gate: Crossref/OpenAlex verification + retractio |
| `asreview_asreview` | 479 | 12.7 Mio | 84,564 | 122 | 0 | `79d56821` | active learning for systematic-review screening; dual-screening workfl |
| `manubot_manubot` | 175 | 2.5 Mio | 43,361 | 70 | 0 | `859dd158` | open automated manuscripts; citation-by-identifier and reproducible re |
| `Future-House_paper-qa` | 184 | 36.0 Mio | 134,639 | 59 | 0 | `c692d0df` | evidence-grounded question answering over scientific documents with ci |

## Principaux hôtes référencés

| Hôte | Occurrences |
|---|---:|
| `registry.npmjs.org` | 1750 |
| `github.com` | 775 |
| `doi.org` | 520 |
| `web.archive.org` | 451 |
| `purl.obolibrary.org` | 264 |
| `arxiv.org` | 243 |
| `www.w3.org` | 191 |
| `www.ncbi.nlm.nih.gov` | 167 |
| `manubot.org` | 134 |
| `api.openai.com` | 126 |
| `platform.claude.com` | 125 |
| `schemas.microsoft.com` | 123 |

## Ce que ces dépôts ont apporté

| Dépôt | Apport intégré dans ScholarForge |
|---|---|
| agentskills/agentskills | `tools/validate_skill.py`, `sf/spec.py`, mise en conformité frontmatter (description ≤1024, metadata chaînes), `references/23` |
| anthropics/skills | 20 `SKILL.md` officiels indexés dans le registre ; motifs de divulgation progressive |
| chrisyangsong/citegate | `sf/integrity.py`, porte `G-integrity`, `references/24` |
| asreview/asreview | double criblage / apprentissage actif documenté dans `references/05` et `references/28` |
| manubot/manubot | citations par identifiant et traçabilité dans `references/07`, `references/28` |
| Future-House/paper-qa | ancrage des réponses sur preuves dans `references/06`, `references/28` |

## Limites

- Les archives v2 sont **curées** (tests, caches et fichiers >2 Mio exclus), contrairement aux 8 archives v1 qui sont intégrales. Voir `upstream/v2/manifest.json`.
- Les comptes d'étoiles sont un instantané du 2026-10-28, non une mesure vivante.
- Aucun code amont n'a été exécuté : lecture, hachage et analyse AST uniquement.

