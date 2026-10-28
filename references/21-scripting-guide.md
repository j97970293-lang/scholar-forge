# 21 — CLI scripting guide

## Installation
No install. Python 3.9+ standard library only.
```bash
git clone <your-private-repo> scholar-forge
cd scholar-forge
python3 scripts/scholarforge.py doctor
python3 scripts/scholarforge.py selftest
```
Optional: `alias sf='python3 /path/to/scholar-forge/scripts/scholarforge.py'`.
All commands accept `--json`. Exit codes: 0 = pass, 1 = gate failed, 2 = input error.
Network commands fail soft per source.

## Command map
| Command | Input | Output |
|---|---|---|
| `doctor` | — | runtime + asset check |
| `selftest` | — | unittest results |
| `init` | `--path --name --mode` | project workspace |
| `new KIND PATH` | template kind | one rendered file |
| `search QUERY` | `--sources --limit --out --bib` | merged hits with provenance |
| `dedupe FILE` | BibTeX/RIS/JSON | clean bibliography |
| `verify FILE` | BibTeX/RIS/JSON, `--online` | verification report |
| `bib FILE` | `--style` | formatted reference list |
| `prisma FILE` | screening.csv | counts, κ, flow diagram |
| `claims` | `--claims --evidence --manuscript` | ledger validation |
| `lint FILE` | Markdown/LaTeX/text | style + placeholder report |
| `review FILE` | review draft | evidence/tone lint |
| `rebuttal FILE` | reviewer comments | CSV + Markdown matrix |
| `registry search/stats` | query | ecosystem matches |
| `pipeline status/advance/reset/stages` | stage | state machine |
| `audit` | project, `--online` | AUDIT.md + gate verdict |

## Worked pipeline A — from topic to verified draft
```bash
sf init --path ~/papers/velocity --name "RNA velocity benchmarks" --mode full
cd ~/papers/velocity
sf search "single-cell RNA velocity benchmarking" --sources openalex,crossref,arxiv \
  --limit 20 --out sources/hits.json --bib sources/hits.bib
sf dedupe sources/hits.bib --out references.bib
sf verify references.bib --online --out output/verify.md
sf new manuscript draft/manuscript.md --title "RNA velocity benchmarks"
sf lint draft/manuscript.md --out output/lint.md
sf claims --claims evidence/claims.csv --evidence evidence/evidence.csv \
  --manuscript draft/manuscript.md --out output/claims.md
sf audit --online
```

## Worked pipeline B — systematic review
```bash
sf new protocol review/protocol.md --title "…"
# fill protocol, then export records to screening/screening.csv with r1/r2/adjudicated/exclusion_code
sf prisma screening/screening.csv --out screening/PRISMA.md
sf registry search "risk of bias" --stage peer-review
```

## Worked pipeline C — revision round
```bash
sf new review review/reviewer-report.md --venue "NeurIPS"
sf review review/reviewer-report.md
sf rebuttal review/reviews.md
sf claims --claims evidence/claims.csv --evidence evidence/evidence.csv --manuscript draft/manuscript.md
sf audit --online
```

## CSV schemas
`screening.csv`: `id, source, stage, title, r1, r2, adjudicated, exclusion_code, notes`
`evidence.csv`: `evidence_id, source_id, locator, quote, design, stance, notes`
`claims.csv`: `claim_id, claim_text, section, evidence_ids, strength, source_refs, status`
Values are lowercase; `evidence_ids` is `;`-separated; every id must exist.

## Extending
- Add slop phrases / placeholders / thresholds in `config/rules.json`.
- Add a venue in `config/venues.json`; add a reporting guideline in
  `config/reporting-guidelines.json`.
- Add a style in `config/styles.json` and a formatter branch in `sf/bib.py`.
- Add a scholarly API in `sf/sources.py` and `config/sources.json`; keep provenance fields.
- Add a template in `templates/` and a mapping in `sf/scaffold.py`.
- Add a self-eval case in `evals/cases.jsonl`.
Then run `sf selftest` and `sf doctor`.

**Complément 1.1.0** : cinq commandes supplémentaires — `integrity`, `guideline`,
`disclosure`, `searchlog`, `validate` — et des filtres sur `search`. `validate` contrôle
la conformité à la spec Agent Skills (playbook 23). Voir le playbook 27 pour PRISMA-S.
