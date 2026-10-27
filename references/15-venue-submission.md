# 15 — Venue selection, formatting and submission

## The currency rule (mandatory)
Venue rules change every cycle. On the day of submission, re-read the **official** author
guidelines and record the URL + access date in `submission/venue-check.md`. Never rely on a
memorised page limit, anonymity policy, template version or AI-use policy. `config/venues.json`
is a starting checklist, not an authority.

## Venue selection criteria
Scope fit, audience, review timeline, open-access policy/APC, data and code policies,
preprint policy, anonymity requirements, page/word limits, reporting checklists, impact vs.
fit, and ethical concerns (predatory journals). Read 3–5 recent articles from the target
venue to match structure and tone.

## Pre-submission checklist
- [ ] Official template downloaded **today**; document class/version recorded.
- [ ] Page/word limit incl. references/appendices respected; PDF inspected page by page.
- [ ] Anonymisation: author names, acknowledgements, file metadata, Word comments, LaTeX
      `\newcommand` self-citations, repository URLs with author names, PDF properties.
- [ ] All figures/tables cited and readable at final size; source-data files prepared.
- [ ] References verified (`verify --online`); style matches venue; no `??` citations.
- [ ] Reporting guideline completed (CONSORT/PRISMA/STROBE/TRIPOD+AI/ARRIVE…).
- [ ] Data/code availability, ethics/IRB statement, competing interests, CRediT, funding,
      AI-use disclosure — in the exact format the venue requires.
- [ ] Cover letter names the specific contribution and fits the scope.
- [ ] Suggested/opposed reviewers follow the venue's rules.
- [ ] Preprint version has a link and licence; journal's preprint policy checked.
- [ ] All authors approved the final PDF and the author order.
- [ ] `audit --online` verdict PASS.

## LaTeX / DOCX practicalities
- Use `latexmk -pdf`, resolve all overfull boxes and undefined references before submission.
- Bundle only the class/style files the venue allows; remove local absolute paths.
- For Word, use the venue template and accept all tracked changes; inspect the PDF, not just
  the .docx.
- Generate the PDF from source, never from a screenshot.
- Check the PDF's metadata (author, title, producer) for anonymity leaks.

## Cover letter
`templates/cover-letter.md`: novelty in 1–2 sentences, fit to scope in one, key finding with a
number, integrity statements, ethics/preregistration/preprint IDs, suggested reviewers. No
generic flattery, no inflated claims.

## After submission
Record the submission date, manuscript ID, licence and version hash. Keep the exact submitted
PDF and source; any later correction goes through the journal's formal process. Update the
preprint with the journal reference where the policy permits.

## Anti-patterns
- Copying last year's template for this year's deadline.
- Adding a reference at the proof stage without re-verifying it.
- Declaring "no competing interests" on behalf of co-authors without asking them.
- Formatting a double-blind submission with a self-citing GitHub URL.
