#!/usr/bin/env python3
"""validate_skill.py -- CI-friendly Agent Skills spec validator.

Thin build-tool wrapper around ``sf.spec`` so the same checks are available from
the CLI (``scholarforge validate``) and from CI (``python3 tools/validate_skill.py``).
Stdlib only; no PyYAML required at runtime.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sf import spec  # noqa: E402


def main() -> int:
    as_json = "--json" in sys.argv
    report = spec.validate(ROOT)
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(spec.to_markdown(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
