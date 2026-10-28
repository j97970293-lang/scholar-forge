# ScholarForge 1.1.0 — lisez-moi (FR)

**Une seule skill académique pour tout le cycle de recherche, de la question à la soumission.**

- Dépôt GitHub privé : https://github.com/j97970293-lang/scholar-forge
- Dossier Drive : https://drive.google.com/drive/folders/1Rx4AZEyIdm_3EGegllAhNm4nJ1tmQdRt
- Version : **1.1.0** — 28 octobre 2026
- État : **70/70 tests**, spec Agent Skills **PASS**, audit propre **PASS (7/8 portes)**,
  aucun secret dans les fichiers, dépôt privé,Drive synchronisé.

---

## 1. Ce que c'est

Vous aviez huit dépôts de skills académiques dispersés. La 1.0.0 les a fusionnés en une
seule skill. La 1.1.0 ajoute une recherche documentaire datée (2025–2026), six dépôts
complémentaires, la conformité à la spécification ouverte **Agent Skills**, et quatre
contrôles qui manquaient : détection des rétractations, journal de recherche PRISMA-S,
routage des directives de rapport et déclaration structurée de l'usage de l'IA.

**14 dépôts lus · 16 694 fichiers / 2,71 M de lignes scannés · 5 460 entrées de registre ·
28 playbooks · 21 commandes · 8 portes d'audit · 18 cas d'évaluation.**

## 2. Installation en 30 secondes

```bash
# Dézipper l'archive complète, puis :
cd scholar-forge
bash install.sh --target ~/.claude/skills/scholar-forge
python3 scripts/scholarforge.py doctor
python3 scripts/scholarforge.py validate
python3 scripts/scholarforge.py selftest
```

Aucune dépendance, aucune clé API, aucun build. Python 3.9+ standard uniquement.
`install.sh` copie un dossier allégé (le moteur, les playbooks et les données) ; le dépôt
complet reste disponible pour la traçabilité. Le dossier cible doit s'appeler exactement
`scholar-forge` — c'est une exigence de la spec.

## 3. Premier projet

```bash
python3 scripts/scholarforge.py init --path ~/papers/mon-etude --name "Mon étude"
cd ~/papers/mon-etude
python3 scripts/scholarforge.py search "RNA velocity benchmarking" \
    --sources openalex,crossref,pubmed --limit 30 --from-year 2020 --log-path .
python3 scripts/scholarforge.py searchlog                 # journal PRISMA-S
python3 scripts/scholarforge.py integrity references.bib --online
python3 scripts/scholarforge.py guideline --recommend "diagnostic accuracy of an AI test"
python3 scripts/scholarforge.py disclosure --tool "…" --tool-version "…" --purpose writing
python3 scripts/scholarforge.py audit
```

Démo complète et reproductible (échec volontaire puis version corrigée) :

```bash
bash examples/end-to-end/run-demo.sh          # FAIL (4/8 portes)
bash examples/end-to-end/run-demo.sh --fixed  # PASS (7/8 portes)
```

## 4. Les cinq nouveautés de la 1.1.0

| Nouveauté | Pourquoi | Commande |
|---|---|---|
| **Intégrité des références** | Un DOI qui résout peut être celui d'un article rétracté. OpenAlex et Crossref ne sont pas d'accord entre eux. Trois signaux sont croisés ; deux signaux concordants sont nécessaires pour un blocage. | `integrity --online` |
| **Journal PRISMA-S** | La porte G2 promettait « every query logged » sans jamais écrire le journal. Chaque recherche ajoute maintenant une ligne par base, avec filtres appliqués/ignorés et URL d'API. | `search`, `searchlog` |
| **Directives 2024–2026** | TRIPOD+AI remplace TRIPOD 2015 ; STARD-AI (2025) a été corrigé en juillet 2026. 18 directives datées avec URL officielle. | `guideline` |
| **Déclaration IA** | COPE/ICMJE exigent outil + version + finalité + supervision humaine ; une IA n'est jamais auteur. 9 catégories de délégation, lint déterministe. | `disclosure`, `disclosure --check` |
| **Conformité Agent Skills** | La 1.0.0 avait une description de 1 041 caractères (limite : 1 024). Elle fait maintenant 889 ; les métadonnées sont des chaînes ; les références sont à un seul niveau. | `validate` |

## 5. Où trouver quoi

| Besoin | Fichier |
|---|---|
| Le point d'entrée de la skill | `SKILL.md` |
| Guide complet en français | `docs/USAGE.md` |
| Journal de la recherche 2026 (sources primaires) | `docs/RESEARCH_NOTES.md` |
| Questions fréquentes | `docs/FAQ.md` |
| Ce qui a été lu dans les 14 dépôts | `docs/SOURCE_MAP.md`, `docs/SCAN_REPORT.md`, `docs/SCAN_REPORT_V2.md` |
| Provenance et licences | `NOTICE.md`, `upstream/LICENSES.md`, `upstream/manifest.json`, `upstream/v2/manifest.json` |
| Règles modifiables sans coder | `config/*.json` |
| Playbooks (chargés à la demande) | `references/01`…`references/28` |
| Historique des versions | `CHANGELOG.md` |
| Skill seule, prête à installer | `scholar-forge-skill.zip` (dans le dossier Drive) |

## 6. Limites à ne pas oublier

- L'outil vérifie le manuscrit et le **processus déclaré** ; il ne peut pas prouver que les
  expériences ont eu lieu, que les données brutes sont authentiques ou que les résultats se
  reproduisent.
- Un résultat « aucune notice trouvée » n'est **pas** une preuve d'intégrité : les registres
  de rétractation divergent et peuvent être en retard.
- Les checklists générées sont des **aides de travail abrégées**, pas les items officiels.
  Relisez l'énoncé officiel et les instructions aux auteurs le jour de la soumission.
- `--oa-only` signifie « quand l'information est connue » : une source dont le statut OA est
  inconnu n'est pas exclue.
- Licence : code original MIT, mais compilation réservée à un **usage non commercial**
  (une source est CC BY-NC 4.0, trois n'ont pas de licence explicite).

---

*Généré le 2026-10-28 · aucune clé ni jeton n'est stocké dans cette archive.*
