# Notice d'attribution — ScholarForge

ScholarForge is a derivative compilation. The following upstream works were cloned, scanned,
and (where compatible) merged. Full copies of the eight v1 sources are preserved in
`upstream/*.zip` (hashes and commit SHAs in `upstream/manifest.json`); curated snapshots of the
six v2 sources are in `upstream/v2/*.zip` (`upstream/v2/manifest.json`).

| # | Upstream | Licence | Rôle dans la fusion |
|---|---|---|---|
| 1 | [O0000-code/awesome-academic-skills](https://github.com/O0000-code/awesome-academic-skills) | CC0-1.0 | 223 fiches curatées, 749 backlog, schéma JSON, framework de confiance ASDF (13 règles de scan statique), taxonomie du cycle de recherche |
| 2 | [cosen1024/awesome-academic-skills](https://github.com/cosen1024/awesome-academic-skills) | MIT | 43 entrées bilingues vérifiées, commits épinglés, méthodologie de vérification |
| 3 | [kael-odin/awesome-academic-research-skills](https://github.com/kael-odin/awesome-academic-research-skills) | MIT | 114 dépôts classés, historique 60 jours, signaux de tendance |
| 4 | [miketepUR/awesome-claude-skills](https://github.com/miketepUR/awesome-claude-skills) | MIT | 51 liens d'écosystème, modèles de contribution et de validation de liens |
| 5 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | **CC BY-NC 4.0** | 5 skills profondes (pipeline 10 étapes, deep-research 13 agents, academic-paper, reviewer, sr-screener), 478 scripts, contrats JSON, protocoles d'intégrité |
| 6 | [KalarisLabs/research-agent-skills](https://github.com/KalarisLabs/research-agent-skills) | MIT | 281 skills étroites, CLI stdlib testés, benchmarks, catalog/graph, guides APA7/venue/repro/peer-review |
| 7 | [saintgo7/agents-skills](https://github.com/saintgo7/agents-skills) | aucun fichier de licence | 50 stubs de skills, guide IEEE Access, catégorisation coréenne |
| 8 | [ranbot-ai/awesome-skills](https://github.com/ranbot-ai/awesome-skills) | aucun fichier de licence | 2 908 skills dont `content-research-writer` (recherche → plan → rédaction itérative), 1 129 fiches d'agrégateur |

## Ce qui a été réécrit vs conservé

- **Réécrit from scratch** : `SKILL.md`, les 28 `references/`, le CLI `scripts/`, les
  `templates/`, les `config/`, les `tests/`, les `tools/`. Les idées sont attribuées ci-dessus
  et dans `docs/SOURCE_MAP.md`, mais le texte et le code sont originaux.
- **Conservé tel quel** : l'intégralité des huit dépôts dans `upstream/*.zip` (données
  inertes, jamais exécutées), ainsi que les données ouvertes de catalogue (CC0/MIT) fusionnées
  dans `data/registry.json`.

## Restriction

`Imbad0202/academic-research-skills` est sous CC BY-NC 4.0 : la compilation ne peut donc pas
être utilisée à des fins commerciales sans autorisation distincte. Les deux dépôts sans
licence sont conservés uniquement à des fins d'attribution et de traçabilité privée ; leur
contenu n'est pas réconcédé.

## Marques

Les noms de produits, d'éditeurs et de conférences cités (APA, IEEE, PRISMA, CONSORT,
NeurIPS, Nature…) appartiennent à leurs propriétaires respectifs. ScholarForge n'est affilié
à aucun d'entre eux et ne fournit pas de règles officielles — voir la « currency rule » dans
`references/15-venue-submission.md`.


---

## Sources v2 — ajoutées le 2026-10-28

| # | Upstream | Licence | Rôle dans la version 1.1.0 |
|---|---|---|---|
| 9 | [agentskills/agentskills](https://github.com/agentskills/agentskills) | Apache-2.0 | Spécification ouverte Agent Skills et bibliothèque de validation `skills-ref` → `sf/spec.py`, `tools/validate_skill.py`, mise en conformité du frontmatter |
| 10 | [anthropics/skills](https://github.com/anthropics/skills) | **aucune** (THIRD_PARTY_NOTICES.md conservé) | 20 `SKILL.md` officiels étudiés comme motifs de divulgation progressive ; **aucun code copié**, 20 entrées ajoutées au registre |
| 11 | [chrisyangsong/citegate](https://github.com/chrisyangsong/citegate) | MIT | CI de vérification de citations et verdict de rétractation → conception multi-signaux de `sf/integrity.py` |
| 12 | [asreview/asreview](https://github.com/asreview/asreview) | Apache-2.0 | Apprentissage actif pour le criblage de revues systématiques → documentation du double criblage (playbooks 05, 28) |
| 13 | [manubot/manubot](https://github.com/manubot/manubot) | BSD-2-Clause-Patent | Manuscrits ouverts et citation par identifiant → traçabilité des références (playbooks 07, 28) |
| 14 | [Future-House/paper-qa](https://github.com/Future-House/paper-qa) | Apache-2.0 | Question-réponse ancrée sur des documents scientifiques avec citations → exigence d'ancrage des preuves (playbooks 06, 28) |

Les archives v2 sont **curées** : suites de tests, caches, binaires et fichiers >2 Mio
exclus, avec comptabilité des exclusions dans `upstream/v2/manifest.json`. Aucun code de
ces dépôts n'est exécuté par ScholarForge. Les sources primaires de la recherche
documentaire correspondante sont listées dans `docs/RESEARCH_NOTES.md`.
