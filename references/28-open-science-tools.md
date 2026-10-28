# 28 — Outils externes : quand les utiliser, ce qu'ils ne remplacent pas

Six dépôts supplémentaires ont été lus en 2026-10-28 (voir
`docs/SCAN_REPORT_V2.md`). Ils sont **référencés et archivés**, jamais exécutés.
Ils ne font pas partie du runtime stdlib de ScholarForge : ce sont des outils à
envisager quand la tâche dépasse ce qu'un script local peut faire.

| Outil | Licence | Apport | Limite à connaître |
|---|---|---|---|
| `agentskills/agentskills` | Apache-2.0 | Spécification officielle + bibliothèque `skills-ref` de validation | Cible mouvante : relire la spec avant de publier une skill |
| `anthropics/skills` | pas de LICENSE (notices tiers conservées) | 20 `SKILL.md` officiels illustrant la divulgation progressive | Pas de licence explicite → ne pas réutiliser le code ; s'inspirer des motifs seulement |
| `chrisyangsong/citegate` | MIT | Vérification de références en CI (Crossref + OpenAlex), verdicts `retracted` | Un verdict binaire unique ne suffit pas : les registres divergent (playbook 24) |
| `asreview/asreview` | Apache-2.0 | Apprentissage actif pour le criblage de revues systématiques | L'outil accélère le tri ; il ne remplace pas le double criblage humain, l'arbitrage ni κ |
| `manubot/manubot` | BSD-2-Clause-Patent | Manuscrits ouverts, citation par identifiant, références reproductibles | Suppose un flux de publication Manubot |
| `Future-House/paper-qa` | Apache-2.0 | Question-réponse ancrée sur des documents scientifiques avec citations | Système RAG/LLM : nécessite des clés, une infrastructure et une vérification humaine des réponses |

## 1. Ce qui a été réellement intégré

- **Conformité de spec** : `sf/spec.py`, `tools/validate_skill.py`, commande
  `validate`, frontmatter corrigé (description ≤ 1024, `metadata` en chaînes).
- **Intégrité des références** : `sf/integrity.py`, porte `G-integrity`, rapports
  `output/integrity.{json,md}` et playbook 24.
- **Journal de recherche** : `sf/searchlog.py`, `sources/search-log.{md,json}`,
  filtres serveur + local, exports CSV/RIS, playbook 27.
- **Directives de rapport** : `config/reporting-guidelines.json` v2 (18 directives),
  `sf/guidelines.py`, commande `guideline`, playbook 25.
- **Déclaration IA** : `config/ai-disclosure.json`, `sf/disclosure.py`, commande
  `disclosure`, playbook 26.
- **Registre** : 26 entrées supplémentaires (20 skills officiels + 6 outils),
  soit 5 460 entrées au total.

## 2. Ce qui n'a PAS été intégré, et pourquoi

- Les modèles d'apprentissage actif d'ASReview et le RAG de PaperQA2 ne sont pas
  embarqués : ils exigeraient des dépendances et des ressources externes, ce qui
  casserait la promesse « stdlib uniquement, zéro installation ».
- Aucun code de `anthropics/skills` n'est copié : l'absence de licence explicite
  interdit la réutilisation. Seuls les **principes** de structuration sont repris.
- Les checklists officielles ne sont pas reproduites mot à mot : ce serait une
  contrefaçon de la source et une source d'erreur. Le CLI génère des aides de
  travail abrégées avec un lien vers l'énoncé officiel.

## 3. Deux niveaux d'archives — à ne pas confondre

- `upstream/*.zip` (8 archives) : instantanés **intégraux** des dépôts v1, hors
  internals Git. Manifeste : `upstream/manifest.json`.
- `upstream/v2/*.zip` (6 archives) : instantanés **curés** — suites de tests,
  caches, fichiers binaires et fichiers > 2 Mio exclus, avec comptabilité des
  exclusions dans `upstream/v2/manifest.json`.

Cette distinction est délibérée : elle permet d'ajouter des sources sans faire
exploser la taille du dépôt, tout en restant honnête sur ce qui est conservé.
