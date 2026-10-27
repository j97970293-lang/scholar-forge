#!/usr/bin/env python3
"""ScholarForge -- single entry point.

Usage:
    python3 scripts/scholarforge.py --help
    python3 scripts/scholarforge.py doctor
    python3 scripts/scholarforge.py selftest
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sf.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
