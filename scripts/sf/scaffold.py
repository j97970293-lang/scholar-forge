"""Workspace scaffolding and template rendering."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from .util import ROOT, now, read_text, write_csv, write_json, write_text

TEMPLATES = ROOT / "templates"

STARTER_FILES = [
    "manuscript-imrad.md", "prisma-protocol.md", "peer-review-form.md",
    "rebuttal-matrix.md", "cover-letter.md", "data-availability.md",
    "credit-statement.md", "ai-disclosure.md", "preregistration.md",
    "research-brief.md", "pipeline-status.md",
]


def render(template: str, **values: Any) -> str:
    defaults = {"TITLE": "Untitled study", "DATE": date.today().isoformat(),
                "AUTHOR": "Author name", "VENUE": "Target venue", "TOPIC": "research topic",
                "VERSION": "1.0.0", "EMAIL": "author@institution.edu"}
    defaults.update({k: str(v) for k, v in values.items()})
    p = TEMPLATES / template
    text = read_text(p) if p.exists() else f"# {template}\n"
    for k, v in defaults.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def new(kind: str, path: Path | str, **values: Any) -> Path:
    mapping = {
        "manuscript": "manuscript-imrad.md", "imrad": "manuscript-imrad.md",
        "protocol": "prisma-protocol.md", "prisma": "prisma-protocol.md",
        "review": "peer-review-form.md", "rebuttal": "rebuttal-matrix.md",
        "cover": "cover-letter.md", "cover-letter": "cover-letter.md",
        "data": "data-availability.md", "credit": "credit-statement.md",
        "ai": "ai-disclosure.md", "disclosure": "ai-disclosure.md",
        "prereg": "preregistration.md", "brief": "research-brief.md",
        "status": "pipeline-status.md", "latex": "manuscript-imrad.tex",
    }
    tpl = mapping.get(kind.lower())
    if not tpl:
        raise ValueError(f"unknown template kind '{kind}'; choose from {sorted(mapping)}")
    out = Path(path)
    if out.is_dir():
        out = out / tpl
    return write_text(out, render(tpl, **values))


def init_project(root: Path | str, name: str = "My study", mode: str = "full") -> Dict[str, Any]:
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / ".scholarforge").mkdir(exist_ok=True)
    for d in ("draft", "sources", "screening", "evidence", "review", "submission", "output"):
        (root / d).mkdir(exist_ok=True)
    vals = {"TITLE": name}
    write_text(root / "draft/manuscript.md", render("manuscript-imrad.md", **vals))
    write_text(root / "README.md", render("project-readme.md", **vals))
    write_text(root / "references.bib", render("references.bib"))
    for tpl in STARTER_FILES:
        write_text(root / "review" / tpl, render(tpl, **vals))
    for tpl in ("cover-letter.md", "data-availability.md", "credit-statement.md", "ai-disclosure.md"):
        write_text(root / "submission" / tpl, render(tpl, **vals))
    write_csv(root / "evidence/evidence.csv", [
        {"evidence_id": "E001", "source_id": "", "locator": "", "quote": "",
         "design": "", "stance": "supports", "notes": "Replace this example row."},
    ], ["evidence_id", "source_id", "locator", "quote", "design", "stance", "notes"])
    write_csv(root / "evidence/claims.csv", [
        {"claim_id": "C001", "claim_text": "Example claim; rewrite.", "section": "Results",
         "evidence_ids": "E001", "strength": "suggestive", "source_refs": "", "status": "draft"},
    ], ["claim_id", "claim_text", "section", "evidence_ids", "strength", "source_refs", "status"])
    write_csv(root / "screening/screening.csv", [
        {"id": "R001", "source": "OpenAlex", "stage": "ta", "title": "Example record",
         "r1": "include", "r2": "include", "adjudicated": "", "exclusion_code": "", "notes": ""},
    ], ["id", "source", "stage", "title", "r1", "r2", "adjudicated", "exclusion_code", "notes"])
    state = {"schema": "scholarforge-project-v1", "name": name, "mode": mode,
             "created_at": now(), "stage": "S0", "history": []}
    write_json(root / ".scholarforge/state.json", state)
    write_json(root / ".scholarforge/config.json", {
        "citation_style": "apa", "target_venue": "", "language": "en",
        "gates": {"min_style_score": 70, "require_claim_ledger": True,
                  "require_reference_verification": True, "require_prisma": mode in ("full", "review")},
        "online_verification": False,
    })
    return {"root": str(root), "files": [str(p.relative_to(root)) for p in sorted(root.rglob("*")) if p.is_file()],
            "state": state}
