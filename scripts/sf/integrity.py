"""Research-integrity signals: retraction, correction and concern detection.

Design constraint (2025--2026 evidence, see docs/RESEARCH_NOTES.md):

* OpenAlex exposes a single boolean ``is_retracted`` derived from the Retraction
  Watch database. It is known to have produced false positives when corrections
  or expressions of concern were conflated with retractions, and it misses some
  retractions. It is a *signal*, never a verdict.
* Crossref's public ``/works/{doi}`` response now carries ``updated-by`` notices
  with ``type`` (retraction / correction / expression-of-concern / ...) and
  ``source: retraction-watch``. This is a second, partly independent signal.
* Publisher title markers ("RETRACTED:", "WITHDRAWN:") are a third signal that
  also works completely offline.

Therefore this module NEVER claims a paper is retracted. It reports how many
signal families agree, where they came from, and what a human must still
check on the publisher's page. Registers disagree materially; a single flag is
labelled ``suspected`` and is non-blocking by default.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .util import norm_doi

UA = "ScholarForge/1.1 (retraction-signal check; stdlib urllib)"
DEFAULT_TIMEOUT = 10
SCREENING_SCHEMA = "scholarforge-integrity-v2"
CACHE_MAX_AGE_SECONDS = 24 * 60 * 60


def fingerprint(records: List[Dict[str, Any]]) -> str:
    payload = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def cache_matches(report: Any, records: List[Dict[str, Any]],
                  max_age: int = CACHE_MAX_AGE_SECONDS) -> bool:
    if not isinstance(report, dict) or report.get("schema") != SCREENING_SCHEMA:
        return False
    if report.get("input_sha256") != fingerprint(records):
        return False
    summary = report.get("summary")
    results = report.get("results")
    if not isinstance(summary, dict) or not isinstance(results, list):
        return False
    if summary.get("records") != len(records) or len(results) != len(records):
        return False
    if not all(isinstance(r, dict) and "verdict" in r and "blocking" in r for r in results):
        return False
    if summary.get("blocking") != sum(bool(r["blocking"]) for r in results):
        return False
    if summary.get("pass") is not (not any(r["blocking"] for r in results)):
        return False
    try:
        stamp = datetime.fromisoformat(summary["generated_at"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - stamp).total_seconds()
        return 0 <= age <= max_age
    except (ValueError, TypeError, KeyError):
        return False

TITLE_MARKERS = [
    (re.compile(r"^\s*\[?\s*retracted\b", re.I), "title:retracted"),
    (re.compile(r"^\s*\[?\s*withdrawn\b", re.I), "title:withdrawn"),
    (re.compile(r"^\s*\[?\s*retraction note\b", re.I), "title:retraction-note"),
    (re.compile(r"\bexpression of concern\b", re.I), "title:expression-of-concern"),
    (re.compile(r"\bcorrigend(?:um|a)\b|\bcorrection:\s", re.I), "title:correction"),
]

RETRACTION_TYPES = {"retraction", "retracted", "withdrawal", "withdrawn", "removal"}
CONCERN_TYPES = {"correction", "corrected", "expression-of-concern", "expression of concern",
                 "erratum", "concern", "updated", "reinstated"}

CAVEATS = [
    "Registers disagree: Crossref/Retraction Watch, OpenAlex, PubMed and Europe PMC do not "
    "cover the same notices. Absence of a signal is not proof of integrity.",
    "OpenAlex is_retracted is a single boolean derived from Retraction Watch; it has "
    "mislabelled corrections/expressions of concern as retractions and can lag.",
    "OpenAlex and Crossref may share the same Retraction Watch source. Agreement between "
    "APIs is corroboration, not two fully independent investigations.",
    "Only DOIs present in the bibliography can be checked; cited reprints, preprints and "
    "versions without DOIs are invisible here.",
    "A notice attached to a DOI does not tell you whether the manuscript relies on the "
    "retracted finding. A human must read the notice and the citing sentence.",
]


def title_signals(title: str) -> List[str]:
    """Return offline integrity signals found in a work's title."""
    return [label for pattern, label in TITLE_MARKERS if pattern.search(title or "")]


def _get_json(url: str, timeout: int) -> Tuple[bool, Any, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, json.loads(resp.read().decode("utf-8", errors="replace")), ""
    except ValueError as exc:
        return False, None, f"invalid JSON: {exc}"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


def openalex_signal(doi: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    url = "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/")
    ok, data, error = _get_json(url, timeout)
    return {"source": "openalex", "ok": ok, "error": error, "url": url,
            "is_retracted": bool(data.get("is_retracted")) if ok and isinstance(data, dict) else None,
            "title": (data.get("title") or "") if ok and isinstance(data, dict) else ""}


def crossref_signal(doi: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Read Crossref ``updated-by`` / ``update-to`` / ``relation`` notices."""
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
    ok, data, error = _get_json(url, timeout)
    if not ok:
        return {"source": "crossref", "ok": False, "error": error, "url": url,
                "notices": [], "title": ""}
    msg = (data or {}).get("message") or {}
    notices: List[Dict[str, Any]] = []
    for n in (msg.get("updated-by") or []):
        if not isinstance(n, dict):
            continue
        notice = {"type": str(n.get("type") or "").lower(),
                  "label": n.get("label") or "", "source": n.get("source") or "",
                  "notice_doi": n.get("DOI") or "",
                  "date": ""}
        parts = ((n.get("updated") or {}).get("date-parts") or [[]])[0]
        if parts:
            notice["date"] = "-".join(f"{int(p):02d}" if i == 0 else f"{int(p):02d}"
                                      for i, p in enumerate(parts[:3])) if parts[0] else ""
        notices.append(notice)
    for rel in ("is-retracted-by", "has-retraction"):
        for n in (msg.get("relation") or {}).get(rel, []) if isinstance(msg.get("relation"), dict) else []:
            if isinstance(n, dict) and n.get("id"):
                notices.append({"type": "retraction", "label": rel, "source": "crossref-relation",
                                "notice_doi": str(n["id"]), "date": ""})
    for n in (msg.get("update-to") or []) if isinstance(msg.get("update-to"), list) else []:
        if isinstance(n, dict):
            # update-to points FROM a notice TO another work: it does not mean this DOI is retracted.
            notices.append({"type": "outgoing-update", "update_type": str(n.get("type") or "update").lower(),
                            "label": n.get("label") or "",
                            "source": "crossref-update-to", "notice_doi": n.get("DOI") or "", "date": ""})
    titles = msg.get("title") or [""]
    return {"source": "crossref", "ok": True, "error": "", "url": url,
            "notices": notices, "title": titles[0] if titles else ""}


def classify(signals: List[str], notices: List[Dict[str, Any]], online: bool) -> Dict[str, Any]:
    """Combine signals into an honest, non-definitive verdict."""
    retraction_signals = [s for s in signals if s in ("openalex:is_retracted",
                                                      "crossref:retraction", "title:retracted",
                                                      "title:withdrawn", "title:retraction-note")]
    # Multiple markers on one title are one family, not independent corroboration.
    retraction_signals = list(dict.fromkeys(retraction_signals))
    families = {s.split(":", 1)[0] for s in retraction_signals}
    concern_notices = [n for n in notices if n.get("type") in CONCERN_TYPES
                       or n.get("type") in ("expression of concern",)]
    title_only = any(s.startswith("title:") for s in signals)
    if len(families) >= 2:
        verdict, blocking = "retracted-confirmed", True
    elif retraction_signals:
        # A publisher-authored "RETRACTED:" title is strong even offline.
        verdict = "retracted-suspected"
        blocking = any(s in ("title:retracted", "title:withdrawn") for s in retraction_signals)
    elif notices or any(s.startswith("title:") for s in signals):
        verdict, blocking = "notice-found", False
    elif not online:
        verdict, blocking = "not-checked", False
    elif not signals and not notices:
        # Distinguish "both registries answered clean" from "nothing answered".
        verdict, blocking = "no-signal", False
    else:
        verdict, blocking = "no-signal", False
    return {"verdict": verdict, "blocking": blocking, "retraction_signals": retraction_signals,
            "title_only": title_only, "concern_notices": len(concern_notices)}


def check_record(rec: Dict[str, str], online: bool = False,
                 timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    doi = norm_doi(rec.get("doi", ""))
    title = rec.get("title", "") or ""
    rid = rec.get("id") or title[:60] or doi or "unnamed"
    signals: List[str] = list(title_signals(title))
    notices: List[Dict[str, Any]] = []
    sources: Dict[str, Any] = {}
    lookup_ok = 0
    lookup_failed = 0

    if online and doi and re.match(r"^10\.\d{4,9}/\S+$", doi):
        oa = openalex_signal(doi, timeout)
        cr = crossref_signal(doi, timeout)
        sources = {"openalex": {"ok": oa["ok"], "error": oa["error"], "url": oa["url"],
                                "is_retracted": oa["is_retracted"]},
                   "crossref": {"ok": cr["ok"], "error": cr["error"], "url": cr["url"],
                                "notice_count": len(cr["notices"])}}
        lookup_ok = int(oa["ok"]) + int(cr["ok"])
        lookup_failed = 2 - lookup_ok
        if oa["ok"] and oa["is_retracted"]:
            signals.append("openalex:is_retracted")
        if not oa["ok"]:
            signals.append("lookup-failed:openalex")
        if not cr["ok"]:
            signals.append("lookup-failed:crossref")
        notices = cr["notices"]
        if any(n.get("type") in RETRACTION_TYPES for n in notices):
            signals.append("crossref:retraction")
        for n in notices:
            signals.append("notice:" + (n.get("type") or "unknown"))
        if cr["ok"] and cr.get("title"):
            # Check registry titles even when the supplied BibTeX title is out of date.
            signals.extend(title_signals(cr["title"]))
            if not title:
                title = cr["title"]
    elif online and doi:
        signals.append("invalid-doi")
        lookup_failed = 1

    cls = classify([s for s in signals if not s.startswith(("lookup-failed", "notice:", "invalid"))],
                   notices, online)
    if online and lookup_failed >= 2 and not any(s.startswith(("openalex:", "crossref:", "title:")) for s in signals):
        cls["verdict"] = "lookup-failed"
        cls["blocking"] = False
    if online and not sources and not title_signals(title):
        cls["verdict"] = "invalid-doi" if doi else "not-checked"
    signals = list(dict.fromkeys(signals))
    return {"id": rid, "doi": doi, "title": title, "checked_online": bool(sources),
            **cls, "signals": signals, "notices": notices, "sources_checked": sources,
            "lookups_ok": lookup_ok, "lookups_failed": lookup_failed}


def check(records: List[Dict[str, str]], online: bool = False,
          timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    results = [check_record(r, online, timeout) for r in records]
    counts: Dict[str, int] = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    blocking = [r for r in results if r["blocking"]]
    return {
        "schema": SCREENING_SCHEMA, "input_sha256": fingerprint(records),
        "summary": {
            "records": len(results), "online": online, "counts": counts,
            "blocking": len(blocking), "pass": not blocking,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "integrity_note": "Multi-signal screening only. Confirm any notice on the publisher "
                              "page before acting; see docs/RESEARCH_NOTES.md.",
        },
        "results": results, "caveats": CAVEATS,
    }


def to_markdown(report: Dict[str, Any]) -> str:
    s = report["summary"]
    L = ["# Integrity screening — retractions, corrections, concerns", "",
         f"- Références : **{s['records']}**",
         f"- Mode : {'en ligne (OpenAlex + Crossref)' if s['online'] else 'hors ligne (titres uniquement)'}",
         f"- Bloquants : **{s['blocking']}** — verdict : {'FAIL' if not s['pass'] else 'PASS'}",
         f"- Généré : `{s['generated_at']}`", "",
         "| Verdict | Nombre |", "|---|---:|"]
    for k, v in sorted(s["counts"].items()):
        L.append(f"| `{k}` | {v} |")
    L += ["", "## Détail", "",
          "| # | Référence | DOI | Verdict | Signaux |", "|---:|---|---|---|---|"]
    for i, r in enumerate(report["results"], 1):
        t = (r["title"] or r["id"])[:62].replace("|", "/")
        sig = ", ".join(x for x in r["signals"] if not x.startswith("notice:")) or "—"
        L.append(f"| {i} | {t} | {(r['doi'] or '—')[:34]} | `{r['verdict']}` | {sig[:110]} |")
    notices = [(r, n) for r in report["results"] for n in r["notices"]]
    if notices:
        L += ["", "## Notices Crossref", ""]
        for r, n in notices:
            L.append(f"- **{r['doi'] or r['id']}** — `{n.get('type')}` {n.get('label')} "
                     f"(source {n.get('source')}, {n.get('date') or 'date inconnue'}) "
                     f"{('→ ' + n['notice_doi']) if n.get('notice_doi') else ''}")
    L += ["", "## Limites — à lire avant toute décision", ""]
    L += ["- " + c for c in report["caveats"]]
    L += ["", "> " + s["integrity_note"], ""]
    return "\n".join(L)
