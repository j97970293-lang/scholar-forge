# Notes de recherche — 28 octobre 2026

Journal des sources et décisions ayant conduit à **ScholarForge 1.1.0**. Les liens
sont des références documentaires, pas des instructions à exécuter. La recherche
ne garantit ni une couverture exhaustive, ni la pérennité des politiques citées.

## 1. Agent Skills : conformité vérifiable

Source primaire relue : `https://agentskills.io/specification`.
Guide d'écriture : `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`.

| Exigence / recommandation | Défaut trouvé ou décision |
|---|---|
| `description` : 1–1024 caractères | La v1 faisait 1041 caractères ; réécrite à **889** |
| `metadata` : chaînes vers chaînes | Compteurs désormais quotés ; le validateur refuse les nombres et booléens YAML non quotés |
| `name` : 1–64 caractères, kebab-case, identique au dossier | `scholar-forge` ; contrôle automatique |
| Corps recommandé <500 lignes / ~5000 tokens | Instructions détaillées déportées dans 28 playbooks |
| Références directes, éviter les chaînes imbriquées | Index des playbooks dans `SKILL.md` |
| `allowed-tools` expérimental | Jamais indispensable au fonctionnement du CLI |

**Livré :** `sf/spec.py`, `tools/validate_skill.py`, `validate`, CI, playbook 23.
Le parseur stdlib accepte un **sous-ensemble explicite** du YAML ; les scalaires
multilignes non pris en charge sont refusés, pas validés à tort. Pour un frontmatter
YAML général, la bibliothèque officielle `skills-ref` reste la référence. Les
contrôles de taille du corps et d'organisation sont des recommandations de qualité,
pas une extension des champs obligatoires de la spécification.

## 2. Intégrité : corroborer les signaux, lire les notices

Sources primaires :
- OpenAlex work object : `https://docs.openalex.org/api-entities/works/work-object`
- Crossref REST : `https://api.crossref.org/works/{doi}`
- Hauschke et Nazarovets, préprint 2024, article 2025 :
  `https://arxiv.org/abs/2403.13339`, DOI `10.1177/01655515251322478`.
  L'étude documente des erreurs de classement dans OpenAlex pour une période
  **historique** précise ; elle ne mesure pas le taux d'erreur de la base actuelle.

Contrôle empirique effectué sur `10.1016/S0140-6736(97)11096-0` : OpenAlex
signalait une rétractation, Crossref exposait des notices `updated-by` de correction
et de rétractation, et le titre portait un marqueur explicite. Le module ne déduit
jamais de l'absence de notice qu'une publication est intègre.

**Livré :** `sf/integrity.py`, `integrity`, `G-integrity`, playbook 24. Trois familles
(titre, OpenAlex, Crossref), dédoublonnées. **Elles ne sont pas totalement
indépendantes** : les registres peuvent partager Retraction Watch. Un signal isolé
reste suspecté ; un préfixe `RETRACTED`/`WITHDRAWN` provoque toutefois un arrêt de
précaution. Le verdict `retracted-confirmed` signifie « signaux corroborés », pas
confirmation éditoriale définitive.

Durcissement final : distinction des relations entrantes et `update-to` sortantes,
références sans DOI affichées « non contrôlées », cache lié à la bibliographie par
SHA-256 et limité à 24 h. `audit --online` conserve sa résolution Crossref ; la
porte d'intégrité elle-même consomme un cache ou refait uniquement le scan des titres.

Les statistiques de comparaison entre registres trouvées uniquement dans des
sources secondaires n'ont pas été retenues comme seuils ou faits dans le moteur.

## 3. Directives de rapport : versionner et relier à l'original

| Directive | Source vérifiable | Utilisation locale |
|---|---|---|
| TRIPOD+AI, 2024 | `https://pmc.ncbi.nlm.nih.gov/articles/PMC11019967/` ; DOI `10.1136/bmj-2023-078378` | Modèles de prédiction ; remplace TRIPOD 2015 |
| STARD-AI, 2025 | `https://www.nature.com/articles/s41591-025-03953-8` | Exactitude diagnostique IA ; la page signale une correction du **13 juillet 2026**, DOI `10.1038/s41591-026-04570-9` |
| TRIPOD-LLM, 2025 | [1](https://www.nature.com/articles/s41591-024-03425-5) ; PMID 39779929 | Études de LLM en biomédecine |
| CLAIM, mise à jour 2024 | [1](https://pubs.rsna.org/doi/full/10.1148/ryai.240300) ; PMID 38809149 | Imagerie médicale ; ancien lien PubMed incorrect remplacé |
| CONSORT-AI, 2020 | `https://www.nature.com/articles/s41591-020-1034-x` | Extension pour les essais d'interventions IA |
| Autres directives | `https://www.equator-network.org/reporting-guidelines/` | PRISMA, PRISMA-S, STROBE, SPIRIT, CARE, COREQ, etc. |

**Livré :** `config/reporting-guidelines.json` (18 entrées), `sf/guidelines.py`,
`guideline --list/--recommend/--key`, playbook 25. Les listes produites sont des
**aides de travail originales et abrégées**, jamais une copie revendiquée des
checklists officielles. Le routeur utilise des mots-clés : il aide au choix sans
remplacer le protocole, les consignes du journal ou le jugement méthodologique.

## 4. Déclaration IA : tâches déléguées et responsabilité humaine

Sources :
- COPE : `https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools`.
  La position indique qu'une IA ne peut être auteur, que l'outil et son usage doivent
  être déclarés en Materials and Methods ou équivalent, et que les humains restent
  responsables du manuscrit.
- ICMJE : `https://www.icmje.org/icmje-recommendations.pdf`.
- Nature : `https://www.nature.com/nature-portfolio/editorial-policies/ai-policy`.
- GAIDeT : `https://doi.org/10.1080/08989621.2025.2544331`.
  Métadonnées Crossref contrôlées : titre « GAIDeT (Generative AI Delegation Taxonomy):
  A taxonomy for humans to delegate tasks to generative artificial intelligence in
  scientific research and publishing » ; publication en ligne le 8 août 2025,
  volume imprimé 2026.

**Livré :** neuf **catégories locales** inspirées de la notion de délégation,
non reproduction de la taxonomie GAIDeT ; `disclosure`, template, `--check`,
playbook 26. Le linter refuse les placeholders et les champs non remplis ; il
n'atteste pas que la déclaration est vraie ni conforme à chaque politique éditoriale.
Une déclaration explicite de non-usage est une alternative valide. CRediT est
réservé aux personnes. La porte `G-disclosures` contrôle maintenant aussi la
complétude de la déclaration IA, et non sa seule existence.

Une affirmation secondaire concernant un ajout supposé aux motifs de rétractation
COPE en août 2025 n'a pas été confirmée sur une source primaire et est **écartée**.

## 5. Recherche documentaire : traçabilité ≠ exhaustivité

PRISMA-S : `https://www.equator-network.org/reporting-guidelines/prisma-s/`.

La v1 promettait un journal de recherche mais n'en écrivait pas. `searchlog` et
`sf/searchlog.py` enregistrent maintenant une ligne par base et par requête : chaîne
complète, interface, date UTC, restrictions, URL exacte et nombre de notices
**récupérées**. Le JSON conserve les filtres natifs, locaux, non pris en charge
nativement et les métadonnées inconnues. Le Markdown conserve toutes les lignes
antérieures ; un historique JSON corrompu n'est jamais réinitialisé silencieusement.

Limite essentielle : les clients interrogent une **fenêtre bornée** (plafond propre
à chaque API, souvent 50 notices), sans pagination exhaustive. Les comptes ne sont
**pas** les totaux de résultats des bases. Le journal facilite PRISMA-S mais ne
suffit pas à déclarer une revue systématique exhaustive ou conforme. Les filtres
locaux retiennent les notices dont les métadonnées nécessaires sont inconnues,
y compris le statut OA. Ces limites sont documentées dans le playbook 27.

## 6. Six dépôts complémentaires : provenance, licences, intégration

Clones consultés en lecture seule ; commits exacts et SHA-256 des archives dans
`upstream/v2/manifest.json`. Aucun code de ces dépôts n'est exécuté par le moteur.

| Dépôt | Rôle retenu | Licence constatée / portée |
|---|---|---|
| `https://github.com/agentskills/agentskills` | Spec et `skills-ref` | Apache-2.0 à la racine ; documents avec licence propre conservée |
| `https://github.com/anthropics/skills` | Exemples de skills et structuration progressive | **Licences par skill** ; pas de licence globale unique présumée |
| `https://github.com/chrisyangsong/citegate` | Modèle de contrôle de citations en CI | MIT |
| `https://github.com/asreview/asreview` | Priorisation du criblage par apprentissage actif | Apache-2.0 |
| `https://github.com/manubot/manubot` | Manuscrits et citations par identifiant | BSD-2-Clause-Patent |
| `https://github.com/Future-House/paper-qa` | QA sur preuves documentaires | Apache-2.0 à la racine ; sous-paquets avec licences conservées |

**Résultat :** 1440 fichiers inventoriés, 6 archives **curées** (1034 fichiers
conservés, exclusions décrites), 26 entrées supplémentaires de registre. Les 8
archives v1 restent intégrales selon leur politique initiale. Le statut « vérifié »
du registre signifie ici présence et provenance relevées, **pas** audit de sécurité,
validation scientifique ou garantie de droits pour tous les usages.

Aucun module ASReview, Manubot ou PaperQA n'est embarqué dans le runtime : les
méthodes sont documentées et les outils référencés sans imposer leurs dépendances.
Le code des modules ScholarForge est original. Les termes de chaque source restent
applicables ; la compilation conserve sa restriction non commerciale liée à une
source v1 sous CC BY-NC 4.0.

## 7. Vérification et limites de cette passe

- **100 tests déterministes** : historique, cache périmé/modifié, sens des relations,
  pureté des sorties JSON, filtres, déclarations, métadonnées YAML et grammaire Python 3.9.
- Démonstration négative : FAIL attendu ; démonstration corrigée : PASS (7/8 portes,
  `G-pipeline` restant consultative à S0).
- Recherche en ligne et DOI de rétractation exercés séparément ; la CI hors ligne
  ne transforme pas une panne réseau en preuve de validité.
- Pas de benchmark LLM exécuté : les 18 scénarios de `evals/` sont des cas de
  conformité documentés, pas des scores de performance mesurés.
- Pas d'audit juridique ni de vérification des politiques de chaque éditeur.
  La validation des expériences, des données et de la soumission reste humaine.
