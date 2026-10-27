"""BibTeX / RIS parsing, de-duplication, style formatting and integrity checks.

Zero dependencies. Handles the messy bibliographies that agents actually produce.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .util import norm_doi, norm_title, similarity, slug

BIB_FIELDS = ("author", "title", "journal", "journaltitle", "booktitle", "year", "date",
              "volume", "number", "pages", "doi", "url", "publisher", "editor", "edition",
              "series", "address", "note", "abstract", "eprint", "archiveprefix", "keywords",
              "isbn", "issn", "type", "school", "institution", "howpublished")


def parse_bib(text: str) -> List[Dict[str, str]]:
    """Tolerant BibTeX parser: nested braces, @string-free, concatenated values."""
    out: List[Dict[str, str]] = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]*)\s*,", text, re.I):
        kind, key = m.group(1).lower(), m.group(2)
        i, depth = m.end(), 1
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        body = text[m.end():max(m.end(), i - 1)]
        rec: Dict[str, str] = {"type": kind, "id": key}
        for fm in re.finditer(r"([A-Za-z][\w-]*)\s*=\s*", body):
            fname = fm.group(1).lower()
            j = fm.end()
            if j >= len(body):
                continue
            if body[j] == "{":
                k, d = j + 1, 1
                while k < len(body) and d:
                    if body[k] == "{":
                        d += 1
                    elif body[k] == "}":
                        d -= 1
                    k += 1
                val = body[j + 1:k - 1]
            elif body[j] in "\"'":
                q = body[j]
                k = j + 1
                while k < len(body) and body[k] != q:
                    k += 1
                val = body[j + 1:k]
            else:
                k = j
                while k < len(body) and body[k] not in ",}\n":
                    k += 1
                val = body[j:k]
            val = re.sub(r"\s+", " ", val.replace("\\&", "&").strip(" \t\n{},")).strip()
            rec[fname] = val
        out.append(rec)
    return out


RIS_MAP = {
    "TY": "type", "ID": "id", "TI": "title", "T1": "title", "AU": "author", "A1": "author",
    "PY": "year", "Y1": "year", "DA": "date", "JO": "journal", "JF": "journal", "T2": "journal",
    "VL": "volume", "IS": "number", "SP": "pages", "EP": "pages_end", "DO": "doi",
    "UR": "url", "PB": "publisher", "AB": "abstract", "KW": "keywords", "SN": "isbn", "ER": "_end",
}


def parse_ris(text: str) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []
    cur: Dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])\s+-\s*(.*)$", line.strip())
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        field = RIS_MAP.get(tag)
        if tag == "ER":
            if cur:
                recs.append(cur)
            cur = {}
            continue
        if not field:
            continue
        if field in ("author", "keywords"):
            cur.setdefault(field, "")
            cur[field] = (cur[field] + "; " + val).strip("; ")
        elif field == "year":
            ym = re.search(r"(1[5-9]\d{2}|20\d{2}|21\d{2})", val)
            cur[field] = ym.group(1) if ym else val[:4]
        else:
            cur[field] = val
    if cur:
        recs.append(cur)
    for r in recs:
        if r.get("pages_end"):
            r["pages"] = f"{r.get('pages','')}-{r.pop('pages_end')}".strip("-")
        r.setdefault("id", slug(r.get("title", "ref"))[:40])
    return recs


def parse_any(text: str, fmt: str = "auto") -> List[Dict[str, str]]:
    if fmt == "bib" or (fmt == "auto" and re.search(r"@\w+\s*\{", text)):
        return parse_bib(text)
    if fmt == "ris" or (fmt == "auto" and re.search(r"^TY\s+-", text, re.M)):
        return parse_ris(text)
    if fmt == "json" or (fmt == "auto" and text.lstrip().startswith("[")):
        import json
        try:
            obj = json.loads(text)
            if isinstance(obj, list):
                return [{str(k).lower(): str(v) for k, v in r.items()} for r in obj if isinstance(r, dict)]
        except ValueError:
            pass
    return []


def authors_list(rec: Dict[str, str]) -> List[str]:
    a = rec.get("author", "")
    if not a:
        return []
    parts = re.split(r"\s+and\s+|;\s*", a, flags=re.I)
    return [p.strip() for p in parts if p.strip()]


def _surname(name: str) -> str:
    name = name.strip().rstrip(",")
    if "," in name:
        return name.split(",")[0].strip()
    return name.split()[-1] if name.split() else name


def _initials(name: str) -> str:
    if "," in name:
        _, given = name.split(",", 1)
        return " ".join(f"{w[0].upper()}." for w in re.findall(r"[A-Za-z]+", given))
    parts = name.split()
    return " ".join(f"{w[0].upper()}." for w in parts[:-1])


def format_ref(rec: Dict[str, str], style: str = "apa") -> str:
    """Best-effort reference formatter for APA 7, IEEE, Vancouver, Chicago, BibTeX-like plain."""
    style = (style or "apa").lower()
    authors = authors_list(rec)
    title = rec.get("title", "").strip().rstrip(".")
    year = rec.get("year") or (rec.get("date", "")[:4]) or "n.d."
    journal = rec.get("journal") or rec.get("journaltitle") or rec.get("booktitle") or ""
    vol = rec.get("volume", "")
    num = rec.get("number", "")
    pages = rec.get("pages", "")
    doi = norm_doi(rec.get("doi", ""))
    publisher = rec.get("publisher", "")
    url = rec.get("url", "")
    if style.startswith("apa"):
        aa = ", ".join(
            (f"{_surname(a)}, {_initials(a)}" if i < len(authors) - 1 else f"{_surname(a)}, {_initials(a)}")
            for i, a in enumerate(authors)
        )
        aa = re.sub(r"\s+", " ", aa).strip()
        if len(authors) > 1:
            bits = [f"{_surname(a)}, {_initials(a)}".strip() for a in authors[:-1]]
            aa = ", ".join(bits) + ", & " + f"{_surname(authors[-1])}, {_initials(authors[-1])}".strip()
        tail = ""
        if journal:
            tail = f"*{journal}*"
            if vol:
                tail += f", *{vol}*"
            if num:
                tail += f"({num})"
            if pages:
                tail += f", {pages}"
            tail += "."
        elif publisher:
            tail = f"{publisher}."
        s = f"{aa} ({year}). {title}. {tail}".strip()
    elif style.startswith("ieee"):
        aa = ", ".join(f"{p.split()[-1][0].upper()}. {p.split()[-1]}" if "," not in p else f"{p.split(',')[1].strip().split()[0][0].upper()}. {p.split(',')[0]}" for p in authors)
        j = f"*{journal}*" if journal else ""
        extra = ", ".join(x for x in [f"vol. {vol}" if vol else "", f"no. {num}" if num else "",
                                      f"pp. {pages}" if pages else "", year] if x)
        s = f"{aa}, \"{title},\" {j}{', ' if j and extra else ''}{extra}."
        s = re.sub(r"\s+,", ",", s)
    elif style.startswith("vancouver"):
        aa = ", ".join(f"{_surname(a)} {_initials(a).replace('.', '').replace(' ', '')}" for a in authors)
        j = " ".join(x for x in [journal, f"{vol}({num})" if vol else "", year, f":{pages}" if pages else ""] if x)
        s = f"{aa}. {title}. {j}."
    elif style.startswith("chicago"):
        aa = "; ".join(authors)
        s = f"{aa}. \"{title}.\" *{journal}* {vol}" + (f", no. {num}" if num else "") + f" ({year})" + (f": {pages}" if pages else "") + "."
    else:  # mla / plain
        s = f"{', '.join(authors)}. \"{title}.\" {journal} {vol} {year}."
    if doi:
        s += f" https://doi.org/{doi}" if style.startswith(("apa", "chicago")) else f", doi:{doi}"
    elif url and not journal:
        s += f" {url}"
    return re.sub(r"\s{2,}", " ", s).strip()


def to_bibtex(rec: Dict[str, str]) -> str:
    typ = rec.get("type", "article")
    typ = {"journalarticle": "article", "conferencepaper": "inproceedings", "book": "book"}.get(typ, typ)
    key = rec.get("id") or slug((_surname(authors_list(rec)[0]) if authors_list(rec) else "") + rec.get("year", "") + rec.get("title", "")[:20])
    lines = [f"@{typ}{{{key},"]
    for k in BIB_FIELDS:
        if rec.get(k):
            lines.append(f"  {k} = {{{rec[k]}}},")
    lines.append("}")
    return "\n".join(lines)


def detect_problems(rec: Dict[str, str]) -> List[str]:
    problems: List[str] = []
    title = rec.get("title", "").strip()
    if not title:
        problems.append("missing-title")
    if not rec.get("author"):
        problems.append("missing-author")
    if not rec.get("year"):
        problems.append("missing-year")
    else:
        y = re.match(r"(\d{4})", str(rec["year"]))
        if not y or not (1500 <= int(y.group(1)) <= datetime.now().year + 2):
            problems.append("implausible-year")
    doi = norm_doi(rec.get("doi", ""))
    if doi and not re.match(r"^10\.\d{4,9}/\S+$", doi):
        problems.append("malformed-doi")
    for p in ("todo", "tbd", "placeholder", "example.com", "xxx", "lorem ipsum", "insert citation", "[citation needed]"):
        if p in (title + " " + rec.get("author", "") + " " + rec.get("journal", "")).lower():
            problems.append("placeholder-text")
            break
    if not rec.get("doi") and not rec.get("url") and not rec.get("journal") and not rec.get("publisher") and title:
        problems.append("no-resolvable-identifier")
    if re.search(r"\bet al\.?\b", rec.get("author", ""), re.I) and len(authors_list(rec)) <= 1:
        problems.append("et-al-without-author-list")
    return problems


def dedupe(records: List[Dict[str, str]], threshold: float = 0.93) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
    """Group by normalised DOI, else fuzzy title+year. Keeps the richest record."""
    kept: List[Dict[str, str]] = []
    groups: List[List[Dict[str, str]]] = []
    for rec in records:
        doi = norm_doi(rec.get("doi", ""))
        hit = None
        if doi:
            hit = next((g for g in groups if g[0].get("_doi") == doi), None)
            if hit is not None:
                hit[0]["_match_reason"] = "doi"
        if hit is None:
            t = norm_title(rec.get("title", ""))
            for g in groups:
                if t and similarity(t, norm_title(g[0].get("title", ""))) >= threshold:
                    hit = g
                    hit[0]["_match_reason"] = "fuzzy-title"
                    break
        if hit is None:
            r = dict(rec)
            r["_doi"] = doi
            r["_match_reason"] = "doi" if doi else "title"
            groups.append([r])
        else:
            hit.append(dict(rec, _doi=norm_doi(rec.get("doi", ""))))
    report: List[Dict[str, Any]] = []
    for g in groups:
        g.sort(key=lambda r: (len(r.get("author", "")), len(r.get("abstract", "")), len(r)), reverse=True)
        best = {k: v for k, v in g[0].items() if not k.startswith("_")}
        reason = g[0].get("_match_reason", "title")
        for other in g[1:]:
            for k, v in other.items():
                if k.startswith("_") or not v:
                    continue
                if not best.get(k):
                    best[k] = v
        kept.append(best)
        if len(g) > 1:
            report.append({"kept": best.get("id", best.get("title", "")[:40]),
                           "duplicates": [x.get("id", x.get("title", "")[:40]) for x in g[1:]],
                           "reason": reason})
    return kept, report
