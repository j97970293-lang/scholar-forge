# Validation de livraison — ScholarForge 1.1.0

Date : **28 octobre 2026**. Ces contrôles portent sur le logiciel et les données de
provenance, pas sur la véracité scientifique de manuscrits futurs.

| Contrôle | Résultat constaté |
|---|---|
| Tests unitaires hors ligne | **100 exécutés, 0 échec, 0 erreur** dans le dépôt complet |
| Conformité locale Agent Skills | **PASS**, 0 erreur, 0 avertissement ; description de 889 caractères |
| Diagnostic `doctor` | **OK** ; 28 références, 15 templates, 7 JSON de config, registre de 5460 entrées |
| Compilation Python | Tous les scripts, outils et tests compilent |
| Compatibilité de syntaxe | Tous les fichiers du runtime analysés avec la grammaire Python 3.9 |
| JSON, JSONL et YAML de livraison | Fichiers structurés relus et validés |
| Démonstration négative | **FAIL attendu**, 3/8 portes satisfaites |
| Démonstration corrigée | **PASS**, 7/8 portes satisfaites ; `G-pipeline` consultative à S0 |
| Historique de recherche | Deux recherches sur deux bases : **4 lignes conservées** dans le JSON et le Markdown |
| Historique JSON corrompu | Refus d'écriture, ancien contenu conservé |
| Cache d'intégrité | Invalidation après modification des références, schéma inconnu ou âge >24 h |
| Déclaration IA vierge | **FAIL attendu** ; aucun PASS basé sur la seule présence d'un template |
| Déclaration IA complétée | **PASS**, sans avertissement de placeholder |
| Sortie JSON + exports | JSON sans messages parasites ; auteurs RIS séparés |
| Recherche réelle | OpenAlex et Crossref : réponses réussies sur « RNA velocity benchmarking », 3 notices par source demandées |
| Filtres de cette recherche | Années + OA sur OpenAlex ; années natives sur Crossref, OA explicitement signalé non natif / inconnu |
| DOI réellement rétracté | `10.1016/S0140-6736(97)11096-0` : `retracted-confirmed`, deux registres répondent et signaux corroborés |
| DOI témoin | `10.1038/s41596-020-0309-5` : `no-signal`, deux registres répondent ; **ce n'est pas une preuve d'intégrité** |
| Secrets dans les fichiers du projet | Aucun motif de credential détecté par le contrôle local ; les archives amont ne sont pas secret-scannées par cet outil |
| Intégrité des sources archivées | Les 14 ZIP sont contrôlés contre leur manifeste SHA-256 lors du packaging |
| Archives de livraison | CRC ZIP + empreintes fichier par fichier ; `SHA256SUMS.txt` et `release-manifest.json` externes |

## Rejouer les contrôles

```bash
python3 -m compileall -q scripts tools tests
python3 scripts/scholarforge.py selftest
python3 scripts/scholarforge.py validate
python3 scripts/scholarforge.py doctor
python3 tools/check_secrets.py
bash examples/end-to-end/run-demo.sh
bash examples/end-to-end/run-demo.sh --fixed
python3 tools/package_release.py --output /chemin/hors-du-depot
```

La CI est configurée pour Python 3.9, 3.11 et 3.13. Le contrôle local a été exécuté
sur Python 3.13 ; l'analyse de grammaire 3.9 n'est pas équivalente à un test sur
l'interpréteur 3.9. L'installateur PowerShell est fourni mais n'a pas été exécuté
dans cet environnement Linux. Dans l'installation allégée, deux tests d'artefacts
de build sont explicitement ignorés : les 98 autres doivent réussir.

## Ce qu'un PASS ne signifie pas

- Pas de mesure de performance d'un LLM : les 18 cas de `evals/` ne sont pas un
  benchmark exécuté.
- Pas d'attestation des expériences, de l'authenticité des données ou des droits
  de chaque composant.
- Pas de revue systématique exhaustive : les clients API récupèrent des fenêtres
  bornées ; les comptes ne sont pas les totaux des bases.
- Pas de verdict définitif de rétractation : les API peuvent partager des sources
  et les notices doivent être lues sur le site de l'éditeur.

## Stabilisation de la CI distante

Le premier run distant a échoué avant les tests Python 3.9 : `ubuntu-latest` avait migré
vers Ubuntu 26.04, sans binaire 3.9 proposé par `setup-python`. La configuration finale
fixe **Ubuntu 22.04**, utilise `checkout` v5 et `setup-python` v6 (Node 24), épinglés par
SHA, et désactive le fail-fast de la matrice pour conserver les diagnostics de chaque
interpréteur. L'état courant des exécutions est visible dans l'onglet Actions du dépôt.
