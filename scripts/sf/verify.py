"""Reference verification: offline integrity signals + optional DOI resolution.

Design rule inherited from the merged suites: never invent metadata. A reference
is only called "verified" when an authoritative registry returns matching
metadata. Everything else is explicitly labelled unverified.
"""

from __future__ import annotations

from typing import Any, Dict, List

from . import bib, sources
from .util import norm_doi, similarity


def verify(records: List[Dict[str, str]], online: bool = False, timeout: int = 8) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    seen: Dict[str, str] = {}
    for rec in records:
        rid = rec.get("id") or rec.get("title", "")[:50] or f"ref-{len(results)+1}"
        problems = bib.detect_problems(rec)
        doi = norm_doi(rec.get("doi", ""))
        if doi and doi in seen:
            problems.append("duplicate-doi:" + seen[doi])
        elif doi:
            seen[doi] = rid
        title = rec.get("title", "")
        status = "unverified-offline"
        resolved: Dict[str, Any] | None = None
        if doi:
            if online:
                r = sources.verify_doi(doi, timeout=timeout)
                resolved = r.get("crossref")
                if r["status"] == "resolved" and resolved:
                    score = similarity(title, resolved.get("title", ""))
                    if score >= 0.86:
                        status = "verified"
                    elif score >= 0.6:
                        status = "uncertain-match"
                        problems.append(f"title-similarity={score}")
                    else:
                        status = "mismatch"
                        problems.append(f"title-similarity={score}")
                    try:
                        y_local = int(str(rec.get("year", ""))[:4])
                        y_registry = int(str(resolved.get("year") or "0")[:4])
                        if y_registry and abs(y_local - y_registry) > 2:
                            problems.append("year-disagrees-with-registry")
                    except ValueError:
                        problems.append("unparseable-year")
                elif r["status"] == "invalid-format":
                    status = "invalid-doi"
                else:
                    status = "not-resolved"
                    problems.append("doi-did-not-resolve")
            else:
                status = "doi-present-unchecked"
        if problems and status.startswith(("verified", "doi-present")):
            status = "verified-with-warnings" if status == "verified" else "needs-review"
        elif problems and status == "unverified-offline":
            status = "needs-review"
        results.append({
            "id": rid, "title": title, "doi": doi, "status": status,
            "problems": sorted(set(problems)), "registry": resolved,
            "formatted": bib.format_ref(rec, "apa"),
        })
    counts: Dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    blockers = [r for r in results if r["status"] in ("mismatch", "invalid-doi", "not-resolved", "needs-review")]
    summary = {
        "total": len(results), "counts": counts,
        "blocking": len(blockers),
        "pass": not blockers,
        "online": online,
        "integrity_note": "A passing check means metadata is consistent with the cited registry. "
                          "It does not prove the source supports the manuscript's claim.",
    }
    return {"summary": summary, "results": results}


def to_markdown(report: Dict[str, Any]) -> str:
    s = report["summary"]
    lines = ["# Rapport de vérification des références", "",
             f"- Références : **{s['total']}**",
             f"- Mode : {'en ligne (Crossref)' if s['online'] else 'hors ligne (signaux locaux uniquement)'}",
             f"- Bloquants : **{s['blocking']}** — verdict : {'PASS' if s['pass'] else 'FAIL'}", "",
             "| Statut | Nombre |", "|---|---:|"]
    for k, v in sorted(s["counts"].items()):
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## Détail", "", "| # | Référence | Statut | Signaux |", "|---:|---|---|---|"]
    for i, r in enumerate(report["results"], 1):
        title = (r["title"] or r["id"])[:70].replace("|", "/")
        lines.append(f"| {i} | {title} | `{r['status']}` | {', '.join(r['problems']) or '—'} |")
    if s["online"]:
        lines += ["", "## Métadonnées de registre", ""]
        for r in report["results"]:
            if r["registry"]:
                lines.append(f"- **{r['doi']}** → {r['registry'].get('title','')} "
                             f"({r['registry'].get('year','')}, {r['registry'].get('journal','')})")
    lines += ["", "> " + s["integrity_note"], ""]
    return "\n".join(lines)
