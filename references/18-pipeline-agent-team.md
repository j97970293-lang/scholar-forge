# 18 — Pipeline orchestration and agent team

## State machine
Ten stages S0–S9 (see `SKILL.md` §3). Each stage has: required artefacts, an exit gate, a
reference playbook and an owner. The orchestrator does **not** do the substantive work — it
detects the stage, selects the mode, dispatches the work, records the state and enforces the
gate.

```bash
python3 scripts/scholarforge.py pipeline status
python3 scripts/scholarforge.py pipeline advance S5 --force   # records the override
python3 scripts/scholarforge.py pipeline stages --json
```

State lives in `.scholarforge/state.json`; every transition appends a history entry with
timestamp, from/to, and any missing artefacts that were overridden. Don't hide progress in
chat messages — the state file is the source of truth.

## Checkpoints
- **LIGHT** — after a single stage: report artefacts + gate result, continue automatically.
- **FULL** — at S1, S4, S6, S7, S9: stop and ask the human to approve before continuing.
  Show: what changed, what is unverified, the estimated cost/time of the next stage, and the
  exact decision requested.
- **Mid-conversation reinforcement** — restate the active constraints (venue, evidence
  boundary, experiment declaration) every few stages; long sessions drift.

## Agent roles (from the merged suites)
| Role | Responsibility |
|---|---|
| Intake / router | scope, mode, assumptions, state |
| Research questioner | RQ, rivals, falsification |
| Searcher | queries, logs, dedupe, provenance |
| Screener A / B / adjudicator | dual screening, kappa, PRISMA |
| Evidence librarian | evidence rows, claim binding, risk of bias |
| Writer | IMRaD drafting from the ledger, never from imagination |
| Style editor | anti-slop, rhythm, voice preservation |
| Verification agent | references, statistics, figure/claim consistency |
| Reviewer panel | journal-fit, methods, domain, stats, devil's advocate |
| Rebuttal lead | matrix, responses, revision patches |
| Submission officer | venue rules, disclosures, final audit |

Role separation improves coverage; it is **not** a claim that AI personas produce independent
errors. Never describe a single model's five prompts as "five independent reviewers".

## Handoff envelope
Between stages, pass a small JSON envelope:
```
{ "stage": "S4", "artefacts": ["evidence/claims.csv"], "open_questions": [...],
  "unverified": [...], "assumptions": [...], "gate": "G4-claims", "hash": "sha256:…" }
```
The receiver validates the envelope before consuming it; a malformed or missing envelope is a
blocker, not a reason to guess. Cross-model verification (if a second model is available) is
an optional advisory channel, never a substitute for human review.

## Adaptive stopping
Stop early when: the question is unanswerable with available evidence; the venue rules
prohibit the requested method; the human has not supplied confidential data needed for the
next stage; or the budget/time cap is reached. Record the reason in state.

## Anti-patterns
- Running all ten stages in one uninterrupted generation.
- Auto-advancing past a failed integrity gate.
- Rewriting the research question after seeing the results without logging the deviation.
- Treating a completed draft as a completed pipeline.
