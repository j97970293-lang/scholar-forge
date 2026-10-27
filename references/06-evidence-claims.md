# 06 — Evidence and claim binding

## Evidence rows
One row per source passage, not per paper. Fields:
`evidence_id, source_id, locator, quote, design, stance, notes, level`.
- `locator`: page, section, figure/table number, timestamp or dataset row.
- `quote`: short verbatim excerpt (≤25 words in copyright text) or a faithful paraphrase
  labelled as such.
- `design`: rct, cohort, case-control, cross-sectional, systematic-review, case-report,
  simulation, preprint, expert-opinion, secondary-analysis.
- `stance`: supports / contradicts / mixed / background.

## Claim register
One row per manuscript assertion:
`claim_id, claim_text, section, evidence_ids, strength, source_refs, status`.
- `strength`: established / supported / suggestive / speculative.
- Only `established` may use "demonstrates", "proves" — and even then prefer "shows".
- A claim with contradicting evidence in the ledger cannot be `established`.
- Any `[citation needed]`, `[REF]`, `TODO` is a hard error.

```bash
python3 scripts/scholarforge.py claims \
  --claims evidence/claims.csv --evidence evidence/evidence.csv \
  --manuscript draft/manuscript.md --out output/claims.md
```
The validator reports dangling `evidence_id`s, orphan evidence rows, absolute wording without
hedges, strong wording on weak designs, contradicting evidence inside a claim's own ledger,
and claim text that no longer appears in the manuscript (revision drift).

## Evidence appraisal
- **GRADE** for bodies of evidence: high / moderate / low / very low. Downgrade for risk of
  bias, inconsistency, indirectness, imprecision, publication bias; upgrade for large effects,
  dose–response, confounding that would reduce the effect.
- **Risk of bias** by design: RoB 2 (RCT), ROBINS-I (non-randomised), QUADAS-2 (diagnostic),
  AMSTAR 2 (reviews), Newcastle–Ottawa (observational, use cautiously).
- Record domain-level judgements with a quoted justification; a number without criteria is
  not an appraisal.

## Synthesis
- **Narrative**: group by mechanism or outcome, not by author; explicitly surface conflicting
  findings and explain design/population differences.
- **Quantitative**: choose the effect measure first; fixed effect only when a common effect is
  plausible, otherwise random effects; report τ², I² and prediction intervals; pre-specify
  subgroups; inspect funnel asymmetry only with ≥10 studies.
- **Negative results** are evidence. Include them with the same rigour as positive ones.
- **Unverifiable parameter**: mark `UNVERIFIED` in a table, do not guess a plausible value.

## Concept matrix
For literature reviews, build a matrix: rows = studies, columns = theory, method, sample,
key finding, limitation, evidence level, relevance to RQ. It exposes gaps far better than a
chronological list of abstracts.

## Integrity boundary
This module checks internal consistency between the manuscript and its ledger. It cannot
verify that a quoted passage exists in the source, that data are authentic, or that the
analysis was actually run. A human must spot-check the quotes and the numbers.
