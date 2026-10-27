# 02 — Intake, ambiguity and routing

## The intake interview (max 3 questions)
Ask only for facts that change the work:
1. **Deliverable & venue** — paper, thesis chapter, systematic review, grant, rebuttal,
   quick brief? Which journal/conference/style (APA 7, IEEE, LNCS, Nature, house style)?
2. **Scope & depth** — quick (≈1 h), standard (days), full pipeline (weeks), or a single
   stage? What is the date cutoff for the evidence boundary?
3. **Available material** — existing data, corpus, draft, bibliography, reviewer comments,
   ethics approval, preregistration? What must not be sent to external services?

If the user supplies none, proceed with declared assumptions written into
`.scholarforge/config.json`: `{"target_venue":"", "language":"en", "mode":"standard",
"citation_style":"apa", "online_verification":false}`. Never block on missing answers.

## Routing decision table
| Signal | Route |
|---|---|
| "review my paper / referee report" | peer review → `13` |
| "respond to reviewer 2" | revision → `14` |
| "check my references / DOI" | verification → `07`, `08` |
| "find literature / reading list" | discovery → `04` |
| "systematic review / PRISMA" | protocol → `03`, `04`, `05`, `06` |
| "write the discussion / abstract" | writing → `11`, `12` |
| "submit to X" | submission → `15`, `16`, `19` |
| "from idea to submitted paper" | full pipeline → `18` |
| "which skill should I use" | ecosystem → `20`, `registry search` |
| "is this claim true" | critical appraisal → `06`, `09` |

## Escape hatch and explicit intent
`[direct-mode]` at byte 0 means: strip the token, skip the intake questions, act on the
explicit intent. Anywhere else it is ordinary text. Naming a skill is not a bypass of the
integrity rules.

Cross-phase inputs (a draft plus reviewer comments plus a bibliography) require one
clarification question: "Which artefact should I produce first?" — then proceed.

## Mode spectrum
| Mode | Stages | Typical output |
|---|---|---|
| `quick` | S0, S2, S5 | 1–2 page research brief |
| `standard` | S0–S6 | Full draft + verification |
| `review-protocol` | S0–S6 (PRISMA) | Protocol, screening, synthesis |
| `full` | S0–S9 | Submission-ready package |
| `verify` | S6 only | Verification report |
| `revision` | S8 | Rebuttal matrix + revised draft |
| `audit` | S9 | AUDIT.md with gate verdicts |

## Intake record
Write to `README.md` / `.scholarforge/config.json`:
- research question (provisional), date of evidence boundary
- target venue + URL of the official guidelines
- language, citation style, word/page budget
- declared assumptions and constraints
- confidentiality level: `public` / `embargoed` / `confidential`
- experiment intake declaration: `experiments_declared` / `no_experiments_declared`

## Anti-patterns
- Asking five clarifying questions before doing any work.
- Treating "write me a paper" as permission to invent data.
- Choosing a citation style from memory without checking the venue.
- Starting to draft before the evidence boundary is dated.
