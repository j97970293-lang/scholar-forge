"""Ten-stage research pipeline state machine with explicit quality gates.

Stages are adapted from the ARS orchestrator and the KalarisLabs workflow:
each stage has an exit gate, and no stage may be skipped silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .util import find_project, now, read_json, write_json

STAGES: List[Dict[str, Any]] = [
    {"id": "S0", "name": "Intake & scoping", "reference": "02-intake-routing",
     "artifacts": ["README.md", ".scholarforge/config.json"],
     "gate": "Research question, target venue, language and constraints recorded."},
    {"id": "S1", "name": "Question & hypotheses", "reference": "03-question-ideation",
     "artifacts": ["review/preregistration.md"],
     "gate": "Falsifiable RQ, rival explanations, discriminating predictions frozen before analysis."},
    {"id": "S2", "name": "Search & corpus", "reference": "04-search-sources",
     "artifacts": ["sources/search-log.md"],
     "gate": "Every database query, date, filter and hit count logged; saturation assessed."},
    {"id": "S3", "name": "Screening & PRISMA", "reference": "05-screening-prisma",
     "artifacts": ["screening/screening.csv", "screening/PRISMA.md"],
     "gate": "Dual decisions, adjudication, ordered exclusion codes, kappa, flow counts."},
    {"id": "S4", "name": "Evidence & claims", "reference": "06-evidence-claims",
     "artifacts": ["evidence/evidence.csv", "evidence/claims.csv"],
     "gate": "Every claim bound to ≥1 evidence row; no dangling ids; no overclaims."},
    {"id": "S5", "name": "Drafting", "reference": "11-manuscript-writing",
     "artifacts": ["draft/manuscript.md"],
     "gate": "IMRaD complete; figures/tables referenced; no placeholders; no fabricated data."},
    {"id": "S6", "name": "Integrity check I", "reference": "07-citation-verification",
     "artifacts": ["output/verify.md", "output/lint.md"],
     "gate": "References resolve; style score ≥ threshold; no unresolved placeholders."},
    {"id": "S7", "name": "Peer review (simulated)", "reference": "13-peer-review",
     "artifacts": ["review/peer-review-form.md"],
     "gate": "Independent methodological, statistical and devil's-advocate critiques recorded."},
    {"id": "S8", "name": "Revision & rebuttal", "reference": "14-rebuttal-revision",
     "artifacts": ["review/rebuttal-matrix.md"],
     "gate": "Every reviewer comment has a response, an action and a manuscript location."},
    {"id": "S9", "name": "Final audit & submission", "reference": "15-venue-submission",
     "artifacts": ["output/AUDIT.md", "submission/cover-letter.md", "submission/data-availability.md",
                   "submission/credit-statement.md", "submission/ai-disclosure.md"],
     "gate": "All gates pass; venue rules re-checked on the official page; disclosures complete."},
]


def state_path(root: Optional[Path | str] = None) -> Path:
    return find_project(str(root) if root else None) / ".scholarforge/state.json"


def load(root: Optional[Path | str] = None) -> Dict[str, Any]:
    p = state_path(root)
    if not p.exists():
        return {"schema": "scholarforge-project-v1", "stage": "S0", "history": [],
                "created_at": now(), "note": "no project state; run `scholarforge init`"}
    return read_json(p, {}) or {}


def save(state: Dict[str, Any], root: Optional[Path | str] = None) -> Path:
    return write_json(state_path(root), state)


def stage_index(stage: str) -> int:
    return next((i for i, s in enumerate(STAGES) if s["id"].upper() == stage.upper()), -1)


def check_artifacts(root: Path, stage: Dict[str, Any]) -> Dict[str, Any]:
    missing = [a for a in stage["artifacts"] if not (root / a).exists()]
    return {"stage": stage["id"], "required": stage["artifacts"], "missing": missing,
            "satisfied": not missing}


def status(root: Optional[Path | str] = None) -> Dict[str, Any]:
    p = state_path(root)
    project = p.parent.parent
    st = load(root)
    idx = stage_index(st.get("stage", "S0"))
    return {
        "project": str(project), "stage": st.get("stage", "S0"),
        "stage_name": STAGES[idx]["name"] if idx >= 0 else "unknown",
        "progress": f"{idx+1}/{len(STAGES)}",
        "current_gate": STAGES[idx]["gate"] if idx >= 0 else "",
        "artifacts": check_artifacts(project, STAGES[idx]) if idx >= 0 else {},
        "stages": [{"id": s["id"], "name": s["name"], "reference": s["reference"],
                    "done": i < idx, "current": i == idx} for i, s in enumerate(STAGES)],
        "history": st.get("history", []),
    }


def advance(target: str, root: Optional[Path | str] = None, force: bool = False) -> Dict[str, Any]:
    st = load(root)
    cur = stage_index(st.get("stage", "S0"))
    tgt = stage_index(target)
    if tgt < 0:
        raise ValueError(f"unknown stage {target}; choose from {[s['id'] for s in STAGES]}")
    project = state_path(root).parent.parent
    checks = [check_artifacts(project, s) for s in STAGES[max(0, cur):tgt + 1]]
    blocked = [c for c in checks if not c["satisfied"]]
    if blocked and not force:
        return {"ok": False, "reason": "gate artifacts missing",
                "missing": [{"stage": c["stage"], "files": c["missing"]} for c in blocked],
                "hint": "Create the listed artifacts or re-run with --force to record an explicit override."}
    st.setdefault("history", []).append({
        "from": STAGES[cur]["id"] if cur >= 0 else "S0", "to": STAGES[tgt]["id"],
        "at": now(), "force": bool(force and blocked),
        "missing_at_advance": [c["missing"] for c in blocked],
    })
    st["stage"] = STAGES[tgt]["id"]
    st["updated_at"] = now()
    save(st, root)
    return {"ok": True, "stage": st["stage"], "name": STAGES[tgt]["name"],
            "gate": STAGES[tgt]["gate"], "forced": bool(force and blocked)}


def reset(root: Optional[Path | str] = None, stage: str = "S0") -> Dict[str, Any]:
    st = load(root)
    st.setdefault("history", []).append({"reset_to": stage, "at": now()})
    st["stage"] = stage.upper()
    save(st, root)
    return {"ok": True, "stage": st["stage"]}
