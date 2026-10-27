# 03 — Research questions, hypotheses and ideation

## From topic to question
Frameworks (choose one, do not stack them):
- **PICO** — Population, Intervention, Comparator, Outcome (interventions, clinical).
- **SPIDER** — Sample, Phenomenon of Interest, Design, Evaluation, Research type
  (qualitative/mixed).
- **PEO** — Population, Exposure, Outcome (observational).
- **FINER** — Feasible, Interesting, Novel, Ethical, Relevant (sanity check).
- **CIMO** — Context, Intervention, Mechanism, Outcome (design science).

A good question names the unit of analysis, the comparison and the measurable outcome.
"How does X affect Y?" becomes "Among [population/period], does [X] change [Y, measured as Z]
relative to [comparator], and is the effect modified by [W]?"

## Claim types (freeze before analysis)
| Type | Allowed verbs | Typical design |
|---|---|---|
| Descriptive | is, varies, occurs | survey, observational |
| Predictive | predicts, classifies | held-out validation |
| Associational | is associated with | cohort, cross-sectional |
| Causal | causes, reduces, increases | experiment, quasi-experiment |

Never let an associational design produce causal verbs. `lint` and the claim ledger flag
absolute/causal wording when study design is weak.

## Hypothesis generation protocol
1. **Freeze the observation** — what was seen, where, when, with what instrument. No
   interpretation yet.
2. **Set a dated evidence boundary** — what was known before the observation; prevents
   hindsight bias.
3. **Generate rivals first** — at least three competing explanations, including a null one.
4. **Derive discriminating predictions** — what each rival predicts and what would
   distinguish them. If two rivals predict the same observation, the design is uninformative.
5. **Declare the estimand** — population, treatment, outcome, summary measure.
6. **Operationalise measurement** — exact variable definitions, units, timing, reliability.
7. **Match design and analysis** — power, sampling, blinding, controls, model, assumptions.
8. **Set falsification thresholds** — the numeric result that would make you abandon H1.
9. **Pre-register** — `templates/preregistration.md`, OSF/PROSPERO; later additions are
   labelled exploratory.
10. **Log deviations** — date, reason, impact on inference.

## Ideation techniques (from the upstream brainstorming skills)
- **Combinatorial creativity** — cross two distant literatures; state the shared mechanism.
- **Analogical reasoning** — map a solved problem onto the target; list where the analogy breaks.
- **Constraint removal** — "what if compute/data/ethics constraints vanished?" then re-add them
  as engineering requirements.
- **Inversion** — "what result would be most surprising / most boring?" and why.
- **Gap taxonomy** — empirical gap, methodological gap, theoretical tension, reproducibility
  gap, population gap. Every gap claim needs a citation.

## Red-team the idea
Ask: what is the cheapest observation that kills it? Which confounder explains it equally
well? Is the effect size plausible given measurement error? Who would disagree and on what
evidence? Record answers in `review/idea-redteam.md`.

## Deliverable
`preregistration.md` + a one-paragraph plain-language statement of the question, the rival
explanations and the falsification criterion.
