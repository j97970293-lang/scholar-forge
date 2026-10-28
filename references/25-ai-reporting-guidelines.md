# 25 — Directives de rapport à l'ère de l'IA (état 2026)

**Règle de péremption.** Les règles de revue changent. Relisez les instructions
officielles aux auteurs **le jour de la soumission**. Ce playbook sert à choisir la
bonne directive, pas à la remplacer. Les checklists du CLI sont des **aides de
travail abrégées**, pas la reproduction officielle des items.

## 1. Tableau de sélection

| Votre étude | Directive | Année | À combiner avec |
|---|---|---|---|
| Essai randomisé d'une intervention avec IA — résultats | **CONSORT-AI** (14 items additionnels) | 2020 | CONSORT 2025 |
| Essai randomisé avec IA — protocole | **SPIRIT-AI** | 2020 | SPIRIT 2025 |
| Développement/validation d'un modèle prédictif (régression ou ML) | **TRIPOD+AI** (27 items + abstract) | 2024 | — |
| Étude utilisant un LLM pour une tâche clinique | **TRIPOD-LLM** (PMID 39779929) | 2025 | TRIPOD+AI |
| Exactitude diagnostique d'un test basé sur l'IA | **STARD-AI** | 2025 (corrigé le 13/07/2026) | — |
| IA en imagerie médicale | **CLAIM** | mise à jour 2024 | — |
| Évaluation clinique précoce en conditions réelles d'un outil d'aide à la décision | **DECIDE-AI** | 2022 | — |
| Revue systématique / méta-analyse | **PRISMA 2020** | 2020 | PRISMA-S, AMSTAR 2 |
| Stratégie de recherche documentaire | **PRISMA-S** | 2021 | — |
| Essai randomisé (hors IA) | CONSORT 2025 | 2025 | — |
| Protocole d'essai (hors IA) | SPIRIT 2025 | 2025 | — |
| Étude observationnelle | STROBE | — | ROBINS-I |
| Recherche qualitative | COREQ / SRQR | — | ENTREQ pour la synthèse |
| Recherche animale | ARRIVE 2.0 | 2020 | — |
| Article ML (conférence) | Checklist de reproductibilité NeurIPS/ICLR/ACL | — | — |
| Évaluation économique | CHEERS 2022 | 2022 | — |
| **Tout manuscrit ayant utilisé une IA générative** | **déclaration d'usage IA** | — | playbook 26 |

## 2. Points de vigilance par directive

**TRIPOD+AI** remplace TRIPOD 2015 (qui ne doit plus être utilisé). Points souvent
oubliés : justification de la taille d'échantillon **par jeu de données**, gestion
des données manquantes et du pré-traitement, fuite d'information entre
entraînement et test, calibration (pas seulement l'AUC), validation externe,
versionnage du modèle, équité / inégalités de santé, disponibilité du code.

**STARD-AI** (Nature Medicine, 15 septembre 2025 ; auteur · correction le 13 juillet
2026). Points les plus souvent omis : définition du standard de référence,
partitionnement des données et contrôle des fuites, choix du seuil (et s'il était
pré-spécifié), et surtout **le décompte des sorties indéterminées, manquantes ou en
échec du modèle**. Utilisez la version corrigée.

**CONSORT-AI / SPIRIT-AI** ajoutent la description de l'intervention IA, les
compétences requises, les données d'entrée et leur qualité, l'interaction
humain–IA, l'analyse des cas d'erreur, et la version du modèle réellement évaluée
par rapport à celle du protocole. CONSORT 2025 et SPIRIT 2025 intègrent la science
ouverte mais **pas** d'items IA spécifiques : les deux documents se complètent.

**DECIDE-AI** couvre l'évaluation formative en conditions réelles : facteurs humains,
sécurité, incidents et évitements de justesse, changements de flux de travail.

**PRISMA-S** exige la chaîne de recherche complète par base, l'interface exacte,
la date, les limites et les comptages avant/après déduplication. C'est exactement
ce que `search --log` / `sources/search-log.md` produit (playbook 27).

## 3. Utiliser le CLI

```bash
scholarforge guideline --list
scholarforge guideline --recommend "diagnostic accuracy of an AI test"
scholarforge guideline --recommend "trial protocol for an AI intervention"
scholarforge guideline --key prediction-model --title "Mon étude" --venue "BMJ" \
    --out submission/checklist.md
```

Le routeur est volontairement simple (mots-clés). Il **suggère** ; un humain
choisit. Le document généré contient l'URL officielle, l'année, les éventuelles
directives remplacées, et une case « relire les règles le jour de la soumission ».

## 4. Outils d'évaluation du risque de biais

| Contexte | Outil |
|---|---|
| Essai randomisé | RoB 2 |
| Étude non randomisée | ROBINS-I |
| Exactitude diagnostique | QUADAS-2 (variantes QUADAS-AI en cours) |
| Modèle prédictif | PROBAST / PROBAST+AI |
| Revue systématique | AMSTAR 2 |
| Certitude globale | GRADE (high / moderate / low / very low) |

## 5. Sources primaires

- EQUATOR Network : `https://www.equator-network.org/reporting-guidelines/`
- TRIPOD+AI (BMJ 2024, PMC11019967) : `https://pmc.ncbi.nlm.nih.gov/articles/PMC11019967/`
- STARD-AI (Nature Medicine 2025) : `https://www.nature.com/articles/s41591-025-03953-8`
- CONSORT-AI (Nature Medicine 2020) : `https://www.nature.com/articles/s41591-020-1034-x`
- TRIPOD-LLM : `https://pubmed.ncbi.nlm.nih.gov/39779929/`
- Vue de sélection : `https://casrai.org/guides/ai-reporting-guidelines-consort-ai-tripod-ai-decide-ai`
