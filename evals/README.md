# evals/ — auto-évaluation

`cases.jsonl` contient 12 scénarios (refus de fabrication, injection de prompt, honnêteté hors
ligne, échec de porte, style, PRISMA, citation, règles de venue, voix de l'auteur,
reproductibilité). Chaque cas précise le comportement attendu et interdit.

Ce sont des **cas de conformité**, pas un benchmark de performance. Les règles de déclaration
honnête d'un benchmark sont dans `references/22-evals-benchmarks.md`.

Pour les tests déterministes : `python3 scripts/scholarforge.py selftest` (30 tests).
