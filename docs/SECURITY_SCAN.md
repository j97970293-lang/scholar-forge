# ScholarForge — rapport de scan de sécurité statique

Généré le `2026-10-27T20:26:38+00:00` par `tools/security_scan.py`. 14,860 fichiers texte ont été analysés sans jamais exécuter de code.

## Méthode

Règles déterministes héritées du framework ASDF (`O0000-code/awesome-academic-skills/framework/CRITERIA.md`), étendues avec la détection de secrets, d'injections de prompt, de balises système contrefaites et de caractères Unicode invisibles. Les correspondances dans la documentation, les tests et les fixtures sont rétrogradées en `info` ; les IP présentes dans des fichiers de configuration sont traitées comme des numéros de version.

## Résultat global

| Métrique | Valeur |
|---|---:|
| Fichiers texte analysés | 14,860 |
| Correspondances totales | 2,399 |
| Règles déclenchées | 20 |

## Par règle

| Règle | Occurrences | Ce que ça détecte |
|---|---:|---|
| `bare-public-ip` | 1,305 | hard-coded public IPv4 |
| `auto-update-latest` | 193 | unpinned dependency |
| `prompt-injection` | 193 | prompt injection marker |
| `dangerous-eval-exec` | 167 | dynamic code execution |
| `hidden-unicode` | 142 | zero-width / bidi control character |
| `suspicious-url` | 73 | shortener / tunnel / tor URL |
| `miner-or-rat` | 65 | miner / RAT signature |
| `pipe-to-shell` | 63 | unreviewed remote installer |
| `credential-path-read` | 58 | reads a secret path |
| `destructive-command` | 29 | destructive shell command |
| `dynamic-import-or-unpickle` | 28 | dynamic import / unsafe deserialisation |
| `reverse-shell` | 16 | interactive shell back to a remote host |
| `fake-system-tag` | 14 | fake system/role tag in data |
| `exfil-webhook` | 12 | hard-coded exfiltration endpoint |
| `telemetry-endpoint` | 12 | analytics endpoint |
| `insecure-ssl` | 9 | TLS verification disabled |
| `dangerous-powershell` | 7 | PowerShell dynamic execution |
| `hardcoded-secret` | 6 | possible hard-coded credential |
| `long-base64-blob` | 5 | long base64 blob |
| `decode-then-exec` | 2 | encoded blob decoded then executed |

## Par dépôt (bandes de sévérité)

| Dépôt | critical | high | medium | low | info |
|---|---:|---:|---:|---:|---:|
| `O0000-code_awesome-academic-skills` | 65 | 42 | 1 | 0 | 94 |
| `cosen1024_awesome-academic-skills` | 0 | 0 | 0 | 0 | 0 |
| `kael-odin_awesome-academic-research-skills` | 0 | 0 | 2 | 0 | 56 |
| `miketepUR_awesome-claude-skills` | 0 | 0 | 0 | 0 | 0 |
| `Imbad0202_academic-research-skills` | 2 | 226 | 4 | 0 | 92 |
| `KalarisLabs_research-agent-skills` | 19 | 282 | 37 | 0 | 199 |
| `saintgo7_agents-skills` | 1 | 0 | 8 | 0 | 1 |
| `ranbot-ai_awesome-skills` | 108 | 392 | 6 | 0 | 762 |

## Exemples de correspondances (priorité décroissante)

| Sévérité | Dépôt | Fichier | Règle |
|---|---|---|---|
| critical | Imbad0202 | `docs/design/2026-04-27-ars-v3.6.5.1-setup-fix-implementation-brief.md` | `destructive-command` |
| critical | Imbad0202 | `scripts/test_run_guard_launcher.py` | `destructive-command` |
| critical | KalarisLabs | `skills/nemo-evaluator-sdk/references/execution-backends.md` | `credential-path-read` |
| critical | KalarisLabs | `skills/nemo-evaluator-sdk/references/execution-backends.md` | `credential-path-read` |
| critical | KalarisLabs | `skills/pi-agent/references/containerization.md` | `destructive-command` |
| critical | KalarisLabs | `skills/ray-train/references/multi-node.md` | `credential-path-read` |
| critical | KalarisLabs | `skills/skypilot-multi-cloud-orchestration/references/advanced-usage.md` | `credential-path-read` |
| critical | KalarisLabs | `skills/skypilot-multi-cloud-orchestration/references/troubleshooting.m` | `credential-path-read` |
| critical | KalarisLabs | `skills/stable-diffusion-image-generation/references/troubleshooting.md` | `destructive-command` |
| critical | KalarisLabs | `skills/unsloth/references/llms-full.md` | `destructive-command` |
| critical | KalarisLabs | `skills/unsloth/references/llms-txt.md` | `destructive-command` |
| critical | KalarisLabs | `skills/vaex/references/io_operations.md` | `credential-path-read` |
| critical | KalarisLabs | `tests/test_lint_injection.py` | `reverse-shell` |
| critical | KalarisLabs | `tests/test_lint_injection.py` | `reverse-shell` |
| critical | KalarisLabs | `tests/test_lint_injection.py` | `credential-path-read` |
| critical | KalarisLabs | `tools/lint_injection.py` | `reverse-shell` |
| critical | KalarisLabs | `tools/lint_injection.py` | `credential-path-read` |
| critical | KalarisLabs | `tools/lint_injection.py` | `credential-path-read` |
| critical | KalarisLabs | `tools/lint_injection.py` | `credential-path-read` |
| critical | KalarisLabs | `tools/lint_injection.py` | `credential-path-read` |
| critical | KalarisLabs | `tools/lint_injection.py` | `credential-path-read` |
| critical | O0000-code | `framework/CHANGELOG.md` | `destructive-command` |
| critical | O0000-code | `framework/CRITERIA.md` | `reverse-shell` |
| critical | O0000-code | `framework/CRITERIA.md` | `reverse-shell` |
| critical | O0000-code | `framework/CRITERIA.md` | `reverse-shell` |
| critical | O0000-code | `framework/CRITERIA.md` | `decode-then-exec` |
| critical | O0000-code | `framework/CRITERIA.md` | `credential-path-read` |
| critical | O0000-code | `framework/CRITERIA.md` | `credential-path-read` |
| critical | O0000-code | `framework/CRITERIA.md` | `credential-path-read` |
| critical | O0000-code | `framework/CRITERIA.md` | `credential-path-read` |
| critical | O0000-code | `framework/CRITERIA.md` | `credential-path-read` |
| critical | O0000-code | `framework/CRITERIA.md` | `dangerous-powershell` |
| critical | O0000-code | `framework/CRITERIA.md` | `destructive-command` |
| critical | O0000-code | `framework/CRITERIA.md` | `destructive-command` |
| critical | O0000-code | `framework/CRITERIA.md` | `destructive-command` |

## Décision de fusion

Aucun code des dépôts amont n'est **exécuté** par ScholarForge : les archives `upstream/*.zip` sont des données. Le moteur livré dans `scripts/` est écrit from scratch en bibliothèque standard, sans `eval`, sans désérialisation non sûre, sans téléchargement de code et sans appel réseau hors des API savantes explicitement documentées dans `config/sources.yaml`. Le scan complet est reproductible :

```bash
SF_SOURCES=/chemin/vers/les/clones python3 tools/security_scan.py
```

