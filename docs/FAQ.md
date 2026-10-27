# FAQ

**Pourquoi une seule skill et pas un pack de 200 skills ?**
Parce que 3 244 `SKILL.md` concurrents créent des conflits de routage et saturent le contexte.
ScholarForge garde un point d'entrée et charge ses 22 playbooks à la demande. Les skills très
spécialisées restent accessibles via le registre et les archives.

**Est-ce que j'ai perdu du code des dépôts d'origine ?**
Non. `upstream/*.zip` contient les 15 314 fichiers (hors `.git`) avec un manifeste de commits
et d'empreintes SHA-256. `data/scan-inventory.json` indexe les 15 254 fichiers scannés.

**Puis-je utiliser ce dépôt commercialement ?**
Non, pas en l'état : `Imbad0202/academic-research-skills` est sous CC BY-NC 4.0 et deux dépôts
n'ont pas de licence. Voir `LICENSE` et `NOTICE.md`.

**Faut-il des clés API ?**
Non. Les six API fonctionnent sans clé. Des variables optionnelles (`OPENALEX_API_KEY`,
`S2_API_KEY`, `NCBI_API_KEY`) augmentent les limites de débit.

**Que se passe-t-il sans Internet ?**
Tout fonctionne sauf `search` et `verify --online`. Les rapports indiquent explicitement le
mode hors ligne ; aucune métadonnée n'est inventée pour combler le vide.

**Est-ce que l'outil vérifie que mes expériences sont vraies ?**
Non. Il vérifie la cohérence interne du manuscrit et du processus déclaré. Un travail fabriqué
mais rapporté de façon cohérente peut passer. La responsabilité reste humaine.

**Comment ajouter ma discipline ?**
Ajoutez vos clichés dans `config/rules.json`, votre venue dans `config/venues.json`, votre
guide de rapport dans `config/reporting-guidelines.json`, votre API dans `sf/sources.py`.
Puis `selftest` et `doctor`.

**Comment citer ce dépôt ?**
`CITATION.cff` est fourni. Citez aussi les huit dépôts amont listés dans `NOTICE.md`.

**Où sont les résultats des tests ?**
`python3 scripts/scholarforge.py selftest` (30 tests). Les rapports d'un projet sont dans
`output/`. La démo : `bash examples/end-to-end/run-demo.sh`.
