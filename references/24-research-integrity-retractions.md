# 24 — Intégrité de la littérature : rétractations, corrections, inquiétudes

**Règle centrale :** un DOI qui résout prouve qu'un article existe. Cela ne prouve
ni qu'il n'a pas été rétracté, ni qu'il soutient l'affirmation du manuscrit.

## 1. Ce que les sources permettent de conclure

OpenAlex expose `is_retracted` ; Crossref expose les notices déposées sur les DOI.
Le préprint de Hauschke et Nazarovets documente des erreurs de classement dans
OpenAlex pour les données du 22 décembre 2023 au 19 mars 2024. C'est une raison
concrète de vérifier les notices, **pas** un taux d'erreur valable pour la base actuelle.

Sources : `https://docs.openalex.org/api-entities/works/work-object`,
`https://arxiv.org/abs/2403.13339`, DOI `10.1177/01655515251322478`.

| Source | Champ consulté | Limite |
|---|---|---|
| OpenAlex | `is_retracted` | Un booléen agrégé ne précise ni le motif ni la date de l'avis |
| Crossref | `updated-by[]`, relations entrantes de rétractation | Couverture et qualité dépendent des dépôts et des mises à jour |
| Bibliographie / titre Crossref | `RETRACTED:`, `WITHDRAWN:`, expression of concern, corrigendum | Le titre local peut être ancien ou erroné ; ce n'est pas une lecture de la page éditeur |

**Attention à l'indépendance :** OpenAlex et Crossref peuvent partager la même
source Retraction Watch. Deux API concordantes ne sont pas deux enquêtes
indépendantes. L'absence d'un signal n'est jamais une preuve d'intégrité.

## 2. Commandes

```bash
python3 scripts/scholarforge.py integrity references.bib               # titres seulement
python3 scripts/scholarforge.py integrity references.bib --online      # + deux registres
python3 scripts/scholarforge.py integrity references.bib --online --json
```

Le moteur ne transmet que les DOI aux API ; aucun manuscrit n'est envoyé.

| Verdict | Interprétation | Blocage local |
|---|---|---|
| `retracted-confirmed` | Au moins deux familles de signaux concordantes | oui ; confirmation des signaux, pas verdict éditorial définitif |
| `retracted-suspected` | Une seule famille de signaux | non, **sauf** titre explicitement préfixé `RETRACTED` ou `WITHDRAWN` : arrêt de précaution |
| `notice-found` | Correction, inquiétude ou autre notice | non ; lire la notice |
| `no-signal` | Au moins un registre a répondu, pas de signal détecté | non ; voir les erreurs éventuelles de l'autre registre |
| `lookup-failed` | Les deux registres ont échoué | non ; cela ne signifie pas « vérifié » |
| `not-checked` | Mode hors ligne sans marqueur, ou référence sans DOI | non |
| `invalid-doi` | Identifiant non conforme, aucun appel réseau effectué | non ; la vérification bibliographique traite ce défaut |

Plusieurs marqueurs d'un même titre comptent comme **une famille**. Une relation
Crossref `update-to` pointe d'un avis vers l'article visé ; elle ne suffit **pas** à
conclure que le DOI de l'avis lui-même est rétracté. Les directions sont conservées.

## 3. Cache utilisé par l'audit

`integrity` écrit `output/integrity.{json,md}`. La porte `G-integrity` de `audit`
ne reprend le JSON que si son empreinte SHA-256 correspond à **la bibliographie
actuelle**, si le schéma est reconnu et si le rapport a moins de **24 heures**.
Sinon, elle refait le contrôle hors ligne et l'indique. Le rapport Markdown est régénéré.

La porte d'intégrité ne déclenche pas elle-même de requêtes réseau. L'option
`audit --online` active séparément la résolution Crossref de `G-references`.

## 4. Protocole humain

1. Lire l'avis sur la page de l'éditeur, pas seulement dans une base.
2. Repérer la phrase du manuscrit qui s'appuie sur l'article.
3. Retirer, remplacer, ou discuter explicitement la référence — avec justification.
4. Conserver la date du contrôle et refaire celui-ci avant soumission.

## 5. Limites

Ce module ne détecte ni la fraude, ni les images manipulées, ni le p-hacking. Il ne
juge pas le bien-fondé d'un résultat et ne sait pas si la phrase citante repose sur
la partie rétractée. Les versions sans DOI ne sont pas contrôlées en ligne. Il ne
s'agit pas d'un avis juridique ou éditorial ; une décision exige une lecture humaine.
