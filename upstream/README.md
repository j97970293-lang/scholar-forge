# upstream/ — archives sources complètes

Chaque ZIP contient **tous les fichiers** du clone d'origine (hors internals Git, caches et
fichiers `.pyc`), sans aucune suppression de contenu. Ce sont des **données inertes** :
ScholarForge n'exécute jamais de code provenant de ces archives.

`manifest.json` donne, pour chaque dépôt : URL, licence, rôle, commit exact, nombre de
fichiers, tailles brute/compressée et empreinte SHA-256 de l'archive.

| Archive | Fichiers | Taille | Licence |
|---|---:|---:|---|
| O0000-code_awesome-academic-skills.zip | 278 | 834 KB | CC0-1.0 |
| cosen1024_awesome-academic-skills.zip | 15 | 49 KB | MIT |
| kael-odin_awesome-academic-research-skills.zip | 99 | 1.5 MB | MIT |
| miketepUR_awesome-claude-skills.zip | 12 | 20 KB | MIT |
| Imbad0202_academic-research-skills.zip | 2857 | 14.4 MB | CC BY-NC 4.0 |
| KalarisLabs_research-agent-skills.zip | 3186 | 14.6 MB | MIT |
| saintgo7_agents-skills.zip | 82 | 207 KB | non licencié |
| ranbot-ai_awesome-skills.zip | 8785 | 21.7 MB | non licencié |

**Total : 15 314 fichiers / 53,3 Mo d'archives.** L'inventaire fichier par fichier (avec
SHA-256) est dans `data/scan-inventory.json`.

Vérifier une archive :
```bash
sha256sum upstream/*.zip
python3 -c "import json;print(json.dumps(json.load(open('upstream/manifest.json'))['repositories'],indent=2))"
```

Rejouer la création des archives :
```bash
SF_SOURCES=/chemin/vers/les/clones python3 tools/package_upstream.py
```


---

## v2/ — six instantanés curés (2026-10-28)

**Différence importante :** les 8 archives ci-dessus sont intégrales. Les 6 archives de
`v2/` sont des **instantanés curés** : suites de tests, caches, fichiers binaires et
fichiers de plus de 2 Mio sont exclus. Chaque exclusion est comptabilisée dans
`v2/manifest.json`. Ce choix garde le dépôt léger (4,6 Mio au lieu de ~64 Mio) sans
prétendre à l'exhaustivité.

| Archive v2 | Fichiers inclus | Exclus | Taille | Licence |
|---|---:|---:|---:|---|
| agentskills_agentskills.zip | 127 | 11 | 426 Kio | Apache-2.0 |
| anthropics_skills.zip | 389 | 56 | 1.5 Mio | mixte, par skill |
| chrisyangsong_citegate.zip | 15 | 4 | 20 Kio | MIT |
| asreview_asreview.zip | 337 | 142 | 1.4 Mio | Apache-2.0 |
| manubot_manubot.zip | 72 | 103 | 209 Kio | BSD-2-Clause-Patent |
| Future-House_paper-qa.zip | 94 | 90 | 1.1 Mio | Apache-2.0 |

**Total v2 : 1 034 fichiers / 4,6 Mio.** Rapport de scan : `docs/SCAN_REPORT_V2.md`.
Inventaire : `data/scan-v2-inventory.json`. Régénération :
`python3 tools/v2_pipeline.py --sources /chemin/vers/_scan2`.
