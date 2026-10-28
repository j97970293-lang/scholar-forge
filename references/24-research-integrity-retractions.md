# 24 — Intégrité de la littérature : rétractations, corrections, inquiétudes

**Règle centrale :** un DOI qui résout prouve qu'un article existe. Cela ne prouve
ni qu'il n'a pas été rétracté, ni qu'il soutient l'affirmation du manuscrit.

## 1. Pourquoi c'est devenu un point bloquant

La littérature secondaire citant des articles rétractés est massive et persistante.
Une analyse des citations Wikipédia a identifié 1 181 paires « page ↔ article
rétracté » et conclu que 71,6 % des citations examinées étaient problématiques
(arXiv:2509.18403). Des milliers de citations à des travaux très cités rétractés
continuent d'être produites après la date de rétractation, sans avertissement
lisible par machine. Vérifier ses références est donc une tâche de routine, pas une
exception.

## 2. Les registres ne sont pas d'accord — et c'est important

| Registre | Ce qu'il expose | Limite documentée |
|---|---|---|
| OpenAlex | `is_retracted` (booléen), issu de Retraction Watch | Booléen unique : des corrections et des expressions d'inquiétude ont déjà été étiquetées à tort comme rétractations (fenêtre documentée déc. 2023–mars 2024, ~2 300 œuvres). Il manque aussi une partie des rétractations (~7,5 % dans une étude de 2025). |
| Crossref | `updated-by[]` avec `type`, `label`, `source: retraction-watch`, date et DOI de l'avis ; champs `update-to` / `relation` | Acquéreur de Retraction Watch en 2023 ; intégré dans l'API publique à partir de 2025. Les valeurs de type sont hétérogènes (fautes de frappe, valeurs hors énumération observées). |
| Retraction Watch | notices détaillées | Couverture dépend des éditeurs et de la veille. |
| PubMed / Europe PMC | drapeaux de publication type | Orientés biomédecine. |

Des travaux récents montrent que Crossref et Retraction Watch ne s'accordent que sur
environ 72 % des DOI rétractés, et que seule une faible fraction d'une union de
~137 000 DOI fait l'unanimité entre quatre registres. **Conséquence méthodologique :
un seul signal n'est jamais un verdict.** La convergence de signaux indépendants
est le seul indicateur robuste, et l'absence de signal n'est pas une preuve
d'intégrité.

## 3. Ce que fait `integrity` (dans ce dépôt)

```bash
scholarforge integrity references.bib                    # hors ligne : titres seulement
scholarforge integrity references.bib --online          # + OpenAlex + Crossref
scholarforge integrity --online --json                  # pour la CI
```

Trois familles de signaux :

1. **Titre** (hors ligne, gratuit, immédiat) : `RETRACTED:`, `WITHDRAWN:`,
   `RETRACTION NOTE`, « expression of concern », « corrigendum ».
2. **OpenAlex** : `GET /works/https://doi.org/{doi}` → `is_retracted`.
3. **Crossref** : `GET /works/{doi}` → `updated-by[].type` (retraction,
   correction, expression-of-concern), `update-to`, `relation`.

Décision :

| Verdict | Condition | Bloquant |
|---|---|---|
| `retracted-confirmed` | ≥ 2 signaux de rétractation concordants | oui |
| `retracted-suspected` | 1 seul signal | non, sauf marqueur explicite de l'éditeur dans le titre |
| `notice-found` | correction / expression d'inquiétude uniquement | non |
| `no-signal` | registres interrogés, aucun signal | non |
| `lookup-failed` | toutes les sources en échec | non, mais à signaler |
| `not-checked` | mode hors ligne, aucun marqueur | non |

`audit` lit le rapport mis en cache (`output/integrity.json`) dans la porte
`G-integrity`. Exécutez `integrity --online` avant l'audit pour alimenter ce cache ;
l'audit lui-même ne déclenche jamais de rafale réseau.

## 4. Protocole humain obligatoire

1. Lire l'avis sur la page de l'éditeur, pas seulement dans une base.
2. Repérer la phrase du manuscrit qui s'appuie sur cet article.
3. Décider : retirer la référence, remplacer par une version corrigée, ou discuter
   explicitement la controverse — et justifier par écrit.
4. Consigner la date de vérification : les notices apparaissent après la publication.
5. Refaire le contrôle juste avant la soumission.

## 5. Ce que le module ne fait pas

- Il ne détecte pas la fraude, les images manipulées, le p-hacking ou les
  « paper mills ». Les motifs linguistiques détectés par `lint` sont des signaux de
  style, pas des preuves.
- Il ne couvre pas les préprints, les versions sans DOI, les documents cités par
  URL ou les ouvrages.
- Il ne sait pas si vous citez la partie rétractée de l'article.
- Il n'a pas de valeur légale. L'éditeur fait foi.

## 6. Sources primaires

- OpenAlex work object (`is_retracted`) : `https://docs.openalex.org/api-entities/works/work-object`
- Crossref API : `https://api.crossref.org/works/{doi}`
- Hauschke & Nazarovets, « (Non-)retracted academic papers in OpenAlex », 2025 :
  `https://journals.sagepub.com/doi/10.1177/01655515251322478` (préprint arXiv:2403.13339)
- Fletcher & Stevenson, « Predicting retracted research », 2025 :
  `https://link.springer.com/article/10.1186/s41073-025-00168-w`
- Wikipédia / rétractations : `https://arxiv.org/abs/2509.18403`
