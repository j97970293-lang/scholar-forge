"""Shared helpers for the ScholarForge reproducible build tools.

These tools are intentionally dependency-free (Python 3.9+ standard library)
so that the provenance of the merged repository can be re-derived anywhere.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOT = Path(os.environ.get("SF_SOURCES", str(ROOT.parent / "_scan")))

# slug -> (upstream URL, license, role in the merge)
SOURCES: Dict[str, Dict[str, str]] = {
    "O0000-code_awesome-academic-skills": {
        "url": "https://github.com/O0000-code/awesome-academic-skills",
        "license": "CC0-1.0",
        "role": "meta-list: 223 curated skill records + ASDF trust framework + schema",
    },
    "cosen1024_awesome-academic-skills": {
        "url": "https://github.com/cosen1024/awesome-academic-skills",
        "license": "MIT",
        "role": "meta-list: verified bilingual catalog with pinned source_ref commits",
    },
    "kael-odin_awesome-academic-research-skills": {
        "url": "https://github.com/kael-odin/awesome-academic-research-skills",
        "license": "MIT",
        "role": "meta-list: live star/trend rankings + 60-day history",
    },
    "miketepUR_awesome-claude-skills": {
        "url": "https://github.com/miketepUR/awesome-claude-skills",
        "license": "MIT",
        "role": "meta-list: general agent-skill ecosystem + contribution/validation workflows",
    },
    "Imbad0202_academic-research-skills": {
        "url": "https://github.com/Imbad0202/academic-research-skills",
        "license": "CC-BY-NC-4.0",
        "role": "suite: 5 deep skills (pipeline, research, paper, reviewer, screening) + 478 scripts + JSON contracts",
    },
    "KalarisLabs_research-agent-skills": {
        "url": "https://github.com/KalarisLabs/research-agent-skills",
        "license": "MIT",
        "role": "suite: 200+ narrow skills, tested stdlib CLIs, benchmarks, catalog graph",
    },
    "saintgo7_agents-skills": {
        "url": "https://github.com/saintgo7/agents-skills",
        "license": "unlicensed (snapshot retained, attribution kept)",
        "role": "suite: 50 lightweight Korean/English skill stubs + IEEE Access venue guide",
    },
    "ranbot-ai_awesome-skills": {
        "url": "https://github.com/ranbot-ai/awesome-skills",
        "license": "unlicensed (snapshot retained, attribution kept)",
        "role": "general skill aggregator: 2908 skill records incl. content-research-writer",
    },
}

SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode"}
TEXT_EXT = {
    ".md", ".markdown", ".txt", ".py", ".sh", ".bash", ".yml", ".yaml", ".json", ".jsonl",
    ".tex", ".bib", ".csv", ".tsv", ".js", ".mjs", ".ts", ".tsx", ".toml", ".cfg", ".ini",
    ".html", ".css", ".xml", ".svg", ".j2", ".cff", ".ris", ".nbib", ".sty", ".bst", ".rst",
}
CODE_EXT = {".py", ".sh", ".bash", ".js", ".mjs", ".ts", ".tsx", ".tex", ".sql", ".r", ".R"}


def repo_dirs() -> List[Tuple[str, Path]]:
    """Return (slug, path) for every cloned upstream that exists."""
    out = []
    for slug in SOURCES:
        p = SCAN_ROOT / slug
        if p.is_dir() and (p / ".git").exists():
            out.append((slug, p))
    return out


def iter_files(root: Path, skip_dirs: Iterable[str] = SKIP_DIRS) -> Iterator[Path]:
    skip = set(skip_dirs)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            yield Path(dirpath) / name


def read_text(path: Path, limit: Optional[int] = None) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            return fh.read(limit) if limit else fh.read()
    except (OSError, ValueError):
        return ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def write_json(path: Path, obj: Any, *, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=indent, sort_keys=False) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def frontmatter(text: str) -> Dict[str, Any]:
    """Minimal YAML frontmatter reader (no PyYAML dependency at skill runtime)."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    out: Dict[str, Any] = {}
    key = None
    for line in parts[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w.-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            val = val.strip("'\"")
            out[key] = val
        elif key and line.startswith(" ") and line.strip().startswith("- "):
            out.setdefault(key + "_list", []).append(line.strip()[2:].strip("'\""))
    return out


def slugify(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"https?://(www\.)?github\.com/", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:120]


def normalise_repo_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip().rstrip("/")
    url = re.sub(r"^https?://(www\.)?github\.com/", "", url, flags=re.I)
    parts = url.split("/")
    if len(parts) >= 2 and parts[0] not in ("blob", "tree"):
        return (parts[0] + "/" + parts[1]).lower()
    return url.lower()


def human_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024.0
    return f"{n:.1f} GB"
