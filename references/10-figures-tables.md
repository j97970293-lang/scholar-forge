# 10 — Figures, tables and scientific visualisation

## One message per figure
Before drawing, write the single sentence the reader should take away. That sentence is the
first line of the caption. Choose the encoding that makes that message visible:
- comparison → dot/bar plot with raw points
- distribution → violin/box/ecdf/histogram (not a bar of means)
- relationship → scatter with fit + uncertainty
- composition → stacked bar only when totals matter
- time → line with clear units and annotations
- spatial → map with an honest projection and scale

## Mandatory elements
- Axis labels with units, readable tick values, no truncated axes for bar charts.
- Definition of error bars (SD / SE / CI / prediction interval) and the n behind each.
- Legend that does not rely on colour alone; direct labels where possible.
- Colourblind-safe palette (Okabe–Ito, viridis, cividis); check greyscale printing.
- Font sizes ≥7–8 pt at final printed size; export vector (PDF/SVG/EPS) for line art,
  ≥300 dpi raster for images.
- Caption is self-contained: what, where, n, how computed, what the symbols mean.
- Alt text / long description for accessibility; source-data file for each figure.

## Statistical honesty
- Show raw data when n is small; avoid dynamite plunger plots.
- Do not use a second y-axis to imply a correlation; if unavoidable, label clearly.
- Use the same scale across panels that are meant to be compared.
- Report the number of independent replicates, not technical repeats.
- Annotate transformations, normalisation and excluded points with reasons.
- Never adjust contrast or remove bands selectively in images; keep the original file.

## Tables
- One decimal place more than measurement precision, no more.
- Align numbers on the decimal point; use `booktabs` in LaTeX (no vertical rules).
- Define every abbreviation in a footnote; state what * and † mean.
- Keep tables in the manuscript source (Markdown/LaTeX), generated from the analysis script.
- Split large tables into supplements; keep the main table readable.

## Toolchain
- Matplotlib/seaborn for reproducibility, `config`-driven styles.
- Pandoc/LaTeX/Word for the final document; never paste a screenshot of a table.
- `scholarforge` does not render figures; it checks that every figure/table referenced in
  the text exists in the artefacts list and has a caption and provenance row.

## Checklist before submission
- [ ] Every figure/table is cited in the text, in ascending order.
- [ ] Captions are self-contained and state n, units, error-bar definition.
- [ ] Colour is redundant with shape/label; accessible in greyscale.
- [ ] Source data files exist and match the numbers in the manuscript.
- [ ] No decorative 3-D effects, chartjunk, or dual axes without justification.
- [ ] Alt text and a source-data provenance table are included.
