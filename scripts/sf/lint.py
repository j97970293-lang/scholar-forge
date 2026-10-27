"""Manuscript linter: AI-slop detection, style diagnostics, integrity placeholders.

Deterministic, offline, no dependencies. It flags; the author decides.
Rule data lives in config/rules.json so it can be extended without code changes.
"""

from __future__ import annotations

import math
import re
import statistics
from collections import Counter
from typing import Any, Dict, List, Optional

from .util import ROOT, read_json

DEFAULT_RULES = {
    "slop_phrases": [
        "delve into", "tapestry", "pivotal role", "underscores the importance", "in today's fast-paced",
        "it is important to note that", "it is worth noting that", "a testament to", "navigate the complexities",
        "game-changer", "paradigm shift", "cutting-edge", "state-of-the-art", "shed light on",
        "embark on a journey", "at the end of the day", "in conclusion, it is clear",
        "significantly significant", "a wide array of", "a myriad of", "ever-evolving landscape",
        "plays a crucial role", "plays a vital role", "serves as a beacon", "unlock the potential",
        "harness the power", "seamless integration", "robust and comprehensive",
    ],
    "hedge_terms": ["may", "might", "could", "possibly", "perhaps", "potentially", "suggest",
                    "appears", "seems", "arguably", "likely", "unlikely", "generally", "often"],
    "absolute_terms": ["always", "never", "proves", "proven", "definitively", "conclusively",
                       "undoubtedly", "certainly", "all studies", "no doubt"],
    "placeholders": ["TODO", "TBD", "FIXME", "XXX", "[citation needed]", "[REF]", "[INSERT",
                     "Lorem ipsum", "example.com", "placeholder", "<your", "à compléter"],
    "pass_threshold": 70,
}


def _rules() -> Dict[str, Any]:
    r = read_json(ROOT / "config/rules.json", {}) or {}
    merged = dict(DEFAULT_RULES)
    merged.update(r)
    return merged


def _sentences(text: str) -> List[str]:
    t = re.sub(r"^```.*?```", "", text, flags=re.S | re.M)
    t = re.sub(r"^#{1,6}\s+.*$", "", t, flags=re.M)
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}", t)
    return [re.sub(r"\s+", " ", p).strip() for p in parts if len(p.strip()) > 3]


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9'-]+", text))


def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 1
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1:
        n -= 1
    return max(1, n)


def readability(text: str) -> Dict[str, Any]:
    sents = _sentences(text)
    words = re.findall(r"[A-Za-zÀ-ÿ'-]+", text)
    if not sents or not words:
        return {"words": 0, "sentences": 0, "flesch": None, "mean_sentence_length": 0,
                "sentence_length_sd": 0}
    syl = sum(_syllables(w) for w in words)
    wps = len(words) / len(sents)
    spw = syl / len(words)
    flesch = 206.835 - 1.015 * wps - 84.6 * spw
    lengths = [_word_count(s) for s in sents]
    return {"words": len(words), "sentences": len(sents), "flesch": round(flesch, 1),
            "mean_sentence_length": round(wps, 1),
            "sentence_length_sd": round(statistics.pstdev(lengths), 2) if len(lengths) > 1 else 0.0}


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def lint(text: str, rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    r = rules or _rules()
    findings: List[Dict[str, Any]] = []
    low = text.lower()
    for phrase in r["slop_phrases"]:
        for m in re.finditer(re.escape(phrase.lower()), low):
            findings.append({"line": _line_of(text, m.start()), "rule": "slop-phrase",
                             "severity": "warning", "match": phrase,
                             "message": f"Stock AI phrasing: « {phrase} » — replace with a specific statement."})
    for word in r["placeholders"]:
        for m in re.finditer(re.escape(word.lower()), low):
            findings.append({"line": _line_of(text, m.start()), "rule": "placeholder",
                             "severity": "error", "match": word,
                             "message": "Unresolved placeholder must be replaced before submission."})
    for m in re.finditer(r"not\s+only\b[^.]{0,120}\bbut\s+also\b", low):
        findings.append({"line": _line_of(text, m.start()), "rule": "not-only-but-also",
                         "severity": "warning", "match": m.group(0)[:80],
                         "message": "Formulaic contrast construction; state both facts directly."})
    sents = _sentences(text)
    for s in sents:
        n_hedge = sum(len(re.findall(r"\b" + re.escape(h) + r"\b", s.lower())) for h in r["hedge_terms"])
        if n_hedge >= 3:
            findings.append({"line": _line_of(text, text.find(s[:25])), "rule": "hedge-stack",
                             "severity": "warning", "match": s[:90],
                             "message": f"Stacked hedges ({n_hedge}); keep one qualifier and state the evidence."})
        wc = _word_count(s)
        if wc > 45:
            findings.append({"line": _line_of(text, text.find(s[:25])), "rule": "long-sentence",
                             "severity": "info", "match": s[:90], "message": f"Sentence of {wc} words."})
        if re.search(r"\b(was|were|is|are|been|being)\s+\w+(ed|en)\s+by\b", s, re.I):
            findings.append({"line": _line_of(text, text.find(s[:25])), "rule": "passive-voice",
                             "severity": "info", "match": s[:90],
                             "message": "Passive construction; consider naming the actor."})
    em = text.count("—") + text.count(" – ")
    per_k = max(1, _word_count(text) // 1000)
    if em / per_k > 12:
        findings.append({"line": 1, "rule": "em-dash-density", "severity": "warning",
                         "match": f"{em} em-dashes", "message": "Dash pile-up is a common AI tell; vary punctuation."})
    for bad in ("\u200b", "\u200c", "\u200d", "\ufeff", "\u202e"):
        if bad in text:
            findings.append({"line": 1, "rule": "hidden-unicode", "severity": "error",
                             "match": repr(bad), "message": "Invisible Unicode character detected."})
    sections = [m.group(2).strip().lower() for m in re.finditer(r"^(#{1,3})\s+(.+)$", text, re.M)]
    for expected in ("introduction", "method", "result", "discussion"):
        if not any(expected in s for s in sections):
            findings.append({"line": 1, "rule": "missing-section", "severity": "info",
                             "match": expected, "message": f"No heading matching « {expected} » (IMRaD check)."})
    rd = readability(text)
    counts = Counter(f["rule"] for f in findings)
    penalty = (counts["slop-phrase"] * 4 + counts["placeholder"] * 10 + counts["hedge-stack"] * 3
               + counts["not-only-but-also"] * 2 + counts["em-dash-density"] * 5
               + counts["hidden-unicode"] * 10 + counts["long-sentence"] * 0.5
               + counts["passive-voice"] * 0.25)
    score = max(0, min(100, round(100 - penalty, 1)))
    errors = [f for f in findings if f["severity"] == "error"]
    return {
        "summary": {"score": score, "threshold": r.get("pass_threshold", 70),
                    "pass": score >= r.get("pass_threshold", 70) and not errors,
                    "words": rd["words"], "errors": len(errors),
                    "warnings": sum(1 for f in findings if f["severity"] == "warning"),
                    "by_rule": dict(counts), "readability": rd},
        "findings": findings,
    }


def to_markdown(rep: Dict[str, Any]) -> str:
    s = rep["summary"]
    L = ["# Rapport de style / intégrité rédactionnelle", "",
         f"- Score : **{s['score']}/100** (seuil {s['threshold']})",
         f"- Mots : {s['words']} — phrases : {s['readability']['sentences']}",
         f"- Lisibilité de Flesch : {s['readability']['flesch']}",
         f"- Longueur moyenne de phrase : {s['readability']['mean_sentence_length']} mots "
         f"(écart-type {s['readability']['sentence_length_sd']})",
         f"- Erreurs : {s['errors']} — avertissements : {s['warnings']}",
         f"- Verdict : **{'PASS' if s['pass'] else 'FAIL'}**", "",
         "## Règles déclenchées", ""]
    for k, v in sorted(s["by_rule"].items(), key=lambda x: -x[1]):
        L.append(f"- `{k}` : {v}")
    L += ["", "## Constats détaillés", ""]
    for f in rep["findings"][:120]:
        L.append(f"- L{f['line']} **{f['severity']}** `{f['rule']}` — {f['message']} _({f['match'][:70]})_")
    if not rep["findings"]:
        L.append("Aucune anomalie détectée.")
    return "\n".join(L) + "\n"
