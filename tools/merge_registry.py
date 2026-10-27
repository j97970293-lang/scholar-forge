#!/usr/bin/env python3
"""merge_registry.py -- fuse every catalogue found in the eight sources.

Inputs (all optional; the tool reports what it actually found):
  O0000-code/data/skills/*.yml + data/backlog.yml      (YAML, 223 + 749 records)
  cosen1024/data/skills.yaml                            (YAML, verified + pinned)
  kael-odin/data/rankings.json                         (JSON, stars/trend)
  KalarisLabs/catalog/skills.json                      (JSON, 200+ skills)
  ranbot-ai/data/skills.json                           (JSON, 1129+ skills)
  miketepUR/README.md                                  (Markdown links)
  all upstream SKILL.md via data/source-skills.json     (scanned frontmatter)

Outputs:
  data/registry.json          unified, de-duplicated records
  data/registry.csv           flat export (id, name, kind, category, ...)
  data/registry-stats.json    counts / coverage
  data/rankings-snapshot.json latest star & trend snapshot
  docs/REGISTRY.md            curated view

Build dependency: PyYAML (only for this build tool; the shipped skill runs stdlib only).
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    ROOT, SCAN_ROOT, SOURCES, frontmatter, load_json, normalise_repo_url,
    read_text, slugify, write_json,
)

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

ACADEMIC = [
    "academic", "research", "paper", "manuscript", "thesis", "dissertation", "scholar",
    "literature", "citation", "bibliograph", "reference", "peer review", "reviewer",
    "prisma", "systematic review", "meta-analysis", "evidence", "hypothesis", "experiment",
    "scientific", "science", "journal", "conference", "arxiv", "pubmed", "openalex",
    "crossref", "latex", "bibtex", "apa", "ieee", "vancouver", "grant", "proposal",
    "rebuttal", "submission", "reproducib", "statistic", "data analysis", "figure",
    "plot", "writing", "proofread", "plagiar", "ethic", "preprint", "doi", "study",
]
STAGE_KEYS = [
    ("discovery", ["search", "discover", "literature", "arxiv", "pubmed", "database", "lookup", "harvest"]),
    ("citation", ["citation", "reference", "bibliograph", "bibtex", "zotero", "apa", "ris"]),
    ("reading", ["read", "summar", "pdf", "ocr", "parse", "rag", "knowledge"]),
    ("analysis", ["statistic", "analysis", "data", "experiment", "simulation", "model"]),
    ("figures", ["figure", "plot", "visuali", "schematic", "poster", "graphic"]),
    ("writing", ["writ", "draft", "paper", "manuscript", "thesis", "grant", "proposal"]),
    ("writing-quality", ["slop", "humaniz", "polish", "proofread", "style", "de-ai", "edit"]),
    ("peer-review", ["review", "referee", "rebuttal", "audit", "critique"]),
    ("publishing", ["submission", "venue", "template", "format", "arxiv-submission", "publish"]),
    ("suite", ["suite", "pipeline", "orchestrat", "agent", "collection", "awesome"]),
]


def relevance(rec: Dict[str, Any]) -> float:
    blob = " ".join(str(rec.get(k, "")) for k in ("name", "description", "category", "tags")).lower()
    hits = sum(1 for kw in ACADEMIC if kw in blob)
    return round(min(1.0, hits / 5.0), 3)


def stage(rec: Dict[str, Any]) -> str:
    blob = " ".join(str(rec.get(k, "")) for k in ("name", "description", "category")).lower()
    for name, keys in STAGE_KEYS:
        if any(k in blob for k in keys):
            return name
    return "meta"


def base(**kw: Any) -> Dict[str, Any]:
    out = {
        "id": "", "name": "", "kind": "skill", "description": "", "category": "",
        "lifecycle_stage": "", "license": "", "repo": "", "url": "", "skill_path": "",
        "install": "", "stars": 0, "stars_delta_7d": 0, "trend": "", "verified": False,
        "verified_at": "", "network": False, "tags": [], "sources": [], "status": "listed",
        "notes": "", "academic_relevance": 0.0,
    }
    out.update(kw)
    return out


def add(store: Dict[str, Dict[str, Any]], rec: Dict[str, Any], source: str) -> None:
    name = rec.get("name") or rec.get("id") or ""
    repo = normalise_repo_url(rec.get("repo", "") or rec.get("url", ""))
    key = (repo or slugify(rec.get("url", "")), slugify(name))
    rec["academic_relevance"] = max(rec.get("academic_relevance", 0.0), relevance(rec))
    rec["lifecycle_stage"] = rec.get("lifecycle_stage") or stage(rec)
    if key in store:
        cur = store[key]
        for f in ("description", "category", "license", "url", "skill_path", "install", "notes", "trend"):
            if not cur.get(f) and rec.get(f):
                cur[f] = rec[f]
        for f in ("stars", "stars_delta_7d", "academic_relevance"):
            cur[f] = max(cur.get(f) or 0, rec.get(f) or 0)
        cur["verified"] = cur["verified"] or rec["verified"]
        cur["network"] = cur["network"] or rec["network"]
        cur["sources"] = sorted(set(cur["sources"] + [source]))
        cur["tags"] = sorted(set((cur.get("tags") or []) + (rec.get("tags") or [])))[:20]
        return
    rec["sources"] = [source]
    rec["id"] = rec.get("id") or (slugify(repo) + "--" + slugify(name))
    store[key] = rec


def yload(path: Path) -> Any:
    if yaml is None:
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    store: Dict[str, Dict[str, Any]] = {}
    stats: Counter = Counter()
    src = SCAN_ROOT

    # 1. O0000-code curated records
    d = src / "O0000-code_awesome-academic-skills/data/skills"
    if d.is_dir():
        for p in sorted(d.glob("*.yml")):
            o = yload(p) or {}
            net = bool((o.get("security") or {}).get("makes_network_calls"))
            add(store, base(
                name=o.get("name") or p.stem, description=o.get("description", ""),
                category=o.get("category", ""), lifecycle_stage=o.get("lifecycle_stage", ""),
                license=o.get("license", ""), repo=o.get("source_url", ""),
                url=o.get("source_url", ""), kind=o.get("type", "skill"),
                network=net, verified=True, tags=[str(t) for t in (o.get("tags") or [])][:10],
            ), "O0000-code/awesome-academic-skills")
            stats["O0000-listed"] += 1
    backlog = src / "O0000-code_awesome-academic-skills/data/backlog.yml"
    if backlog.exists():
        o = yload(backlog) or {}
        for e in o.get("entries", []) or []:
            if not isinstance(e, dict):
                continue
            add(store, base(
                name=e.get("repo", "").split("/")[-1] or e.get("repo", ""),
                description=str(e.get("held_for", ""))[:240], repo=e.get("url", ""),
                url=e.get("url", ""), stars=e.get("stars", 0) or 0,
                status="backlog", kind="suite",
            ), "O0000-code/awesome-academic-skills (backlog)")
            stats["O0000-backlog"] += 1

    # 2. cosen1024 verified catalogue
    p = src / "cosen1024_awesome-academic-skills/data/skills.yaml"
    if p.exists():
        o = yload(p) or {}
        catmap = {c.get("id"): c.get("name_en", "") for c in (o.get("categories") or [])}
        for e in o.get("skills", []) or []:
            add(store, base(
                name=e.get("skill") or e.get("id", ""),
                description=e.get("purpose_en") or e.get("purpose_zh", ""),
                category=catmap.get(e.get("category"), e.get("category", "")),
                lifecycle_stage=stage({"category": catmap.get(e.get("category"), "")}),
                repo=e.get("repository_url", ""), url=e.get("source_url", ""),
                skill_path=e.get("skill_path", ""), license=e.get("license", ""),
                install=e.get("install_command", ""), verified=e.get("verification_status") == "verified",
                verified_at=str(e.get("verified_at", "")), kind=e.get("entry_type", "skill"),
                notes=(e.get("notes_en") or "")[:240],
                tags=[str(x) for x in (e.get("platforms") or [])][:10],
            ), "cosen1024/awesome-academic-skills")
            stats["cosen1024"] += 1

    # 3. kael-odin rankings
    p = src / "kael-odin_awesome-academic-research-skills/data/rankings.json"
    if p.exists():
        o = load_json(p, {}) or {}
        write_json(ROOT / "data/rankings-snapshot.json", o)
        for e in o.get("items", []) or []:
            lic = (e.get("license") or {}).get("spdx_id", "") if isinstance(e.get("license"), dict) else ""
            add(store, base(
                name=e.get("repo", "").split("/")[-1] or e.get("repo", ""),
                description=e.get("description", ""), category=(e.get("category") or {}).get("en", ""),
                repo=e.get("url", ""), url=e.get("url", ""), license=lic,
                stars=e.get("stars", 0) or 0, stars_delta_7d=e.get("star_delta_7d", 0) or 0,
                trend=(e.get("trend") or {}).get("id", ""), kind="suite",
                tags=[str(t) for t in (e.get("topics") or [])][:12],
                notes="skills_count=%s" % e.get("skills_count", ""),
            ), "kael-odin/awesome-academic-research-skills")
            stats["kael-odin"] += 1

    # 4. Kalaris catalog
    p = src / "KalarisLabs_research-agent-skills/catalog/skills.json"
    if p.exists():
        o = load_json(p, {}) or {}
        for e in o.get("skills", []) or []:
            if not isinstance(e, dict):
                continue
            add(store, base(
                name=e.get("name") or e.get("id", ""), description=e.get("description", ""),
                category=e.get("category", ""), repo=o.get("repository", ""),
                url=e.get("url", "") or e.get("path", ""), tags=[str(t) for t in (e.get("tags") or [])][:10],
                license="MIT",
            ), "KalarisLabs/research-agent-skills (catalog)")
            stats["kalaris-catalog"] += 1

    # 5. ranbot-ai aggregator
    p = src / "ranbot-ai_awesome-skills/data/skills.json"
    if p.exists():
        o = load_json(p, {}) or {}
        for e in o.get("skills", []) or []:
            if not isinstance(e, dict):
                continue
            add(store, base(
                name=e.get("name", ""), description=(e.get("description") or "")[:400],
                category=e.get("category", ""), repo=e.get("repoUrl", ""),
                url=e.get("skillUrl", "") or e.get("repoUrl", ""),
                tags=[str(e.get("source", ""))], notes="aggregator source: %s" % e.get("source", ""),
            ), "ranbot-ai/awesome-skills")
            stats["ranbot-ai"] += 1

    # 6. miketepUR README links
    p = src / "miketepUR_awesome-claude-skills/README.md"
    if p.exists():
        txt = read_text(p)
        for name, url in re.findall(r"\[([^\]\[]{2,80})\]\((https?://[^)\s]+)\)", txt):
            if "github.com" not in url or url.endswith((".png", ".svg", ".jpg")):
                continue
            clean = re.sub(r"[`*_]", "", name).strip()
            if not clean or clean.lower() in ("here", "read more", "link", "source"):
                continue
            add(store, base(name=clean, repo=url, url=url, kind="link",
                            description="Listed in miketepUR/awesome-claude-skills"),
                "miketepUR/awesome-claude-skills")
            stats["miketepUR"] += 1

    # 7. every upstream SKILL.md (from the exhaustive scan)
    scanned_skills = load_json(ROOT / "data/source-skills.json", []) or []
    for s in scanned_skills:
        add(store, base(
            name=s.get("name", ""), description=s.get("description", ""),
            category=s.get("category", ""), license=s.get("license", ""),
            repo=SOURCES.get(s["repo"], {}).get("url", "") + "/" + s["path"].split("/")[0],
            url=SOURCES.get(s["repo"], {}).get("url", "") + "/blob/main/" + s["path"],
            skill_path=s["path"], kind="skill", tags=[s["repo"].split("_")[0]],
            notes="bundled upstream SKILL.md (full text in upstream/*.zip)",
        ), s["repo"] + " (SKILL.md)")
        stats["SKILL.md"] += 1

    records = sorted(store.values(), key=lambda r: (-r["academic_relevance"], -(r["stars"] or 0), r["name"].lower()))
    for i, r in enumerate(records, 1):
        r["rank"] = i
        r["tags"] = [t for t in r["tags"] if t][:12]
    write_json(ROOT / "data/registry.json", {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "schema_version": "1.0",
        "description": "Unified academic agent-skill registry merged from all eight source repositories.",
        "count": len(records), "source_counts": dict(stats), "entries": records,
    }, indent=1)
    cols = ["rank", "id", "name", "kind", "category", "lifecycle_stage", "license", "repo",
            "url", "stars", "stars_delta_7d", "verified", "academic_relevance", "sources", "status"]
    with (ROOT / "data/registry.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in records:
            row = dict(r)
            row["sources"] = ";".join(r["sources"])
            w.writerow(row)
    stats_out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_entries": len(records), "by_source": dict(stats),
        "by_kind": dict(Counter(r["kind"] for r in records)),
        "by_stage": dict(Counter(r["lifecycle_stage"] for r in records)),
        "academic_entries": sum(1 for r in records if r["academic_relevance"] >= 0.4),
        "verified_entries": sum(1 for r in records if r["verified"]),
        "backlog_entries": sum(1 for r in records if r["status"] == "backlog"),
        "github_repos": len({r["repo"] for r in records if r["repo"]}),
    }
    write_json(ROOT / "data/registry-stats.json", stats_out)

    L = ["# ScholarForge — registre unifié\n",
         f"Généré par `tools/merge_registry.py` le `{stats_out['generated_utc']}`. "
         f"**{len(records):,}** entrées dédupliquées issues des {len(stats)} catalogues amont. "
         "Champs complets dans `data/registry.json`, export plat dans `data/registry.csv`.\n",
         "## Couverture\n",
         "| Jeu de données | Entrées |\n|---|---:|"]
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        L.append(f"| `{k}` | {v:,} |")
    L.append(f"\n| Total dédupliqué | **{len(records):,}** |")
    L.append(f"| Entrées à pertinence académique ≥ 0,4 | {stats_out['academic_entries']:,} |")
    L.append(f"| Entrées vérifiées | {stats_out['verified_entries']:,} |")
    L.append(f"| Dépôts GitHub distincts | {stats_out['github_repos']:,} |\n")
    L.append("## Répartition par étape du cycle de recherche\n")
    L.append("| Étape | Entrées |\n|---|---:|")
    for k, v in sorted(stats_out["by_stage"].items(), key=lambda x: -x[1]):
        L.append(f"| `{k}` | {v:,} |")
    L.append("\n## Top 40 par étoiles\n")
    L.append("| # | Nom | Dépôt | ★ | Δ7j | Étape |\n|---:|---|---|---:|---:|---|")
    for r in sorted(records, key=lambda r: -(r["stars"] or 0))[:40]:
        L.append(f"| {r['rank']} | `{r['name'][:38]}` | `{str(r['repo'])[-46:]}` | {r['stars']:,} | "
                 f"{r['stars_delta_7d']:,} | {r['lifecycle_stage']} |")
    L.append("\n## Exploitation\n")
    L.append("```bash\npython3 scripts/scholarforge.py registry search --query \"citation verification\" --limit 10\n"
             "python3 scripts/scholarforge.py registry stats\n```\n")
    (ROOT / "docs/REGISTRY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("registry entries:", len(records), "from", dict(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
