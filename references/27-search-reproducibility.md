# 27 — Recherche reproductible et PRISMA-S

**Problème.** « Nous avons recherché PubMed, Scopus et Web of Science » n'est pas
reproductible. PRISMA-S demande : la chaîne exacte, la base **et l'interface**, la
date, les limites, les filtres, les doublons et les comptages. C'est la porte G2.

## 1. Anatomie d'une recherche traçable

| Élément | Où c'est enregistré dans ScholarForge |
|---|---|
| Chaîne exacte | `sources/search-log.md`, colonne Query |
| Base + interface | colonne Database + `REST API` dans `search-log.json` |
| Date UTC | colonne UTC date |
| Filtres demandés | colonne Requested filters |
| Filtres réellement appliqués | `filters_applied.native` et `filters_applied.applied` |
| Filtres ignorés par une source | `filters_applied.ignored` |
| URL exacte de l'API | colonne Endpoint |
| Nombre de résultats | colonnes Hits et Unique |
| Version de l'outil | colonne CLI |

Chaque résultat porte aussi `source`, `source_url` et `retrieved_at` dans le JSON
d'export. Aucune clé API n'est nécessaire pour les six sources configurées.

## 2. Utiliser le CLI

```bash
scholarforge search "RNA velocity benchmarking" \
  --sources openalex,crossref,arxiv,semanticscholar,pubmed,europepmc \
  --limit 30 --from-year 2020 --to-year 2026 --oa-only --min-citations 5 \
  --out sources/hits.json --bib sources/hits.bib \
  --csv sources/hits.csv --ris sources/hits.ris \
  --log-path /chemin/du/projet

scholarforge searchlog --path /chemin/du/projet
```

Filtres disponibles : `--from-year`, `--to-year`, `--min-citations`, `--oa-only`,
`--type`. Ils sont appliqués **côté serveur quand l'API le permet** (OpenAlex,
Crossref, Semantic Scholar, PubMed, Europe PMC) puis **réappliqués localement** à
toutes les sources pour garantir un comportement homogène. Les filtres non pris en
charge par une source sont consignés, pas tus.

**Piège honnête :** le post-filtrage local s'applique à la fenêtre de résultats
déjà récupérée. Un filtre sévère sur `--limit 5` peut produire zéro résultat alors
que la base en contient des milliers. Augmentez `--limit` quand vous filtrez, et
notez-le dans la méthode.

`--no-log` désactive le journal (déconseillé pour une revue systématique).

## 3. Saturation et arrêt de la recherche

Une recherche n'est « terminée » que si vous pouvez justifier l'arrêt :
- saturation des références (les nouvelles requêtes ne ramènent plus que des
  doublons) ;
- couverture des bases et des registres d'essais pertinents au domaine ;
- recherche ascendante/descendante (citations et bibliographies) consignée ;
- recherche de la littérature grise si le protocole le prévoit ;
- **mise à jour juste avant la soumission**, avec une nouvelle ligne dans le
  journal et une nouvelle date.

## 4. Doublons

`dedupe` fusionne par DOI puis par similarité de titre et **justifie chaque
regroupement** (`_match_reason`). PRISMA-S demande le nombre de doublons retirés et
la méthode utilisée : exportez le JSON de déduplication en annexe.

## 5. Ce que le journal ne prouve pas

- Il ne prouve pas que la stratégie est exhaustive.
- Les API ne renvoient pas les mêmes résultats que les interfaces web : indiquez
  toujours laquelle vous avez utilisée.
- Les index changent : un comptage daté n'est valable qu'à sa date.
- Une source en panne n'invalide pas les autres, mais doit apparaître comme
  `error` dans le journal — ne la supprimez pas silencieusement.

## 6. Sources

- PRISMA-S : `https://www.equator-network.org/reporting-guidelines/prisma-s/`
- PRISMA 2020 : `http://www.prisma-statement.org/`
- OpenAlex filters : `https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/filter-entity-lists`
- Crossref REST API : `https://api.crossref.org/`
