# 23 — Conformité à la spec Agent Skills et portabilité

**Statut :** vérifié le 2026-10-28 contre `https://agentskills.io/specification` et
`https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`.
La spec a été ouverte en décembre 2025 et transférée à l'Agentic AI Foundation en
octobre 2026 ; le format `SKILL.md` n'a pas changé pour autant.

## 1. Le contrat formel

| Champ | Requis | Contrainte |
|---|---|---|
| `name` | oui | 1–64 caractères, `a-z`, `0-9`, `-` uniquement ; ni au début ni à la fin ; pas de `--` ; identique au nom du dossier |
| `description` | oui | 1–1024 caractères, non vide, sans balise XML ; dit **ce que fait** la skill et **quand** l'utiliser |
| `license` | non | nom court de licence ou référence à un fichier joint |
| `compatibility` | non | ≤ 500 caractères ; environnement, paquets, réseau |
| `metadata` | non | map de chaînes vers chaînes (pas de nombres YAML non quotés) |
| `allowed-tools` | non | chaîne d'outils séparés par des espaces ; champ expérimental, prise en charge variable |

`SKILL.md` doit être exactement ce nom, sensible à la casse. Le dossier de la skill est
en `kebab-case`. Le corps suit le frontmatter YAML sans contrainte de format.

## 2. Divulgation progressive — trois niveaux

1. **Métadonnées** (~100 tokens) : `name` + `description` de toutes les skills chargés
   au démarrage.
2. **Instructions** (< 5000 tokens recommandés, < 500 lignes) : le corps de `SKILL.md`
   chargé uniquement quand la skill est activée.
3. **Ressources** : `scripts/`, `references/`, `assets/` lus à la demande. Conséquence
   directe : un détail qui n'est utile que dans 10 % des tâches ne doit **jamais** être
   dans `SKILL.md`.

**Règle des références à un niveau.** Les fichiers liés depuis `SKILL.md` doivent être
directs. Un fichier de `references/` qui renvoie à un autre fichier de `references/`
risque d'être lu partiellement (`head -100`) : l'information est alors perdue. Les
playbooks de ce dépôt se citent par leur numéro, jamais par un chemin imbriqué.

## 3. Ce que ScholarForge applique

- `name: scholar-forge`, identique au dossier d'installation.
- `description` maintenue **sous 1024 caractères** (contrôle automatique).
- `metadata` : toutes les valeurs sont des chaînes, y compris les compteurs.
- Corps < 500 lignes, ~3 400 tokens ; les 28 playbooks restent hors contexte.
- `license` renvoie à `LICENSE` + `NOTICE.md` (compilation non commerciale).
- `compatibility` annonce Python 3.9+, stdlib seul, réseau optionnel.
- `tools/validate_skill.py` et la commande `validate` rejouent tous ces contrôles.

```bash
python3 scripts/scholarforge.py validate            # PASS / FAIL
python3 scripts/scholarforge.py validate --json    # pour la CI
```

## 4. Degré de liberté des consignes

La documentation officielle recommande d'adapter la précision à la fragilité de la
tâche :
- **Haute liberté** (texte) : rédaction, revue, idéation — plusieurs chemins valides.
- **Liberté moyenne** (pseudo-code, paramètres) : rapports, checklists.
- **Basse liberté** (script exact, sans option) : opérations fragiles — ici,
  `pipeline advance`, `audit`, `integrity` et toute écriture de l'état du projet.

Ne transformez jamais une consigne de type "script exact" en "fais de ton mieux".

## 5. Portabilité

Le format est repris par de nombreux hôtes (Claude Code, Codex CLI, Cursor, Gemini
CLI, Copilot, etc.). Les différences portent sur `allowed-tools` et sur la façon dont
les scripts sont exécutés. Pour rester portable :
- n'utilisez aucun outil spécifique à un hôte dans `SKILL.md` ;
- gardez le CLI en Python standard, sans dépendance ;
- testez la skill sur chaque modèle visé (les petits modèles ont besoin de plus
  de détails, les grands de moins).

`install.sh` produit un dossier de skill allégé : `SKILL.md`, `LICENSE`, `NOTICE.md`,
`references/`, `scripts/`, `templates/`, `config/`, `data/`. Les rapports, les outils
de build, les tests et les archives `upstream/` restent dans le dépôt, pas dans le
dossier installé.

## 6. Échecs connus

| Symptôme | Cause |
|---|---|
| La skill ne se déclenche jamais | `description` trop vague ou sans mots-clés de déclenchement |
| Contexte saturé | corps > 500 lignes ou références chargées en bloc |
| Champ `metadata` ignoré | valeurs numériques non quotées |
| `allowed-tools` sans effet | champ expérimental, non pris en charge par l'hôte |
| Liens morts | référence à un fichier déplacé ; `validate` les détecte |
