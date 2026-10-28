"""Generate and check a structured, COPE/ICMJE-aligned AI-use disclosure.

Nothing here decides policy for you. It produces a complete, auditable draft
naming tool + version + delegated tasks + human verification, and it lints an
existing disclosure for the fields publishers consistently require.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List, Optional

from .util import ROOT, read_json

CONFIG = ROOT / "config" / "ai-disclosure.json"


def load() -> Dict[str, Any]:
    return read_json(CONFIG, {}) or {}


def categories() -> List[Dict[str, str]]:
    return list(load().get("delegation_categories") or [])


def generate(tool: str = "", version: str = "", purposes: Optional[List[str]] = None,
             oversight: str = "", verification: str = "", prompts: str = "",
             title: str = "", venue: str = "", policy_date: str = "",
             authors: str = "") -> Dict[str, Any]:
    cfg = load()
    purposes = [p.strip() for p in (purposes or []) if p.strip()]
    idx = {c["key"]: c for c in categories()}
    unknown = [p for p in purposes if p not in idx]
    if unknown:
        raise ValueError("unknown delegation category %s; choose from %s"
                         % (unknown, sorted(idx)))
    return {
        "schema": "scholarforge-disclosure-v1",
        "generated": date.today().isoformat(),
        "study": title or "Untitled study", "venue": venue or "Target venue",
        "tool": tool, "version_or_date": version, "authors": authors,
        "categories": [{"key": p, **idx[p]} for p in purposes] if purposes else [],
        "specific_purpose": "; ".join(idx[p]["label"] for p in purposes),
        "human_oversight": oversight, "verification_steps": verification,
        "prompts_or_code_availability": prompts,
        "venue_policy_checked_on": policy_date or "NOT YET CHECKED",
        "settled_rules": list(cfg.get("settled_rules") or []),
        "credit_roles_for_humans": list(cfg.get("credit_roles_for_humans") or []),
        "sources": list(cfg.get("sources") or []),
    }


def to_markdown(d: Dict[str, Any]) -> str:
    L = ["# AI-use disclosure — " + d["study"], "",
         f"- **Purpose(s):** {d['specific_purpose'] or 'À COMPLÉTER'}",
         f"- Target venue: {d['venue']}",
         f"- Official author guidelines last checked on: **{d['venue_policy_checked_on']}**",
         f"- Tool / model: **{d['tool'] or 'À COMPLÉTER'}**",
         f"- Version / access date: **{d['version_or_date'] or 'À COMPLÉTER'}**",
         f"- Generated: {d['generated']}", "",
         "## Statement to paste into the manuscript", "",
         "> During the preparation of this work the author(s) used "
         f"**{d['tool'] or '[TOOL]'}** ({d['version_or_date'] or '[VERSION / DATE]'}) "
         f"for {d['specific_purpose'] or '[SPECIFIC PURPOSE]'}. "
         "After using this tool/service, the author(s) reviewed and edited the content as needed "
         "and take(s) full responsibility for the content of the publication. "
         "No AI tool is listed as an author.", ""]
    if d["categories"]:
        L += ["## Delegation table (what was delegated, and to whom accountability stays)", "",
              "| Stage | Typical tasks | Human verification |", "|---|---|---|"]
        for c in d["categories"]:
            L.append(f"| {c['label']} | {c['typical_tasks']} | {c['human_check']} |")
        L.append("")
    L += ["## Human oversight and verification", "",
          f"- **Named accountable author(s):** {d['authors'] or 'À COMPLÉTER'}",
          f"- **Oversight:** {d['human_oversight'] or 'À COMPLÉTER'}",
          f"- **Verification steps:** {d['verification_steps'] or 'À COMPLÉTER'}",
          f"- **Prompts / code availability:** {d['prompts_or_code_availability'] or 'À COMPLÉTER'}", "",
          "## CRediT (humans only)", "",
          "Assign these roles to people, never to the tool: " + ", ".join(d["credit_roles_for_humans"]) + ".", "",
          "## Rules that do not change", ""]
    L += ["- " + r for r in d["settled_rules"]]
    L += ["", "## Primary sources to re-check on submission day", ""]
    L += ["- " + s["name"] + " — " + s["url"] for s in d["sources"]]
    L += ["", "---", "",
          "This document is a *draft*. A human author must complete all empty fields, "
          "confirm the venue's current policy, and approve the final wording."]
    return "\n".join(L) + "\n"


PLACEHOLDER_RE = re.compile(
    r"(?i)à compléter|not yet checked|\{\{[^}]+\}\}|"
    r"\[(?:tool[^\]]*|version[^\]]*|specific\s+purpose|date)\]")
NO_USE_RE = re.compile(
    r"(?im)^\s*(?:[-*>]\s*)?(?:No (?:generative )?AI (?:tools? )?(?:was|were) used\b|"
    r"Aucun (?:outil d.IA n.a été utilisé|usage (?:de l.IA|d.IA))\b)")


def lint(text: str) -> Dict[str, Any]:
    from . import guidelines
    if NO_USE_RE.search(text) and not PLACEHOLDER_RE.search(text):
        return {"summary": {"required": 0, "missing": 0, "warnings": 0, "pass": True},
                "findings": [], "note": "Explicit no-use statement; the human author must confirm its truth."}
    rep = guidelines.lint_disclosure(text)
    if PLACEHOLDER_RE.search(text):
        rep["findings"].append({"severity": "error",
                                "issue": "unfilled placeholder or unchecked venue policy remains in the draft"})
    rep["summary"]["warnings"] = sum(1 for f in rep["findings"] if f["severity"] == "warning")
    rep["summary"]["missing"] = sum(1 for f in rep["findings"] if f["severity"] == "error")
    rep["summary"]["pass"] = not any(f["severity"] == "error" for f in rep["findings"])
    return rep
