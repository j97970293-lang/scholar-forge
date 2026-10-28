# Architecture (1.1.0)

```
            ┌───────────────────────────────────────────────────┐
            │  SKILL.md  — 1 seul point d'entrée, 288 lignes    │
            │  frontmatter conforme Agent Skills · 12 règles ·  │
            │  routeur 18 intentions · 10 étapes · contrat       │
            └──────────────────────┬────────────────────────────┘
                                   │ divulgation progressive (1 niveau)
     ┌─────────────────────────────┼────────────────────────────┐
     ▼                             ▼                            ▼
references/ (28)            config/ (7 JSON)             templates/ (15)
playbooks chargés à la      règles éditables sans        artefacts texte
demande                    toucher au code
                                   │
                                   ▼
        ┌─────────────────────────────────────────────────────┐
        │ scripts/scholarforge.py — CLI, 21 commandes          │
        │ ┌─────────────────────────────────────────────────┐ │
        │ │ cœur  : bib · verify · prisma · claims · lint    │ │
        │ │        scaffold · review · pipeline · audit      │ │
        │ │ v1.1  : integrity · searchlog · guidelines      │ │
        │ │        disclosure · spec                        │ │
        │ │ infra : sources · registry · util · cli          │ │
        │ └─────────────────────────────────────────────────┘ │
        │ Python 3.9+ stdlib uniquement · réseau optionnel     │
        └──────────┬────────────────────────┬─────────────────┘
                   ▼                        ▼
   data/ (registre 5 460,          upstream/  8 ZIP intégraux
   inventaires v1/v2,              upstream/v2/ 6 ZIP curés
   sécurité, classements)          + manifestes SHA-256
                   ▲                        ▲
                   └────── tools/ (8) ─────┘
        scan · security · merge · package · v2_pipeline
        · validate_skill · check_secrets
```

## Principes de conception

1. **Une skill, pas 3 244.** Le `SKILL.md` tient dans ~4 300 tokens ; la charge cognitive est
   reportée dans `references/` via un index explicite. Conformité vérifiée par `validate`.
2. **Déterministe avant LLM.** Tout ce qui peut être vérifié par un script l'est : DOI,
   rétractations, dédoublonnage, κ, cohérence du registre, placeholders, score de style,
   complétude d'une déclaration IA.
3. **Échec fermé.** Une porte échoue → arrêt. Huit portes dans `audit` ; `G-pipeline` reste
   consultative (non bloquante).
4. **Dégradation gracieuse.** Réseau optionnel, panne par source, aucune clé requise. `audit`
   ne fait jamais d'appel réseau par lui-même : il consomme `output/integrity.json`.
5. **Provenance partout.** Chaque résultat d'API, chaque ligne de `search-log.md`, chaque
   entrée de registre, chaque archive porte son origine et son horodatage.
6. **Données ≠ code.** Les ZIP amont ne sont jamais exécutés ; le moteur est original.
7. **Honnêteté sur les sources.** Les checklists sont abrégées et liées aux énoncés officiels ;
   les verdicts d'intégrité sont multi-signaux et jamais définitifs. Le journal daté de la
   recherche est dans `docs/RESEARCH_NOTES.md`.

## Flux de données d'un projet type

```
search ──► hits.{json,bib,csv,ris} ──► dedupe ──► references.bib ──┐
   └──► sources/search-log.{md,json} (PRISMA-S)                    │
                                                                    │
references.bib ──► verify ──► verify.md ───────────────────────────┤
references.bib ──► integrity --online ──► integrity.json ──────────┤
screening.csv ──► prisma ──► PRISMA.md ────────────────────────────┼──► audit ──► AUDIT.md
evidence.csv + claims.csv ──► claims ──► claims.md ────────────────┤     (8 portes)
draft/manuscript.md ──► lint ──► lint.md ──────────────────────────┤
reviews.md ──► rebuttal ──► rebuttal-matrix.csv ────────────────────┤
guideline ──► submission/checklist.md ─────────────────────────────┤
disclosure ──► submission/ai-disclosure.md ────────────────────────┘
                    .scholarforge/state.json (S0…S9)
```

## Les quatre ajouts de la 1.1.0

| Module | Entrées | Sorties | Raison |
|---|---|---|---|
| `sf/integrity.py` | BibTeX + OpenAlex + Crossref | `output/integrity.{json,md}`, `G-integrity` | Un DOI résolu peut être rétracté ; les registres divergent |
| `sf/searchlog.py` | Rapport `search_all` | `sources/search-log.{md,json}` | La porte G2 promettait un journal qui n'était pas écrit |
| `sf/guidelines.py` | `config/reporting-guidelines.json` | checklist Markdown, recommandations | Directives 2024–2026 absentes de la v1 |
| `sf/disclosure.py` | `config/ai-disclosure.json` | déclaration + lint | Déclaration « AI was used » insuffisante pour COPE/ICMJE |
| `sf/spec.py` | `SKILL.md` | rapport PASS/FAIL | La v1 dépassait la limite de 1 024 caractères |

## Sécurité

Voir `docs/SECURITY_SCAN.md`. Le moteur n'utilise ni `eval`, ni `exec`, ni `pickle`, ni
`subprocess(shell=True)`, ni téléchargement de code, ni chemins de secrets. Les seules
requêtes réseau sortantes ciblent les API savantes listées dans `config/sources.json` et les
deux endpoints d'intégrité (OpenAlex, Crossref) avec un timeout borné. `check_secrets.py`
vérifie l'absence de jetons dans les fichiers texte ; les archives sont couvertes par les
manifestes SHA-256.
