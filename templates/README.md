# Templates

Rendering: `python3 scripts/scholarforge.py new manuscript draft/paper.md --title "My study"`.

Placeholders `{{TITLE}}`, `{{AUTHOR}}`, `{{VENUE}}`, `{{DATE}}`, `{{EMAIL}}` are substituted
at render time. Templates are intentionally plain Markdown/LaTeX so they work offline, in Git,
in any editor and in any Agent Skills host.

| Template | Purpose |
|---|---|
| manuscript-imrad.md / .tex | Full paper scaffold (Markdown + LaTeX/biblatex) |
| prisma-protocol.md | Frozen review protocol with ordered exclusion codes |
| peer-review-form.md | Evidence-bounded referee report with intake gate |
| rebuttal-matrix.md | Point-by-point author response tracker |
| cover-letter.md | Editor cover letter |
| data-availability.md | Data/code/materials statement |
| credit-statement.md | CRediT contributor taxonomy |
| ai-disclosure.md | AI-assistance disclosure and human accountability |
| preregistration.md | Pre-analysis plan with rivals and falsification thresholds |
| research-brief.md | Evidence brief with provenance |
| pipeline-status.md | Human-readable stage dashboard |
| project-readme.md | Workspace layout (used by `init`) |
| references.bib | Canonical BibTeX skeleton |
