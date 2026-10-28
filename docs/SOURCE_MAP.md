# Carte de fusion — de 14 dépôts à 1 skill

Ce document montre, composant par composant, **ce qui a été lu** dans chaque dépôt et **où cela
a atterri** dans ScholarForge. C'est la trace de l'instruction « scanne tous les codes pour les
fusionner ».

## 1. Méta-listes

| Source | Fichiers scannés | Éléments extraits | Destination |
|---|---|---|---|
| O0000-code/awesome-academic-skills | 268 (223 `data/skills/*.yml`, `data/backlog.yml` 749 entrées, `framework/` ASDF, `schema/skill.schema.json`, `config.yaml`, 9 scripts) | Taxonomie en 16 stades du cycle, 13 règles de scan statique, schéma de fiche, 972 fiches | `config/gates.json`, `config/rules.json`, `tools/security_scan.py`, `data/registry.json`, `references/19`, `references/20` |
| cosen1024/awesome-academic-skills | 14 (`data/skills.yaml` 65 Ko, 3 scripts, 7 docs) | 43 fiches vérifiées bilingues avec `source_ref` épinglé, catégories EN/ZH, commandes d'installation | `data/registry.json` (champ `verified`, `install`), `references/20` |
| kael-odin/awesome-academic-research-skills | 92 (60 JSON d'historique, `rankings.json`, `scripts/update_rankings.py` 62 Ko, site HTML/CSS/JS) | 114 dépôts classés, Δétoiles 1/7/30 j, tendances, catégories | `data/rankings-snapshot.json`, `data/registry.json` (stars/trend), `docs/REGISTRY.md` |
| miketepUR/awesome-claude-skills | 4 (README 26 Ko, 5 workflows/templates d'issue, CONTRIBUTING) | 51 liens d'écosystème, règles de contribution, validation de liens | `data/registry.json`, `.github/workflows/ci.yml`, `CONTRIBUTING.md` |

## 2. Suites complètes

| Source | Fichiers scannés | Éléments extraits | Destination |
|---|---|---|---|
| Imbad0202/academic-research-skills | 2 840 (5 `SKILL.md` ~260 Ko, 1 146 Markdown, 478 scripts Python, 590 JSON, 201 YAML, `shared/contracts/` ~100 schémas, 16 PDF d'exemple) | Pipeline 10 étapes, 13 agents de recherche, 12 agents de rédaction, panel de revue 5 sièges, criblage dual, « Material Passport », registre de claims, protocole anti-fuite, vérification d'intégrité, 11 modes opératoires | `references/01`, `05`, `06`, `13`, `18`, `19` ; `scripts/sf/pipeline.py`, `claims.py`, `prisma.py` ; `templates/preregistration.md`, `rebuttal-matrix.md` ; `config/gates.json` |
| KalarisLabs/research-agent-skills | 3 169 (281 `SKILL.md`, 2 023 Markdown, 549 scripts, `catalog/graph.json` 304 Ko, `catalog/skills.json` 303 Ko, benchmarks, CLI TypeScript, docs) | `citation-verification` (4 index), `unslop-academic-writing` (linter), `scientific-writing` (8 CLI), `peer-review` (7 CLI), `apa7`, `venue-templates`, `reproducibility-statement`, `systematic-review-prisma`, `hypothesis-generation`, `paper-lookup` (18 API), `rebuttal`, `research-grants` | `scripts/sf/sources.py`, `verify.py`, `lint.py`, `review.py`, `bib.py` ; `references/04`, `07`, `08`, `09`, `11`, `12`, `15`, `16`, `17` ; `config/sources.json`, `config/styles.json`, `config/venues.json`, `config/reporting-guidelines.json` |
| saintgo7/agents-skills | 82 (50 `SKILL.md` stubs, `ieee-access/SKILL.md` 8,7 Ko, 24 CSV, `install.sh`) | Taxonomie 10 catégories / 50 skills, règles IEEE Access 2026, structure minimale d'une skill | `references/15`, `config/venues.json` (profil ieee-access), `templates/`, `install.sh` |

## 3. Écriture

| Source | Fichiers scannés | Éléments extraits | Destination |
|---|---|---|---|
| ranbot-ai/awesome-skills | 8 785 (2 908 `SKILL.md`, 2 908 fiches JSON, `data/skills.json` 6,3 Mo, `search-index.json`, `skills/content-research-writer/SKILL.md`, web + scraper) | Boucle « recherche → plan → accroche → retour section par section → voix de l'auteur → citations », 1 129 fiches d'agrégateur | `references/11`, `references/12`, `scripts/sf/scaffold.py`, `data/registry.json` |
| cosen1024 — docs de méthodologie | 7 docs | Règles de vérification et de neutralité | `docs/SOURCE_MAP.md`, `references/02` |

## 4. Ce qui n'a pas été repris, et pourquoi

| Élément | Décision |
|---|---|
| ~200 skills très spécialisées à un domaine (RDKit, scVelo, PyTorch FSDP2, AlphaGenome, Nextflow, quantum, GPU serving…) | Conservées intégralement dans `upstream/*.zip` + référencées dans `data/registry.json` (`registry search`), mais **pas embarquées** : une seule skill doit rester légère et progressivement divulguée. Voir `references/20`. |
| ~500 scripts de CI internes, 300 fichiers `.log`, 16 PDF de démonstration, benchmarks JSON de plusieurs Mo | Archivés sans perte ; non dupliqués dans le moteur. |
| Hooks, commandes slash, plugins `.claude-plugin`, workflows propres à chaque dépôt | Archivés ; remplacés par un seul point d'entrée (`scripts/scholarforge.py`) et une CI locale. |
| Systèmes de « cross-model verification » dépendant de Codex/abonnements | Réduits à un protocole d'enveloppe de transfert optionnel dans `references/18`. |
| Règles de venue figées à une année (IEEE Access 2026, NeurIPS 2026…) | Conservées comme **valeurs de départ** avec une règle de vérification obligatoire le jour de la soumission (`references/15`). |

## 5. Améliorations apportées pendant la fusion

1. **Un routeur unique** au lieu de 3 244 `SKILL.md` concurrents : 18 intentions → 28 références,
   frontmatter conforme à la spec Agent Skills (description ≤ 1024 caractères).
2. **Un moteur testé** : 100 tests unitaires et 18 cas d'évaluation, aucune dépendance, aucune clé API, dégradation
   hors ligne par source (là où les suites amont supposaient un hôte Claude/Codex spécifique).
3. **Portes explicites** : G0–G9 machine à états + `AUDIT.md`, au lieu de règles dispersées
   dans des fichiers Markdown de 50–100 Ko.
4. **Traçabilité totale** : inventaire SHA-256 de 16 694 fichiers, manifestes des 14 archives
   (8 intégrales + 6 curées),
   rapports de scan et de sécurité reproductibles via `tools/`.
5. **Registre unifié** : 5 460 entrées dédupliquées avec stade, licence, vérification,
   étoiles et pertinence académique, interrogeable hors ligne.
6. **Honnêteté par défaut** : statuts `UNVERIFIED`/`unverified-offline`, intégrité en trois
   couches (existence ≠ soutien ≠ vérité) et limites affichées dans chaque rapport.
7. **Sécurité** : aucun code amont exécuté, archives inertes, scan statique systématique,
   pas d'`eval`, pas de désérialisation non sûre, pas de téléchargement de code.
8. **Internationalisation** : consignes FR/EN, règles CJK, préservation des diacritiques,
   doubles résumés.
9. **Recherche documentaire datée** : 4 ajouts fondés sur des sources primaires 2025–2026
   (rétractations multi-signaux, PRISMA-S, directives IA, disclosure structurée), journalisés
   dans `docs/RESEARCH_NOTES.md` avec leurs limites.

---

## 5. Sources v2 — recherche 2026-10-28

Ces six dépôts ont été ajoutés après une passe de recherche documentaire et une exploration
de l'API GitHub. Consulter `docs/RESEARCH_NOTES.md` pour les sources primaires et
`docs/SCAN_REPORT_V2.md` pour les métriques du scan (1 440 fichiers, 325 337 lignes).

| Source | Fichiers lus | Éléments extraits | Destination |
|---|---:|---|---|
| agentskills/agentskills (Apache-2.0) | 138 | Spec ouverte : `name`, `description` ≤1024, `metadata` chaînes, corps <500 lignes, références à un niveau ; bibliothèque `skills-ref` | `scripts/sf/spec.py`, `tools/validate_skill.py`, commande `validate`, frontmatter corrigé, playbook 23 |
| anthropics/skills (licences par skill) | 445 (20 `SKILL.md`) | Motifs officiels de divulgation progressive et de structuration | 20 entrées de registre, playbooks 23 et 28 — **aucun code copié** |
| chrisyangsong/citegate (MIT) | 19 | CI de vérification de citations, verdict `retracted` | Conception multi-signaux de `scripts/sf/integrity.py`, porte `G-integrity`, playbook 24 |
| asreview/asreview (Apache-2.0) | 479 | Apprentissage actif, double criblage, priorisation des références | Notes dans playbooks 05 et 28, entrée de registre |
| manubot/manubot (BSD-2-Clause-Patent) | 175 | Citation par identifiant, manuscrits reproductibles | Notes dans playbooks 07 et 28, entrée de registre |
| Future-House/paper-qa (Apache-2.0) | 184 | QA ancrée sur documents avec citations, vérification des extraits | Rappel de l'ancrage des preuves dans playbooks 06 et 28, entrée de registre |

### Ce qui a été ajouté sans dépôt amont

| Besoin identifié | Implémentation originale |
|---|---|
| Conformité à la spec (description 1 041 > 1 024 caractères en v1) | `sf/spec.py` + `tools/validate_skill.py` + `SKILL.md` réécrit |
| Journal de recherche promis par G2 mais jamais écrit | `sf/searchlog.py`, `sources/search-log.{md,json}`, filtres serveur/local, exports CSV/RIS |
| Directives de rapport 2024–2026 manquantes | `config/reporting-guidelines.json` v2 (18 directives), `sf/guidelines.py`, commande `guideline` |
| Déclaration IA structurée (GAIDeT / COPE / ICMJE) | `config/ai-disclosure.json` (9 catégories), `sf/disclosure.py`, commande `disclosure` |
| Rétractations non détectées | `sf/integrity.py` (3 familles de signaux), porte `G-integrity`, playbook 24 |
