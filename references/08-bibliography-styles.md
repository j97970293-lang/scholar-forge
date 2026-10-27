# 08 — Bibliography and citation styles

## Canonical storage
Keep one master `references.bib` with a DOI for every entry. All other styles are generated
views; never hand-maintain two bibliographies. For camera-ready output use the official CSL
style with Pandoc/Zotero or `biblatex` + `biber`; the bundled formatter is best-effort.

```bash
python3 scripts/scholarforge.py bib references.bib --style apa     > output/references-apa.md
python3 scripts/scholarforge.py bib references.bib --style ieee    > output/references-ieee.md
```

## Style cheat-sheet
| Style | In-text | Order | DOI | Common venue |
|---|---|---|---|---|
| APA 7 | (Author, Year) | alphabetical | `https://doi.org/…` | psychology, education, social sciences |
| IEEE | [1] | appearance | `doi: …` | engineering, computer science |
| Vancouver | (1) / superscript | appearance | `doi:…` | medicine, ICMJE |
| Chicago NB | footnote | alphabetical | URL | humanities |
| Nature | superscript | appearance | URL | Nature Portfolio |

## APA 7 essentials
- Student vs professional title page differ (running head, author note, course/instructor).
- Levels 1–5 headings with exact capitalisation rules.
- In-text: 1–2 authors always named; ≥3 → `et al.` from first citation; separate multiple
  works with `;` and order alphabetically.
- Reference list: hanging indent, sentence-case article titles, italic journal + volume,
  issue in parentheses only when each issue starts at page 1.
- Dataset, software, webpage and generative-AI entries have their own templates.
- Bias-free language: specific labels, person-first or identity-first as the community
  prefers, no deficit framing.

## IEEE / numbered styles
- Numbers are assigned in order of first appearance and reused, never re-numbered after
  edits without regenerating.
- Bracketed citations at sentence level: `… as shown [3], [5]–[7].`
- Reference list includes DOI at the end; use `\cite` with `IEEEtran.bst` in LaTeX.

## LaTeX / BibTeX hygiene
- Protect capitalisation in titles with `{…}`.
- Escape special characters; keep Unicode with `inputenc`/`fontenc` or use XeLaTeX.
- Use `\bibliographystyle` matching the venue class, compile `pdflatex → biber → pdflatex ×2`.
- Check for `Overfull \hbox`, missing citations (`??`), undefined references, duplicate keys.
- Cross-check the compiled PDF's reference list against `references.bib`.

## Interoperability
- RIS/NBIB/CSV imports from Zotero, EndNote, Web of Science, PubMed.
- `dedupe` merges by DOI then fuzzy title. Always review the duplicate report.
- Keep `CITATION.cff` for software artefacts and a machine-readable `sources.json` for
  datasets.
- Locale rules: never transliterate author names automatically; preserve CJK author order;
  keep diacritics; mark machine translations.

## Anti-patterns
- Editing the numbered bibliography by hand after adding a citation.
- Mixing APA in-text citations with a numbered reference list.
- Citing a paper from a secondary source without "as cited in".
- Letting the formatter silently drop an author or a year.
