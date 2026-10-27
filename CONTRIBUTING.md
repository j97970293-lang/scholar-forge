# Contribuer

## Règles de base
- Aucune dépendance externe dans `scripts/` : Python 3.9+ stdlib uniquement.
- Aucune clé, aucun token, aucun secret dans les fichiers (voir `SECURITY.md`).
- Toute nouvelle règle doit être **donnée**, pas codée en dur : `config/*.json`.
- Toute nouvelle commande doit avoir un test dans `tests/test_scholarforge.py`.
- Toute affirmation de performance doit être accompagnée des conditions de mesure
  (`references/22-evals-benchmarks.md`).

## Boucle de développement
```bash
python3 scripts/scholarforge.py selftest
python3 scripts/scholarforge.py doctor
bash examples/end-to-end/run-demo.sh
bash examples/end-to-end/run-demo.sh --fixed
python3 -m compileall -q scripts tools tests
```

## Ajouter une API savante
1. Écrire `_client()` dans `scripts/sf/sources.py` avec la même signature que les autres.
2. L'ajouter à `_CLIENT` et à `SOURCES`.
3. Documenter endpoint, docs, clé, limites et force/faiblesse dans `config/sources.json`.
4. Ajouter un test hors ligne (format de la réponse) avec une fixture locale.

## Ajouter un style de citation
`sf/bib.py::format_ref` + `config/styles.json`. Pour une sortie camera-ready, recommander le
CSL officiel plutôt que d'étendre le formateur best-effort.

## Ajouter une venue
`config/venues.json` avec l'URL officielle et une note « vérifier le jour J ». Ne jamais
présenter une règle figée comme actuelle.

## Ré-attribuer
Si vous réutilisez du contenu de `upstream/`, respectez la licence du dépôt d'origine et
mettez à jour `NOTICE.md`.

## Style de code
PEP 8 souple, annotations de type, docstrings de module, pas d'`eval`/`exec`, pas de
`subprocess(shell=True)`, pas de désérialisation non sûre. Les messages CLI sont en français
ou en anglais, mais cohérents au sein d'un même rapport.
