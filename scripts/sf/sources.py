"""Scholarly API clients (stdlib only, network optional, always fail-soft).

Every result carries provenance: which API, the exact request URL, and the
retrieval timestamp. No API key is required for any default source; optional
keys raise rate limits only. See config/sources.json.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .util import norm_doi, slug

UA = "ScholarForge/1.0 (academic research skill; stdlib urllib)"
DEFAULT_TIMEOUT = 12

SOURCES: Dict[str, Dict[str, str]] = {
    "openalex": {
        "name": "OpenAlex", "endpoint": "https://api.openalex.org/works",
        "docs": "https://docs.openalex.org/", "key_env": "OPENALEX_API_KEY",
        "note": "Broad multidisciplinary coverage; inverted abstracts; citation graphs.",
    },
    "crossref": {
        "name": "Crossref", "endpoint": "https://api.crossref.org/works",
        "docs": "https://api.crossref.org/", "key_env": "",
        "note": "DOI registry of record; best for metadata verification.",
    },
    "arxiv": {
        "name": "arXiv", "endpoint": "https://export.arxiv.org/api/query",
        "docs": "https://info.arxiv.org/help/api/", "key_env": "",
        "note": "Physics/CS/math preprints; Atom feed; no DOI for many entries.",
    },
    "semanticscholar": {
        "name": "Semantic Scholar", "endpoint": "https://api.semanticscholar.org/graph/v1/paper/search",
        "docs": "https://api.semanticscholar.org/api-docs/", "key_env": "S2_API_KEY",
        "note": "Citation graph and TLDRs; rate-limited without a key.",
    },
    "pubmed": {
        "name": "PubMed", "endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        "docs": "https://www.ncbi.nlm.nih.gov/books/NBK25501/", "key_env": "NCBI_API_KEY",
        "note": "Biomedical literature; esearch + esummary.",
    },
    "europepmc": {
        "name": "Europe PMC", "endpoint": "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        "docs": "https://europepmc.org/RestfulWebService", "key_env": "",
        "note": "Life sciences incl. preprints and full text links.",
    },
}


def _get(url: str, timeout: int = DEFAULT_TIMEOUT, accept: str = "application/json") -> Tuple[bool, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"


def _stamp(source: str, url: str, rec: Dict[str, Any]) -> Dict[str, Any]:
    rec.setdefault("source", source)
    rec.setdefault("source_url", url)
    rec.setdefault("retrieved_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    rec.setdefault("id", slug((rec.get("doi") or rec.get("title") or "ref"))[:60])
    return rec


def _openalex(q: str, limit: int, timeout: int) -> Tuple[str, List[Dict[str, Any]], str]:
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": q, "per-page": min(limit, 50), "mailto": "scholarforge@localhost"})
    ok, body = _get(url, timeout)
    if not ok:
        return url, [], body
    try:
        data = json.loads(body)
    except ValueError:
        return url, [], "invalid JSON from OpenAlex"
    out = []
    for w in data.get("results", []):
        inv = w.get("abstract_inverted_index") or {}
        abstract = ""
        if inv:
            pos = [(i, word) for word, idxs in inv.items() for i in idxs]
            abstract = " ".join(w for _, w in sorted(pos))[:1200]
        ids = w.get("ids") or {}
        out.append(_stamp("openalex", url, {
            "title": w.get("title") or w.get("display_name") or "",
            "author": "; ".join(a["author"]["display_name"] for a in (w.get("authorships") or []) if a.get("author")),
            "year": str((w.get("publication_year") or "")),
            "journal": ((w.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
            "doi": norm_doi((w.get("doi") or "").replace("https://doi.org/", "")),
            "url": w.get("primary_location", {}).get("landing_page_url") if isinstance(w.get("primary_location"), dict) else ids.get("doi", ""),
            "abstract": abstract, "cited_by": w.get("cited_by_count", 0),
            "type": w.get("type", ""),
        }))
    return url, out, ""


def _crossref(q: str, limit: int, timeout: int) -> Tuple[str, List[Dict[str, Any]], str]:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode({
        "query.bibliographic": q, "rows": min(limit, 50),
        "select": "DOI,title,author,issued,container-title,volume,issue,page,publisher,URL,type,abstract,subject"})
    ok, body = _get(url, timeout)
    if not ok:
        return url, [], body
    try:
        items = json.loads(body)["message"]["items"]
    except (ValueError, KeyError, TypeError):
        return url, [], "invalid JSON from Crossref"
    out = []
    for w in items:
        year = ""
        try:
            year = str(w["issued"]["date-parts"][0][0])
        except (KeyError, IndexError, TypeError):
            pass
        out.append(_stamp("crossref", url, {
            "title": (w.get("title") or [""])[0],
            "author": "; ".join(" ".join(filter(None, [a.get("given", ""), a.get("family", "")])) for a in (w.get("author") or [])),
            "year": year, "journal": (w.get("container-title") or [""])[0],
            "volume": w.get("volume", ""), "number": w.get("issue", ""), "pages": w.get("page", ""),
            "publisher": w.get("publisher", ""), "doi": norm_doi(w.get("DOI", "")),
            "url": w.get("URL", ""), "abstract": re.sub(r"<[^>]+>", "", w.get("abstract", ""))[:1200],
            "type": w.get("type", ""),
        }))
    return url, out, ""


def _arxiv(q: str, limit: int, timeout: int) -> Tuple[str, List[Dict[str, Any]], str]:
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": "all:" + q, "start": 0, "max_results": min(limit, 50), "sortBy": "relevance"})
    ok, body = _get(url, timeout, accept="application/atom+xml")
    if not ok:
        return url, [], body
    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        return url, [], f"invalid Atom from arXiv: {exc}"
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in root.findall("a:entry", ns):
        def t(name: str) -> str:
            n = e.find("a:" + name, ns)
            return (n.text or "").strip() if n is not None else ""
        out.append(_stamp("arxiv", url, {
            "title": re.sub(r"\s+", " ", t("title")), "author": "; ".join(
                (a.find("a:name", ns).text or "") for a in e.findall("a:author", ns) if a.find("a:name", ns) is not None),
            "year": t("published")[:4], "journal": "arXiv preprint",
            "doi": "", "url": t("id"), "abstract": re.sub(r"\s+", " ", t("summary"))[:1200],
            "type": "preprint",
        }))
    return url, out, ""


def _semanticscholar(q: str, limit: int, timeout: int) -> Tuple[str, List[Dict[str, Any]], str]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode({
        "query": q, "limit": min(limit, 50),
        "fields": "title,authors,year,venue,externalIds,url,abstract,citationCount"})
    ok, body = _get(url, timeout)
    if not ok:
        return url, [], body
    try:
        data = json.loads(body)
    except ValueError:
        return url, [], "invalid JSON from Semantic Scholar"
    out = []
    for w in data.get("data", []):
        ids = w.get("externalIds") or {}
        out.append(_stamp("semanticscholar", url, {
            "title": w.get("title", ""), "author": "; ".join(a.get("name", "") for a in (w.get("authors") or [])),
            "year": str(w.get("year") or ""), "journal": w.get("venue", ""),
            "doi": norm_doi(ids.get("DOI", "")), "url": w.get("url", ""),
            "abstract": (w.get("abstract") or "")[:1200], "cited_by": w.get("citationCount", 0),
            "type": "article",
        }))
    return url, out, ""


def _pubmed(q: str, limit: int, timeout: int) -> Tuple[str, List[Dict[str, Any]], str]:
    s_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": q, "retmax": min(limit, 50), "retmode": "json"})
    ok, body = _get(s_url, timeout)
    if not ok:
        return s_url, [], body
    try:
        ids = json.loads(body)["esearchresult"]["idlist"]
    except (ValueError, KeyError, TypeError):
        return s_url, [], "invalid JSON from PubMed esearch"
    if not ids:
        return s_url, [], ""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    ok, body = _get(url, timeout)
    if not ok:
        return url, [], body
    try:
        res = json.loads(body)["result"]
    except (ValueError, KeyError, TypeError):
        return url, [], "invalid JSON from PubMed esummary"
    out = []
    for uid in ids:
        w = res.get(uid) or {}
        doi = ""
        for aid in w.get("articleids", []) or []:
            if aid.get("idtype") == "doi":
                doi = norm_doi(aid.get("value", ""))
        out.append(_stamp("pubmed", url, {
            "title": w.get("title", ""), "author": "; ".join(a["name"] for a in (w.get("authors") or []) if a.get("name")),
            "year": (w.get("pubdate") or "")[:4], "journal": w.get("fulljournalname", w.get("source", "")),
            "volume": w.get("volume", ""), "number": w.get("issue", ""), "pages": w.get("pages", ""),
            "doi": doi, "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/", "pmid": uid,
            "abstract": "", "type": "article",
        }))
    return url, out, ""


def _europepmc(q: str, limit: int, timeout: int) -> Tuple[str, List[Dict[str, Any]], str]:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": q, "format": "json", "pageSize": min(limit, 50), "resultType": "core"})
    ok, body = _get(url, timeout)
    if not ok:
        return url, [], body
    try:
        items = json.loads(body)["resultList"]["result"]
    except (ValueError, KeyError, TypeError):
        return url, [], "invalid JSON from Europe PMC"
    out = []
    for w in items:
        out.append(_stamp("europepmc", url, {
            "title": w.get("title", ""), "author": w.get("authorString", ""),
            "year": str(w.get("pubYear", "")), "journal": ((w.get("journalInfo") or {}).get("journal") or {}).get("title", ""),
            "volume": (w.get("journalInfo") or {}).get("volume", ""),
            "doi": norm_doi(w.get("doi", "")), "url": w.get("fullTextUrl", "") or w.get("doi", ""),
            "abstract": (w.get("abstractText") or "")[:1200], "pmid": w.get("pmid", ""),
            "type": w.get("pubType", ""),
        }))
    return url, out, ""


_CLIENT = {
    "openalex": _openalex, "crossref": _crossref, "arxiv": _arxiv,
    "semanticscholar": _semanticscholar, "pubmed": _pubmed, "europepmc": _europepmc,
}


def search(source: str, query: str, limit: int = 10, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    if source not in _CLIENT:
        return {"source": source, "ok": False, "count": 0, "results": [],
                "error": "unknown source; choose from " + ", ".join(SOURCES),
                "url": "", "query": query}
    url, results, error = _CLIENT[source](query, limit, timeout)
    return {"source": source, "ok": not error, "error": error, "url": url,
            "query": query, "count": len(results), "results": results,
            "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def search_all(query: str, sources: Optional[List[str]] = None, limit: int = 10,
               timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    sources = sources or ["openalex", "crossref", "arxiv", "semanticscholar"]
    reports = {s: search(s, query, limit, timeout) for s in sources}
    merged: Dict[str, Dict[str, Any]] = {}
    for s, rep in reports.items():
        for rec in rep["results"]:
            key = rec.get("doi") or slug(rec.get("title", ""))[:70]
            if not key:
                continue
            if key in merged:
                merged[key].setdefault("also_in", []).append(s)
                for f in ("doi", "pmid", "abstract", "url"):
                    if not merged[key].get(f) and rec.get(f):
                        merged[key][f] = rec[f]
            else:
                merged[key] = dict(rec, also_in=[s])
    return {"query": query, "sources": reports, "merged": list(merged.values()),
            "total_hits": sum(r.get("count", 0) for r in reports.values()),
            "unique_hits": len(merged),
            "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def verify_doi(doi: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    doi = norm_doi(doi)
    if not re.match(r"^10\.\d{4,9}/\S+$", doi):
        return {"doi": doi, "status": "invalid-format", "crossref": None}
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
    ok, body = _get(url, timeout)
    if not ok:
        return {"doi": doi, "status": "lookup-error", "error": body, "crossref": None}
    try:
        m = json.loads(body)["message"]
    except (ValueError, KeyError):
        return {"doi": doi, "status": "lookup-error", "error": "invalid JSON", "crossref": None}
    return {"doi": doi, "status": "resolved", "crossref": {
        "title": (m.get("title") or [""])[0],
        "author": "; ".join(" ".join(filter(None, [a.get("given", ""), a.get("family", "")])) for a in (m.get("author") or [])),
        "year": str((m.get("issued", {}).get("date-parts") or [[""]])[0][0]),
        "journal": (m.get("container-title") or [""])[0],
        "type": m.get("type", ""), "publisher": m.get("publisher", ""),
        "url": m.get("URL", ""),
    }, "source_url": url}
