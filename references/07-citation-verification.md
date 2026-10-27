# 07 — Citation verification and bibliographic integrity

## The four-index check
For every reference, check in order:
1. **Structural** — required fields present (author, title, year, container or publisher,
   DOI/URL), year plausible, DOI matches `10.\d{4,9}/\S+`.
2. **Registry existence** — DOI resolves in Crossref (`verify_doi`). Record the exact
   registry record and retrieval date.
3. **Metadata agreement** — title similarity ≥0.86 with the registry; year within ±2 years;
   journal/publisher plausible. Similarity 0.6–0.86 = `uncertain-match`; <0.6 = `mismatch`.
4. **Claim support** — does the source actually say what the manuscript claims? Only by
   reading the passage; see `06-evidence-claims.md`.

```bash
python3 scripts/scholarforge.py verify references.bib --online --out output/verify.md
python3 scripts/scholarforge.py dedupe refs_raw.bib --out references.bib
```

## Status vocabulary
`verified` · `verified-with-warnings` · `uncertain-match` · `mismatch` · `not-resolved` ·
`invalid-doi` · `doi-present-unchecked` (offline) · `needs-review` · `unverified-offline`.
Never upgrade a status to make a report look better.

## Integrity signals worth checking
- Retraction / expression of concern (Crossref, Retraction Watch, publisher notices).
- "Tortured phrases" indicating paraphrased/plagiarised text ("counterfeit consciousness",
  "great language model"…).
- Citation cartels and coercive self-citation suggestions.
- Reference to a retracted paper used as primary evidence.
- DOI resolving to a different paper (publisher correction, transferred journal).
- Hallucinated arXiv IDs and conference page numbers.
- Predatory venue, discontinued ISSN, impossible volume/issue.
- Uncited references and cited-but-missing references.

## Handling hard cases
- **No DOI**: use ISBN, PMID, arXiv ID, URL + access date, or an archival repository. Report
  as `unverified` if no authoritative registry is available.
- **Preprint later published**: cite the version you actually read; note the published
  version if both exist.
- **Non-English sources**: keep original script; add a translation in brackets marked as
  the author's translation; do not transliterate automatically.
- **Datasets/software**: cite the deposited version/DOI, not the website; include the version
  and commit.

## Reporting
`output/verify.md` lists per-reference status, signals, and the registry metadata when online.
Report explicitly: "N references, X verified, Y blocking". Add the integrity note: a passing
check means metadata consistency, not claim validity.

## Anti-patterns
- Generating a plausible DOI from a title pattern.
- Treating Semantic Scholar's fuzzy search hit as confirmation of a citation.
- Removing an inconvenient reference instead of investigating it.
- Claiming "all citations verified" after an offline-only run.
