"""Claim–evidence ledger: bind every manuscript assertion to a source.

A claim without evidence is a blocker. A strong claim supported only by weak
evidence is an overclaim. A source quoted in the ledger but never used is waste.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Optional

STRENGTH = {"established": 3, "supported": 2, "suggestive": 1, "speculative": 0}
EVIDENCE_LEVEL = {"systematic-review": 5, "rct": 4, "cohort": 3, "case-control": 2,
                  "cross-sectional": 2, "case-report": 1, "preprint": 1, "expert-opinion": 0,
                  "simulation": 1, "secondary-analysis": 3}
ABSOLUTE = re.compile(r"\b(always|never|proves?|proven|certain|undoubtedly|all studies|no evidence|"
                      r"definitively|conclusively|causes?|guarantees?|universally)\b", re.I)
HEDGE = re.compile(r"\b(may|might|could|suggests?|appears?|possibly|likely|preliminary|"
                   r"we hypothesi[sz]e|in this sample)\b", re.I)


def _split_ids(value: str) -> List[str]:
    return [x.strip() for x in re.split(r"[;,|\s]+", value or "") if x.strip()]


def validate(claims: List[Dict[str, str]], evidence: List[Dict[str, str]],
             manuscript: Optional[str] = None) -> Dict[str, Any]:
    ev_index = {(e.get("evidence_id") or e.get("id") or "").strip(): e for e in evidence}
    ev_index.pop("", None)
    used: Counter = Counter()
    findings: List[Dict[str, str]] = []
    for i, c in enumerate(claims, 2):
        cid = (c.get("claim_id") or c.get("id") or f"row-{i}").strip()
        text = (c.get("claim_text") or c.get("claim") or "").strip()
        where = f"{cid}"
        if not text:
            findings.append({"where": where, "severity": "error", "issue": "empty claim text"})
            continue
        ids = _split_ids(c.get("evidence_ids", ""))
        if not ids:
            findings.append({"where": where, "severity": "error", "issue": "claim has no evidence_ids"})
        for eid in ids:
            used[eid] += 1
            if eid not in ev_index:
                findings.append({"where": where, "severity": "error", "issue": f"dangling evidence_id '{eid}'"})
        strength = (c.get("strength") or "").strip().lower()
        if strength and strength not in STRENGTH:
            findings.append({"where": where, "severity": "warning",
                             "issue": f"strength '{strength}' not in {sorted(STRENGTH)}"})
        known = [ev_index[e] for e in ids if e in ev_index]
        if known:
            levels = [EVIDENCE_LEVEL.get((e.get("design") or e.get("level") or "").lower(), 2) for e in known]
            top = max(levels) if levels else 2
            if STRENGTH.get(strength, 1) >= 3 and top < 4:
                findings.append({"where": where, "severity": "warning",
                                 "issue": "established/proven wording without high-level evidence"})
            negatives = [e for e in known if (e.get("stance") or "").lower() in ("contradicts", "refutes", "against")]
            if negatives and STRENGTH.get(strength, 1) >= 3:
                findings.append({"where": where, "severity": "error",
                                 "issue": "strong claim has contradicting evidence in ledger"})
        if ABSOLUTE.search(text) and not HEDGE.search(text) and STRENGTH.get(strength, 1) >= 2:
            findings.append({"where": where, "severity": "warning",
                             "issue": "absolute wording without hedge; check against evidence"})
        if manuscript and len(text) > 25:
            needle = re.sub(r"\s+", " ", text)[:45].lower()
            if needle not in manuscript.lower():
                findings.append({"where": where, "severity": "warning",
                                 "issue": "claim text not found verbatim in manuscript (check drift)"})
        if re.search(r"\[(citation needed|ref|todo|\?)\]", text, re.I):
            findings.append({"where": where, "severity": "error", "issue": "unresolved citation placeholder"})
    for eid in ev_index:
        if used[eid] == 0:
            findings.append({"where": eid, "severity": "info", "issue": "evidence row unused by any claim"})
    duplicate_sources = [k for k, v in Counter(
        (e.get("source_id") or "").strip() for e in evidence if (e.get("source_id") or "").strip()).items() if v > 3]
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    return {
        "summary": {
            "claims": len(claims), "evidence_rows": len(evidence),
            "claims_with_evidence": sum(1 for c in claims if _split_ids(c.get("evidence_ids", ""))),
            "strengths": dict(Counter((c.get("strength") or "unspecified").lower() for c in claims)),
            "errors": len(errors), "warnings": len(warnings),
            "pass": not errors,
        },
        "findings": findings,
        "integrity_note": "Claim–evidence binding checks internal consistency of the ledger, "
                          "not the truth of the underlying science.",
    }


def to_markdown(rep: Dict[str, Any]) -> str:
    s = rep["summary"]
    L = ["# Registre des affirmations", "",
         f"- Affirmations : **{s['claims']}**",
         f"- Lignes de preuve : **{s['evidence_rows']}**",
         f"- Affirmations avec preuve : **{s['claims_with_evidence']}**",
         f"- Erreurs bloquantes : **{s['errors']}**",
         f"- Avertissements : **{s['warnings']}**",
         f"- Verdict : **{'PASS' if s['pass'] else 'FAIL'}**", "",
         "## Niveaux de force", ""]
    for k, v in sorted(s["strengths"].items()):
        L.append(f"- `{k}` : {v}")
    L += ["", "## Constats", ""]
    for f in rep["findings"][:100]:
        L.append(f"- **{f['severity']}** — {f['where']} : {f['issue']}")
    if not rep["findings"]:
        L.append("Aucune anomalie.")
    L += ["", "> " + rep["integrity_note"], ""]
    return "\n".join(L)
