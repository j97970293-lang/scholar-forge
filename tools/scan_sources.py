#!/usr/bin/env python3
"""scan_sources.py -- exhaustive, reproducible scan of every upstream repository.

Walks every file of all eight cloned sources (excluding .git), parses Python via
AST, reads YAML/JSON front matter, extracts Markdown headings and links, records
network endpoints, and emits:

    data/scan-inventory.json   one record per file (path, hash, size, lines, meta)
    data/scan-summary.json     machine-readable aggregates
    docs/SCAN_REPORT.md        human-readable scan report

Usage:  python3 tools/scan_sources.py [--sources /path/to/clones]
"""

from __future__ import annotations

import argparse
import ast
import collections
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    CODE_EXT, ROOT, SCAN_ROOT, SOURCES, TEXT_EXT, frontmatter, human_bytes,
    iter_files, read_text, repo_dirs, sha256_file, write_json,
)

URL_RE = re.compile(r"https?://([A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+)")
HOST_RE = re.compile(r"^([A-Za-z0-9.-]+)")
GH_RE = re.compile(r"https?://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")
HEAD_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.M)


def python_meta(text: str) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        meta["parse_error"] = True
        return meta
    imports: set = set()
    funcs: List[str] = []
    classes: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
    meta["imports"] = sorted(imports)[:40]
    meta["functions"] = funcs[:40]
    meta["function_count"] = len(funcs)
    meta["classes"] = classes[:25]
    meta["has_cli"] = bool(re.search(r"__name__\s*==\s*['\"]__main__['\"]", text)) or "argparse" in imports
    doc = ast.get_docstring(tree) or ""
    meta["docstring"] = doc.strip().splitlines()[0][:200] if doc.strip() else ""
    return meta


def scan_file(path: Path, slug: str) -> Dict[str, Any]:
    rel = str(path.relative_to(SCAN_ROOT / slug))
    ext = path.suffix.lower()
    size = path.stat().st_size
    rec: Dict[str, Any] = {
        "repo": slug,
        "path": rel,
        "ext": ext or "(none)",
        "size": size,
        "sha256": sha256_file(path),
    }
    text = read_text(path, limit=1_500_000) if ext in TEXT_EXT and size < 6_000_000 else ""
    if text:
        rec["lines"] = text.count("\n") + 1
        rec["chars"] = len(text)
        if ext == ".py":
            rec["python"] = python_meta(text)
        elif ext in (".md", ".markdown", ".rst", ".txt"):
            rec["headings"] = [m.group(2).strip()[:120] for m in HEAD_RE.finditer(text)][:40]
            if path.name.upper() == "SKILL.MD":
                fm = frontmatter(text)
                rec["skill"] = {
                    "name": fm.get("name", ""),
                    "description": fm.get("description", "")[:400],
                    "license": fm.get("license", ""),
                    "category": fm.get("category", ""),
                    "version": fm.get("version", ""),
                }
        elif ext in (".yml", ".yaml", ".json", ".jsonl", ".toml", ".cff"):
            if ext in (".json", ".jsonl"):
                try:
                    obj = json.loads(text)
                    rec["top_keys"] = list(obj.keys())[:25] if isinstance(obj, dict) else ["<list:%d>" % len(obj)]
                except ValueError:
                    rec["top_keys"] = []
            else:
                rec["top_keys"] = list(dict.fromkeys(re.findall(r"^([A-Za-z_][\w .-]*):", text, re.M)))[:25]
        elif ext in (".tex", ".sty", ".bib"):
            rec["headings"] = [m.group(2).strip()[:120] for m in HEAD_RE.finditer(text)][:20]
        for host in URL_RE.findall(text):
            hm = HOST_RE.match(host)
            if hm:
                rec.setdefault("hosts", [])
                if hm.group(1) not in rec["hosts"]:
                    rec["hosts"].append(hm.group(1))
        rec["hosts"] = rec.get("hosts", [])[:25]
    return rec


def main() -> int:
    global SCAN_ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default=str(SCAN_ROOT))
    args = ap.parse_args()
    SCAN_ROOT = Path(args.sources)
    repos = [(slug, SCAN_ROOT / slug) for slug in SOURCES if (SCAN_ROOT / slug / ".git").exists()]
    if not repos:
        print("No cloned sources found under", SCAN_ROOT, file=sys.stderr)
        return 2

    records: List[Dict[str, Any]] = []
    per_repo: Dict[str, Dict[str, Any]] = {}
    host_counter: collections.Counter = collections.Counter()
    ext_counter: collections.Counter = collections.Counter()
    ext_bytes: collections.Counter = collections.Counter()
    github_links: collections.Counter = collections.Counter()
    skills: List[Dict[str, str]] = []
    py_scripts: List[Dict[str, str]] = []
    api_hosts: collections.Counter = collections.Counter()

    for slug, root in repos:
        n = size = lines = 0
        exts: collections.Counter = collections.Counter()
        pys = shs = mds = yamls = jsons = 0
        for p in iter_files(root):
            rec = scan_file(p, slug)
            records.append(rec)
            n += 1
            size += rec["size"]
            lines += rec.get("lines", 0)
            e = rec["ext"]
            exts[e] += 1
            ext_counter[e] += 1
            ext_bytes[e] += rec["size"]
            pys += e == ".py"
            shs += e in (".sh", ".bash")
            mds += e in (".md", ".markdown")
            yamls += e in (".yml", ".yaml")
            jsons += e in (".json", ".jsonl")
            for h in rec.get("hosts", []):
                host_counter[h] += 1
                if h.startswith(("api.", "export.", "www.ncbi", "eutils", "api.crossref", "api.openalex",
                                 "api.semanticscholar", "api.unpaywall", "api.core.ac.uk", "api.datacite",
                                 "api.zenodo", "www.ebi.ac.uk")):
                    api_hosts[h] += 1
            txt = read_text(p, limit=250_000) if e in (".md", ".yaml", ".yml", ".json") else ""
            for m in GH_RE.findall(txt):
                github_links[m.rstrip(".").lower()] += 1
            if rec.get("skill"):
                skills.append({"repo": slug, "path": rec["path"], **rec["skill"]})
            if e == ".py" and rec.get("python", {}).get("has_cli"):
                py_scripts.append({"repo": slug, "path": rec["path"],
                                   "doc": rec["python"].get("docstring", "")})
        per_repo[slug] = {
            "files": n, "bytes": size, "human_bytes": human_bytes(size),
            "lines": lines, "python": pys, "shell": shs, "markdown": mds,
            "yaml": yamls, "json": jsons, "top_extensions": exts.most_common(8),
            "url": SOURCES[slug]["url"], "license": SOURCES[slug]["license"],
            "role": SOURCES[slug]["role"],
        }
        print(f"scanned {slug}: {n} files / {human_bytes(size)}")

    total = sum(r["files"] for r in per_repo.values())
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_root": str(SCAN_ROOT),
        "repositories": len(repos),
        "total_files": total,
        "total_bytes": sum(r["bytes"] for r in per_repo.values()),
        "total_lines": sum(r["lines"] for r in per_repo.values()),
        "skill_md_files": len(skills),
        "python_cli_scripts": len(py_scripts),
        "distinct_extensions": len(ext_counter),
        "distinct_hosts": len(host_counter),
        "distinct_github_links": len(github_links),
        "per_repo": per_repo,
        "extensions": ext_counter.most_common(30),
        "api_hosts": api_hosts.most_common(40),
        "top_hosts": host_counter.most_common(40),
        "top_github_links": github_links.most_common(50),
    }
    write_json(ROOT / "data/scan-summary.json", summary)
    write_json(ROOT / "data/scan-inventory.json", {"generated_utc": summary["generated_utc"], "files": records}, indent=1)
    write_json(ROOT / "data/source-skills.json", skills)
    write_json(ROOT / "data/source-python-clis.json", py_scripts)

    # ---- human report ----
    L: List[str] = []
    L.append("# ScholarForge — rapport de scan exhaustif des sources\n")
    L.append(f"Généré le `{summary['generated_utc']}` par `tools/scan_sources.py`. "
             f"Tous les fichiers des clones sont parcourus, hachés (SHA-256) et indexés ; "
             f"le code Python est analysé via AST, les `SKILL.md` via leur frontmatter, "
             f"et les URL/hôtes réseau sont extraits de chaque fichier texte.\n")
    L.append("## 1. Chiffres globaux\n")
    L.append("| Métrique | Valeur |\n|---|---:|")
    L.append(f"| Dépôts scannés | {len(repos)} |")
    L.append(f"| Fichiers indexés | {total:,} |")
    L.append(f"| Volume total | {human_bytes(summary['total_bytes'])} |")
    L.append(f"| Lignes de texte lues | {summary['total_lines']:,} |")
    L.append(f"| Fichiers `SKILL.md` | {len(skills)} |")
    L.append(f"| Scripts Python avec CLI | {len(py_scripts)} |")
    L.append(f"| Extensions distinctes | {summary['distinct_extensions']} |")
    L.append(f"| Hôtes HTTP distincts | {summary['distinct_hosts']} |")
    L.append(f"| Dépôts GitHub référencés | {summary['distinct_github_links']} |\n")
    L.append("## 2. Par dépôt\n")
    L.append("| Dépôt | Rôle | Licence | Fichiers | Taille | Lignes | .py | .sh | .md | SKILL.md |\n|---|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for slug, r in per_repo.items():
        nsk = sum(1 for s in skills if s["repo"] == slug)
        L.append(f"| [`{slug}`]({r['url']}) | {r['role']} | {r['license']} | {r['files']:,} | "
                 f"{r['human_bytes']} | {r['lines']:,} | {r['python']} | {r['shell']} | {r['markdown']} | {nsk} |")
    L.append("\n## 3. Extensions rencontrées (top 20)\n")
    L.append("| Extension | Fichiers | Volume |\n|---|---:|---:|")
    for e, c in ext_counter.most_common(20):
        L.append(f"| `{e}` | {c:,} | {human_bytes(ext_bytes[e])} |")
    L.append("\n## 4. API et hôtes réseau détectés dans le code\n")
    L.append("| Hôte | Fichiers le mentionnant |\n|---|---:|")
    for h, c in api_hosts.most_common(35):
        L.append(f"| `{h}` | {c} |")
    L.append("\n## 5. Extrait des compétences découvertes\n")
    L.append("Les `SKILL.md` complets sont conservés dans `upstream/*.zip` ; "
             "la liste indexée est dans `data/source-skills.json`.\n")
    L.append("| Dépôt | Nom | Catégorie | Déclencheur (extrait) |\n|---|---|---|---|")
    for s in skills[:60]:
        L.append(f"| {s['repo'].split('_')[0]} | `{s.get('name','?')[:38]}` | {s.get('category','-')[:22]} | "
                 f"{s.get('description','')[:90].replace('|','/')} |")
    if len(skills) > 60:
        L.append(f"\n… et {len(skills) - 60} autres entrées dans `data/source-skills.json`.\n")
    L.append("\n## 6. Scripts Python exécutables relevés\n")
    L.append(f"{len(py_scripts)} scripts Python exposent un point d'entrée CLI. "
             "Inventaire complet : `data/source-python-clis.json`. Exemples :\n")
    for s in py_scripts[:25]:
        L.append(f"- `{s['repo'].split('_')[0]}/{s['path'].split('/')[-1]}` — {s['doc'][:110]}")
    L.append("\n## 7. Dépôts GitHub les plus cités par les méta-listes\n")
    L.append("| Dépôt | Occurrences |\n|---|---:|")
    for name, c in github_links.most_common(30):
        L.append(f"| `{name}` | {c} |")
    L.append("\n## 8. Reproduction\n")
    L.append("```bash\nSF_SOURCES=/chemin/vers/les/clones python3 tools/scan_sources.py\n```\n")
    L.append("Les archives sources complètes (sans les `.git`) sont dans `upstream/` ; "
             "leurs empreintes sont dans `upstream/manifest.json`.\n")
    (ROOT / "docs/SCAN_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote data/scan-*.json and docs/SCAN_REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
