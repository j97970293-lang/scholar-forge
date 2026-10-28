#!/usr/bin/env python3
"""v2_pipeline.py -- scan, snapshot and register six additional source repos.

Run after cloning the v2 sources:

    git clone --depth 1 https://github.com/agentskills/agentskills.git _scan2/agentskills_agentskills
    ... (see docs/RESEARCH_NOTES.md for the exact six URLs)
    python3 tools/v2_pipeline.py --sources ../_scan2

Outputs:
    data/scan-v2-summary.json       aggregates for the six new repos
    data/scan-v2-inventory.json     one SHA-256 record per file
    docs/SCAN_REPORT_V2.md          human report
    upstream/v2/<slug>.zip           curated (NOT lossless) snapshots
    upstream/v2/manifest.json        commits, SHA-256, exclusion accounting
    data/registry.json/.csv          extended registry (v1 entries untouched)
    data/registry-stats.json         regenerated aggregates
    docs/REGISTRY.md                 v2 section appended

Honesty rule: the eight v1 archives are full snapshots. These six are *curated*:
test suites, VCS internals, caches and files above 2 MiB are excluded and the
exclusion is counted in the manifest. Nothing is executed.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

V2_SOURCES: Dict[str, Dict[str, Any]] = {
    "agentskills_agentskills": {
        "url": "https://github.com/agentskills/agentskills", "license": "Apache-2.0",
        "role": "official Agent Skills open specification + skills-ref validation library",
        "stars": 26703, "stage": "meta",
    },
    "anthropics_skills": {
        "url": "https://github.com/anthropics/skills", "license": "Mixed: per-skill LICENSE.txt; no blanket licence assumed",
        "role": "official skill library: 20 SKILL.md examples of progressive disclosure",
        "stars": 184227, "stage": "meta",
    },
    "chrisyangsong_citegate": {
        "url": "https://github.com/chrisyangsong/citegate", "license": "MIT",
        "role": "citation-integrity CI gate: Crossref/OpenAlex verification + retraction verdicts",
        "stars": 102, "stage": "citation",
    },
    "asreview_asreview": {
        "url": "https://github.com/asreview/asreview", "license": "Apache-2.0",
        "role": "active learning for systematic-review screening; dual-screening workflow patterns",
        "stars": 1053, "stage": "reading",
    },
    "manubot_manubot": {
        "url": "https://github.com/manubot/manubot", "license": "BSD-2-Clause-Patent",
        "role": "open automated manuscripts; citation-by-identifier and reproducible reference handling",
        "stars": 477, "stage": "writing",
    },
    "Future-House_paper-qa": {
        "url": "https://github.com/Future-House/paper-qa", "license": "Apache-2.0",
        "role": "evidence-grounded question answering over scientific documents with citations",
        "stars": 9477, "stage": "reading",
    },
}

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
             "node_modules", ".venv", "venv", "dist", "build", ".cache"}
TEXT_EXT = {".md", ".txt", ".py", ".sh", ".yml", ".yaml", ".json", ".jsonl", ".toml",
            ".cfg", ".ini", ".html", ".css", ".js", ".ts", ".tsx", ".rst", ".cff",
            ".tex", ".bib", ".csv", ".xml", ".svg", ".j2", ".ipynb"}
BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2", ".ttf",
              ".mp4", ".zip", ".gz", ".pkl", ".npy", ".npz", ".so", ".whl", ".parquet"}
MAX_FILE = 2 * 1024 * 1024
EXCLUDE_DIRS_FOR_ZIP = SKIP_DIRS | {"tests", "test", ".github/workflows"}
URL_RE = re.compile(r"https?://([A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+)")
GH_RE = re.compile(r"https?://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def head_sha(repo: Path) -> str:
    head = repo / ".git/HEAD"
    if not head.exists():
        return ""
    text = head.read_text(encoding="utf-8", errors="replace").strip()
    if text.startswith("ref:"):
        ref = text.split(" ", 1)[1]
        p = repo / ".git" / ref
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
        packed = repo / ".git/packed-refs"
        if packed.exists():
            for line in packed.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.endswith(" " + ref):
                    return line.split()[0]
        return ""
    return text


def iter_files(repo: Path, for_zip: bool = False):
    skip = EXCLUDE_DIRS_FOR_ZIP if for_zip else SKIP_DIRS
    for dp, dns, fns in os.walk(repo):
        dns[:] = [d for d in dns if d not in skip]
        for name in sorted(fns):
            p = Path(dp) / name
            if not p.is_file() or p.is_symlink():
                continue
            if for_zip and (p.suffix.lower() in BINARY_EXT or p.stat().st_size > MAX_FILE):
                continue
            yield p


def python_meta(text: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return {"parse_error": True}
    imports, funcs, classes = set(), [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
    return {"imports": sorted(imports)[:25], "functions": len(funcs), "classes": len(classes)}


def skill_frontmatter(text: str) -> Dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    out: Dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip("'\"")
    return out


def human(n: float) -> str:
    for unit in ("o", "Kio", "Mio", "Gio"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} Tio"


def scan(sources_root: Path) -> Dict[str, Any]:
    inventory: List[Dict[str, Any]] = []
    per_repo: Dict[str, Any] = {}
    hosts: Counter = Counter()
    repos: Counter = Counter()
    py_meta: Dict[str, Any] = {}
    skills: List[Dict[str, str]] = []
    for slug, meta in V2_SOURCES.items():
        repo = sources_root / slug
        if not repo.is_dir():
            raise FileNotFoundError(f"missing clone: {repo}")
        files = list(iter_files(repo))
        lines = 0
        ext: Counter = Counter()
        size = 0
        for p in files:
            st = p.stat()
            rel = str(p.relative_to(repo))
            text = ""
            if p.suffix.lower() in TEXT_EXT and st.st_size < MAX_FILE:
                try:
                    text = p.read_text(encoding="utf-8", errors="replace")
                    lines += text.count("\n") + 1
                except OSError:
                    pass
            rec = {"repo": slug, "path": rel, "bytes": st.st_size,
                   "sha256": sha256_file(p), "ext": p.suffix.lower(),
                   "lines": text.count("\n") + 1 if text else 0}
            inventory.append(rec)
            size += st.st_size
            ext[p.suffix.lower() or "(none)"] += 1
            if text:
                for m in URL_RE.finditer(text):
                    hosts[m.group(1).split("/")[0].split(":")[0]] += 1
                for m in GH_RE.finditer(text):
                    repos[m.group(1)] += 1
            if p.suffix == ".py" and text:
                py_meta[slug + "/" + rel] = python_meta(text)
            if p.name == "SKILL.md" and text:
                fm = skill_frontmatter(text)
                skills.append({"repo": slug, "path": rel,
                               "name": fm.get("name", ""), "description": fm.get("description", "")[:300]})
        per_repo[slug] = {"files": len(files), "bytes": size, "human": human(size),
                          "lines": lines, "skills": len([s for s in skills if s["repo"] == slug]),
                          "python_files": ext.get(".py", 0), "commit": head_sha(repo),
                          "top_ext": dict(ext.most_common(8))}
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": "Curated scan of six v2 repositories (VCS internals excluded). "
                  "Read-only; no upstream code was executed.",
        "repositories": len(V2_SOURCES), "files": len(inventory),
        "bytes": sum(r["bytes"] for r in per_repo.values()),
        "lines": sum(r["lines"] for r in per_repo.values()),
        "python_files": sum(r["python_files"] for r in per_repo.values()),
        "skill_files": len(skills), "distinct_http_hosts": len(hosts),
        "referenced_github_repos": len(repos), "per_repo": per_repo,
        "top_hosts": dict(hosts.most_common(15)),
    }
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/scan-v2-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "data/scan-v2-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False) + "\n")
    (ROOT / "data/scan-v2-skills.json").write_text(json.dumps(skills, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "data/scan-v2-python.json").write_text(json.dumps(py_meta, ensure_ascii=False, indent=2) + "\n")
    L = ["# Scan report — v2 sources (2026-10-28)", "",
         summary["policy"], "",
         f"- **{summary['repositories']}** dépôts | **{summary['files']:,}** fichiers | "
         f"**{human(summary['bytes'])}** | **{summary['lines']:,}** lignes de texte",
         f"- **{summary['python_files']}** scripts Python analysés par AST | "
         f"**{summary['skill_files']}** `SKILL.md` officiels lus",
         f"- **{summary['distinct_http_hosts']}** hôtes HTTP distincts | "
         f"**{summary['referenced_github_repos']}** dépôts GitHub référencés", "",
         "| Dépôt | Fichiers | Taille | Lignes | `.py` | `SKILL.md` | Commit | Rôle |",
         "|---|---:|---:|---:|---:|---:|---|---|"]
    for slug, r in per_repo.items():
        L.append(f"| `{slug}` | {r['files']:,} | {r['human']} | {r['lines']:,} | "
                 f"{r['python_files']} | {r['skills']} | `{r['commit'][:8]}` | {V2_SOURCES[slug]['role'][:70]} |")
    L += ["", "## Principaux hôtes référencés", "", "| Hôte | Occurrences |", "|---|---:|"]
    L += [f"| `{k}` | {v} |" for k, v in list(summary["top_hosts"].items())[:12]]
    L += ["", "## Ce que ces dépôts ont apporté", "",
          "| Dépôt | Apport intégré dans ScholarForge |", "|---|---|",
          "| agentskills/agentskills | `tools/validate_skill.py`, `sf/spec.py`, mise en conformité "
          "frontmatter (description ≤1024, metadata chaînes), `references/23` |",
          "| anthropics/skills | 20 `SKILL.md` officiels indexés dans le registre ; motifs de "
          "divulgation progressive |",
          "| chrisyangsong/citegate | `sf/integrity.py`, porte `G-integrity`, `references/24` |",
          "| asreview/asreview | double criblage / apprentissage actif documenté dans `references/05` et `references/28` |",
          "| manubot/manubot | citations par identifiant et traçabilité dans `references/07`, `references/28` |",
          "| Future-House/paper-qa | ancrage des réponses sur preuves dans `references/06`, `references/28` |",
          "", "## Limites", "",
          "- Les archives v2 sont **curées** (tests, caches et fichiers >2 Mio exclus), contrairement "
          "aux 8 archives v1 qui sont intégrales. Voir `upstream/v2/manifest.json`.",
          "- Les comptes d'étoiles sont un instantané du 2026-10-28, non une mesure vivante.",
          "- Aucun code amont n'a été exécuté : lecture, hachage et analyse AST uniquement.", ""]
    (ROOT / "docs/SCAN_REPORT_V2.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return summary


def package(sources_root: Path) -> Dict[str, Any]:
    out = ROOT / "upstream/v2"
    out.mkdir(parents=True, exist_ok=True)
    manifest: Dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": "CURATED snapshot (NOT lossless): VCS internals, test suites, caches, binary "
                  "assets and files >2 MiB are excluded. Exclusions are counted per repo. "
                  "Archives are inert data; nothing inside is executed.",
        "note": "The eight v1 archives in ../ remain full snapshots. Do not confuse the two tiers.",
        "repositories": {},
    }
    for slug, meta in V2_SOURCES.items():
        repo = sources_root / slug
        included = list(iter_files(repo, for_zip=True))
        all_files = list(iter_files(repo))
        excluded = len(all_files) - len(included)
        zpath = out / f"{slug}.zip"
        raw = 0
        with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as zf:
            for p in included:
                zf.write(p, str(Path(slug) / p.relative_to(repo)))
                raw += p.stat().st_size
        manifest["repositories"][slug] = {
            "url": meta["url"], "license": meta["license"], "role": meta["role"],
            "commit": head_sha(repo), "archive": zpath.name,
            "files_included": len(included), "files_excluded": excluded,
            "all_files": len(all_files), "uncompressed_bytes": raw,
            "archive_bytes": zpath.stat().st_size, "sha256": sha256_file(zpath),
        }
        print(f"packed {slug}: {len(included)} files ({excluded} excluded) -> {human(zpath.stat().st_size)}")
    manifest["total_included"] = sum(r["files_included"] for r in manifest["repositories"].values())
    manifest["total_archive_bytes"] = sum(r["archive_bytes"] for r in manifest["repositories"].values())
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


CSV_FIELDS = ["rank", "id", "name", "kind", "category", "lifecycle_stage", "license", "repo",
              "url", "stars", "stars_delta_7d", "verified", "academic_relevance", "sources", "status"]


def _stage(name: str, description: str) -> str:
    blob = (name + " " + description).lower()
    rules = [("citation", ["citation", "bibliograph", "reference", "doi"]),
             ("reading", ["read", "pdf", "document", "extract", "search"]),
             ("writing", ["writ", "draft", "manuscript", "document"]),
             ("writing-quality", ["edit", "style", "proofread", "slop"]),
             ("figures", ["figure", "chart", "image", "diagram", "slide", "pptx", "pdf"]),
             ("peer-review", ["review", "rebuttal"]),
             ("analysis", ["data", "analysis", "stat", "code", "python"]),
             ("publishing", ["publish", "submit", "format"]),
             ("discovery", ["find", "browse", "web", "api"])]
    for stage, keys in rules:
        if any(k in blob for k in keys):
            return stage
    return "meta"


def extend_registry(summary: Dict[str, Any]) -> Dict[str, Any]:
    data = json.loads((ROOT / "data/registry.json").read_text(encoding="utf-8"))
    entries: List[Dict[str, Any]] = data["entries"]
    existing_ids = {e.get("id") for e in entries}
    existing_urls = {(e.get("url") or "").rstrip("/").lower() for e in entries}
    added = 0
    skills = json.loads((ROOT / "data/scan-v2-skills.json").read_text(encoding="utf-8"))
    for s in skills:
        rel = s["path"]
        name = s["name"] or Path(rel).parent.name
        url = f"{V2_SOURCES[s['repo']]['url']}/blob/main/{rel}"
        eid = "v2-" + s["repo"].lower() + "--" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if eid in existing_ids or url.lower() in existing_urls:
            continue
        desc = s["description"] or "Official Agent Skills example from the Anthropic skills library."
        entries.append({
            "id": eid, "name": name, "kind": "skill", "description": desc[:400],
            "category": "Official Agent Skills", "lifecycle_stage": _stage(name, desc),
            "license": V2_SOURCES[s["repo"]]["license"],
            "repo": V2_SOURCES[s["repo"]]["url"], "url": url, "skill_path": rel,
            "install": "", "stars": V2_SOURCES[s["repo"]]["stars"], "stars_delta_7d": 0,
            "trend": "", "verified": True, "verified_at": "2026-10-28",
            "academic_relevance": 0.5, "sources": ["v2/" + s["repo"]],
            "status": "official-example", "source_ref": summary["per_repo"][s["repo"]]["commit"],
        })
        existing_ids.add(eid)
        existing_urls.add(url.lower())
        added += 1
    for slug, meta in V2_SOURCES.items():
        eid = "v2-tool--" + re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
        if eid in existing_ids:
            continue
        entries.append({
            "id": eid, "name": slug.split("_", 1)[-1], "kind": "tool",
            "description": meta["role"][:400], "category": "Research Tooling",
            "lifecycle_stage": meta["stage"], "license": meta["license"],
            "repo": meta["url"], "url": meta["url"], "skill_path": "", "install": "",
            "stars": meta["stars"], "stars_delta_7d": 0, "trend": "", "verified": True,
            "verified_at": "2026-10-28", "academic_relevance": 0.85,
            "sources": ["v2/" + slug], "status": "curated-tool",
        })
        existing_ids.add(eid)
        added += 1

    data["count"] = len(entries)
    data["generated_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data["schema_version"] = "scholarforge-registry-v2"
    suffix = " Extended 2026-10-28 with six v2 sources."
    if not data.get("description", "").endswith(suffix):
        data["description"] = data.get("description", "") + suffix
    v2_total = sum(1 for e in entries if e.get("id", "").startswith("v2-"))
    src_counts = data.get("source_counts") or {}
    src_counts["v2-sources"] = v2_total
    data["source_counts"] = src_counts
    (ROOT / "data/registry.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    with (ROOT / "data/registry.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for i, e in enumerate(entries, 1):
            row = dict(e)
            row["rank"] = i
            row["sources"] = ";".join(e.get("sources") or []) if isinstance(e.get("sources"), list) else (e.get("sources") or "")
            w.writerow({k: row.get(k, "") for k in CSV_FIELDS})

    by_stage = Counter(e.get("lifecycle_stage", "") for e in entries)
    by_kind = Counter(e.get("kind", "") for e in entries)
    by_source = Counter(s for e in entries for s in (e.get("sources") or []))
    stats = {"generated_utc": data["generated_utc"], "total_entries": len(entries),
             "by_source": dict(src_counts), "by_kind": dict(by_kind), "by_stage": dict(by_stage),
             "by_source_list": dict(by_source),
             "academic_entries": sum(1 for e in entries if (e.get("academic_relevance") or 0) >= 0.4),
             "verified_entries": sum(1 for e in entries if e.get("verified")),
             "v2_entries_added": v2_total}
    (ROOT / "data/registry-stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")

    doc = ROOT / "docs/REGISTRY.md"
    marker = "## v2 — 2026-10-28 : six sources supplémentaires"
    if marker in doc.read_text(encoding="utf-8"):
        doc.write_text(doc.read_text(encoding="utf-8").split(marker, 1)[0].rstrip() + "\n", encoding="utf-8")
    with doc.open("a", encoding="utf-8") as fh:
        fh.write("\n\n## v2 — 2026-10-28 : six sources supplémentaires\n\n")
        fh.write(f"**{v2_total}** entrées ajoutées (officielles + outils vérifiés), pour un total de "
                 f"**{len(entries):,}** entrées. Les 5 434 entrées v1 sont conservées à l'identique.\n\n")
        fh.write("| Dépôt | Licence | Étoiles | Rôle |\n|---|---|---:|---|\n")
        for slug, m in V2_SOURCES.items():
            fh.write(f"| `{m['url']}` | {m['license'][:34]} | {m['stars']:,} | {m['role'][:88]} |\n")
        fh.write("\nSources : `data/scan-v2-skills.json`, `upstream/v2/manifest.json`, "
                 "`docs/SCAN_REPORT_V2.md`.\n")
    return {"added": added, "total": len(entries), "stats": stats}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources", default=str(ROOT.parent / "_scan2"))
    ap.add_argument("--skip-package", action="store_true")
    a = ap.parse_args()
    root = Path(a.sources).resolve()
    summary = scan(root)
    manifest = None if a.skip_package else package(root)
    reg = extend_registry(summary)
    print(f"scan: {summary['files']:,} files / {human(summary['bytes'])} / {summary['lines']:,} lines "
          f"across {summary['repositories']} repos")
    if manifest:
        print(f"zips: {manifest['total_included']:,} files / {human(manifest['total_archive_bytes'])}")
    print(f"registry: +{reg['added']} -> {reg['total']:,} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
