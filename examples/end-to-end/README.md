# End-to-end demo — "Does retrieval augmentation reduce citation errors?"

A tiny, fully synthetic project that exercises all 21 ScholarForge commands offline.
Numbers are illustrative and must never be used as real evidence.

```bash
bash examples/end-to-end/run-demo.sh
```

The script copies these files into a temporary project, runs the CLI checks and prints the
final audit. It deliberately contains one bad reference and one AI-slop paragraph so you can
see a gate FAIL and how to fix it. Use `--fixed` to run the cleaned variant instead.

The 1.1.0 script also runs `integrity` (offline title scan), `guideline --recommend`,
`guideline --key`, `disclosure` + `--check`, `searchlog` and `validate`. The search log is
empty here because the demo is fully offline; run `search --log-path <project>` against the
real APIs to populate it.

Expected results: dirty run → `Verdict: FAIL (4/8 gates pass)`; `--fixed` →
`Verdict: PASS (7/8 gates pass)` (`G-pipeline` stays advisory at S0).
