# 05 — Screening and PRISMA 2020

## Before screening
Freeze eligibility criteria in `templates/prisma-protocol.md`: population, design, outcome,
time window, language, publication status. Register the protocol (PROSPERO/OSF) where
possible. Every reviewer reads the same criteria. Pilot on 20–50 records and compute agreement
before the main run.

## Ordered exclusion codes (first match wins)
```
E1-duplicate · E2-not-primary-research · E3-wrong-population · E4-wrong-intervention
E5-wrong-outcome · E6-wrong-design · E7-wrong-language · E8-full-text-unavailable
E9-retracted · E10-other (free-text justification required)
```
Ordering prevents the same record being excluded for different reasons on different days.

## Two independent decision passes
- `r1` and `r2` are independent: include / exclude / unclear. "unclear" is a valid state
  that triggers adjudication — it is never auto-resolved.
- Disagreement → `adjudicated` by a third reviewer with a written reason.
- `final` = adjudicated decision, else the agreement of r1/r2, else `unclear` (blocker).
- AI reviewers are **decision support**. The human review team signs off.

## Quality control
- Insert known seed studies (must be included) and near-miss studies (must be excluded).
- Re-screen a random 10% sample blind; compare with the original decisions.
- Compute Cohen's κ and PABAK on paired title/abstract decisions; report the value, not just
  "good agreement". κ > 0.8 almost perfect, 0.6–0.8 substantial, 0.4–0.6 moderate.
- Track criteria drift: if the exclusion-reason distribution shifts between batches, pause.

## Running the tool
```bash
python3 scripts/scholarforge.py prisma screening/screening.csv --out screening/PRISMA.md
```
CSV columns: `id, source, stage (ta|ft), title, r1, r2, adjudicated, exclusion_code, notes`.
The report gives counts by source, exclusion reasons, κ/PABAK, a Mermaid flow diagram and a
list of anomalies. `pass` requires zero unresolved decisions and zero validation errors.

## PRISMA 2020 counts
```
identified → duplicates removed → records screened (title/abstract)
          → excluded with reasons → full texts assessed
          → excluded with reasons → studies included in synthesis
```
Every number must trace to a row in `screening.csv`. Never copy numbers from a flow-diagram
template. Keep the full search strings for each source in the protocol.

## Reporting
PRISMA 2020 checklist (27 items), PRISMA-S for search reporting, AMSTAR 2 for appraising
existing reviews, and the appropriate risk-of-bias tool per design. State the synthesis
method (random/fixed effects and why), heterogeneity statistics and publication-bias
assessment where ≥10 studies are available.

## Anti-patterns
- One reviewer only, described as "double screening" because an LLM was asked twice.
- Excluding by "not relevant" with no ordered code.
- Reporting n included but not n excluded by reason.
- Reusing a PRISMA diagram from a previous review.

**Complément 1.1.0** : pour de grands corpus, un outil d'apprentissage actif
peut prioriser les références, mais il ne remplace pas le double criblage humain ni le
calcul de κ. Voir les playbooks 27 (journal de recherche) et 28 (outils externes).
