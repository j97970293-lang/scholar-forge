#!/usr/bin/env bash
# Reproducible offline demonstration of the whole ScholarForge CLI.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SF="python3 $ROOT/scripts/scholarforge.py"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
FIXED=0
[ "${1:-}" = "--fixed" ] && FIXED=1
BIBFILE="$HERE/references.bib"; MANFILE="$HERE/manuscript.md"
[ "$FIXED" = "1" ] && BIBFILE="$HERE/references.fixed.bib" && MANFILE="$HERE/manuscript.fixed.md"

echo "== 0. doctor =="; $SF doctor
echo "== 1. init =="; $SF init --path "$WORK/project" --name "Demo study" --mode full
P="$WORK/project"
cp "$BIBFILE" "$P"/references.bib
cp "$HERE"/evidence.csv "$HERE"/claims.csv "$P"/evidence/
cp "$HERE"/screening.csv "$P"/screening/
cp "$HERE"/reviews.md "$P"/review/
cp "$MANFILE" "$P"/draft/manuscript.md
[ "$FIXED" = "1" ] && sed -i 's/| open |/| resolved |/g' "$P/review/rebuttal-matrix.md" 2>/dev/null || true

echo "== 2. registry =="; $SF registry stats | head -8
$SF registry search "citation verification" --limit 3
echo "== 3. dedupe =="; $SF dedupe "$P/references.bib" --out "$P/references-clean.bib" --json
echo "== 4. verify (offline) =="; $SF verify "$P/references.bib" --out "$P/output/verify.md" || true
echo "== 5. bib (APA) =="; $SF bib "$P/references.bib" --style apa | head -6
echo "== 6. lint =="; $SF lint "$P/draft/manuscript.md" --out "$P/output/lint.md" || true
echo "== 7. claims =="; $SF claims --claims "$P/evidence/claims.csv" --evidence "$P/evidence/evidence.csv" \
     --manuscript "$P/draft/manuscript.md" --out "$P/output/claims.md" || true
echo "== 8. prisma =="; $SF prisma "$P/screening/screening.csv" --out "$P/screening/PRISMA.md" || true
echo "== 9. rebuttal =="; $SF rebuttal "$P/review/reviews.md" --out-csv "$P/review/rebuttal-matrix.csv" \
     --out-md "$P/review/rebuttal-matrix.md"
echo "== 9b. integrity (offline) =="; $SF integrity "$P/references.bib" --path "$P" || true
echo "== 9c. guideline =="; $SF guideline --recommend "diagnostic accuracy of an AI test" | head -5
$SF guideline --key prediction-model --title "Demo study" --venue "BMJ" --out "$P/submission/checklist.md"
echo "== 9d. disclosure =="; $SF disclosure --tool "Claude Sonnet" --tool-version "2026-10-28" \
     --purpose search,writing,editing --oversight "Named author verified every claim" \
     --verification "Crossref + claim ledger" --authors "Demo author (synthetic example)" \
     --prompts "Demo script, illustrative only" --policy-date "2026-10-28" \
     --title "Demo study" --out "$P/output/ai-disclosure-draft.md"
[ "$FIXED" = "1" ] && cp "$P/output/ai-disclosure-draft.md" "$P/submission/ai-disclosure.md"
$SF disclosure --check "$P/output/ai-disclosure-draft.md" || true
echo "== 9e. searchlog =="; $SF searchlog --path "$P" | head -8
echo "== 9f. spec validation =="; $SF validate | head -6
echo "== 10. pipeline =="; $SF pipeline status --path "$P" | head -6
[ "$FIXED" = "1" ] && sed -i 's/| open |/| resolved |/g' "$P/review/rebuttal-matrix.md" 2>/dev/null || true
echo "== 11. audit =="; $SF audit --path "$P" || true
echo "== 12. selftest =="; $SF selftest 2>&1 | tail -4
echo "Workspace: $P (temporary; removed on exit)"
echo "Reports written to: $P/output, $P/screening, $P/review"
