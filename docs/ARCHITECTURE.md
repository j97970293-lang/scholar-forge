# Architecture

```
                ┌───────────────────────────────────────────┐
                │  SKILL.md  (1 seul point d'entrée)        │
                │  frontmatter · 12 règles · routeur ·      │
                │  10 étapes · 7 portes · contrat de sortie │
                └───────────────┬───────────────────────────┘
                                │ divulgation progressive
        ┌───────────────────────┼────────────────────────┐
        ▼                       ▼                        ▼
 references/ (22)        config/ (6 JSON)         templates/ (15)
 playbooks chargés       règles éditables         artefacts texte
 à la demande            sans toucher au code
                                │
                                ▼
                ┌───────────────────────────────────────────┐
                │ scripts/scholarforge.py (CLI, 16 commandes)│
                │  ┌─────────────────────────────────────┐  │
                │  │ sf/ sources · bib · verify · prisma │  │
                │  │     claims · lint · scaffold        │  │
                │  │     review · pipeline · audit       │  │
                │  │     registry · util · cli           │  │
                │  └─────────────────────────────────────┘  │
                │  Python 3.9+ stdlib uniquement            │
                └───────────┬───────────────┬───────────────┘
                            │               │
                            ▼               ▼
                   data/ (registre,     upstream/ (8 ZIP
                   scan, sécurité)      + manifeste SHA-256)
                            ▲               ▲
                            └── tools/ ─────┘
                        scan · security · merge · package
```

## Principes de conception
1. **Une skill, pas 3 244.** Le `SKILL.md` tient dans un contexte raisonnable ; la charge
   cognitive est reportée dans `references/` via un index explicite.
2. **Déterministe avant LLM.** Tout ce qui peut être vérifié par un script l'est : DOI,
   dédoublonnage, κ, cohérence du registre, placeholders, score de style.
3. **Échec fermé.** Une porte échoue → arrêt. Pas de « passage avec réserves » implicite.
4. **Dégradation gracieuse.** Réseau optionnel, panne par source, aucune clé requise.
5. **Provenance partout.** Chaque résultat d'API, chaque entrée de registre, chaque archive
   porte son origine et son horodatage.
6. **Données ≠ code.** Les ZIP amont ne sont jamais exécutés ; le moteur est original.

## Flux de données d'un projet type
```
search ──► hits.json ──► dedupe ──► references.bib ──► verify ──┐
                                                                  ├──► audit ──► AUDIT.md
screening.csv ──► prisma ──► PRISMA.md ──────────────────────────┤
evidence.csv + claims.csv ──► claims ──► claims.md ──────────────┤
draft/manuscript.md ──► lint ──► lint.md ────────────────────────┤
reviews.md ──► rebuttal ──► rebuttal-matrix.csv ─────────────────┘
                        pipeline.state.json (S0…S9)
```

## Sécurité
Voir `docs/SECURITY_SCAN.md`. Le moteur n'utilise ni `eval`, ni `exec`, ni `pickle`, ni
`subprocess(shell=True)`, ni téléchargement de code, ni chemins de secrets. Les seules
requêtes réseau sortantes ciblent les API savantes listées dans `config/sources.json`.
