"""PRISMA 2020 screening accounting, dual-reviewer agreement and flow diagram.

Input: a screening CSV with columns
  id, source, stage (ta|ft), r1, r2, adjudicated, exclusion_code, include
Values for r1/r2/adjudicated: include | exclude | unclear
Every decision must be explicit; no silent defaults.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any, Dict, List

ORDERED_EXCLUSION_CODES = [
    "E1-duplicate", "E2-not-primary-research", "E3-wrong-population", "E4-wrong-intervention",
    "E5-wrong-outcome", "E6-wrong-design", "E7-wrong-language", "E8-full-text-unavailable",
    "E9-retracted", "E10-other",
]


def _dec(v: str) -> str:
    v = (v or "").strip().lower()
    if v in ("include", "yes", "y", "1", "in", "true"):
        return "include"
    if v in ("exclude", "no", "n", "0", "out", "false"):
        return "exclude"
    return "unclear"


def agreement(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    both = [r for r in rows if _dec(r.get("r1", "")) in ("include", "exclude")
            and _dec(r.get("r2", "")) in ("include", "exclude")]
    n = len(both)
    if not n:
        return {"n": 0, "observed_agreement": None, "kappa": None, "pabak": None,
                "note": "no paired decisions found"}
    agree = sum(1 for r in both if _dec(r["r1"]) == _dec(r["r2"]))
    po = agree / n
    p1 = sum(1 for r in both if _dec(r["r1"]) == "include") / n
    p2 = sum(1 for r in both if _dec(r["r2"]) == "include") / n
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    return {"n": n, "agreements": agree, "observed_agreement": round(po, 4),
            "kappa": round(kappa, 4), "pabak": round(2 * po - 1, 4),
            "interpretation": ("almost perfect" if kappa > 0.8 else "substantial" if kappa > 0.6
                               else "moderate" if kappa > 0.4 else "fair" if kappa > 0.2
                               else "slight/poor")}


def counts(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    by_source: Counter = Counter()
    for r in rows:
        by_source[(r.get("source") or "unspecified").strip()] += 1
    ta = [r for r in rows if (r.get("stage") or "ta").lower() in ("ta", "title", "abstract", "title/abstract", "")]
    ft = [r for r in rows if (r.get("stage") or "").lower() in ("ft", "full", "fulltext", "full-text")]
    excl_ta = [r for r in ta if _dec(r.get("final")) == "exclude"]
    excl_ft = [r for r in ft if _dec(r.get("final")) == "exclude"]
    included = [r for r in rows if _dec(r.get("final")) == "include"]
    unresolved = [r for r in rows if _dec(r.get("final")) not in ("include", "exclude")]
    duplicates = [r for r in rows if (r.get("exclusion_code") or "").startswith("E1")]
    return {
        "records_identified": len(rows),
        "by_source": dict(by_source),
        "duplicates_removed": len(duplicates),
        "records_screened_ta": len(ta),
        "records_excluded_ta": len(excl_ta),
        "records_screened_ft": len(ft),
        "records_excluded_ft": len(excl_ft),
        "studies_included": len(included),
        "unresolved_decisions": len(unresolved),
        "exclusion_reasons": dict(Counter((r.get("exclusion_code") or "UNCODED") for r in excl_ta + excl_ft)),
    }


def validate(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    ids: set = set()
    for i, r in enumerate(rows, 2):
        rid = (r.get("id") or "").strip()
        line = f"row {i} ({rid or 'no-id'})"
        if not rid:
            issues.append({"where": line, "severity": "error", "issue": "missing record id"})
        elif rid in ids:
            issues.append({"where": line, "severity": "error", "issue": "duplicate record id"})
        ids.add(rid)
        a, b, f = _dec(r.get("r1")), _dec(r.get("r2")), _dec(r.get("final"))
        if a == "unclear" or b == "unclear":
            issues.append({"where": line, "severity": "error", "issue": "missing/ambiguous reviewer decision (no silent defaults)"})
        if a != b and not (r.get("adjudicated") or "").strip():
            issues.append({"where": line, "severity": "error", "issue": "disagreement without adjudication"})
        if f == "unclear":
            issues.append({"where": line, "severity": "error", "issue": "no final decision"})
        code = (r.get("exclusion_code") or "").strip()
        if f == "exclude":
            if not code:
                issues.append({"where": line, "severity": "error", "issue": "exclusion without ordered reason code"})
            elif code not in ORDERED_EXCLUSION_CODES:
                issues.append({"where": line, "severity": "warning", "issue": f"non-standard exclusion code {code}"})
        if f == "include" and code and not code.startswith("E1"):
            issues.append({"where": line, "severity": "warning", "issue": "included record carries an exclusion code"})
    return issues


def normalise(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Add a `final` column: adjudicated when present, else agreed r1/r2, else unclear."""
    out = []
    for r in rows:
        r = dict(r)
        a, b = _dec(r.get("r1")), _dec(r.get("r2"))
        adj = _dec(r.get("adjudicated"))
        r["final"] = adj if adj != "unclear" else (a if a == b and a != "unclear" else "unclear")
        out.append(r)
    return out


def flow(c: Dict[str, Any]) -> str:
    return "\n".join([
        "```mermaid",
        "flowchart TD",
        f'    A["Records identified<br/>n = {c["records_identified"]}"]',
        f'    B["Duplicates removed<br/>n = {c["duplicates_removed"]}"]',
        f'    C["Title/abstract screened<br/>n = {c["records_screened_ta"]}"]',
        f'    D["Excluded at screening<br/>n = {c["records_excluded_ta"]}"]',
        f'    E["Full texts assessed<br/>n = {c["records_screened_ft"]}"]',
        f'    F["Excluded at full text<br/>n = {c["records_excluded_ft"]}"]',
        f'    G["Studies included<br/>n = {c["studies_included"]}"]',
        "    A --> B --> C --> D", "    C --> E --> F", "    E --> G", "```",
    ])


def report(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    rows = normalise(rows)
    c = counts(rows)
    issues = validate(rows)
    agr = agreement(rows)
    errors = [i for i in issues if i["severity"] == "error"]
    return {
        "counts": c, "agreement": agr, "issues": issues,
        "ordered_exclusion_codes": ORDERED_EXCLUSION_CODES,
        "pass": not errors and c["unresolved_decisions"] == 0,
        "flow_mermaid": flow(c),
    }


def to_markdown(rep: Dict[str, Any]) -> str:
    c, a = rep["counts"], rep["agreement"]
    L = ["# PRISMA 2020 — rapport de sélection", "",
         "| Étape | n |", "|---|---:|",
         f"| Références identifiées | {c['records_identified']} |",
         f"| Doublons retirés | {c['duplicates_removed']} |",
         f"| Résumés examinés | {c['records_screened_ta']} |",
         f"| Exclus (titre/résumé) | {c['records_excluded_ta']} |",
         f"| Textes intégraux évalués | {c['records_screened_ft']} |",
         f"| Exclus (texte intégral) | {c['records_excluded_ft']} |",
         f"| **Études incluses** | **{c['studies_included']}** |",
         f"| Décisions non résolues | {c['unresolved_decisions']} |", "",
         "## Sources", ""]
    for k, v in c["by_source"].items():
        L.append(f"- `{k}` : {v}")
    L += ["", "## Motifs d'exclusion", ""]
    for k, v in sorted(c["exclusion_reasons"].items(), key=lambda x: -x[1]):
        L.append(f"- `{k}` : {v}")
    L += ["", "## Accord inter-lecteurs", "",
          f"- Décisions appariées : {a['n']}",
          f"- Accord observé : {a.get('observed_agreement')}",
          f"- κ de Cohen : **{a.get('kappa')}** ({a.get('interpretation','n/a')})",
          f"- PABAK : {a.get('pabak')}", "",
          "## Diagramme de flux", "", rep["flow_mermaid"], "",
          "## Anomalies", ""]
    if rep["issues"]:
        for i in rep["issues"][:60]:
            L.append(f"- **{i['severity']}** — {i['where']} : {i['issue']}")
    else:
        L.append("Aucune anomalie détectée.")
    L += ["", f"**Verdict : {'PASS' if rep['pass'] else 'FAIL'}**", ""]
    return "\n".join(L)
