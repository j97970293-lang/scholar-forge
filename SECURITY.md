# Politique de sécurité

## Surface d'attaque
- `scripts/` : Python stdlib, aucune élévation, aucun shell, aucune désérialisation, aucune
  écriture hors du projet (sauf `--out` explicite).
- `search` / `verify --online` : requêtes HTTPS GET vers les six hôtes listés dans
  `config/sources.json`. Aucune clé n'est requise ; les clés optionnelles sont lues dans
  l'environnement, jamais écrites sur disque.
- `upstream/*.zip` : **données inertes**. Aucun fichier de ces archives n'est importé,
  exécuté ou évalué par le moteur.
- `tools/` : scripts de build qui lisent les clones et écrivent uniquement dans `data/`,
  `docs/` et `upstream/`.

## Scan statique
`tools/security_scan.py` applique 21 règles (reverse-shell, decode-then-exec, lecture de
secrets, PowerShell dangereux, commandes destructives, webhooks d'exfiltration, miners/RAT,
eval/exec, URL suspectes, IP publiques, pipe-to-shell, dépendances non épinglées, pickle,
longs blobs base64, injection de prompt, fausses balises système, Unicode invisible,
télémétrie, secrets codés en dur, TLS désactivé). Résultats : `docs/SECURITY_SCAN.md` et
`data/security-findings.json`.

## Signaler un problème
Ouvrez une issue privée dans le dépôt en décrivant : fichier, ligne, commande, impact et
preuve de concept. Ne publiez jamais de secret dans une issue.

## Secrets et jetons
Aucun jeton d'authentification n'est stocké dans ce dépôt. Les jetons GitHub utilisés pour la
publication sont passés en mémoire aux commandes `curl`/`git` et ne figurent ni dans les
fichiers, ni dans `.git/config`, ni dans les journaux. Un jeton partagé en clair dans une
conversation doit être considéré comme compromis et révoqué/remplacé depuis les paramètres
GitHub → Developer settings → Personal access tokens. Vérification locale (et en CI) :
```bash
python3 tools/check_secrets.py
```

## Limites
ScholarForge n'est pas un antivirus. Le scan statique produit des indicateurs, pas des preuves
d'absence de code malveillant. N'exécutez jamais de code tiers sans relecture humaine.
