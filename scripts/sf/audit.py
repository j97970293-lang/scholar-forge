"""Final submission audit: aggregate every local gate into one verdict."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from . import bib, claims, disclosure, integrity, lint, pipeline, prisma, verify
from .util import ROOT, find_project, now, read_csv, read_json, read_text, write_json, write_text


def _first(root: Path, *candidates: str) -> Optional[Path]:
    for c in candidates:
        p = root / c
        if p.is_file():
            return p
    return None


def _gate(name: str, passed: Optional[bool], detail: str, blocking: bool = True) -> Dict[str, Any]:
    return {"gate": name, "status": "pass" if passed else ("fail" if passed is False else "missing"),
            "blocking": blocking, "detail": detail}


def run(root: Optional[Path | str] = None, online: bool = False) -> Dict[str, Any]:
    project = find_project(str(root) if root else None)
    cfg = read_json(project / ".scholarforge/config.json", {}) or {}
    gates_cfg = read_json(ROOT / "config/gates.json", {}) or {}
    out: List[Dict[str, Any]] = []
    details: Dict[str, Any] = {}

    manuscript = _first(project, "draft/manuscript.md", "manuscript.md", "paper/main.md")
    if manuscript:
        text = read_text(manuscript)
        rep = lint.lint(text)
        details["style"] = rep
        threshold = (cfg.get("gates") or {}).get("min_style_score", 70)
        out.append(_gate("G-style", rep["summary"]["score"] >= threshold and rep["summary"]["errors"] == 0,
                         f"score {rep['summary']['score']}/{rep['summary']['threshold']}, "
                         f"{rep['summary']['errors']} placeholders, {rep['summary']['warnings']} warnings"))
        write_text(project / "output/lint.md", lint.to_markdown(rep))
    else:
        out.append(_gate("G-style", None, "manuscript not found"))

    recs = []
    refspath = _first(project, "references.bib", "draft/references.bib", "refs.bib", "draft/refs.bib")
    if refspath:
        recs = bib.parse_any(read_text(refspath), "auto")
        rep = verify.verify(recs, online=online)
        details["references"] = rep
        out.append(_gate("G-references", rep["summary"]["pass"] and len(recs) > 0,
                         f"{rep['summary']['total']} references, {rep['summary']['blocking']} blocking, online={online}"))
        write_text(project / "output/verify.md", verify.to_markdown(rep))
    else:
        out.append(_gate("G-references", None, "references.bib not found"))

    # G-integrity — retraction / correction / expression-of-concern screening.
    # Uses the cached online report when `integrity` has been run; otherwise it
    # performs the offline title-marker pass so the gate is deterministic.
    cached = read_json(project / "output/integrity.json", None)
    if integrity.cache_matches(cached, recs):
        irep = cached
        idetail = "cached " + ("online" if irep["summary"].get("online") else "offline") + " screening (input SHA-256 + age <24h checked)"
    else:
        # Never fan out to the network from inside an audit: `integrity --online`
        # writes the cached report that this branch consumes. Deterministic CI.
        irep = integrity.check(recs if refspath else [], online=False)
        idetail = "offline title scan; run `integrity --online` for registry notices"
        write_json(project / "output/integrity.json", irep)
        write_text(project / "output/integrity.md", integrity.to_markdown(irep))
    # Always regenerate the human report, including when a valid JSON cache is reused.
    write_text(project / "output/integrity.md", integrity.to_markdown(irep))
    details["integrity"] = irep
    isum = irep["summary"]
    notices = sum(1 for r in irep["results"] if r["verdict"] in ("notice-found", "retracted-confirmed",
                                                                  "retracted-suspected"))
    out.append(_gate("G-integrity", isum["pass"] if refspath else None,
                     f"{isum['records']} refs, {notices} notices/suspicions, "
                     f"{isum['blocking']} blocking ({idetail})"))

    claimsp = _first(project, "evidence/claims.csv", "claims.csv")
    evidencep = _first(project, "evidence/evidence.csv", "evidence.csv")
    if claimsp and evidencep:
        rep = claims.validate(read_csv(claimsp), read_csv(evidencep),
                              read_text(manuscript) if manuscript else None)
        details["claims"] = rep
        out.append(_gate("G-claims", rep["summary"]["pass"],
                         f"{rep['summary']['claims']} claims / {rep['summary']['evidence_rows']} evidence rows, "
                         f"{rep['summary']['errors']} errors"))
        write_text(project / "output/claims.md", claims.to_markdown(rep))
    else:
        out.append(_gate("G-claims", None, "claim/evidence ledger not found",
                         blocking=bool((cfg.get("gates") or {}).get("require_claim_ledger", True))))

    screenp = _first(project, "screening/screening.csv", "screening.csv")
    need_prisma = bool((cfg.get("gates") or {}).get("require_prisma", False))
    if screenp:
        rep = prisma.report(read_csv(screenp))
        details["prisma"] = rep
        out.append(_gate("G-prisma", rep["pass"],
                         f"{rep['counts']['studies_included']} included, kappa={rep['agreement'].get('kappa')}"))
        write_text(project / "screening/PRISMA.md", prisma.to_markdown(rep))
    else:
        out.append(_gate("G-prisma", None, "screening log not found", blocking=need_prisma))

    disclosures = ["submission/data-availability.md", "submission/credit-statement.md",
                   "submission/ai-disclosure.md", "submission/cover-letter.md"]
    present = [d for d in disclosures if (project / d).is_file()]
    aipath = project / "submission/ai-disclosure.md"
    ai_ok = False
    if aipath.is_file():
        aitext = read_text(aipath)
        airep = disclosure.lint(aitext)
        ai_ok = airep["summary"]["pass"]
        details["ai_disclosure"] = airep
    out.append(_gate("G-disclosures", len(present) == len(disclosures) and ai_ok,
                     f"{len(present)}/{len(disclosures)} statements present; AI disclosure "
                     f"{'complete' if ai_ok else 'incomplete'}"))

    rebut = _first(project, "review/rebuttal-matrix.md")
    if rebut:
        txt = read_text(rebut)
        open_rows = txt.count("| open |")
        out.append(_gate("G-rebuttal", open_rows == 0 or "Example" in txt,
                         f"{open_rows} unresolved reviewer comments"))
    else:
        out.append(_gate("G-rebuttal", None, "rebuttal matrix not found", blocking=False))

    st = pipeline.status(project)
    out.append(_gate("G-pipeline", st["stage"] == "S9",
                     f"current stage {st['stage']} ({st['progress']})", blocking=False))

    blocking_failures = [g for g in out if g["blocking"] and g["status"] in ("fail", "missing")]
    verdict = "PASS" if not blocking_failures else "FAIL"
    report = {
        "project": str(project), "generated_at": now(), "verdict": verdict,
        "online_verification": online,
        "summary": {"gates": len(out), "passed": sum(1 for g in out if g["status"] == "pass"),
                    "failed": sum(1 for g in out if g["status"] == "fail"),
                    "missing": sum(1 for g in out if g["status"] == "missing"),
                    "blocking_failures": len(blocking_failures)},
        "gates": out,
        "limits": "Local, deterministic checks only. They cannot verify that experiments were "
                  "actually run, that raw data are authentic, or that results reproduce.",
    }
    (project / "output").mkdir(exist_ok=True)
    write_json(project / "output/audit.json", {k: v for k, v in report.items() if k != "details"})
    L = ["# Audit final — ScholarForge", "",
         f"Projet : `{project}`", f"Généré : `{report['generated_at']}`",
         f"Vérification en ligne : `{'oui' if online else 'non'}`", "",
         f"## Verdict : **{verdict}**", "",
         "| Porte | Statut | Bloquante | Détail |", "|---|---|---|---|"]
    for g in out:
        L.append(f"| `{g['gate']}` | {g['status']} | {'oui' if g['blocking'] else 'non'} | {g['detail']} |")
    L += ["", "## Limites", "", report["limits"], "",
          "Rapports détaillés : `output/lint.md`, `output/verify.md`, `output/claims.md`, "
          "`output/integrity.md`, `screening/PRISMA.md`, `output/audit.json`.", ""]
    write_text(project / "output/AUDIT.md", "\n".join(L) + "\n")
    report["details"] = details
    return report
