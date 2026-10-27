"""Query the unified academic skill registry built from all eight sources."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from .util import ROOT, read_json


def load() -> Dict[str, Any]:
    return read_json(ROOT / "data/registry.json", {"entries": [], "count": 0}) or {"entries": [], "count": 0}


def _score(entry: Dict[str, Any], terms: List[str]) -> float:
    blob = " ".join(str(entry.get(k, "")) for k in ("name", "description", "category", "tags", "repo")).lower()
    hits = sum(1 for t in terms if t in blob)
    if not hits:
        return 0.0
    return hits / len(terms) + min(0.3, (entry.get("academic_relevance") or 0) * 0.2) + (
        0.05 if entry.get("verified") else 0.0)


def search(query: str, limit: int = 10, stage: str = "", min_relevance: float = 0.0,
           verified_only: bool = False) -> Dict[str, Any]:
    data = load()
    terms = [t for t in re.split(r"[^a-z0-9+]+", query.lower()) if t]
    out: List[Dict[str, Any]] = []
    for e in data.get("entries", []):
        if stage and e.get("lifecycle_stage") != stage:
            continue
        if (e.get("academic_relevance") or 0) < min_relevance:
            continue
        if verified_only and not e.get("verified"):
            continue
        score = _score(e, terms)
        if score > 0:
            out.append({**{k: e.get(k) for k in ("name", "kind", "category", "lifecycle_stage",
                                                 "license", "repo", "url", "stars", "verified",
                                                 "academic_relevance", "sources", "status")},
                        "score": round(score, 4)})
    out.sort(key=lambda r: (-r["score"], -(r["stars"] or 0), r["name"]))
    return {"query": query, "count": len(out), "results": out[:limit],
            "registry_size": data.get("count", 0)}


def stats() -> Dict[str, Any]:
    data = load()
    entries = data.get("entries", [])
    return {
        "total": len(entries),
        "by_stage": dict(Counter(e.get("lifecycle_stage", "") for e in entries)),
        "by_kind": dict(Counter(e.get("kind", "") for e in entries)),
        "by_source_list": dict(Counter(s for e in entries for s in e.get("sources", []))),
        "verified": sum(1 for e in entries if e.get("verified")),
        "academic": sum(1 for e in entries if (e.get("academic_relevance") or 0) >= 0.4),
        "generated_utc": data.get("generated_utc", ""),
    }
