# 16 — Reproducibility, open science and research ethics

## Data and code availability
Choose and state one status honestly: (a) open with a persistent DOI, (b) available on
reasonable request with a named gatekeeper, (c) restricted by ethics/licence with the exact
condition, (d) no new data generated. A fake "available on request" with no mechanism is a
failed statement.

`templates/data-availability.md` requires: repository, DOI/accession, version/commit, licence,
embargo, exact repository structure and a one-command reproduction path. Include a
`CITATION.cff` for software, an environment lockfile, seeds and a hash of the raw data.

## Reproducibility checklists
NeurIPS, ICML, ICLR, ACL ARR and Nature reporting summaries differ. Fill the current one; do
not attach a checklist from a previous year. Record compute budget, number of runs, variance,
hyperparameter search scope and the licence of every asset used.

## Author contributions and accountability
- CRediT taxonomy (`templates/credit-statement.md`) with explicit roles per author.
- Every author approves the final version and is accountable for accuracy/integrity.
- Authorship disputes are resolved before submission; guest/gift authorship is misconduct.
- AI tools are never authors; a human signs the accountability statement.

## AI-use disclosure
`templates/ai-disclosure.md`: tool/version, stage, purpose, human verification, retained
output. Check the venue's AI policy on submission day; if writing assistance is prohibited,
say so and change the workflow. Never send a confidential manuscript to a training service.

## Ethics and human subjects
- IRB/ethics committee approval and protocol ID where required; consent process;
  de-identification of personal data; risk/benefit; vulnerable populations.
- For secondary data, verify the original consent covers the new analysis and sharing.
- Report adverse events and deviations.
- For animal work: ARRIVE 2.0, 3Rs, randomisation, blinding, sample-size rationale.
- For dual-use or security-sensitive work, state the risk assessment and mitigation.

## Competing interests and funding
Declare financial and non-financial interests for **all** authors, including employment,
consultancies, patents, advisory roles and personal relationships. State the funder's role
(or explicit absence of a role) in design, analysis, writing and the decision to publish.

## Misconduct boundaries
Never: fabricate or falsify data, plagiarise, use tortured paraphrase, salami-slice,
suppress negative results, ghost-author, coerce citations, use predatory venues, or use
illegal full-text sources. If any is discovered in a source, stop, report it and do not reuse
the content.

## Integrity boundary of this skill
ScholarForge checks reported process and internal consistency. It cannot verify that
procedures were performed, that raw data are authentic, or that results reproduce. A
consistently reported fabrication can pass every local gate.

**Complément 1.1.0** : `disclosure` génère une déclaration d'usage de l'IA
structurée par catégorie de délégation, et `disclosure --check` en vérifie les champs
obligatoires. Voir le playbook 26 pour les positions COPE/ICMJE.
