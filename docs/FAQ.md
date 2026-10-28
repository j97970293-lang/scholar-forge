# FAQ

**Pourquoi une seule skill et pas un pack de 200 skills ?**
Parce que 3 244 `SKILL.md` concurrents créent des conflits de routage et saturent le contexte.
ScholarForge garde un point d'entrée et charge ses 28 playbooks à la demande. Les skills très
spécialisées restent accessibles via le registre (5 460 entrées) et les archives.

**Est-ce que j'ai perdu du code des dépôts d'origine ?**
Non, mais il faut distinguer deux niveaux. Les 8 dépôts v1 sont conservés **intégralement**
dans `upstream/*.zip` (15 314 fichiers, manifeste de commits et SHA-256). Les 6 dépôts v2 sont
conservés sous forme d'**instantanés curés** dans `upstream/v2/*.zip` (1 034 fichiers ; tests,
caches, binaires >2 Mio exclus, exclusions comptabilisées). `data/scan-inventory.json` et
`data/scan-v2-inventory.json` indexent l'ensemble des 16 694 fichiers lus.

**La skill est-elle conforme à la spécification Agent Skills ?**
Oui depuis la 1.1.0 : `validate` vérifie `name` (kebab-case, identique au dossier),
`description` ≤ 1024 caractères, `metadata` en chaînes, corps < 500 lignes, références à un
niveau et liens résolus. La 1.0.0 avait une description de 1 041 caractères, donc hors spec.
Voir le playbook 23.

**Pourquoi faut-il 2 signaux pour déclarer une rétractation ?**
Parce que les registres divergent. OpenAlex expose un booléen `is_retracted` unique qui a déjà
étiqueté à tort des corrections comme rétractations et qui en manque d'autres ; Crossref expose
les notices `updated-by` issues de Retraction Watch. Le titre de l'éditeur est un troisième
signal. Un signal isolé est « suspecté » et non bloquant ; deux signaux convergents déclenchent
`retracted-confirmed`. Aucun verdict n'est définitif : il faut lire l'avis sur la page de
l'éditeur. Voir le playbook 24 et `docs/RESEARCH_NOTES.md`.

**Le journal de recherche est-il automatique ?**
Oui. Chaque appel à `search` ajoute une ligne par base dans `sources/search-log.md` et dans
`sources/search-log.json` (chaîne, date UTC, filtres demandés/appliqués/ignorés, URL d'API,
hits, version du CLI). `--no-log` le désactive ; `--log-path` choisit le projet. `searchlog`
affiche la synthèse. Les filtres appliqués localement n'agissent que sur la fenêtre récupérée :
augmentez `--limit` quand vous filtrez. Voir le playbook 27.

**Les checklists du CLI sont-elles les vraies checklists officielles ?**
Non, et c'est volontaire. Ce sont des **aides de travail abrégées** classées par domaine de
rapport. Chaque document généré renvoie à l'énoncé officiel, précise l'année, les éventuelles
directives remplacées, et rappelle de relire les règles le jour de la soumission. TRIPOD+AI
(2024) remplace TRIPOD 2015 ; STARD-AI (2025) a été corrigé en juillet 2026. Voir le
playbook 25.

**Comment déclarer l'usage de l'IA ?**
`disclosure` génère une déclaration structurée : outil, version/date, 9 catégories de
délégation possibles, supervision humaine, vérification, disponibilité des consignes, rôles
CRediT **humains**. `disclosure --check` vérifie les cinq champs structurels requis. L'IA
n'est jamais auteur (positions COPE/ICMJE). La politique de la revue doit être relue le jour
de la soumission. Voir le playbook 26.

**Puis-je utiliser ce dépôt commercialement ?**
Non, pas en l'état : `Imbad0202/academic-research-skills` est sous CC BY-NC 4.0 et trois
sources n'ont pas de licence explicite. Voir `LICENSE`, `NOTICE.md` et
`upstream/LICENSES.md`.

**Faut-il des clés API ?**
Non. Les six API savantes fonctionnent sans clé. Des variables optionnelles
(`OPENALEX_API_KEY`, `S2_API_KEY`, `NCBI_API_KEY`) augmentent les limites de débit.

**Que se passe-t-il sans Internet ?**
Tout fonctionne sauf `search`, `verify --online` et `integrity --online`. Les rapports
indiquent explicitement le mode hors ligne ; aucune métadonnée n'inventée pour combler le vide.
`integrity` continue de détecter les marqueurs de titre (`RETRACTED:`, `WITHDRAWN:`),
et `audit` ne déclenche jamais de rafale réseau : il lit le rapport mis en cache par
`integrity --online`.

**Est-ce que l'outil vérifie que mes expériences sont vraies ?**
Non. Il vérifie la cohérence interne du manuscrit et du processus déclaré. Un travail fabriqué
mais rapporté de façon cohérente peut passer les 8 portes. La responsabilité reste humaine.

**Comment ajouter ma discipline ?**
Ajoutez vos clichés dans `config/rules.json`, votre venue dans `config/venues.json`, votre
guide de rapport dans `config/reporting-guidelines.json`, vos catégories de délégation dans
`config/ai-disclosure.json`, votre API dans `sf/sources.py`. Puis `selftest`, `doctor` et
`validate`.

**Comment citer ce dépôt ?**
`CITATION.cff` est fourni (version 1.1.0). Citez aussi les quatorze dépôts amont listés dans
`NOTICE.md`.

**Où sont les résultats des tests ?**
`python3 scripts/scholarforge.py selftest` (70 tests). `validate` vérifie la spec. Les rapports
d'un projet sont dans `output/`. La démo : `bash examples/end-to-end/run-demo.sh --fixed`.
