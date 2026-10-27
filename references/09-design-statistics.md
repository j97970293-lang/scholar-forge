# 09 — Experimental design, power and statistics

## Match the design to the claim
Write the estimand first (population, treatment/exposure, comparator, outcome, time horizon,
summary measure). Then choose a design that identifies it. If identification is impossible,
downgrade the claim from causal to associational in the manuscript — not just in the
limitations.

| Claim | Minimum design | Must report |
|---|---|---|
| Prevalence / description | representative sample | sampling frame, response rate, weighting |
| Prediction | train/validation/test split | leakage checks, calibration, external validation |
| Association | cohort/cross-sectional | confounder set chosen a priori, missing data |
| Causation | randomised / strong quasi-experiment | assignment, blinding, attrition, ITT |
| Mechanism | mediation / process experiment | assumptions, temporal order, manipulation check |

## Power and sample size
- Compute power for the **primary** outcome with a pre-specified smallest effect size of
  interest, not a hoped-for effect. Record the tool, version and all assumptions.
- Report attrition and the resulting effective n. Post-hoc power based on the observed effect
  is uninformative; report precision (CI width) instead.
- For clustered/hierarchical data account for the design effect / ICC.
- For ML studies, report the number of runs/seeds and variance, not the best single run.

## Analysis plan essentials
`templates/preregistration.md`: primary model with formula and link, covariates with
rationale, missing-data handling (prefer multiple imputation over complete-case when
plausible), multiplicity control (Holm/Bonferroni/FDR — state which family), assumption
checks, sensitivity analyses, robustness to alternative specifications, software/version,
random seeds. Anything added after seeing the data is labelled exploratory.

## Reporting numbers
- Effect sizes with confidence/credible intervals; never a bare p-value.
- Exact n, denominators, units, precision of instruments, and how uncertainty was computed.
- Distinguish statistical from practical/clinical significance.
- Report negative/null results and failed replications with the same prominence.
- Avoid "trend toward significance"; say "the confidence interval includes both…".
- Multiplicity: state the number of tests and the correction; don't cherry-pick.

## Common fallacies (flag on sight)
1. HARKing — hypothesis presented as if pre-specified.
2. p-hacking / garden of forking paths.
3. Treating a non-significant result as evidence of no effect.
4. Difference between "significant" and "not significant" treated as significant.
5. Regression to the mean mistaken for treatment effect.
6. Simpson's paradox / aggregation bias.
7. Survivorship and selection bias; collider conditioning.
8. Data leakage (preprocessing fitted on the test set, duplicated records).
9. Baseline imbalance testing in randomised trials as a validity check.
10. Pseudoreplication (treating repeated measures as independent).
11. Correlation used as causal evidence.
12. Unvalidated proxy used as ground truth.

## Reporting guidelines (verify current version on equator-network.org)
`config/reporting-guidelines.json`: CONSORT (RCT), STROBE (observational), PRISMA 2020
(reviews), STARD (diagnostic), TRIPOD+AI (prediction), COREQ/SRQR (qualitative), ARRIVE 2.0
(animals), SPIRIT (protocols), CARE (case reports), CHEERS (economics), plus ML venue
reproducibility checklists. Fill the checklist, don't just cite it.

## Reproducible analysis
- One command reproduces all tables/figures from raw data.
- Environment lockfile, versions, seeds, hashes of input data.
- Separate raw (immutable), interim and processed data.
- Never hand-edit a results table; generate it from the analysis script.
- Store the analysis script next to the ledger; the manuscript cites figure/table IDs.

## Integrity boundary
A reported p-value can be internally consistent and still be fabricated. Local checks cannot
verify that an experiment was run, that raw data are authentic, or that results reproduce.
