# Guide d'utilisation détaillé (1.1.0)

Toutes les commandes s'appellent via `python3 scripts/scholarforge.py <commande>` (abrégé
`sf` ci-dessous). `--json` est disponible sur toutes les commandes pour un usage machine.

## 1. Installer la skill
```bash
bash install.sh --target ~/.claude/skills/scholar-forge
# ou, sous Windows PowerShell
./install.ps1 -Target "$HOME\.claude\skills\scholar-forge"
python3 scripts/scholarforge.py doctor
python3 scripts/scholarforge.py validate      # spec Agent Skills
```
Le dossier cible doit s'appeler exactement `scholar-forge` (le `name` du frontmatter doit
correspondre au nom du dossier). `install.sh` copie un dossier allégé : `SKILL.md`,
`LICENSE`, `NOTICE.md`, `references/`, `scripts/`, `templates/`, `config/`, `data/`,
`tests/`, `evals/`. Les archives `upstream/`, les outils de build et les rapports restent
dans le dépôt.
`--link` lie le dépôt entier pour le développement.

## 2. Choisir un mode
Voir `SKILL.md` §2. En résumé : `quick` (brief), `standard` (brouillon + vérification),
`review-protocol` (PRISMA), `full` (S0→S9), `verify`, `revision`, `audit`, `design`,
`submit`, `check`.

## 3. Espace de travail
`init` crée 19 fichiers en texte brut. Tout est versionnable dans Git ; aucune base de
données, aucun fichier binaire propriétaire. L'état de la pipeline est dans
`.scholarforge/state.json`.

## 4. Recherche reproductible (PRISMA-S)
```bash
sf search "single-cell RNA velocity benchmarking" \
   --sources openalex,crossref,arxiv,semanticscholar,pubmed,europepmc \
   --limit 30 --from-year 2020 --to-year 2026 --oa-only --min-citations 5 \
   --out sources/hits.json --bib sources/hits.bib \
   --csv sources/hits.csv --ris sources/hits.ris --log-path .
sf searchlog                 # synthèse du journal
```
Chaque appel ajoute une ligne par base à `sources/search-log.md` et à
`sources/search-log.json` : chaîne exacte, date UTC, filtres demandés, filtres réellement
appliqués (natif + local), filtres ignorés, URL d'API, nombre de résultats, version du CLI.
Les filtres sont appliqués côté serveur quand l'API le permet, puis réappliqués localement
pour homogénéiser les sources. **Attention :** le filtrage local n'agit que sur la fenêtre
récupérée — augmentez `--limit` quand vous filtrez. `--no-log` désactive le journal.
Voir le playbook 27.

## 5. Bibliographie et intégrité
`dedupe` fusionne par DOI puis par similarité de titre (≥0,93). `verify --online` résout les
DOI via Crossref et compare les titres ; `bib --style` produit une vue APA/IEEE/Vancouver/
Chicago. Pour une soumission finale, utilisez le CSL officiel avec Pandoc ou `biblatex`.

**Nouveau :** `integrity --online` croise trois familles de signaux (marqueur de titre,
`is_retracted` d'OpenAlex, notices `updated-by` de Crossref). Deux signaux concordants
donnent `retracted-confirmed` (bloquant) ; une seule famille donne `retracted-suspected`
(non bloquant, sauf préfixe RETRACTED/WITHDRAWN dans le titre : arrêt de précaution).
Les registres peuvent partager une même source ; ce n'est pas une preuve indépendante. Le rapport `output/integrity.md` liste les notices avec leur date et leur DOI.
```bash
sf integrity references.bib --online --out output/integrity.md
```
Exécutez cette commande **avant** `audit` : l'audit lit le rapport mis en cache
(`output/integrity.json`) si son SHA-256 correspond aux références et s'il date de moins de
24 h. Sinon il refait le scan des titres. La porte d'intégrité ne fait pas d'appel réseau ;
`audit --online` conserve séparément la résolution Crossref de `G-references`. Voir le playbook 24.

## 6. Criblage
Remplissez `screening/screening.csv` avec deux décisions indépendantes et une colonne
`adjudicated`. `prisma` calcule les effectifs, κ/PABAK, les motifs d'exclusion et un diagramme
Mermaid. Toute ligne `unclear` bloque la porte G3. Pour de grands corpus, un outil
d'apprentissage actif comme ASReview peut aider à prioriser — sans remplacer le double
criblage humain (playbook 28).

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

## 10. Directives de rapport (2024–2026)
```bash
sf guideline --list
sf guideline --recommend "diagnostic accuracy of an AI test"
sf guideline --key prediction-model --title "Mon étude" --venue "BMJ" \
   --out submission/checklist.md
```
18 directives sont configurées avec année, URL officielle, périmètre, éventuelle directive
remplacée et checklist de travail abrégée. Le routeur suggère ; un humain choisit.
TRIPOD+AI (2024) remplace TRIPOD 2015 ; STARD-AI (2025) a reçu une correction en juillet
2026. Les checklists générées **ne sont pas** les items officiels : vérifiez-les sur la source
primaire et relisez les instructions aux auteurs le jour de la soumission. Voir le playbook 25.

## 11. Déclaration d'usage de l'IA
```bash
sf disclosure --tool "Claude Sonnet 4.5" --tool-version "2026-09-29" \
   --purpose search,writing,editing \
   --oversight "Le Dr X a relu et vérifié chaque affirmation" \
   --verification "Crossref + registre preuves/affirmations" \
   --prompts "Annexe B" --policy-date 2026-10-28 --venue "Nature" \
   --out submission/ai-disclosure.md
sf disclosure --check submission/ai-disclosure.md
```
Catégories : `ideation`, `search`, `screening`, `extraction`, `analysis`, `writing`,
`editing`, `translation`, `figures`. Cinq champs structurels sont vérifiés par `--check` :
outil, version/date, finalité, supervision humaine, absence de statut d'auteur pour l'IA.
Les placeholders et une politique marquée « NOT YET CHECKED » font échouer le contrôle.
Une déclaration explicite de non-usage est acceptée.
L'IA n'est jamais auteur (COPE/ICMJE). Voir le playbook 26.

## 12. Portes et audit
`pipeline status|advance|reset`, puis `audit` agrège **huit** portes et écrit
`output/AUDIT.md` : `G-style`, `G-references`, `G-integrity`, `G-claims`, `G-prisma`,
`G-disclosures`, `G-rebuttal`, `G-pipeline` (cette dernière est consultative). Un échec nomme
la porte et l'artefact manquant. `--force` sur `advance` enregistre une dérogation horodatée
dans l'historique. Seuils dans `config/gates.json` et `config/rules.json`.

## 13. Travailler hors ligne
Toutes les commandes fonctionnent sans réseau sauf `search`, `verify --online` et
`integrity --online`. En mode hors ligne, `verify` n'inspecte que la structure et `integrity`
que les titres ; les rapports l'indiquent explicitement. Aucune métadonnée n'est inventée.

## 14. Valider et étendre
```bash
sf validate           # spec Agent Skills (name, description, metadata, références)
sf validate --json    # pour la CI
tools/validate_skill.py
```
Voir le playbook 21 pour l'ajout de règles, de venues, de styles, d'API, de templates et de
cas d'évaluation — puis `selftest`, `doctor` et `validate`.

## Dépannage

| Symptôme | Cause | Solution |
|---|---|---|
| `validate` = FAIL sur `name` | dossier cible mal nommé | renommer en `scholar-forge` |
| `doctor` = INCOMPLETE | dépôt copié partiellement | recloner / dézipper l'archive Drive |
| `search` renvoie 0 pour une source | API indisponible, throttlée ou filtre trop sévère | lire `error`, augmenter `--limit`, essayer une autre source |
| `searchlog` = 0 ligne | `search` lancé avec `--no-log` ou hors projet | relancer avec `--log-path .` |
| `verify` = `not-resolved` | DOI invalide ou non déposé | ouvrir le DOI, corriger la référence |
| `integrity` = `lookup-failed` | les deux registres injoignables | réessayer ; ne pas conclure à l'absence de rétractation |
| `prisma` = FAIL | décision manquante / désaccord non arbitré | compléter `r2` ou `adjudicated` |
| `disclosure --check` = FAIL | champ structurel absent | compléter l'outil, la version, la finalité, la supervision |
| `audit` = FAIL | une porte bloquante | lire `output/AUDIT.md`, corriger l'artefact nommé |

**Portée des comptes de recherche :** les clients récupèrent une fenêtre bornée par API
(souvent au plus 50 notices), pas l'ensemble paginé d'une base. Les comptes du journal sont
des notices récupérées, pas les totaux de résultats. Les métadonnées inconnues sont
conservées par les filtres locaux. Le journal facilite PRISMA-S sans certifier l'exhaustivité.
