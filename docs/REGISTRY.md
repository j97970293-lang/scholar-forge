# ScholarForge — registre unifié

**5,460 entrées** au total en 1.1.0. Le noyau v1 (`tools/merge_registry.py`,
`2026-10-27T20:27:18+00:00`) fournit **5 434** entrées dédupliquées issues des 8 catalogues
amont ; la vague v2 (`tools/v2_pipeline.py`, 2026-10-28) ajoute **26** entrées (20 `SKILL.md`
officiels + 6 outils vérifiés), détaillées en fin de document. Les entrées v1 sont conservées
à l'identique. Champs complets dans `data/registry.json`, export plat dans `data/registry.csv`.

## Couverture

| Jeu de données | Entrées |
|---|---:|
| `SKILL.md` | 3,244 |
| `ranbot-ai` | 1,129 |
| `O0000-backlog` | 749 |
| `kalaris-catalog` | 281 |
| `O0000-listed` | 223 |
| `kael-odin` | 114 |
| `miketepUR` | 51 |
| `cosen1024` | 43 |
| `v2-sources` (2026-10-28) | 26 |

| Total dédupliqué v1 | **5,434** |
| Total 1.1.0 | **5,460** |
| Entrées à pertinence académique ≥ 0,4 | 1,054 |
| Entrées vérifiées | 291 |
| Dépôts GitHub distincts | 1,121 |

## Répartition par étape du cycle de recherche

| Étape | Entrées |
|---|---:|
| `discovery` | 1,779 |
| `meta` | 956 |
| `suite` | 582 |
| `analysis` | 488 |
| `reading` | 464 |
| `citation` | 285 |
| `writing` | 267 |
| `peer-review` | 226 |
| `figures` | 127 |
| `writing-quality` | 110 |
| `publishing` | 100 |
| `discipline` | 26 |
| `autonomous` | 18 |
| `ocr` | 6 |

## Top 40 par étoiles

| # | Nom | Dépôt | ★ | Δ7j | Étape |
|---:|---|---|---:|---:|---|
| 401 | `scientific-agent-skills` | `/github.com/K-Dense-AI/scientific-agent-skills` | 54,840 | 1,774 | suite |
| 1 | `academic-research-skills` | `/github.com/Imbad0202/academic-research-skills` | 54,091 | 1,032 | suite |
| 402 | `nature-skills` | `https://github.com/Yuan1z0825/nature-skills` | 50,870 | 1,377 | suite |
| 1029 | `claude-plugins-official` | `/github.com/anthropics/claude-plugins-official` | 28,942 | 0 | suite |
| 659 | `Auto-claude-code-research-in-sleep` | `/wanshuiyin/Auto-claude-code-research-in-sleep` | 18,134 | 376 | discovery |
| 1030 | `AI-Research-SKILLs` | `thub.com/Orchestra-Research/AI-Research-SKILLs` | 13,990 | 255 | discovery |
| 2 | `academic-research-skills-codex` | `b.com/imbad0202/academic-research-skills-codex` | 13,579 | 380 | suite |
| 1031 | `Supervisor-Skills` | `https://github.com/HKUSTDial/Supervisor-Skills` | 10,736 | 575 | meta |
| 660 | `hamuleite` | `https://github.com/hoochanlon/hamuleite` | 9,945 | 29 | meta |
| 231 | `figures4papers` | `https://github.com/ChenLiu-1996/figures4papers` | 9,040 | 296 | figures |
| 403 | `visual-explainer` | `https://github.com/nicobailon/visual-explainer` | 8,628 | 0 | analysis |
| 404 | `Research-Paper-Writing-Skills` | `b.com/Master-cai/Research-Paper-Writing-Skills` | 7,843 | 222 | discovery |
| 661 | `MathModelAgent` | `https://github.com/jihe520/MathModelAgent` | 6,255 | 33 | reading |
| 232 | `codex-claude-academic-skills` | `thub.com/zlanqing/codex-claude-academic-skills` | 5,364 | 261 | reading |
| 233 | `Auto-Empirical-Research-Skills` | `cewang-stanford/Auto-Empirical-Research-Skills` | 4,788 | 102 | discovery |
| 662 | `autoresearch` | `https://github.com/uditgoenka/autoresearch` | 4,768 | 0 | discovery |
| 405 | `anti-defensive-writing-Skill` | `.com/Adkid-Zephyr/anti-defensive-writing-Skill` | 4,157 | 650 | writing |
| 663 | `ai-for-grant-writing` | `ttps://github.com/eseckel/ai-for-grant-writing` | 4,133 | 0 | writing |
| 406 | `research-writing-skill` | `/github.com/norman-bury/research-writing-skill` | 3,537 | 57 | discovery |
| 234 | `llm-for-zotero` | `https://github.com/yilewang/llm-for-zotero` | 3,424 | 65 | discovery |
| 1032 | `arscontexta` | `tps://github.com/agenticnotetaking/arscontexta` | 3,370 | 0 | meta |
| 3 | `FAROS` | `https://github.com/OpenNSWM-Lab/FAROS` | 3,035 | 0 | discovery |
| 235 | `ChineseResearchLaTeX` | `tps://github.com/huangwb8/ChineseResearchLaTeX` | 2,979 | 22 | discovery |
| 4 | `paper-search-mcp` | `https://github.com/openags/paper-search-mcp` | 2,931 | 63 | discovery |
| 5 | `academic-humanizer` | `github.com/AIScientists-Dev/academic-humanizer` | 2,791 | 482 | discovery |
| 407 | `academic-figure-generator` | `ithub.com/LigphiDonk/academic-figure-generator` | 2,745 | 68 | discovery |
| 664 | `harness-anything` | `https://github.com/yb2460/harness-anything` | 2,623 | 289 | discovery |
| 236 | `AcademicForge` | `https://github.com/HughYau/AcademicForge` | 2,611 | 8 | suite |
| 1823 | `diagram-design` | `ttps://github.com/cathrynlavery/diagram-design` | 2,503 | 0 | reading |
| 1033 | `Deep-Research-skills` | `tps://github.com/Weizhena/Deep-Research-skills` | 2,429 | 41 | discovery |
| 6 | `paperbanana` | `https://github.com/llmsresearch/paperbanana` | 2,419 | 11 | discovery |
| 237 | `academic-ai-prompt` | `https://github.com/bohyy/academic-ai-prompt` | 2,218 | 58 | discovery |
| 665 | `drawio-skill` | `https://github.com/agents365-ai/drawio-skill` | 1,997 | 0 | reading |
| 7 | `medical-research-skills` | `ps://github.com/aipoch/medical-research-skills` | 1,991 | 17 | suite |
| 238 | `math-modeling-skill` | `://github.com/xiaomacoltai/math-modeling-skill` | 1,887 | 11 | discovery |
| 408 | `awesome-ai-agent-papers` | `//github.com/VoltAgent/awesome-ai-agent-papers` | 1,873 | 17 | discovery |
| 8 | `claude-prism` | `https://github.com/delibae/claude-prism` | 1,829 | 6 | discovery |
| 666 | `evil-read-arxiv` | `https://github.com/juliye2025/evil-read-arxiv` | 1,761 | 20 | discovery |
| 9 | `claude-code-my-workflow` | `//github.com/pedrohcgs/claude-code-my-workflow` | 1,671 | 6 | writing |
| 239 | `paperdebugger` | `https://github.com/PaperDebugger/paperdebugger` | 1,549 | 3 | writing |

## Exploitation

```bash
python3 scripts/scholarforge.py registry search --query "citation verification" --limit 10
python3 scripts/scholarforge.py registry stats
```



## v2 — 2026-10-28 : six sources supplémentaires

**26** entrées ajoutées (officielles + outils vérifiés), pour un total de **5,460** entrées. Les 5 434 entrées v1 sont conservées à l'identique.

| Dépôt | Licence | Étoiles | Rôle |
|---|---|---:|---|
| `https://github.com/agentskills/agentskills` | Apache-2.0 | 26,703 | official Agent Skills open specification + skills-ref validation library |
| `https://github.com/anthropics/skills` | mixte (licences par skill) | 184,227 | official skill library: 20 SKILL.md examples of progressive disclosure |
| `https://github.com/chrisyangsong/citegate` | MIT | 102 | citation-integrity CI gate: Crossref/OpenAlex verification + retraction verdicts |
| `https://github.com/asreview/asreview` | Apache-2.0 | 1,053 | active learning for systematic-review screening; dual-screening workflow patterns |
| `https://github.com/manubot/manubot` | BSD-2-Clause-Patent | 477 | open automated manuscripts; citation-by-identifier and reproducible reference handling |
| `https://github.com/Future-House/paper-qa` | Apache-2.0 | 9,477 | evidence-grounded question answering over scientific documents with citations |

Sources : `data/scan-v2-skills.json`, `upstream/v2/manifest.json`, `docs/SCAN_REPORT_V2.md`.
