"""Shared, dependency-free helpers for the ScholarForge runtime."""

from __future__ import annotations

import csv
import difflib
import hashlib
import io
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[2]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_text(path: Path | str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"file not found: {p}")
    return p.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path | str, text: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def read_json(path: Path | str, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return default


def write_json(path: Path | str, obj: Any, indent: int = 2) -> Path:
    return write_text(path, json.dumps(obj, ensure_ascii=False, indent=indent) + "\n")


def read_csv(path: Path | str) -> List[Dict[str, str]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"csv not found: {p}")
    with p.open("r", encoding="utf-8-sig", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def write_csv(path: Path | str, rows: Iterable[Dict[str, Any]], fields: Optional[List[str]] = None) -> Path:
    rows = list(rows)
    if fields is None:
        fields = list(rows[0].keys()) if rows else ["id"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})
    return write_text(path, buf.getvalue())


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:100]


def norm_doi(value: str) -> str:
    v = (value or "").strip().lower()
    v = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", v)
    return v.strip().rstrip(".")


def norm_title(value: str) -> str:
    v = unicodedata.normalize("NFKD", value or "").lower()
    v = re.sub(r"[^a-z0-9 ]+", " ", v)
    return re.sub(r"\s+", " ", v).strip()


def similarity(a: str, b: str) -> float:
    return round(difflib.SequenceMatcher(None, norm_title(a), norm_title(b)).ratio(), 4)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def out(obj: Any, as_json: bool, human: Optional[str] = None) -> None:
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    elif human is not None:
        print(human)
    else:
        print(obj)


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


def find_project(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    cwd = Path.cwd()
    for p in (cwd, *cwd.parents):
        if (p / ".scholarforge").is_dir():
            return p
    return cwd


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def table(rows: List[List[Any]], header: Optional[List[str]] = None) -> str:
    data = [[str(c) for c in r] for r in rows]
    if header:
        data.insert(0, [str(h) for h in header])
    widths = [max(len(r[i]) for r in data) for i in range(len(data[0]))]
    lines = []
    for idx, row in enumerate(data):
        lines.append(" | ".join(row[i].ljust(widths[i]) for i in range(len(row))))
        if idx == 0 and header:
            lines.append("-+-".join("-" * w for w in widths))
    return "\n".join(lines)
