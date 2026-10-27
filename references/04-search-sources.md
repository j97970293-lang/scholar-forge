# 04 — Search strategy, scholarly APIs and saturation

## Reproducible query construction
1. Split the question into concepts (PICO/SPIDER facets).
2. For each concept list synonyms, acronyms, older terminology, spelling variants and
   controlled-vocabulary terms (MeSH, EMTREE, IEEE terms).
3. Combine within a concept with OR, across concepts with AND; use NOT sparingly (it removes
   relevant records).
4. Adapt syntax per database — field tags are not portable:
   - PubMed: `"term"[Title/Abstract] AND ("mesh"[MeSH Terms])`
   - OpenAlex: `search=` free text; `filter=` for structured constraints.
   - Crossref: `query.bibliographic=`; use `query.title=` for precision.
   - arXiv: `all:` / `ti:` / `au:` / `abs:` with `AND`/`OR`/`ANDNOT`.
5. Record the exact string, platform, filters (date/language/type), date run, hits and the
   operator's name in `sources/search-log.md`.
6. Add citation chasing (backward references + forward citations), trial registries, theses,
   preprints and grey literature where the question warrants it.

## Bundled clients (`config/sources.json`)
| Source | Strength | Caveat |
|---|---|---|
| OpenAlex | broad coverage, citation graph, concepts | inherited metadata; verify DOI |
| Crossref | DOI registry of record | no abstract for many records |
| arXiv | preprints + full text | not peer reviewed; version overlap |
| Semantic Scholar | citation graph, TLDR, OA links | rate-limited without key; CS/biomed skew |
| PubMed | authoritative biomedical indexing | life sciences only; no full text |
| Europe PMC | life-science preprints/abstracts | biomedical scope |
| Unpaywall | legal OA locations | email required; never bypass paywalls |

```bash
python3 scripts/scholarforge.py search "single-cell RNA velocity benchmarking" \
  --sources openalex,crossref,arxiv,semanticscholar --limit 12 \
  --out sources/hits.json --bib sources/hits.bib
```
Every returned record carries `source`, `source_url`, `retrieved_at` and `also_in` when
merged. Network failures are per-source and never crash the search.

## Source quality hierarchy
1. Systematic reviews / meta-analyses of primary studies (for orientation only).
2. Registered reports and preregistered replications.
3. Peer-reviewed primary research with open data/code.
4. Peer-reviewed primary research without open artefacts.
5. Preprints (label as such; check for a published version).
6. Conference abstracts, theses, reports, patents.
7. Blogs, press releases, encyclopaedias — background only, not evidence for a claim.

Record the level in the evidence ledger; do not let a preprint silently become "journal
article" in the bibliography.

## Saturation and stopping
- Track cumulative new relevant records per search block; stop when two consecutive blocks
  add <5% new eligible records **and** all planned concepts/databases are covered.
- Log the stop decision with the numbers. "I got tired of searching" is not a criterion.
- Keep an explicit rejection log with ordered reasons — it feeds the PRISMA flow.

## De-duplication
`dedupe` groups by normalised DOI, else fuzzy title similarity (≥0.93), keeps the richest
record and writes a duplicate report. Check the report manually: two genuinely different
conference/journal versions of the same work may need to stay separate.

## Legal and ethical full text
Use publisher pages, institutional repositories, Unpaywall, author copies and open archives.
Never use Sci-Hub or access-control bypasses. Respect robots.txt, rate limits and terms of
use. Cache responses; never hammer a public API.

## Anti-patterns
- One database only, presented as "the literature".
- A query string that exists only in prose ("we searched PubMed and Scopus") without the
  actual string and date.
- Treating hit counts as quality.
- Letting an LLM paraphrase an abstract into a citation without retrieving the record.
