"""ScholarForge command-line interface -- one entry point for the whole skill."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import (audit, bib, claims, disclosure, guidelines, integrity, lint, pipeline,
               prisma, registry, review, scaffold, searchlog, sources, spec, verify)
from .util import (ROOT, find_project, out, read_csv, read_json, read_text, table,
                   write_csv, write_json, write_text)

__version__ = "1.1.0"


def _p(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="scholarforge",
        description="ScholarForge — one skill for the whole academic research & writing lifecycle.",
        epilog="Docs: README.md · references/ · docs/USAGE.md",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"ScholarForge {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    q = sub.add_parser("doctor", help="check runtime, files and optional connectivity")
    _p(q)

    q = sub.add_parser("init", help="create a project workspace from templates")
    q.add_argument("--path", default="."); q.add_argument("--name", default="My study")
    q.add_argument("--mode", default="full", choices=["full", "quick", "review"]); _p(q)

    q = sub.add_parser("search", help="query scholarly APIs (OpenAlex/Crossref/arXiv/S2/PubMed/EuropePMC)")
    q.add_argument("query"); q.add_argument("--sources", default="openalex,crossref,arxiv,semanticscholar")
    q.add_argument("--limit", type=int, default=8); q.add_argument("--timeout", type=int, default=12)
    q.add_argument("--out", default=""); q.add_argument("--bib", default="", help="also write results as BibTeX")
    q.add_argument("--csv", default="", help="also write merged hits as CSV")
    q.add_argument("--ris", default="", help="also write merged hits as RIS")
    q.add_argument("--from-year", type=int, default=0, help="earliest publication year")
    q.add_argument("--to-year", type=int, default=0, help="latest publication year")
    q.add_argument("--min-citations", type=int, default=0, help="minimum citation count where known")
    q.add_argument("--oa-only", action="store_true", help="open-access only where the source exposes it")
    q.add_argument("--type", dest="work_type", default="", help="work type filter (e.g. article, preprint)")
    q.add_argument("--log-path", default="", help="project root whose sources/search-log.md receives this query")
    q.add_argument("--no-log", action="store_true", help="disable the automatic PRISMA-S search log")
    _p(q)

    q = sub.add_parser("dedupe", help="de-duplicate a BibTeX/RIS/JSON bibliography")
    q.add_argument("file"); q.add_argument("--out", default=""); q.add_argument("--format", default="auto",
                                                                              choices=["auto", "bib", "ris", "json"])
    q.add_argument("--to", default="bibtex", choices=["bibtex", "ris", "json"]); _p(q)

    q = sub.add_parser("verify", help="verify references (offline signals + optional Crossref)")
    q.add_argument("file"); q.add_argument("--online", action="store_true")
    q.add_argument("--format", default="auto", choices=["auto", "bib", "ris", "json"])
    q.add_argument("--out", default=""); _p(q)

    q = sub.add_parser("bib", help="format a bibliography in a citation style")
    q.add_argument("file"); q.add_argument("--style", default="apa",
                                          choices=["apa", "ieee", "vancouver", "chicago"])
    q.add_argument("--format", default="auto"); q.add_argument("--out", default=""); _p(q)

    q = sub.add_parser("prisma", help="PRISMA counts, kappa and flow diagram from a screening CSV")
    q.add_argument("file"); q.add_argument("--out", default=""); _p(q)

    q = sub.add_parser("claims", help="validate the claim–evidence ledger")
    q.add_argument("--claims", required=True); q.add_argument("--evidence", required=True)
    q.add_argument("--manuscript", default=""); q.add_argument("--out", default=""); _p(q)

    q = sub.add_parser("lint", help="lint a manuscript (AI slop, placeholders, readability)")
    q.add_argument("file"); q.add_argument("--out", default=""); _p(q)

    q = sub.add_parser("new", help="render a single template")
    q.add_argument("kind", help="manuscript|protocol|review|rebuttal|cover|data|credit|ai|prereg|brief|status|latex")
    q.add_argument("path"); q.add_argument("--title", default=""); q.add_argument("--venue", default="")
    _p(q)

    q = sub.add_parser("review", help="lint a review draft for evidence-bounded, respectful comments")
    q.add_argument("file"); q.add_argument("--out", default=""); _p(q)

    q = sub.add_parser("rebuttal", help="build a point-by-point rebuttal matrix from reviewer comments")
    q.add_argument("file"); q.add_argument("--out-csv", default="review/rebuttal-matrix.csv")
    q.add_argument("--out-md", default="review/rebuttal-matrix.md"); _p(q)

    q = sub.add_parser("registry", help="search the unified 5k+ skill registry")
    rsub = q.add_subparsers(dest="registry_command", required=True)
    r = rsub.add_parser("search"); r.add_argument("query"); r.add_argument("--limit", type=int, default=10)
    r.add_argument("--stage", default=""); r.add_argument("--min-relevance", type=float, default=0.0)
    r.add_argument("--verified", action="store_true"); _p(r)
    r = rsub.add_parser("stats"); _p(r)

    q = sub.add_parser("pipeline", help="ten-stage state machine")
    psub = q.add_subparsers(dest="pipeline_command", required=True)
    r = psub.add_parser("status"); r.add_argument("--path", default=""); _p(r)
    r = psub.add_parser("advance"); r.add_argument("stage"); r.add_argument("--path", default="")
    r.add_argument("--force", action="store_true"); _p(r)
    r = psub.add_parser("reset"); r.add_argument("--stage", default="S0"); r.add_argument("--path", default=""); _p(r)
    r = psub.add_parser("stages"); _p(r)

    q = sub.add_parser("audit", help="aggregate all gates into output/AUDIT.md")
    q.add_argument("--path", default=""); q.add_argument("--online", action="store_true"); _p(q)

    q = sub.add_parser("integrity", help="screen references for retractions/corrections (offline + online signals)")
    q.add_argument("file", nargs="?", default="")
    q.add_argument("--online", action="store_true", help="also query OpenAlex and Crossref notices")
    q.add_argument("--timeout", type=int, default=10)
    q.add_argument("--out", default=""); q.add_argument("--path", default=""); _p(q)

    q = sub.add_parser("guideline", help="reporting-guideline router and working checklist")
    q.add_argument("--list", action="store_true"); q.add_argument("--key", default="")
    q.add_argument("--recommend", default="", help="free-text study description")
    q.add_argument("--title", default=""); q.add_argument("--venue", default="")
    q.add_argument("--out", default=""); _p(q)

    q = sub.add_parser("disclosure", help="generate or lint a structured AI-use disclosure")
    q.add_argument("--tool", default=""); q.add_argument("--tool-version", default="")
    q.add_argument("--purpose", default="", help="comma-separated delegation categories")
    q.add_argument("--oversight", default=""); q.add_argument("--verification", default="")
    q.add_argument("--prompts", default=""); q.add_argument("--title", default="")
    q.add_argument("--venue", default=""); q.add_argument("--authors", default="")
    q.add_argument("--policy-date", default=""); q.add_argument("--check", default="",
                                                                help="lint an existing disclosure file")
    q.add_argument("--out", default="submission/ai-disclosure.md"); _p(q)

    q = sub.add_parser("searchlog", help="show the PRISMA-S search log for a project")
    q.add_argument("--path", default=""); q.add_argument("--out", default=""); _p(q)

    q = sub.add_parser("validate", help="check SKILL.md against the Agent Skills open specification")
    _p(q)

    q = sub.add_parser("selftest", help="run the bundled offline unit tests"); _p(q)
    return p


def _write_report(path: str, text: str) -> None:
    if path:
        write_text(path, text)
        print(f"[ok] wrote {path}")
    else:
        print(text)


def cmd_doctor(a: argparse.Namespace) -> int:
    checks = {
        "python": sys.version.split()[0],
        "skill_root": str(ROOT),
        "SKILL.md": (ROOT / "SKILL.md").is_file(),
        "references": len(list((ROOT / "references").glob("*.md"))),
        "templates": len(list((ROOT / "templates").iterdir())),
        "registry_entries": registry.load().get("count", 0),
        "config_files": len(list((ROOT / "config").glob("*.json"))),
        "upstream_archives": len(list((ROOT / "upstream").glob("*.zip"))),
        "tests": (ROOT / "tests/test_scholarforge.py").is_file(),
        "references_v2": len(list((ROOT / "references").glob("2[3-8]-*.md"))),
        "reporting_guidelines": len((read_json(ROOT / "config/reporting-guidelines.json", {}) or {}).get("guidelines", {})),
        "delegation_categories": len((read_json(ROOT / "config/ai-disclosure.json", {}) or {}).get("delegation_categories", [])),
        "upstream_v2_archives": len(list((ROOT / "upstream/v2").glob("*.zip"))),
    }
    ok = checks["SKILL.md"] and checks["references"] >= 15 and checks["templates"] >= 10 and checks["registry_entries"] > 1000
    if a.json:
        out({"ok": ok, **checks}, True)
    else:
        print("ScholarForge", __version__, "—", "OK" if ok else "INCOMPLETE")
        for k, v in checks.items():
            print(f"  {k:22} {v}")
        print("\nNetwork sources configured:")
        for k, v in sources.SOURCES.items():
            print(f"  {k:18} {v['endpoint']}")
    return 0 if ok else 1


def cmd_search(a: argparse.Namespace) -> int:
    srcs = [s.strip() for s in a.sources.split(",") if s.strip()]
    filters = {"from_year": a.from_year or None, "to_year": a.to_year or None,
               "min_citations": a.min_citations or None, "oa_only": a.oa_only,
               "type": a.work_type}
    rep = sources.search_all(a.query, srcs, a.limit, a.timeout, filters)
    if a.out:
        write_json(a.out, rep)
        print(f"[ok] wrote {a.out} ({rep['unique_hits']} unique hits)")
    if a.bib:
        lines = []
        for r in rep["merged"]:
            rec = {"type": "article", "id": r.get("id", ""), **{k: str(v) for k, v in r.items()
                   if k in ("title", "author", "year", "journal", "doi", "url", "abstract", "volume", "number", "pages")}}
            lines.append(bib.to_bibtex(rec))
        write_text(a.bib, "\n\n".join(lines) + "\n")
        print(f"[ok] wrote {a.bib}")
    if a.csv:
        write_csv(a.csv, rep["merged"])
        print(f"[ok] wrote {a.csv}")
    if a.ris:
        ris = []
        ris_fields = (("TI", "title"), ("AU", "author"), ("PY", "year"), ("JO", "journal"),
                      ("DO", "doi"), ("UR", "url"), ("AB", "abstract"))
        for r in rep["merged"]:
            lines = ["TY  - JOUR"]
            for tag, key in ris_fields:
                if r.get(key):
                    lines.append(f"{tag}  - {str(r[key]).replace(chr(10), ' ')}")
            lines.append("ER  - ")
            ris.append("\n".join(lines) + "\n\n")
        write_text(a.ris, "".join(ris))
        print(f"[ok] wrote {a.ris}")
    if not a.no_log:
        project = find_project(a.log_path or None)
        try:
            log = searchlog.append(project, rep, rep.get("filters"), __version__)
            print(f"[ok] search log +{log['rows_added']} rows -> {log['markdown']}")
        except (OSError, ValueError) as exc:
            print(f"[warn] search log not written: {exc}", file=sys.stderr)
    if a.json or not a.out:
        if a.json:
            out(rep, True)
        else:
            rows = [[i, (r.get("title") or "")[:78], r.get("year", ""), r.get("doi", "")[:34],
                     ",".join(r.get("also_in", []))] for i, r in enumerate(rep["merged"][:30], 1)]
            print(f"Query: {a.query!r} | {rep['total_hits']} hits / {rep['unique_hits']} unique")
            for s, r in rep["sources"].items():
                print(f"  {s:18} {'ok' if r['ok'] else 'FAIL'} {r['count']:>3} results {r['error'][:60]}")
            print(table(rows, ["#", "title", "year", "doi", "sources"]))
    return 0


def cmd_dedupe(a: argparse.Namespace) -> int:
    recs = bib.parse_any(read_text(a.file), a.format)
    kept, dups = bib.dedupe(recs)
    if a.to == "bibtex":
        text = "\n\n".join(bib.to_bibtex(r) for r in kept) + "\n"
    elif a.to == "json":
        text = json.dumps(kept, ensure_ascii=False, indent=2) + "\n"
    else:
        text = "\n".join("TY  - JOUR\n" + "".join(f"{k.upper()}  - {v}\n" for k, v in r.items() if k != "type") + "ER  - \n" for r in kept)
    if a.out:
        write_text(a.out, text)
        print(f"[ok] wrote {a.out}")
    if a.json or not a.out:
        out({"input": len(recs), "kept": len(kept), "duplicates": dups}, a.json,
            None if a.json else f"{len(recs)} -> {len(kept)} references; {len(dups)} duplicate groups")
    return 0


def cmd_verify(a: argparse.Namespace) -> int:
    recs = bib.parse_any(read_text(a.file), a.format)
    rep = verify.verify(recs, online=a.online)
    if a.json:
        out(rep, True)
    else:
        _write_report(a.out, verify.to_markdown(rep))
    if a.out and not a.json:
        print(f"verdict: {'PASS' if rep['summary']['pass'] else 'FAIL'} ({rep['summary']['blocking']} blocking)")
    return 0 if rep["summary"]["pass"] else 1


def cmd_bib(a: argparse.Namespace) -> int:
    recs = bib.parse_any(read_text(a.file), a.format)
    lines = [f"{i}. " + bib.format_ref(r, a.style) for i, r in enumerate(recs, 1)]
    text = "\n\n".join(lines) + "\n"
    if a.out:
        write_text(a.out, text)
        print(f"[ok] wrote {a.out}")
    if a.json:
        out({"style": a.style, "references": lines}, True)
    elif not a.out:
        print(text)
    return 0


def cmd_prisma(a: argparse.Namespace) -> int:
    rep = prisma.report(read_csv(a.file))
    if a.json:
        out(rep, True)
    else:
        _write_report(a.out, prisma.to_markdown(rep))
    return 0 if rep["pass"] else 1


def cmd_claims(a: argparse.Namespace) -> int:
    rep = claims.validate(read_csv(a.claims), read_csv(a.evidence),
                          read_text(a.manuscript) if a.manuscript else None)
    if a.json:
        out(rep, True)
    else:
        _write_report(a.out, claims.to_markdown(rep))
    return 0 if rep["summary"]["pass"] else 1


def cmd_lint(a: argparse.Namespace) -> int:
    rep = lint.lint(read_text(a.file))
    if a.json:
        out(rep, True)
    else:
        _write_report(a.out, lint.to_markdown(rep))
    return 0 if rep["summary"]["pass"] else 1


def cmd_review(a: argparse.Namespace) -> int:
    rep = review.lint_review(read_text(a.file))
    if a.json:
        out(rep, True)
    else:
        text = "\n".join([f"# Review lint — {'PASS' if rep['pass'] else 'FAIL'}",
                          f"Words: {rep['summary']['words']}", ""] +
                         [f"- **{f['severity']}** {f['issue']}" for f in rep["findings"]]) + "\n"
        _write_report(a.out, text)
    return 0 if rep["pass"] else 1


def cmd_rebuttal(a: argparse.Namespace) -> int:
    rep = review.write_rebuttal(read_text(a.file), a.out_csv, a.out_md)
    out({"ok": True, **rep}, a.json,
        f"{rep['comments']} comments -> {a.out_csv}, {a.out_md}")
    return 0


def cmd_registry(a: argparse.Namespace) -> int:
    if a.registry_command == "stats":
        s = registry.stats()
        if a.json:
            out(s, True)
        else:
            print(f"Registry: {s['total']:,} entries (generated {s['generated_utc']})")
            print("Verified:", s["verified"], "| Academic:", s["academic"])
            print("By stage:", json.dumps(s["by_stage"], indent=2))
        return 0
    rep = registry.search(a.query, a.limit, a.stage, a.min_relevance, a.verified)
    if a.json:
        out(rep, True)
    else:
        rows = [[r["name"][:38], r["category"][:24], r["lifecycle_stage"][:16],
                 r["stars"], "yes" if r["verified"] else "", (r["url"] or "")[:60], r["score"]]
                for r in rep["results"]]
        print(f"{rep['count']} matches in {rep['registry_size']:,} entries")
        print(table(rows, ["name", "category", "stage", "stars", "verified", "url", "score"]))
    return 0


def cmd_pipeline(a: argparse.Namespace) -> int:
    if a.pipeline_command == "stages":
        data = [{"id": s["id"], "name": s["name"], "reference": s["reference"], "gate": s["gate"]} for s in pipeline.STAGES]
        out(data, a.json, None if a.json else table([[s["id"], s["name"], s["reference"]] for s in pipeline.STAGES],
                                                    ["stage", "name", "reference"]))
        return 0
    if a.pipeline_command == "status":
        rep = pipeline.status(a.path or None)
    elif a.pipeline_command == "advance":
        rep = pipeline.advance(a.stage, a.path or None, a.force)
    else:
        rep = pipeline.reset(a.path or None, a.stage)
    if a.json:
        out(rep, True)
    else:
        if a.pipeline_command == "status":
            print(f"Stage {rep['stage']} — {rep['stage_name']} ({rep['progress']})")
            print("Gate:", rep["current_gate"])
            print("Artifacts:", rep["artifacts"])
            print(table([[s["id"], s["name"], "done" if s["done"] else ("current" if s["current"] else "")]
                         for s in rep["stages"]], ["stage", "name", "state"]))
        else:
            print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep.get("ok", True) else 1


def cmd_selftest(a: argparse.Namespace) -> int:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if a.json:
        out({"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
             "ok": result.wasSuccessful()}, True)
    return 0 if result.wasSuccessful() else 1


def _resolve_integrity_file(a: argparse.Namespace) -> str:
    if a.file:
        return a.file
    project = find_project(a.path or None)
    for name in ("references.bib", "draft/references.bib", "refs.bib"):
        if (project / name).is_file():
            return str(project / name)
    raise FileNotFoundError("no references.bib found; pass a BibTeX/RIS/JSON file explicitly")


def cmd_integrity(a: argparse.Namespace) -> int:
    recs = bib.parse_any(read_text(_resolve_integrity_file(a)), "auto")
    rep = integrity.check(recs, online=a.online, timeout=a.timeout)
    project = find_project(a.path or None)
    (project / "output").mkdir(exist_ok=True)
    write_json(project / "output/integrity.json", rep)
    write_text(project / "output/integrity.md", integrity.to_markdown(rep))
    if a.out:
        write_text(a.out, integrity.to_markdown(rep))
        print(f"[ok] wrote {a.out}")
    if a.json:
        out(rep, True)
    else:
        s = rep["summary"]
        print(f"Integrity: {'PASS' if s['pass'] else 'FAIL'} — {s['records']} references, "
              f"{s['blocking']} blocking, online={s['online']}")
        for r in rep["results"]:
            if r["verdict"] != "no-signal" and r["verdict"] != "not-checked":
                print(f"  {r['verdict']:<22} {(r['title'] or r['id'])[:60]}")
    return 0 if rep["summary"]["pass"] else 1


def cmd_guideline(a: argparse.Namespace) -> int:
    if a.list or (not a.key and not a.recommend):
        rows = guidelines.catalogue()
        if a.json:
            out({"guidelines": rows}, True)
        else:
            print(table([[r["key"], r["name"][:40], r["year"], r["items"],
                         "AI" if r["ai_specific"] else "", r["use_for"][:52]] for r in rows],
                        ["key", "guideline", "year", "items", "AI", "use for"]))
            print("\nRun: scholarforge guideline --key <key> --out submission/checklist.md")
        return 0
    if a.recommend:
        rec = guidelines.recommend(a.recommend)
        if a.json:
            out({"recommendations": rec}, True)
        else:
            print("Suggested guidelines (verify against the official statement):")
            for r in rec:
                print(f"  {r['key']:<24} {r['name'][:38]:<38} score {r['score']}  {r['url']}")
        return 0
    c = guidelines.checklist(a.key, a.title, a.venue)
    text = guidelines.to_markdown(c)
    if a.out:
        write_text(a.out, text)
        print(f"[ok] wrote {a.out} ({len(c['items'])} items)")
    if a.json:
        out(c, True)
    elif not a.out:
        print(text)
    return 0


def cmd_disclosure(a: argparse.Namespace) -> int:
    if a.check:
        rep = disclosure.lint(read_text(a.check))
        if a.json:
            out(rep, True)
        else:
            print(f"Disclosure: {'PASS' if rep['summary']['pass'] else 'FAIL'} "
                  f"({rep['summary']['missing']} missing fields)")
            for f in rep["findings"]:
                print(f"  {f['severity']:<8} {f['issue']}")
        return 0 if rep["summary"]["pass"] else 1
    purposes = [x.strip() for x in a.purpose.split(",") if x.strip()]
    d = disclosure.generate(tool=a.tool, version=a.tool_version, purposes=purposes,
                            oversight=a.oversight, verification=a.verification, prompts=a.prompts,
                            title=a.title, venue=a.venue, policy_date=a.policy_date, authors=a.authors)
    text = disclosure.to_markdown(d)
    write_text(a.out, text)
    if a.json:
        out(d, True)
    else:
        print(f"[ok] wrote {a.out} ({len(d['categories'])} delegation categories)")
        print("Categories:", ", ".join(sorted(c["key"] for c in disclosure.categories())))
    return 0


def cmd_searchlog(a: argparse.Namespace) -> int:
    project = find_project(a.path or None)
    s = searchlog.summary(project)
    if a.json:
        out({"summary": s, "entries": searchlog.read(project)}, True)
    else:
        text = searchlog.to_markdown(project)
        if a.out:
            write_text(a.out, text)
            print(f"[ok] wrote {a.out}")
        else:
            print(text)
    return 0


def cmd_validate(a: argparse.Namespace) -> int:
    rep = spec.validate()
    if a.json:
        out(rep, True)
    else:
        print(spec.to_markdown(rep))
    return 0 if rep["ok"] else 1


HANDLERS = {
    "doctor": cmd_doctor, "init": None, "search": cmd_search, "dedupe": cmd_dedupe,
    "verify": cmd_verify, "bib": cmd_bib, "prisma": cmd_prisma, "claims": cmd_claims,
    "lint": cmd_lint, "new": None, "review": cmd_review, "rebuttal": cmd_rebuttal,
    "registry": cmd_registry, "pipeline": cmd_pipeline, "audit": None, "selftest": cmd_selftest,
    "integrity": cmd_integrity, "guideline": cmd_guideline, "disclosure": cmd_disclosure,
    "searchlog": cmd_searchlog, "validate": cmd_validate,
}


def main(argv: Optional[List[str]] = None) -> int:
    p = build_parser()
    a = p.parse_args(argv)
    try:
        if a.command == "init":
            rep = scaffold.init_project(a.path, a.name, a.mode)
            out(rep, a.json, None if a.json else f"[ok] project created at {rep['root']} ({len(rep['files'])} files)")
            return 0
        if a.command == "new":
            dest = scaffold.new(a.kind, a.path, TITLE=a.title or "Untitled study", VENUE=a.venue or "Target venue")
            out({"path": str(dest)}, a.json, f"[ok] wrote {dest}")
            return 0
        if a.command == "audit":
            rep = audit.run(a.path or None, online=a.online)
            if a.json:
                out({k: v for k, v in rep.items() if k != "details"}, True)
            else:
                print(f"Verdict: {rep['verdict']}  ({rep['summary']['passed']}/{rep['summary']['gates']} gates pass)")
                print(table([[g["gate"], g["status"], g["detail"]] for g in rep["gates"]],
                            ["gate", "status", "detail"]))
            return 0 if rep["verdict"] == "PASS" else 1
        return HANDLERS[a.command](a)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
