"""Reporting-guideline router and working-checklist generator.

The config is data, this module is behaviour. It never claims to reproduce an
official checklist verbatim (see the `honesty_note` in the config); it emits a
working document with the official URL and a currency reminder so a human can
verify each item on submission day.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List, Optional

from .util import ROOT, read_json

CONFIG = ROOT / "config" / "reporting-guidelines.json"


def load() -> Dict[str, Any]:
    return read_json(CONFIG, {}) or {}


def catalogue() -> List[Dict[str, Any]]:
    cfg = load()
    rows = []
    for key, g in (cfg.get("guidelines") or {}).items():
        rows.append({"key": key, "name": g.get("name", ""), "year": g.get("year", ""),
                     "use_for": g.get("use_for", ""), "items": len(g.get("checklist") or []),
                     "ai_specific": bool(g.get("ai_specific")), "url": g.get("url", ""),
                     "supersedes": g.get("supersedes", "")})
    return sorted(rows, key=lambda r: (str(r["year"]), r["key"]))


def recommend(text: str) -> List[Dict[str, Any]]:
    """Very small keyword router. It suggests; a human decides."""
    t = (text or "").lower()
    hits: Dict[str, int] = {}
    for hint in load().get("selection_hints") or []:
        when = hint.get("when", "").lower()
        words = [w for w in re.split(r"[^a-z0-9+]+", when) if len(w) > 3
                 and w not in ("used", "with", "that", "from", "report", "results", "trial", "study")]
        score = sum(1 for w in words if w in t or w.rstrip("s") in t)
        if score:
            for key in hint.get("use") or []:
                hits[key] = hits.get(key, 0) + score
    if not hits and re.search(r"\bai\b|machine learning|llm|generative", t):
        hits = {"ml-paper": 1, "prediction-model": 1}
    if not hits:
        hits = {"systematic-review": 1, "ml-paper": 1}
    rows = {r["key"]: r for r in catalogue()}
    return [dict(rows[k], score=v) for k, v in sorted(hits.items(), key=lambda x: -x[1]) if k in rows]


def checklist(key: str, title: str = "", venue: str = "") -> Dict[str, Any]:
    cfg = load()
    g = (cfg.get("guidelines") or {}).get(key)
    if not g:
        raise ValueError("unknown guideline '%s'; run 'guideline --list'" % key)
    return {"key": key, "name": g.get("name", ""), "year": g.get("year", ""),
            "url": g.get("url", ""), "use_for": g.get("use_for", ""),
            "note": g.get("note", ""), "supersedes": g.get("supersedes", ""),
            "items": list(g.get("checklist") or []), "extras": list(g.get("extras") or []),
            "ai_specific": bool(g.get("ai_specific")), "title": title,
            "venue": venue, "currency_rule": cfg.get("currency_rule", ""),
            "honesty_note": cfg.get("honesty_note", ""),
            "ai_disclosure_note": cfg.get("ai_disclosure_note", ""),
            "generated": date.today().isoformat()}


def to_markdown(c: Dict[str, Any]) -> str:
    L = [f"# Reporting checklist — {c['name']}", "",
         f"- Study: {c['title'] or '—'}",
         f"- Target venue: {c['venue'] or '—'}",
         f"- Generated: {c['generated']}",
         f"- Official statement: {c['url'] or 'see EQUATOR Network'}",
         f"- Guideline year: {c['year']}",
         f"- Working items: {len(c['items'])} (abridged, not verbatim)", ""]
    if c["supersedes"]:
        L += [f"> Supersedes: **{c['supersedes']}**.", ""]
    if c["note"]:
        L += ["> " + c["note"], ""]
    L += ["| # | Item | Addressed? | Location / evidence |", "|---:|---|---|---|"]
    for i, item in enumerate(c["items"], 1):
        L.append(f"| {i} | {item} | [ ] |  |")
    if c["extras"]:
        L += ["", "## Extra artefacts commonly required", ""] + ["- [ ] " + x for x in c["extras"]]
    L += ["", "## Before submission", "",
          "- [ ] " + c["currency_rule"],
          "- [ ] Each item above checked against the official statement linked above",
          "- [ ] " + c["honesty_note"]]
    if c["ai_specific"] or c["ai_disclosure_note"]:
        L += ["- [ ] " + (c["ai_disclosure_note"] or "AI-use disclosure generated and placed in Methods/Acknowledgements")]
    return "\n".join(L) + "\n"


REQUIRED_DISCLOSURE = [
    (re.compile(r"(?i)\b(tool|model|system|chatgpt|claude|gemini|copilot|llm)\b"), "names the AI tool/model"),
    (re.compile(r"(?i)\b(v?\d+\.\d+|version|versioned|snapshot|accessed on|date of use)\b"), "states version or access date"),
    (re.compile(r"(?i)(\bpurpose\b|used (?:it|the tool) (?:to|for)|in order to|for (?:drafting|editing|translation|search|analysis|screening))"), "states the purpose"),
    (re.compile(r"(?i)\b(review(?:ed)?|verif(?:ied|ication)|checked|human|responsib(?:le|ility)|oversight)\b"), "affirms human verification/responsibility"),
    (re.compile(r"(?i)\bnot (?:an? )?authors?\b|\bcannot be (?:an? )?authors?\b|\bno ai authorship\b"), "states AI is not an author"),
]


def lint_disclosure(text: str) -> Dict[str, Any]:
    """Deterministic completeness check for an AI-use disclosure statement."""
    findings = []
    for pattern, label in REQUIRED_DISCLOSURE:
        if not pattern.search(text or ""):
            findings.append({"severity": "error", "issue": "missing: " + label})
    if re.search(r"(?i)\bwe (?:acknowledge|thank) (?:chatgpt|claude|an? ai)\b", text or "") or \
       re.search(r"(?i)\b(?:chatgpt|claude|gemini) (?:is|was) (?:an? )?(?:co-)?author\b", text or ""):
        findings.append({"severity": "error", "issue": "AI appears to be credited as an author"})
    if re.search(r"\[(?:tool|version|specific purpose|date)\]", text or "", re.I):
        findings.append({"severity": "warning", "issue": "unresolved placeholder in disclosure"})
    return {"summary": {"required": len(REQUIRED_DISCLOSURE),
                        "missing": sum(1 for f in findings if f["severity"] == "error"),
                        "pass": not any(f["severity"] == "error" for f in findings)},
            "findings": findings,
            "note": "Checks structure only. Verify the current publisher policy separately."}
