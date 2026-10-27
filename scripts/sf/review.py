"""Peer-review drafting and rebuttal traceability helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .util import write_csv, write_text

COMMENT_RE = re.compile(r"(?:^|\n)\s*(?:[-*]\s*)?(?:\*\*)?(R(?P<r>\d+)[.\-_ ]?(?:C|Q|Comment)?[.\-_ ]?(?P<n>\d+))(?:\*\*)?\s*[:.)\-]?\s*(?P<text>[^\n]+)", re.I)
GENERIC_RE = re.compile(r"(?:^|\n)\s*(?P<idx>\d+)[.)]\s+(?P<text>[^\n]{15,})")

CATEGORY_KEYS = [
    ("methods", ["method", "design", "sample", "procedure", "protocol", "bias"]),
    ("statistics", ["statistic", "p-value", "significan", "power", "confidence", "regression", "test"]),
    ("literature", ["reference", "citation", "related work", "literature", "prior work"]),
    ("clarity", ["clear", "writing", "explain", "confusing", "notation", "structure", "figure", "table"]),
    ("novelty", ["novel", "contribution", "original", "incremental"]),
    ("ethics", ["ethic", "consent", "irb", "privacy", "data availability", "reproduc"]),
]


def parse_comments(text: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for m in COMMENT_RE.finditer(text):
        r, n, body = m.group("r") or "1", m.group("n") or str(len(out) + 1), m.group("text").strip()
        out.append({"comment_id": f"R{r}C{n}", "reviewer": f"R{r}", "comment": body})
    if not out:
        for m in GENERIC_RE.finditer(text):
            out.append({"comment_id": f"C{int(m.group('idx')):02d}", "reviewer": "R1",
                        "comment": m.group("text").strip()})
    if not out:
        out = [{"comment_id": "C01", "reviewer": "R1", "comment": text.strip()[:200]}]
    return out


def categorise(text: str) -> str:
    low = text.lower()
    for name, keys in CATEGORY_KEYS:
        if any(k in low for k in keys):
            return name
    return "general"


def rebuttal_matrix(text: str) -> List[Dict[str, str]]:
    rows = []
    for c in parse_comments(text):
        rows.append({
            "comment_id": c["comment_id"], "reviewer": c["reviewer"],
            "category": categorise(c["comment"]), "comment": c["comment"],
            "author_response": "", "action_taken": "", "manuscript_location": "",
            "evidence_ids": "", "status": "open",
        })
    return rows


def lint_review(text: str) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []
    if len(text.split()) < 80:
        findings.append({"severity": "warning", "issue": "Review is very short; check coverage of methods, results and limitations."})
    if re.search(r"\b(stupid|idiotic|lazy|incompetent|garbage|trash)\b", text, re.I):
        findings.append({"severity": "error", "issue": "Disrespectful/ad hominem language is not acceptable in a review."})
    if re.search(r"\b(accept|reject)\b", text, re.I) and not re.search(r"\bbecause\b|\bjustification\b|\brationale\b", text, re.I):
        findings.append({"severity": "warning", "issue": "Recommendation without an explicit justification."})
    if not re.search(r"(Section|Fig\.|Table|line|p\.|Equation|Algorithm)\s*\d+|L\d+", text):
        findings.append({"severity": "warning", "issue": "No location-anchored comments; add section/line/figure pointers."})
    if re.search(r"\b(always|never|obviously|clearly everyone)\b", text, re.I):
        findings.append({"severity": "warning", "issue": "Absolute wording; bind the critique to evidence."})
    return {"pass": not any(f["severity"] == "error" for f in findings),
            "summary": {"words": len(text.split()), "findings": len(findings)},
            "findings": findings}


def write_rebuttal(text: str, out_csv: Path | str, out_md: Path | str | None = None) -> Dict[str, Any]:
    rows = rebuttal_matrix(text)
    write_csv(out_csv, rows, ["comment_id", "reviewer", "category", "comment", "author_response",
                              "action_taken", "manuscript_location", "evidence_ids", "status"])
    if out_md:
        L = ["# Matrice de réponse aux reviewers", "",
             "| ID | Reviewer | Catégorie | Commentaire | Réponse | Action | Emplacement | Preuve | Statut |",
             "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append("| {comment_id} | {reviewer} | {category} | {comment} | {author_response} | "
                     "{action_taken} | {manuscript_location} | {evidence_ids} | {status} |".format(**r))
        write_text(out_md, "\n".join(L) + "\n")
    return {"comments": len(rows), "by_category": {c: sum(1 for r in rows if r["category"] == c)
                                                   for c in {x["category"] for x in rows}},
            "csv": str(out_csv)}
