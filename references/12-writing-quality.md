# 12 — Writing quality, anti-slop and authorial voice

## What "AI slop" is
Fluent text that is specific-looking but evidentially empty. It has recognisable symptoms:
stock vocabulary, empty emphasis, stacked hedges, formulaic signposting, monotone rhythm,
and claims vaguer than the underlying data. The linter detects the surface symptoms; the
author fixes the substance.

```bash
python3 scripts/scholarforge.py lint draft/manuscript.md --out output/lint.md
```
Rules live in `config/rules.json`; add your discipline's clichés there.

## Symptom → repair
| Symptom | Example | Repair |
|---|---|---|
| Stock phrase | "delves into the tapestry of…" | Name the thing and the finding. |
| Empty emphasis | "plays a pivotal role" | State the measured effect. |
| Hedge stack | "may possibly suggest that…" | One qualifier + the evidence. |
| Formulaic contrast | "not only X but also Y" | Two plain sentences. |
| Dash pile-up | 20 em-dashes in a page | Use colons, semicolons, parentheses. |
| Monotone rhythm | every sentence 18–22 words | Mix 8-word and 30-word sentences. |
| Vague claim | "significantly improved outcomes" | "reduced 30-day readmission by 4.1 pp (95% CI 1.2–7.0)". |
| Nominalisation | "the implementation of the analysis" | "we analysed". |
| Universal claim | "all studies show" | Name the studies/count the exceptions. |

## Rewrite procedure (in order)
1. **Verify first** — never polish a sentence containing an unverified claim.
2. Delete stock phrases and filler openers.
3. Replace vague nouns/verbs with the actual measurement or mechanism.
4. Cut one hedge per stack; keep the one that reflects real uncertainty.
5. Break any sentence >40 words; vary the rhythm.
6. Convert passive voice to active when the actor matters.
7. Re-check that no number, citation or qualifier changed meaning.
8. Run the linter again and compare scores.

## Hedging is not the enemy
Academic hedging expresses genuine uncertainty. Keep "may/might/suggest" when the design
warrants it. The problem is *stacked* hedging ("may possibly suggest") and hedges used to
smuggle in an unsupported claim. Match the hedge to the evidence level from the ledger.

## Voice preservation
- Ask for two paragraphs of the author's previous writing and mirror their sentence length,
  terminology and preferred tense; do not impose a house "AI voice".
- Keep discipline-specific jargon where it is precise; remove it where it obscures.
- Never replace a technical term with a popular synonym to sound readable.

## Multilingual writing
- Write each language version natively; do not translate idioms literally.
- Bilingual abstracts must be semantically equivalent, including numbers and hedges.
- Preserve CJK author names and reference ordering; do not ASCII-fold.
- Mark machine-translated passages for human review.
- LaTeX: use `babel`/`polyglossia`, XeLaTeX/LuaLaTeX for CJK, and check hyphenation.

## What the linter cannot judge
Scientific correctness, whether a citation supports a claim, whether the tone fits the venue,
or whether the author's voice is authentic. It flags; a human decides. A high score is not a
quality certificate.
