# 14 — Rebuttal and revision

## Step 1 — Triage before writing
Classify every reviewer comment:
- **Factual correction** → fix, cite location.
- **Clarification** → rewrite the passage; no new experiment needed.
- **Additional analysis** → feasible now? run it, report honestly; if not, say why and what
  the existing evidence can/cannot support.
- **Scope/novelty critique** → sharpen positioning with evidence, not adjectives.
- **Disagreement** → respectful, evidence-based counter-argument with a compromise.
- **Out of scope** → explain the boundary and, where cheap, add a limitation sentence.

Use `templates/rebuttal-matrix.md`. Never merge two comments into one answer.

```bash
python3 scripts/scholarforge.py rebuttal review/reviews.md \
  --out-csv review/rebuttal-matrix.csv --out-md review/rebuttal-matrix.md
```

## Step 2 — Do the work first
The response letter describes changes already made. Running no new experiment but writing
"we have added the experiment" is fabrication. If a promise cannot be kept by the deadline,
remove the promise and state the constraint.

## Step 3 — Reply pattern
> **R2C3 (methods, §3.2, p. 7):** "The sample size justification is missing."
> **Response:** We agree. We added an a priori power calculation for the primary outcome
> (80% power at α = 0.05 for a 5-point difference, SD = 12, n = 92 per arm), now in
> §3.2, p. 7, lines 201–208.
> **Change:** §3.2 + Table S2. **Evidence:** E014.

Rules: quote or faithfully paraphrase, answer first, then context, then the change, then the
exact location. Keep the venue's word/character limit; details belong in the manuscript.

## Disagreeing well
- Acknowledge the concern and the reviewer's underlying goal.
- Provide evidence (data, a cited methodological argument, a reported constraint).
- Offer a compromise (a sensitivity analysis, a toned-down claim, a limitations sentence).
- Never use "the reviewer misunderstood" — write "our original wording was ambiguous".

## Revision patches and traceability
- Keep a change log with `comment_id → file, section, diff, claim_ids affected`.
- After revision, re-run the claim ledger: claim text drift and claim-strength drift are
  checked by `claims` with `--manuscript`.
- Re-run citation verification on the new bibliography; added references are a common source
  of fabricated DOIs.
- Check that all figures/tables still match the new numbers.

## Cover note to the editor
Summarise the three most substantive changes, confirm compliance with the revision policy,
note any unresolved disagreement honestly, and include the point-by-point response.

## Anti-patterns
- Answering only the easy comments.
- Repeating the abstract instead of addressing the concern.
- Promising future work as if it were done.
- Silently strengthening conclusions while claiming to only "clarify".
