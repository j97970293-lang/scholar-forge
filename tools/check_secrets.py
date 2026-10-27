#!/usr/bin/env python3
"""check_secrets.py -- verify that no credential was committed.

The detection patterns are assembled at runtime so that this file, the CI workflow,
SECURITY.md and tools/security_scan.py (which legitimately *define* the patterns) do not
match themselves. Archives in upstream/ are binary data and are scanned via the manifest
hashes, not by regex.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "upstream", "__pycache__", ".venv", "node_modules", "build", "dist"}
SKIP_FILES = {
    "tools/security_scan.py", "tools/check_secrets.py", "SECURITY.md",
    ".github/workflows/ci.yml", "README.md",
}
TEXT_EXT = {".md", ".py", ".json", ".jsonl", ".yml", ".yaml", ".sh", ".ps1", ".txt",
            ".tex", ".bib", ".cff", ".csv", ".tsv", ".toml", ".cfg", ".ini", ".html", ".js", ".ts"}

PATTERNS = [
    "gh" + "[pousr]_[A-Za-z0-9]{20,}",
    "AKIA" + "[0-9A-Z]{16}",
    "sk-" + "[A-Za-z0-9]{32,}",
    "-----BEGIN " + "(RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "xox[baprs]-" + "[A-Za-z0-9-]{10,}",
    "AIza" + "[A-Za-z0-9_-]{30,}",
]
RX = re.compile("|".join("(?:" + p + ")" for p in PATTERNS))


def main() -> int:
    hits = []
    scanned = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        rel = str(path.relative_to(ROOT))
        if any(part in SKIP_DIRS for part in path.parts) or rel in SKIP_FILES:
            continue
        if path.suffix.lower() not in TEXT_EXT and path.name not in ("LICENSE", "Makefile", ".gitignore"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        for i, line in enumerate(text.splitlines(), 1):
            if RX.search(line):
                hits.append((rel, i, "credential-like pattern"))
    if hits:
        for h in hits:
            print(f"[FAIL] {h[0]}:{h[1]} — {h[2]}", file=sys.stderr)
        print(f"{len(hits)} match(es) over {scanned} files", file=sys.stderr)
        return 1
    print(f"[ok] no credential-like pattern found in {scanned} text files "
          f"(archives verified separately by upstream/manifest.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
