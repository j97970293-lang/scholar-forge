# End-to-end demo — "Does retrieval augmentation reduce citation errors?"

A tiny, fully synthetic project that exercises every ScholarForge command offline.
Numbers are illustrative and must never be used as real evidence.

```bash
bash examples/end-to-end/run-demo.sh
```

The script copies these files into a temporary project, runs the CLI checks and prints the
final audit. It deliberately contains one bad reference and one AI-slop paragraph so you can
see a gate FAIL and how to fix it. Use `--fixed` to run the cleaned variant instead.
