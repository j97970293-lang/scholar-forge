# Guide d'utilisation détaillé

## 1. Installer la skill
```bash
bash install.sh --target ~/.claude/skills/scholar-forge
# ou, sous Windows PowerShell
./install.ps1 -Target "$HOME\.claude\skills\scholar-forge"
python3 scripts/scholarforge.py doctor
```

## 2. Choisir un mode
Voir `SKILL.md` §2. En résumé : `quick` (brief), `standard` (brouillon + vérification),
`review-protocol` (PRISMA), `full` (S0→S9), `verify`, `revision`, `audit`.

## 3. Espace de travail
`init` crée 19 fichiers en texte brut. Tout est versionnable dans Git ; aucune base de
données, aucun fichier binaire propriétaire. L'état de la pipeline est dans
`.scholarforge/state.json`.

## 4. Recherche reproductible
```bash
sf search "single-cell RNA velocity benchmarking" \
   --sources openalex,crossref,arxiv,semanticscholar,pubmed,europepmc \
   --limit 20 --out sources/hits.json --bib sources/hits.bib
```
Le JSON contient, par source : l'URL exacte de la requête, le statut, le nombre de résultats et
l'horodatage. Recopiez les chaînes dans `sources/search-log.md`.

## 5. Bibliographie
`dedupe` fusionne par DOI puis par similarité de titre (≥0,93). `verify --online` résout les
DOI via Crossref et compare les titres ; `bib --style` produit une vue APA/IEEE/Vancouver/
Chicago. Pour une soumission finale, utilisez le CSL officiel avec Pandoc ou `biblatex`.

## 6. Criblage
Remplissez `screening/screening.csv` avec deux décisions indépendantes et une colonne
`adjudicated`. `prisma` calcule les effectifs, κ/PABAK, les motifs d'exclusion et un diagramme
Mermaid. Toute ligne `unclear` bloque la porte G3.

## 7. Preuves et affirmations
`evidence/evidence.csv` = une ligne par passage source. `evidence/claims.csv` = une ligne par
affirmation du manuscrit. `claims --manuscript` détecte aussi la dérive : une affirmation qui
n'apparaît plus dans le texte après révision.

## 8. Rédaction et style
`new manuscript` produit la structure IMRaD ; `lint` détecte les tics de LLM, les
placeholders, les phrases trop longues, les empilements de nuances et les caractères Unicode
invisibles. Le score est un signal, pas un jugement scientifique.

## 9. Revue et réponse
`new review` génère la grille multi-sièges ; `review` vérifie le ton et l'ancrage des
commentaires ; `rebuttal` transforme des commentaires `R1C1: …` en matrice de réponse avec
actions et emplacements.

## 10. Portes et audit
`pipeline status|advance|reset`, puis `audit --online` agrège les 7 contrôles locaux et écrit
`output/AUDIT.md`. Un échec nomme la porte et l'artefact manquant. `--force` sur `advance`
enregistre une dérogation horodatée dans l'historique.

## 11. Travailler hors ligne
Toutes les commandes fonctionnent sans réseau sauf `search` et `verify --online`.
En mode hors ligne, `verify` n'inspecte que la structure ; le rapport l'indique explicitement.

## 12. Étendre
Voir `references/21-scripting-guide.md` : ajout de règles, de venues, de styles, d'API, de
templates et de cas d'évaluation — puis `selftest` et `doctor`.

## Dépannage

| Symptôme | Cause | Solution |
|---|---|---|
| `doctor` = INCOMPLETE | dépôt copié partiellement | recloner / dézipper l'archive Drive |
| `search` renvoie 0 pour une source | API indisponible ou throttlée | vérifier le champ `error`, réessayer avec une autre source |
| `verify` = `not-resolved` | DOI invalide ou non déposé | ouvrir le DOI, corriger la référence |
| `prisma` = FAIL | décision manquante / désaccord non arbitré | compléter `r2` ou `adjudicated` |
| `audit` = FAIL | une porte bloquante | lire `output/AUDIT.md`, corriger l'artefact nommé |
