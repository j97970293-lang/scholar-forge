# ScholarForge — rapport de scan exhaustif des sources

Généré le `2026-10-27T20:27:17+00:00` par `tools/scan_sources.py`. Tous les fichiers des clones sont parcourus, hachés (SHA-256) et indexés ; le code Python est analysé via AST, les `SKILL.md` via leur frontmatter, et les URL/hôtes réseau sont extraits de chaque fichier texte.

## 1. Chiffres globaux

| Métrique | Valeur |
|---|---:|
| Dépôts scannés | 8 |
| Fichiers indexés | 15,254 |
| Volume total | 136.7 MB |
| Lignes de texte lues | 2,387,424 |
| Fichiers `SKILL.md` | 3244 |
| Scripts Python avec CLI | 748 |
| Extensions distinctes | 40 |
| Hôtes HTTP distincts | 1713 |
| Dépôts GitHub référencés | 1712 |

## 2. Par dépôt

| Dépôt | Rôle | Licence | Fichiers | Taille | Lignes | .py | .sh | .md | SKILL.md |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| [`O0000-code_awesome-academic-skills`](https://github.com/O0000-code/awesome-academic-skills) | meta-list: 223 curated skill records + ASDF trust framework + schema | CC0-1.0 | 268 | 1.5 MB | 21,755 | 9 | 0 | 11 | 0 |
| [`cosen1024_awesome-academic-skills`](https://github.com/cosen1024/awesome-academic-skills) | meta-list: verified bilingual catalog with pinned source_ref commits | MIT | 14 | 138.9 KB | 1,986 | 3 | 0 | 7 | 0 |
| [`kael-odin_awesome-academic-research-skills`](https://github.com/kael-odin/awesome-academic-research-skills) | meta-list: live star/trend rankings + 60-day history | MIT | 92 | 8.4 MB | 306,405 | 4 | 0 | 5 | 0 |
| [`miketepUR_awesome-claude-skills`](https://github.com/miketepUR/awesome-claude-skills) | meta-list: general agent-skill ecosystem + contribution/validation workflows | MIT | 4 | 35.7 KB | 894 | 0 | 0 | 2 | 0 |
| [`Imbad0202_academic-research-skills`](https://github.com/Imbad0202/academic-research-skills) | suite: 5 deep skills (pipeline, research, paper, reviewer, screening) + 478 scripts + JSON contracts | CC-BY-NC-4.0 | 2,840 | 38.3 MB | 579,331 | 478 | 9 | 1146 | 5 |
| [`KalarisLabs_research-agent-skills`](https://github.com/KalarisLabs/research-agent-skills) | suite: 200+ narrow skills, tested stdlib CLIs, benchmarks, catalog graph | MIT | 3,169 | 35.6 MB | 918,802 | 549 | 4 | 2023 | 281 |
| [`saintgo7_agents-skills`](https://github.com/saintgo7/agents-skills) | suite: 50 lightweight Korean/English skill stubs + IEEE Access venue guide | unlicensed (snapshot retained, attribution kept) | 82 | 550.9 KB | 4,871 | 3 | 1 | 53 | 50 |
| [`ranbot-ai_awesome-skills`](https://github.com/ranbot-ai/awesome-skills) | general skill aggregator: 2908 skill records incl. content-research-writer | unlicensed (snapshot retained, attribution kept) | 8,785 | 52.2 MB | 553,380 | 0 | 4 | 2910 | 2908 |

## 3. Extensions rencontrées (top 20)

| Extension | Fichiers | Volume |
|---|---:|---:|
| `.json` | 6,873 | 54.6 MB |
| `.md` | 6,157 | 52.0 MB |
| `.py` | 1,046 | 17.2 MB |
| `.log` | 302 | 44.4 KB |
| `.yml` | 227 | 667.9 KB |
| `.yaml` | 216 | 342.9 KB |
| `.txt` | 78 | 613.4 KB |
| `.csv` | 44 | 505.6 KB |
| `.tex` | 34 | 408.9 KB |
| `(none)` | 32 | 48.2 KB |
| `.svg` | 28 | 812.3 KB |
| `.ts` | 21 | 108.0 KB |
| `.sh` | 18 | 151.7 KB |
| `.bib` | 18 | 46.6 KB |
| `.html` | 17 | 901.6 KB |
| `.pdf` | 17 | 2.3 MB |
| `.sty` | 16 | 256.6 KB |
| `.jsonl` | 15 | 343.8 KB |
| `.tsx` | 14 | 96.3 KB |
| `.png` | 11 | 3.0 MB |

## 4. API et hôtes réseau détectés dans le code

| Hôte | Fichiers le mentionnant |
|---|---:|
| `api.example.com` | 55 |
| `www.ncbi.nlm.nih.gov` | 28 |
| `api.crossref.org` | 23 |
| `eutils.ncbi.nlm.nih.gov` | 20 |
| `www.ebi.ac.uk` | 20 |
| `api.openai.com` | 15 |
| `api.libreoffice.org` | 15 |
| `export.arxiv.org` | 14 |
| `api.openalex.org` | 13 |
| `api.github.com` | 12 |
| `api.fiscaldata.treasury.gov` | 10 |
| `api.semanticscholar.org` | 9 |
| `api.anthropic.com` | 8 |
| `api.labarchives.com` | 6 |
| `api.cloudflare.com` | 6 |
| `api.expo.dev` | 6 |
| `api.stripe.com` | 6 |
| `api.bedbase.org` | 4 |
| `api.datacite.org` | 4 |
| `api.imaging.datacommons.cancer.gov` | 4 |
| `api.deepseek.com` | 3 |
| `api.genomicintelligence.ai` | 3 |
| `api.materialsproject.org` | 3 |
| `api.biorxiv.org` | 3 |
| `api.hasdata.com` | 3 |
| `api.agentphone.ai` | 3 |
| `api.telegram.org` | 3 |
| `api.mercury.build` | 3 |
| `api.equibles.com` | 3 |
| `api.covalenthq.com` | 3 |
| `api.getchord.xyz` | 3 |
| `api.agenthustle.ai` | 3 |
| `api.loganalytics.azure.cn` | 3 |
| `api.cognitive.microsofttranslator.com` | 3 |
| `api.calendly.com` | 3 |

## 5. Extrait des compétences découvertes

Les `SKILL.md` complets sont conservés dans `upstream/*.zip` ; la liste indexée est dans `data/source-skills.json`.

| Dépôt | Nom | Catégorie | Déclencheur (extrait) |
|---|---|---|---|
| Imbad0202 | `academic-pipeline` |  | Orchestrator for the full academic research pipeline: research -> write -> integrity check |
| Imbad0202 | `deep-research` |  | Universal deep research agent team. 13-agent pipeline for rigorous academic research on an |
| Imbad0202 | `sr-screener` |  | Protocol-driven study screening for systematic, scoping and rapid reviews. Turns a proposa |
| Imbad0202 | `academic-paper` |  | 12-agent academic paper writing pipeline. 11 modes (full/plan/outline/revision/revision-co |
| Imbad0202 | `academic-paper-reviewer` |  | Multi-perspective academic paper review with dynamic reviewer personas. Runs a 5-seat, rol |
| KalarisLabs | `clinical-reports` |  | Generates fail-closed draft JSON templates and runs local deterministic structure and cons |
| KalarisLabs | `presenting-conference-talks` |  | Generates conference presentation slides (Beamer LaTeX PDF and editable PPTX) from a compi |
| KalarisLabs | `tensorrt-llm` |  | Optimizes LLM inference with NVIDIA TensorRT for maximum throughput and lowest latency. Us |
| KalarisLabs | `networkx` |  | Create, analyze, and visualize complex networks and graphs in Python with NetworkX. Use wh |
| KalarisLabs | `polars-bio` |  | Python library polars-bio for genomic interval operations and bioinformatics file I/O on P |
| KalarisLabs | `pyzotero` |  | Reads and writes Zotero libraries from Python with pyzotero 1.13.0 and the Zotero Web API  |
| KalarisLabs | `llamaguard` |  | Classifies LLM prompts and responses as safe or unsafe using Meta''s LlamaGuard (7B v1, 8B |
| KalarisLabs | `research-agent-skills` |  | Navigate the Research Agent Skills collection by Kalaris Labs for academia across AI, mach |
| KalarisLabs | `statsmodels` |  | Statistical models library for Python. Use when you need specific model classes (OLS, GLM, |
| KalarisLabs | `nemo-guardrails` |  | Adds runtime safety rails to LLM applications with NVIDIA NeMo Guardrails, configured thro |
| KalarisLabs | `13c-metabolic-flux` |  | Estimates intracellular metabolic fluxes from steady-state carbon-13 isotope-tracing measu |
| KalarisLabs | `arxiv-submission` |  | Prepare and post preprints to arXiv without processing failures or leaks, covering TeX sou |
| KalarisLabs | `reference-manager-interop` |  | Move and sync reference libraries between Zotero, Mendeley, EndNote, JabRef, Paperpile and |
| KalarisLabs | `medchem` |  | Filters and triages small-molecule libraries with the Python medchem library (datamol-io,  |
| KalarisLabs | `guidance` |  | Constrains LLM output during generation with Guidance (Microsoft Research), using regex, s |
| KalarisLabs | `skypilot-multi-cloud-orchestration` |  | Multi-cloud orchestration for ML workloads with automatic cost optimization. Use when you  |
| KalarisLabs | `simpo-training` |  | Simple Preference Optimization for LLM alignment. Reference-free alternative to DPO with b |
| KalarisLabs | `matplotlib` |  | Low-level plotting library for full customization. Use when you need fine-grained control  |
| KalarisLabs | `benchling-integration` |  | Benchling Python SDK and REST API integration for registry entities, inventory, ELN entrie |
| KalarisLabs | `llama-factory` |  | Guides fine-tuning of large language models with LLaMA-Factory, covering the WebUI no-code |
| KalarisLabs | `nnsight-remote-interpretability` |  | Provides guidance for interpreting and manipulating neural network internals using nnsight |
| KalarisLabs | `scientific-schematics` |  | Generates publication-style scientific diagrams as raster PNG images from a natural-langua |
| KalarisLabs | `modal-serverless-gpu` |  | Serverless GPU cloud platform for running ML workloads. Use when you need on-demand GPU ac |
| KalarisLabs | `scientific-visualization` |  | Create and audit truthful, accessible, publication-ready scientific figures with Matplotli |
| KalarisLabs | `faiss` |  | Facebook's library for efficient similarity search and clustering of dense vectors. Suppor |
| KalarisLabs | `autoskill` |  | Observe the user's screen via screenpipe, detect repeated research workflows, match them a |
| KalarisLabs | `pytorch-fsdp2` |  | Adds PyTorch FSDP2 (fully_shard) to training scripts with correct init, sharding, mixed pr |
| KalarisLabs | `markdown-mermaid-writing` |  | Writes scientific documents and documentation as markdown with embedded Mermaid diagrams a |
| KalarisLabs | `nemo-curator` |  | GPU-accelerated data curation for LLM training. Supports text/image/video/audio. Features  |
| KalarisLabs | `rdkit` |  | Guides use of RDKit (Python) for reading and writing SMILES, MOL/SDF, and InChI, computing |
| KalarisLabs | `cover-letter-to-editor` |  | Write journal submission cover letters, presubmission inquiries, transfer requests, and re |
| KalarisLabs | `scientific-brainstorming` |  | Facilitates evidence-aware scientific ideation with independent generation, structured dis |
| KalarisLabs | `prompt-guard` |  | Classifies text with Meta's Prompt Guard, an 86M-parameter model loaded from HuggingFace,  |
| KalarisLabs | `genomic-intelligence` |  | Predict regulatory features, gene structure, and expression directly from DNA sequence usi |
| KalarisLabs | `liteparse` |  | Local document and PDF parsing that returns spatial text with bounding boxes. Use for extr |
| KalarisLabs | `onekgpd` |  | Query the 1000 Genomes Project dataset (3,202 whole-genome-sequenced individuals, GRCh38)  |
| KalarisLabs | `exa-search` |  | Web toolkit powered by Exa, tuned for scientific and technical content. Use this skill whe |
| KalarisLabs | `dnanexus-integration` |  | Build and operate reproducible genomics workloads on DNAnexus with the dx CLI, dxpy, apps/ |
| KalarisLabs | `parallel-web` |  | Runs the parallel-cli tool for web workflows: web search, URL and PDF extraction, deep res |
| KalarisLabs | `academic-plotting` |  | Generates publication-quality figures for ML papers from research context. Given a paper s |
| KalarisLabs | `nextflow` |  | Build, run, and debug Nextflow data pipelines and nf-core workflows end to end. Use whenev |
| KalarisLabs | `protocolsio-integration` |  | Reads, validates, and exports protocols.io data using the documented REST v3/v4 endpoints  |
| KalarisLabs | `cobrapy` |  | Runs constraint-based metabolic modeling with COBRApy (Python, import cobra) on genome-sca |
| KalarisLabs | `pyhealth` |  | Builds clinical deep-learning pipelines with PyHealth using its Dataset → Task → Model → T |
| KalarisLabs | `shap` |  | Explain and audit machine-learning predictions with SHAP. Use for selecting SHAP explainer |
| KalarisLabs | `nature-portfolio` |  | Prepare manuscripts for Nature and Nature Portfolio journals (Nature, Nature Communication |
| KalarisLabs | `constitutional-ai` |  | Anthropic's method for training harmless AI through self-improvement. Two-phase approach - |
| KalarisLabs | `flowio` |  | Read, inspect, and write Flow Cytometry Standard (FCS) 2.0, 3.0, and 3.1 files with FlowIO |
| KalarisLabs | `torchforge-rl-training` |  | Provides guidance for PyTorch-native agentic RL using torchforge, Meta's library separatin |
| KalarisLabs | `peer-review` |  | Prepare evidence-bounded, constructive peer-review drafts and structured manuscript assess |
| KalarisLabs | `umap-learn` |  | Reduces and embeds high-dimensional data with umap-learn (UMAP) in Python, including 2D/3D |
| KalarisLabs | `hqq-quantization` |  | Half-Quadratic Quantization for LLMs without calibration data. Use when quantizing models  |
| KalarisLabs | `scientific-writing` |  | Draft, revise, and audit scientific manuscripts or reports with explicit evidence provenan |
| KalarisLabs | `ncats-arax` |  | Queries the NCATS Translator ARAX production API for bounded, typed, provenance-rich one-h |
| KalarisLabs | `tensorboard` |  | Logs and views ML training data in TensorBoard using PyTorch SummaryWriter and TensorFlow/ |

… et 3184 autres entrées dans `data/source-skills.json`.


## 6. Scripts Python exécutables relevés

748 scripts Python exposent un point d'entrée CLI. Inventaire complet : `data/source-python-clis.json`. Exemples :

- `O0000-code/check_public.py` — Hard gate: every listed repo must be PUBLICLY reachable.
- `O0000-code/check_unmaintained.py` — Flag entries whose repos look unmaintained (RF §4 check #7, selfhosted's
- `O0000-code/generate_readme.py` — Generate README.md and README.zh-CN.md from data/skills/*.yml + config.yaml.
- `O0000-code/update_metadata.py` — Fill the CI-maintained fields of each data/skills/*.yml from the GitHub API.
- `O0000-code/schema_check.py` — Validate every data/skills/*.yml against schema/skill.schema.json, then apply
- `O0000-code/security_scan.py` — ASDF Stage-1 deterministic static security scanner.
- `cosen1024/render_readmes.py` — Render the catalog tables in README.md and README_EN.md from YAML.
- `cosen1024/validate_data.py` — Validate the structure and curation invariants of data/skills.yaml.
- `cosen1024/check_links.py` — Check repository, pinned source, and install-entry links in the catalog.
- `kael-odin/update_rankings.py` — Update the academic research skills ranking.
- `kael-odin/test_ranking.py` — 
- `Imbad0202/check_role_scoped_contract.py` — Pin Schema 13.2 role-scoped reviewer delivery surfaces.
- `Imbad0202/test_check_persuasion_invariance_fixtures.py` — Mutation tests for check_persuasion_invariance_fixtures.py (#576 Spec B §14 v0.1).
- `Imbad0202/check_v3_9_0_triangulation.py` — Cross-version contamination-suffix lint: finalizer suffix table contract +
- `Imbad0202/test_check_392_citation_verification_intake.py` — Unit tests for check_392_citation_verification_intake.py (#392 lint).
- `Imbad0202/check_review_form_note_sync.py` — Review-form note sync lint (#921).
- `Imbad0202/check_agents_mirror_sync.py` — Lint: plugin-root agents/ mirrors stay byte-identical REAL files (#413).
- `Imbad0202/check_command_skill_dispatch.py` — Check plugin command entry points and rooted skill references (#857).
- `Imbad0202/verify_submission_package.py` — verify_submission_package CLI — deterministic submission-package verifier
- `Imbad0202/dispatch_calibration_panel.py` — Isolated dispatch of ONE reviewer-calibration panel (#653).
- `Imbad0202/check_task_type.py` — Lint: every top-level SKILL.md must declare metadata.task_type.
- `Imbad0202/revision_roadmap.py` — Validate and replay the #670 revision-authority contract.
- `Imbad0202/test_check_task_type.py` — Unit tests for check_task_type.py lint script.
- `Imbad0202/check_cross_document_consistency_advisory_integration.py` — Check the hermetic #672 cross-document advisory integration boundary.
- `Imbad0202/test_check_stage_capability_matrix.py` — Mutation tests for scripts/check_stage_capability_matrix.py (#745).

## 7. Dépôts GitHub les plus cités par les méta-listes

| Dépôt | Occurrences |
|---|---:|
| `sickn33/antigravity-awesome-skills` | 10189 |
| `composiohq/awesome-claude-skills` | 4133 |
| `kalarislabs/research-agent-skills` | 520 |
| `imbad0202/academic-research-skills` | 450 |
| `anthropics/skills` | 133 |
| `prat011/awesome-llm-skills` | 131 |
| `openhands/openhands` | 119 |
| `obra/superpowers` | 106 |
| `k-dense-ai/scientific-agent-skills` | 101 |
| `yuan1z0825/nature-skills` | 98 |
| `orchestra-research/ai-research-skills` | 87 |
| `imbad0202/academic-research-skills-codex` | 82 |
| `sponsors/ljharb` | 81 |
| `master-cai/research-paper-writing-skills` | 73 |
| `norman-bury/research-writing-skill` | 71 |
| `huangwb8/chineseresearchlatex` | 69 |
| `199-biotechnologies/claude-deep-research-skill` | 66 |
| `weizhena/deep-research-skills` | 66 |
| `ganzhi-black/humanities-thesis-skill` | 65 |
| `lishix520/academic-paper-skills` | 65 |
| `pedrohcgs/claude-code-my-workflow` | 65 |
| `hughyau/academicforge` | 65 |
| `wanshuiyin/auto-claude-code-research-in-sleep` | 65 |
| `aipoch/medical-research-skills` | 65 |
| `light0305/light-skills` | 65 |
| `ar9av/paperorchestra` | 64 |
| `yanlin-cheng/skill-thesis-writer` | 64 |
| `hanlulong/econ-writing-skill` | 64 |
| `alfonso0512/research-writing-skill` | 64 |
| `claesbackman/ai-research-feedback` | 64 |

## 8. Reproduction

```bash
SF_SOURCES=/chemin/vers/les/clones python3 tools/scan_sources.py
```

Les archives sources complètes (sans les `.git`) sont dans `upstream/` ; leurs empreintes sont dans `upstream/manifest.json`.

