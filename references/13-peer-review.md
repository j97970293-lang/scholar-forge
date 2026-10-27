# 13 — Peer review (simulated and real)

## Safety boundary
Only review a manuscript you are authorised to review. Never upload a confidential manuscript
to an external service. A simulated review is labelled **simulated** — it is not a real
referee report, and role-separated AI personas are not independent error processes.

## Seat structure (adapted from the merged suites)
| Seat | Focus |
|---|---|
| Journal-fit reviewer | Scope, novelty, expected readership, format compliance |
| Methods reviewer | Design, identification, measurement, bias |
| Domain reviewer | Prior literature, theoretical framing, plausibility |
| Statistics reviewer | Model, assumptions, uncertainty, multiplicity |
| Devil's advocate | Strongest counter-argument, falsification, logical fallacies |
| Editorial synthesizer | Conflicts between seats, decision, revision roadmap |

Each seat works independently, cites locations (section/line/figure), and distinguishes
observation from inference. The synthesizer never invents a concern and never deletes an
inconvenient one.

## Review workflow
1. **Intake gate** — competing interests, authorisation, completeness, confidentiality.
2. **Orient without deciding** — 100–150 word summary in the reviewer's own words.
3. **Select reporting guideline** — CONSORT/STROBE/PRISMA/TRIPOD+AI per design.
4. **Map claims to evidence** — build a claim–evidence table; flag unsupported claims.
5. **Methods and statistics** — power, randomisation, confounders, missing data, multiplicity,
   assumption checks, uncertainty, reproducibility.
6. **Reproducibility and transparency** — data/code, preregistration, seeds, versions.
7. **Ethics and integrity** — IRB/consent, image manipulation, tortured phrases, suspicious
   citations, AI disclosure.
8. **Figures/tables** — captions, units, n, error bars, colour accessibility.
9. **Actionable comments** — location + observation + why it matters + concrete fix,
   ordered by severity.
10. **Recommendation** — accept / minor / major / reject with explicit justification and a
    confidence level.
11. **Lint** — `scholarforge review review/draft.md` checks for respectful tone, anchored
    comments and justified recommendations.

## Quality rubrics
Score each of novelty, methodological rigour, evidence quality, clarity, reproducibility and
ethical compliance on 1–5 with a written reason. Never average rubric numbers into an
accept/reject decision; the justification decides.

## Re-review mode
Compare the revision against the original concerns: resolved / partially resolved / not
addressed / new issue introduced. Verify that claim strength did not silently increase during
revision (claim drift). Check the response-to-reviewers matrix for promises that were not
fulfilled.

## Anti-patterns
- Generic praise followed by three trivial typos.
- Demanding experiments the venue/timeframe cannot support.
- Recommending rejection for a fixable methodological clarification.
- Inventing a missing reference and telling the authors to cite it.
- Leaking a confidential decision or sharing the manuscript with a third party.
