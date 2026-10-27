# 19 — Quality gates and audit artefacts

## Gate definitions
`config/gates.json` is the machine-readable source of truth. Summary:

| Gate | Stage | Blocking check |
|---|---|---|
| G0-scope | S0 | RQ, venue, language, constraints, data-access level |
| G1-falsifiability | S1 | Rival hypotheses + discriminating predictions frozen |
| G2-reproducible-search | S2 | Query log with database, string, filters, date, hits |
| G3-screening | S3 | Dual decisions, adjudication, codes, kappa, PRISMA counts |
| G4-claims | S4 | Every claim bound; no dangling ids; no overclaims |
| G5-draft | S5 | IMRaD complete, no placeholders, figures referenced |
| G6-integrity-1 | S6 | References resolve; style score ≥ 70; no `TODO` |
| G7-review | S7 | ≥3 evidence-anchored perspectives recorded |
| G8-revision | S8 | Every reviewer comment has response, action, location |
| G9-final | S9 | All gates pass; disclosures complete; venue re-checked |

## Status vocabulary
`pass` — deterministic check succeeded. `fail` — check ran and found a problem. `missing` —
artefact absent, so no check could run. Both `fail` and `missing` block a blocking gate.
`advisory` — non-blocking, recorded for transparency.

## Running the audit
```bash
python3 scripts/scholarforge.py audit --online --json
```
Aggregates: `lint` (style/placeholders), `verify` (references, optional Crossref online),
`claims` (ledger consistency), `prisma` (screening, when required), rebuttal closure,
disclosure presence, and pipeline stage. Writes `output/AUDIT.md`, `output/audit.json`,
`output/lint.md`, `output/verify.md`, `output/claims.md`, `screening/PRISMA.md`.

## Rule precedence
1. Hard integrity rules (no fabrication, confidentiality, legality) — never overridable.
2. Blocking gates — overridable only by an explicit human `--force` recorded in state.
3. Advisory gates — reported, never blocking.
4. Style preferences — advisory only; the author's voice wins.

## Honest reporting
Report the counts, not just the verdict: "6/8 gates pass, 1 fail (G4-claims, 3 dangling
evidence ids), 1 missing (G-prisma)". State whether verification was online. Include the
integrity note that a PASS does not establish empirical truth.

## Common gate failures and fixes
| Failure | Fix |
|---|---|
| `placeholder` in lint | Replace `TODO`/`[citation needed]` with verified content. |
| `mismatch` DOI | Open the DOI, correct the reference or remove the claim. |
| dangling `evidence_id` | Add the evidence row or fix the typo in claims.csv. |
| unresolved screening row | Obtain the second decision or adjudicate. |
| `open` rebuttal row | Write the response, action and manuscript location. |
| missing disclosure | Render the template and fill it with real facts. |

## Audit limitations (always print)
Gates examine the manuscript and its reported process. They cannot verify that experiments were
performed, that raw data are authentic, or that results reproduce. A consistently reported
fabrication can pass. Human accountability is not transferable to the tool.
