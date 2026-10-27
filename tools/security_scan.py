#!/usr/bin/env python3
"""security_scan.py -- static trust gate over every upstream file.

Implements the deterministic half of the ASDF framework inherited from
O0000-code/awesome-academic-skills (framework/CRITERIA.md), plus secret and
prompt-injection detection. It never executes scanned code.

Outputs: data/security-findings.json, docs/SECURITY_SCAN.md
"""

from __future__ import annotations

import collections
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    ROOT, SCAN_ROOT, SOURCES, TEXT_EXT, iter_files, read_text, repo_dirs, write_json,
)

RULES: List[Tuple[str, str, str, str]] = [
    ("reverse-shell", "critical", r"/dev/tcp/|nc\s+-e\b|bash\s+-i\b|pty\.spawn\(|socket\.connect\(", "interactive shell back to a remote host"),
    ("decode-then-exec", "critical", r"base64\s+-d[^\n]{0,80}\|\s*(ba)?sh|b64decode\([^)]*\)\s*\)?\s*\)?\s*(exec|eval)|atob\([^)]*\)\s*\)?\s*eval", "encoded blob decoded then executed"),
    ("credential-path-read", "critical", r"\.ssh/id_(rsa|ed25519)|\.aws/credentials|/etc/shadow|\.netrc|\.git-credentials|\.kube/config", "reads a secret path"),
    ("dangerous-powershell", "critical", r"DownloadString\(|FromBase64String\(|-EncodedCommand|IEX\s*\(", "PowerShell dynamic execution"),
    ("destructive-command", "critical", r"rm\s+-rf\s+[/~*]|chmod\s+777|dd\s+[^\n]*of=/dev/sd|:\(\)\s*\{\s*:\|:&", "destructive shell command"),
    ("exfil-webhook", "critical", r"hooks\.slack\.com/services|discord(app)?\.com/api/webhooks|api\.telegram\.org/bot|webhook\.site|requestbin|pipedream\.net", "hard-coded exfiltration endpoint"),
    ("miner-or-rat", "critical", r"xmrig|stratum\+tcp://|mimikatz|meterpreter|njrat", "miner / RAT signature"),
    ("dangerous-eval-exec", "high", r"\beval\(|\bexec\(|os\.system\(|subprocess\([^)]*shell\s*=\s*True|yaml\.load\((?![^)]*Loader)", "dynamic code execution"),
    ("suspicious-url", "high", r"bit\.ly/|pastebin\.com/raw|ngrok|trycloudflare|\.onion\b", "shortener / tunnel / tor URL"),
    ("bare-public-ip", "high", r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])", "hard-coded public IPv4"),
    ("pipe-to-shell", "medium", r"curl[^\n]{0,120}\|\s*(ba)?sh|wget[^\n]{0,120}\|\s*(ba)?sh", "unreviewed remote installer"),
    ("auto-update-latest", "medium", r"@latest\b|pip\s+install\s+-U\b|cargo\s+install\s+--git", "unpinned dependency"),
    ("dynamic-import-or-unpickle", "medium", r"__import__\(|pickle\.loads\(|marshal\.loads\(", "dynamic import / unsafe deserialisation"),
    ("long-base64-blob", "medium", r"[A-Za-z0-9+/]{220,}={0,2}", "long base64 blob"),
    ("prompt-injection", "medium", r"ignore (all )?previous instructions|ignore (all )?prior instructions|developer mode|DAN mode|do anything now|jailbreak", "prompt injection marker"),
    ("fake-system-tag", "medium", r"<\s*system\s*>|\[INST\]|<<SYS>>", "fake system/role tag in data"),
    ("hidden-unicode", "medium", "[\u200b\u200c\u200d\u2060\ufeff\u202a-\u202e\u2066-\u2069]", "zero-width / bidi control character"),
    ("telemetry-endpoint", "low", r"google-analytics\.com|googletagmanager|sentry\.io|mixpanel\.com|segment\.io", "analytics endpoint"),
    ("hardcoded-secret", "critical", r"gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|sk-[A-Za-z0-9]{32,}", "possible hard-coded credential"),
    ("insecure-ssl", "low", r"verify\s*=\s*False|InsecureSkipVerify|CURLOPT_SSL_VERIFYPEER,\s*0", "TLS verification disabled"),
]
COMPILED = [(name, sev, re.compile(pat, re.I if name != "hidden-unicode" else 0), desc)
            for name, sev, pat, desc in RULES]

DOC_EXT = {".md", ".txt", ".rst", ".html", ".yaml", ".yml", ".json"}
BAND_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def main() -> int:
    repos = repo_dirs()
    findings: List[Dict[str, Any]] = []
    per_rule: collections.Counter = collections.Counter()
    per_repo: Dict[str, collections.Counter] = {slug: collections.Counter() for slug, _ in repos}
    scanned = 0
    for slug, root in repos:
        for p in iter_files(root):
            ext = p.suffix.lower()
            if ext not in TEXT_EXT or p.stat().st_size > 3_000_000:
                continue
            text = read_text(p, limit=1_000_000)
            if not text:
                continue
            scanned += 1
            rel = str(p.relative_to(root))
            is_doc = ext in DOC_EXT or "test" in rel.lower() or "fixture" in rel.lower()
            for name, sev, rx, desc in COMPILED:
                for m in rx.finditer(text):
                    band = "info" if is_doc and sev in ("medium", "low") else sev
                    # Version-string IPs in manifests are a known false positive.
                    if name == "bare-public-ip" and ext in (".json", ".yml", ".yaml", ".txt"):
                        band = "info"
                    per_rule[name] += 1
                    per_repo[slug][band] += 1
                    if len(findings) < 1200:
                        line = text.count("\n", 0, m.start()) + 1
                        snippet = text[max(0, m.start() - 50):m.end() + 50].replace("\n", " ")
                        findings.append({
                            "repo": slug, "path": rel, "line": line, "rule": name,
                            "severity": band, "description": desc,
                            "snippet": snippet[:200],
                        })
    findings.sort(key=lambda f: (BAND_ORDER.get(f["severity"], 9), f["repo"], f["path"]))
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files_scanned": scanned,
        "repositories": len(repos),
        "total_matches": int(sum(per_rule.values())),
        "by_rule": dict(per_rule.most_common()),
        "by_repo": {k: dict(v) for k, v in per_repo.items()},
        "note": "Documentation/test context downgrades medium+low matches to info. "
                "Matches are static indicators, not proof of malicious behaviour.",
    }
    write_json(ROOT / "data/security-findings.json", {"summary": summary, "findings": findings})
    write_json(ROOT / "data/security-summary.json", summary)

    L: List[str] = ["# ScholarForge — rapport de scan de sécurité statique\n",
                    f"Généré le `{summary['generated_utc']}` par `tools/security_scan.py`. "
                    f"{scanned:,} fichiers texte ont été analysés sans jamais exécuter de code.\n",
                    "## Méthode\n",
                    "Règles déterministes héritées du framework ASDF "
                    "(`O0000-code/awesome-academic-skills/framework/CRITERIA.md`), étendues avec la "
                    "détection de secrets, d'injections de prompt, de balises système contrefaites et "
                    "de caractères Unicode invisibles. Les correspondances dans la documentation, les "
                    "tests et les fixtures sont rétrogradées en `info` ; les IP présentes dans des "
                    "fichiers de configuration sont traitées comme des numéros de version.\n",
                    "## Résultat global\n",
                    "| Métrique | Valeur |\n|---|---:|",
                    f"| Fichiers texte analysés | {scanned:,} |",
                    f"| Correspondances totales | {summary['total_matches']:,} |",
                    f"| Règles déclenchées | {len(per_rule)} |\n",
                    "## Par règle\n",
                    "| Règle | Occurrences | Ce que ça détecte |\n|---|---:|---|"]
    for name, count in per_rule.most_common():
        desc = next(d for n, _, _, d in RULES if n == name)
        L.append(f"| `{name}` | {count:,} | {desc} |")
    L.append("\n## Par dépôt (bandes de sévérité)\n")
    L.append("| Dépôt | critical | high | medium | low | info |\n|---|---:|---:|---:|---:|---:|")
    for slug, c in per_repo.items():
        L.append(f"| `{slug}` | {c['critical']} | {c['high']} | {c['medium']} | {c['low']} | {c['info']} |")
    L.append("\n## Exemples de correspondances (priorité décroissante)\n")
    L.append("| Sévérité | Dépôt | Fichier | Règle |\n|---|---|---|---|")
    for f in findings[:35]:
        L.append(f"| {f['severity']} | {f['repo'].split('_')[0]} | `{f['path'][:70]}` | `{f['rule']}` |")
    L.append("\n## Décision de fusion\n")
    L.append("Aucun code des dépôts amont n'est **exécuté** par ScholarForge : les archives "
             "`upstream/*.zip` sont des données. Le moteur livré dans `scripts/` est écrit from "
             "scratch en bibliothèque standard, sans `eval`, sans désérialisation non sûre, sans "
             "téléchargement de code et sans appel réseau hors des API savantes explicitement "
             "documentées dans `config/sources.yaml`. Le scan complet est reproductible :\n")
    L.append("```bash\nSF_SOURCES=/chemin/vers/les/clones python3 tools/security_scan.py\n```\n")
    (ROOT / "docs/SECURITY_SCAN.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("security scan:", summary["total_matches"], "matches over", scanned, "files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
