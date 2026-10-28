"""Reproducible search log (PRISMA-S style provenance for gate G2).

The skill promises "every query logged with database, string, filters, date and
hit count". This module is the machine that honours that promise: each ``search``
invocation appends one row per database to ``sources/search-log.md`` and a
machine-readable twin ``sources/search-log.json``.

No network access, no dependencies. Offline-friendly: each invocation adds rows (repeating a search is a new event).
Malformed history is never silently overwritten. Use a single writer per project.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .util import read_json, read_text, write_json, write_text

MD_NAME = "search-log.md"
JSON_NAME = "search-log.json"
HEADER = [
    "# Search log — ScholarForge",
    "",
    "Append-only provenance for gate G2 (reproducible search). One row per database, per query.",
    "PRISMA-S asks for the full search string, the database/platform, the date, the limits",
    "applied and the number of records returned. All of those are recorded here.",
    "",
    "| UTC date | Database | Query | Requested filters | Retrieved | Unique (run) | Endpoint | CLI | Status |",
    "|---|---|---|---|---:|---:|---|---|---|",
]
FOOTER = [
    "",
    "## How to report this",
    "",
    "- Paste the table (or export `search-log.json`) into the supplementary material.",
    "- Record the exact interface searched (API vs web UI): they return different counts.",
    "- Note the retrieval date in the manuscript; counts drift as indexes update.",
    "- A requested filter is not always supported by every API. `search-log.json` records "
    "`filters_native`, `filters_applied` (local) and `filters_ignored` per database; say so in the methods.",
    "- Counts are retrieved records after filtering, NOT the total database hit count. "
    "The clients retrieve a bounded window, not every matching record.",
    "- Client-side filters act on the retrieved window only: raise `--limit` when filtering.",
    "- Re-run the search immediately before submission and log the new row too.",
    "",
]


def _filters_text(filters: Optional[Dict[str, Any]]) -> str:
    if not filters:
        return "none"
    bits = []
    for k in ("from_year", "to_year", "min_citations", "oa_only", "type"):
        v = filters.get(k)
        if v not in (None, "", False):
            bits.append(f"{k}={v}")
    return ", ".join(bits) or "none"


def _cell(value: Any, limit: int = 150) -> str:
    # Do not truncate query strings or endpoints: reproducibility needs the full value.
    return str(value if value is not None else "").replace("|", "&#124;").replace("\n", "<br>")


def entries_from_report(rep: Dict[str, Any], filters: Optional[Dict[str, Any]] = None,
                        cli_version: str = "") -> List[Dict[str, Any]]:
    """Turn a ``sources.search_all`` report into one log entry per database."""
    stamp = rep.get("retrieved_at") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    out: List[Dict[str, Any]] = []
    for name, r in (rep.get("sources") or {}).items():
        applied = (rep.get("filters_applied") or {}).get(name, {})
        out.append({
            "date_utc": stamp,
            "database": name,
            "platform": "REST API",
            "query": rep.get("query", ""),
            "filters": _filters_text(filters),
            "filters_applied": applied.get("applied", []),
            "filters_native": applied.get("native", []),
            "filters_ignored": applied.get("ignored", []),
            "filters_details": applied,
            "count_scope": "retrieved-window-after-filters",
            "retrieved_before_filters": r.get("retrieved_before_filters", r.get("count", 0)),
            "requested_limit": r.get("requested_limit"),
            "hits": r.get("count", 0),
            "unique": rep.get("unique_hits", 0),
            "endpoint": r.get("url", ""),
            "cli_version": cli_version,
            "status": "ok" if r.get("ok") else "error",
            "error": (r.get("error") or "")[:200],
        })
    return out


def append(root: Path | str, report: Dict[str, Any],
           filters: Optional[Dict[str, Any]] = None, cli_version: str = "") -> Dict[str, Any]:
    root = Path(root)
    src = root / "sources"
    src.mkdir(parents=True, exist_ok=True)
    json_path, md_path = src / JSON_NAME, src / MD_NAME
    history: List[Dict[str, Any]] = []
    if json_path.exists():
        try:
            history = json.loads(read_text(json_path))
        except ValueError as exc:
            raise ValueError(f"search history is invalid; preserved unchanged: {json_path}") from exc
        if not isinstance(history, list) or not all(isinstance(r, dict) for r in history):
            raise ValueError(f"search history must be a list of rows; preserved unchanged: {json_path}")
    new = entries_from_report(report, filters, cli_version)
    history.extend(new)
    write_json(json_path, history)

    lines: List[str]
    if md_path.exists():
        existing = read_text(md_path).splitlines()
        # Keep everything above the footer; append new rows at the end of the table.
        lines = list(existing)  # retain ALL old data rows and manual annotations
        # Strip old footer if present.
        try:
            cut = next(i for i, ln in enumerate(lines) if ln.strip() == "## How to report this")
            lines = lines[:cut]
        except StopIteration:
            pass
        while lines and not lines[-1].strip():
            lines.pop()
    else:
        lines = list(HEADER)
    for e in new:
        lines.append("| " + " | ".join([
            _cell(e["date_utc"], 25), _cell(e["database"], 20), _cell(e["query"], 110),
            _cell(e["filters"], 70), str(e["hits"]), str(e["unique"]),
            _cell(e["endpoint"], 150), _cell(e["cli_version"], 12),
            _cell(e["status"] + (" " + e["error"] if e["error"] else ""), 60),
        ]) + " |")
    lines += FOOTER
    write_text(md_path, "\n".join(lines) + "\n")
    return {"rows_added": len(new), "total_rows": len(history),
            "markdown": str(md_path), "json": str(json_path)}


def read(root: Path | str) -> List[Dict[str, Any]]:
    data = read_json(Path(root) / "sources" / JSON_NAME, []) or []
    return data if isinstance(data, list) else []


def summary(root: Path | str) -> Dict[str, Any]:
    rows = read(root)
    by_db: Dict[str, int] = {}
    for r in rows:
        by_db[r.get("database", "?")] = by_db.get(r.get("database", "?"), 0) + int(r.get("hits") or 0)
    dates = [r.get("date_utc", "")[:10] for r in rows if r.get("date_utc")]
    return {"queries": len(rows), "hits": sum(by_db.values()), "by_database": by_db,
            "first": min(dates) if dates else "", "last": max(dates) if dates else "",
            "complete": bool(rows) and all(r.get("query") and r.get("endpoint") for r in rows)}


def to_markdown(root: Path | str) -> str:
    s = summary(root)
    L = ["# Search-log summary", "",
         f"- Rows: **{s['queries']}** | retrieved records: **{s['hits']}**",
         f"- Period: {s['first'] or '—'} → {s['last'] or '—'}",
         f"- Recorded API provenance complete: **{'yes' if s['complete'] else 'no'}**", "",
         "| Database | Hits |", "|---|---:|"]
    for k, v in sorted(s["by_database"].items()):
        L.append(f"| {k} | {v} |")
    return "\n".join(L) + "\n"
