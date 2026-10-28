# Notes de recherche — 28 octobre 2026

Ce document consigne la recherche documentaire qui a motivé la version 1.1.0.
Il est **daté** : chaque affirmation renvoie à sa source primaire, et la règle de
péremption du projet s'applique (relire les pages officielles avant soumission).
Aucune de ces sources n'a été copiée dans le code ; elles ont servi à orienter des
choix d'implémentation.

---

## 1. Spécification Agent Skills — conformité

**Consulté le 2026-10-28.**

| Point | Constat | Ce que cela a changé |
|---|---|---|
| `description` ≤ 1024 caractères | Notre v1.0.0 faisait 1 041 caractères : **non conforme** | Description réécrite à 889 caractères |
| `metadata` = map chaîne → chaîne | Nos compteurs étaient des entiers YAML non quotés | Valeurs quotées (`"16694"`, `"5460"`, …) |
| `name` = nom du dossier, kebab-case, ≤ 64 | `scholar-forge` conforme | Contrôle automatique ajouté |
| Corps < 500 lignes, ~< 5 000 tokens | 271 lignes, ~4 258 tokens | Marge conservée ; tout nouveau détail va dans `references/` |
| Références à un seul niveau | Les références imbriquées peuvent être lues partiellement (`head -100`) | Les playbooks se citent par numéro, jamais par chemin |
| `compatibility` ≤ 500 caractères | 112 caractères | Conforme |
| `allowed-tools` expérimental | Prise en charge variable selon l'hôte | Documenté, jamais requis pour fonctionner |

Sources :
- Specification — Agent Skills, `https://agentskills.io/specification`
- Skill authoring best practices — Claude Platform Docs,
  `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
- « Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the
  Path Forward », arXiv:2602.12430, `https://arxiv.org/html/2602.12430v3`
- « What Keeps Agent Skills from Being Reusable? Evidence from 138K SKILL.md Files »,
  arXiv:2608.08453, `https://arxiv.org/html/2608.08453v1`
- Repo officiel `https://github.com/agentskills/agentskills` (Apache-2.0) et
  `https://github.com/anthropics/skills` (pas de LICENSE explicite).

**Résultat livré :** `sf/spec.py`, `tools/validate_skill.py`, commande `validate`,
playbook `references/23-agent-skills-spec.md`, étape CI dédiée.

---

## 2. Rétractations : plusieurs registres, aucun verdict unique

**Consulté le 2026-10-28.** Vérification empirique faite sur un DOI réel
(`10.1016/S0140-6736(97)11096-0`, article Wakefield 1998 rétracté en 2010) :

- OpenAlex renvoie `is_retracted: true` et un titre préfixé `RETRACTED:`.
- Crossref renvoie `updated-by[]` avec deux notices : une `correction` (2004) et
  une `retraction` (2010), `source: retraction-watch`, dates et DOI d'avis.
- Le titre de l'éditeur fournit un troisième signal indépendant, utilisable hors ligne.

Littérature sur les limites :
- Hauschke & Nazarovets (2025), « (Non-)retracted academic papers in OpenAlex » —
  `is_retracted` est un booléen unique qui a étiqueté à tort des corrections et
  expressions d'inquiétude comme rétractations (fenêtre déc. 2023–mars 2024,
  ~2 300 œuvres). `https://journals.sagepub.com/doi/10.1177/01655515251322478`
  (préprint `https://arxiv.org/abs/2403.13339`).
- Fletcher & Stevenson (2025) — environ 7,5 % des articles signalés par Retraction
  Watch ne sont pas marqués comme rétractés dans OpenAlex.
  `https://link.springer.com/article/10.1186/s41073-025-00168-w`
- OpenAlex work object — `is_retracted` dérivé de la base Retraction Watch.
  `https://docs.openalex.org/api-entities/works/work-object`
- Ontologie des registres (2026) — accord d'environ 72 % entre Crossref et
  Retraction Watch sur les DOI rétractés ; faible intersection entre quatre
  registres. `https://gov.tesseract.academy/research/scholarly-record-ontology`
- Persistance des citations : arXiv:2509.18403 — 1 181 paires page Wikipédia ↔
  article rétracté, 71,6 % de citations problématiques.
  `https://arxiv.org/abs/2509.18403`
- `chrisyangsong/citegate` (MIT) — exemple d'outil de CI avec verdict `retracted`.
  `https://github.com/chrisyangsong/citegate`

**Décision d'implémentation :** ne jamais dire « cet article est rétracté ».
`sf/integrity.py` collecte trois familles de signaux, exige **≥ 2 signaux
concordants** pour un verdict bloquant, étiquette un signal isolé `suspected`, et
imprime quatre limites explicites dans chaque rapport. Porte `G-integrity`
ajoutée à `audit` (8 portes au total). Playbook `references/24`.

---

## 3. Directives de rapport 2024–2026

**Consulté le 2026-10-28.**

| Directive | Année | Point retenu |
|---|---|---|
| TRIPOD+AI | 2024 (BMJ) | 27 items + checklist abstract ; **remplace TRIPOD 2015**, qui ne doit plus être utilisé |
| STARD-AI | 15 sept. 2025 (Nature Medicine) | Correction d'auteur publiée le 13 juillet 2026 ; points critiques : standard de référence, partitionnement, seuil, sorties indéterminées/en échec |
| TRIPOD-LLM | 2025 (Nature Medicine, PMID 39779929) | Études utilisant des LLM pour des tâches cliniques |
| CONSORT-AI / SPIRIT-AI | 2020 | 14 items additionnels ; modèle réellement évalué vs version du protocole, interaction humain–IA, analyse des cas d'erreur |
| DECIDE-AI | 2022 | Évaluation clinique précoce en conditions réelles, facteurs humains, sécurité |
| CLAIM | mise à jour 2024 | IA en imagerie médicale |
| CONSORT 2025 / SPIRIT 2025 | avril 2025 | Science ouverte intégrée, **mais pas d'items IA** : ils complètent CONSORT-AI/SPIRIT-AI |
| PRISMA-S | 2021 | Chaînes complètes, interface, date, limites, déduplication |

Sources :
- EQUATOR Network — `https://www.equator-network.org/reporting-guidelines/`
- TRIPOD+AI — `https://pmc.ncbi.nlm.nih.gov/articles/PMC11019967/` et
  `https://www.equator-network.org/reporting-guidelines/tripod-statement/`
- STARD-AI — `https://www.nature.com/articles/s41591-025-03953-8`
- CONSORT-AI — `https://www.nature.com/articles/s41591-020-1034-x` et
  `https://www.equator-network.org/reporting-guidelines/consort-artificial-intelligence/`
- TRIPOD-LLM — `https://pubmed.ncbi.nlm.nih.gov/39779929/`
- Vue de sélection — `https://casrai.org/guides/ai-reporting-guidelines-consort-ai-tripod-ai-decide-ai`
- Autres — `https://ramkumarmd.com/medical-ai/evaluation-safety/reporting-guidelines`,
  `https://www.editage.com/blog/ai-reporting-guidelines-for-research-what-authors-need-to-disclose-and-report/`

**Décision :** `config/reporting-guidelines.json` passe de 12 à 18 directives avec
année, URL officielle, `supersedes`, `ai_specific` et checklist abrégée. Le
générateur indique explicitement que ces listes ne sont **pas** la reproduction
officielle des items. Routeur `guideline --recommend`. Playbook `references/25`.

---

## 4. Déclaration d'usage de l'IA

**Consulté le 2026-10-28.**

Positions convergentes de COPE (position statement 2023, toujours en vigueur),
ICMJE (recommandations mises à jour janvier 2026), Nature, Wiley, Wolters Kluwer,
WAME et du réseau JAMA :
- pas d'auteur IA (absence de responsabilité, de personnalité juridique, de
  gestion des conflits d'intérêts et du copyright) ;
- divulgation de l'outil **et de sa version**, de la finalité précise, et de la
  supervision humaine, en Methods/Remerciements et souvent dans la cover letter ;
- responsabilité humaine entière sur le contenu ;
- interdiction pour les éditeurs/relecteurs de téléverser des manuscrits
  confidentiels dans des services qui s'entraînent sur les entrées.

Apport 2025 : **GAIDeT** (Generative AI Delegation Taxonomy,
DOI `10.1080/08989621.2025.2544331`) structure la déclaration par tâche déléguée
plutôt que par simple mention « AI was used ». Le forum COPE 2025 (couvert par le
Scholarly Kitchen) décrit le passage de la détection de texte IA au contrôle du
respect des règles de déclaration, avec supervision humaine sur données,
citations, méthode et analyse critique.

Sources :
- `https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools`
- `https://www.icmje.org/icmje-recommendations.pdf`
- `https://www.nature.com/nature-portfolio/editorial-policies/ai-policy`
- `https://doi.org/10.1080/08989621.2025.2544331`
- `https://scholarlykitchen.sspnet.org/2025/08/25/from-detection-to-disclosure-key-takeaways-on-ai-ethics-from-copes-forum/`
- `https://casrai.org/guides/can-ai-be-listed-as-an-author`
- `https://www.wolterskluwer.com/en/solutions/lippincott-journals/lippincott-journals-ethical-best-practices-in-scholarly-publishing`

**Décision :** `config/ai-disclosure.json` (9 catégories de délégation),
`sf/disclosure.py` (génération + `--check` déterministe), commande `disclosure`,
playbook `references/26`, template existant conservé et enrichi par la commande.

⚠️ Une source secondaire affirme que COPE aurait ajouté en août 2025 « l'implication
non divulguée de l'IA » aux motifs de rétractation. Cette affirmation n'a **pas**
pu être confirmée sur une page COPE primaire pendant cette session ; elle est
donc **volontairement absente** du code et des playbooks. La consigne donnée est
« vérifier la politique courante de la revue », pas une affirmation datée.

---

## 5. Reproductibilité de la recherche documentaire (PRISMA-S)

PRISMA-S exige chaîne complète, interface, date, limites et comptages. Le dépôt
v1.0.0 promettait « every query logged » (`config/gates.json`, G2) mais le CLI
n'écrivait aucun journal. C'était une dette de conformité interne.

**Décision :** `sf/searchlog.py` journalise une ligne par base et par requête dans
`sources/search-log.md` + `sources/search-log.json` ; ajout de filtres
`--from-year/--to-year/--min-citations/--oa-only/--type` appliqués côté serveur
quand l'API le permet et réappliqués localement ; exports CSV et RIS. Les filtres
ignorés par une source sont consignés, pas tus. Playbook `references/27`.

Sources : `https://www.equator-network.org/reporting-guidelines/prisma-s/`,
`https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/filter-entity-lists`,
`https://api.crossref.org/`.

---

## 6. Six dépôts complémentaires

Recherche via l'API GitHub le 2026-10-28 (mots-clés + vérification individuelle
des licences et de la taille). Clones `--depth 1`, lecture seule.

| Dépôt | Licence | Étoiles | Apport |
|---|---|---:|---|
| `agentskills/agentskills` | Apache-2.0 | 26 703 | spec + `skills-ref` |
| `anthropics/skills` | aucune (notices tiers) | 184 227 | 20 `SKILL.md` officiels |
| `chrisyangsong/citegate` | MIT | 102 | CI d'intégrité des citations |
| `asreview/asreview` | Apache-2.0 | 1 053 | apprentissage actif pour le criblage |
| `manubot/manubot` | BSD-2-Clause-Patent | 477 | manuscrits ouverts, citations par identifiant |
| `Future-House/paper-qa` | Apache-2.0 | 9 477 | QA ancrée sur preuves |

**Décision :** archives **curées** (tests/caches/binaires >2 Mio exclus, exclusions
comptabilisées) pour ne pas alourdir le dépôt — 4,6 Mio au lieu de ~64 Mio.
Les 8 archives v1 restent intégrales. Playbook `references/28`,
`docs/SCAN_REPORT_V2.md`, `upstream/v2/manifest.json`, +26 entrées de registre.

⚠️ `anthropics/skills` n'a pas de fichier LICENSE : aucun code n'en est copié,
seuls des motifs de structuration sont repris, et l'attribution est conservée.
La compilation reste **non commerciale** (CC BY-NC 4.0 d'une source v1).

---

## 7. Ce que cette recherche n'a PAS fait

- Elle n'a pas relu les conditions d'utilisation de chaque API au-delà de la
  documentation publique citée.
- Elle n'a pas vérifié les policies de chaque éditeur individuellement — la
  consigne « vérifier le jour de la soumission » reste une obligation humaine.
- Elle n'a pas exécuté le code des six dépôts.
- Elle n'a pas transformé des résultats de recherche web en vérités figées :
  ce document est un journal daté, pas une base de connaissances permanente.
