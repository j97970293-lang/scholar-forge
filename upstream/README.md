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
