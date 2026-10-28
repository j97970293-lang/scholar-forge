# 26 — Déclarer l'usage de l'IA : taxonomie de délégation

**Deux principes stabilisés** (COPE, ICMJE, Nature, Wiley, Cambridge, WAME,
JAMA — positions convergentes depuis 2023, réaffirmées depuis) :

1. **Une IA ne peut pas être auteur.** Elle n'est pas une entité juridique, ne peut
   pas assumer la responsabilité du travail, déclarer un conflit d'intérêts, gérer
   un accord de copyright ni approuver la version finale.
2. **Tout usage substantiel doit être divulgué**, en nommant l'outil **et sa
   version**, et en décrivant **ce pour quoi** il a servi — généralement dans la
   section Methods (ou équivalent), souvent aussi dans les remerciements et la
   lettre d'accompagnement.

Les auteurs humains restent **entièrement responsables** de chaque affirmation,
citation, figure et de la décision de soumettre.

## 1. Pourquoi une déclaration structurée

La déclaration générique « AI was used » ne dit rien de contrôlable. La taxonomie
**GAIDeT** (Generative AI Delegation Taxonomy, 2025,
DOI `10.1080/08989621.2025.2544331`) propose de décrire **ce qui a été délégué** et
**sous quelle supervision**. Le Scholarly Kitchen, à la suite du forum COPE 2025,
résume le déplacement : on passe de la « détection de texte IA » à la vérification
du respect des règles de déclaration, avec une supervision humaine sur les données,
les citations, la méthode et l'analyse critique.

## 2. Neuf catégories de délégation (config `ai-disclosure.json`)

| Clé | Délégué | Vérification humaine minimale |
|---|---|---|
| `ideation` | question, hypothèses, design concurrent | l'auteur nommé arrête la question et le design ; les suggestions IA ne sont pas des preuves |
| `search` | expansion de synonymes, traduction de requêtes | journaliser chaque requête finale (PRISMA-S) |
| `screening` | priorisation, classement par apprentissage actif | double criblage humain + arbitrage + κ |
| `extraction` | tables d'extraction, codes | vérifier chaque valeur sur le texte source et conserver la citation/localisateur |
| `analysis` | scripts, débogage, explication de sorties | relancer depuis les données brutes ; archiver code, environnement, graines |
| `writing` | premiers jets de sections | réécrire dans la voix des auteurs ; lier chaque assertion au registre des preuves |
| `editing` | correction linguistique, mise en forme | confirmer qu'aucun sens n'a changé ; souvent exempté par les revues |
| `translation` | traduction d'abrégés ou d'instruments | révision bilingue ou rétro-traduction |
| `figures` | code de tracé, mise en page | **jamais** générer ni modifier des images de recherche originales ; vérifier chaque nombre |

Les rôles CRediT (Conceptualisation, Methodologie, Validation, Rédaction, etc.)
s'attribuent **à des personnes**, jamais à l'outil.

## 3. Ce que fait le CLI

```bash
scholarforge disclosure \
  --tool "Claude Sonnet 4.5" --tool-version "2026-09-29" \
  --purpose search,writing,editing \
  --oversight "Dr X a relu et vérifié chaque affirmation" \
  --verification "Crossref + registre preuves/affirmations" \
  --prompts "Annexe B, jeux de consignes archivés" \
  --policy-date 2026-10-28 --venue "Nature" --title "Mon étude" \
  --out submission/ai-disclosure.md

scholarforge disclosure --check submission/ai-disclosure.md
```

`--check` vérifie cinq champs structurels : outil, version/date d'accès, finalité,
supervision humaine, absence de statut d'auteur pour l'IA. Il détecte aussi les
placeholders non remplis et les formulations qui créditeraient l'IA comme auteur.
Il ne vérifie **pas** la politique de votre revue : c'est une tâche humaine.

## 4. Modèle de paragraphe (à adapter, jamais à copier aveuglément)

> During the preparation of this work the author(s) used **[outil, version]** for
> **[finalité précise]**. After using this tool/service, the author(s) reviewed and
> edited the content as needed and take(s) full responsibility for the content of
> the publication. No AI tool is listed as an author.

Ajoutez : la date d'accès, le degré de supervision, où trouver les consignes et le
code, et la politique de la revue consultée le jour de la soumission.

## 5. Risques concrets

- Plusieurs éditeurs considèrent l'absence de déclaration comme un manquement
  éthique pouvant justifier une correction, une expression d'inquiétude ou une
  rétractation. Vérifiez toujours la version courante de la politique.
- Les éditeurs et relecteurs ne doivent pas téléverser de manuscrit confidentiel
  dans un service qui s'entraîne sur les entrées.
- Une IA ne doit pas produire ni altérer des images de données originales
  (blots, radiographies, mesures, photos).
- Une déclaration vague (« AI was used for writing ») ne satisfait généralement
  pas l'exigence de précision.

## 6. Sources primaires

- COPE, « Authorship and AI tools » : `https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools`
- ICMJE Recommendations : `https://www.icmje.org/icmje-recommendations.pdf`
- Nature Portfolio AI policy : `https://www.nature.com/nature-portfolio/editorial-policies/ai-policy`
- GAIDeT : `https://doi.org/10.1080/08989621.2025.2544331`
- COPE forum (Scholarly Kitchen, 2025) : `https://scholarlykitchen.sspnet.org/2025/08/25/from-detection-to-disclosure-key-takeaways-on-ai-ethics-from-copes-forum/`
- CASRAI, « Can AI be listed as an author? » : `https://casrai.org/guides/can-ai-be-listed-as-an-author`
- Wolters Kluwer, author AI policy : `https://www.wolterskluwer.com/en/solutions/lippincott-journals/lippincott-journals-ethical-best-practices-in-scholarly-publishing`
