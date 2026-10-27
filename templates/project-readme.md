# {{TITLE}} — ScholarForge workspace

Created {{DATE}} by `scholarforge init`. All artefacts are plain text so they can be versioned.

```
.
├── draft/manuscript.md          # the paper
├── references.bib               # canonical bibliography (DOI for every entry)
├── sources/search-log.md        # reproducible queries
├── screening/screening.csv      # dual-screening decisions
├── screening/PRISMA.md          # generated flow + counts
├── evidence/evidence.csv        # one row per source passage
├── evidence/claims.csv          # one row per manuscript claim
├── review/                      # peer review, rebuttal, disclosures
├── submission/                  # final statements and cover letter
├── output/                      # lint, verify, claims, AUDIT
└── .scholarforge/state.json     # pipeline stage
```

## Routine
```bash
python3 scripts/scholarforge.py pipeline status
python3 scripts/scholarforge.py verify references.bib --online
python3 scripts/scholarforge.py lint draft/manuscript.md
python3 scripts/scholarforge.py claims --claims evidence/claims.csv --evidence evidence/evidence.csv
python3 scripts/scholarforge.py prisma screening/screening.csv
python3 scripts/scholarforge.py audit --online
```
