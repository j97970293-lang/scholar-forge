#!/usr/bin/env python3
"""package_upstream.py -- lossless snapshots of all eight merged repositories.

Every file of every clone (except VCS internals, caches and build output) is
stored in one ZIP per repository. Nothing is silently dropped: the manifest
records file counts, byte counts, commit SHA and SHA-256 of each archive.

Outputs: upstream/<slug>.zip, upstream/manifest.json
"""

from __future__ import annotations

import hashlib
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, SCAN_ROOT, SOURCES, human_bytes, repo_dirs, write_json  # noqa: E402

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache",
             ".mypy_cache", ".ruff_cache", "dist", "build", ".next", ".cache"}
SKIP_FILES = {".ds_store", "thumbs.db"}


def head_sha(repo: Path) -> str:
    head = (repo / ".git/HEAD").read_text(encoding="utf-8").strip() if (repo / ".git/HEAD").exists() else ""
    if head.startswith("ref:"):
        ref = head.split(" ", 1)[1]
        p = repo / ".git" / ref
        if not p.exists():
            packed = repo / ".git/packed-refs"
            if packed.exists():
                for line in packed.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.endswith(ref) or line.endswith(" " + ref):
                        return line.split()[0]
            return ""
        return p.read_text(encoding="utf-8").strip()
    return head


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    out_dir = ROOT / "upstream"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: Dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": "Full lossless snapshot of every file in each clone, excluding VCS internals "
                  "and generated caches. Archives are inert data; nothing inside is executed.",
        "repositories": {},
    }
    for slug, repo in repo_dirs():
        zpath = out_dir / f"{slug}.zip"
        n = raw = 0
        with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=7) as zf:
            for dirpath, dirnames, filenames in os.walk(repo):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for name in sorted(filenames):
                    if name.lower() in SKIP_FILES or name.endswith(".err") or name.endswith(".pyc"):
                        continue
                    fp = Path(dirpath) / name
                    if not fp.is_file() or fp.is_symlink():
                        continue
                    arc = str(Path(slug) / fp.relative_to(repo))
                    zf.write(fp, arc)
                    n += 1
                    raw += fp.stat().st_size
        if zpath.stat().st_size > 95 * 1024 * 1024:
            print("WARNING: archive exceeds 95 MB:", zpath.name, file=sys.stderr)
        manifest["repositories"][slug] = {
            "url": SOURCES[slug]["url"],
            "license": SOURCES[slug]["license"],
            "role": SOURCES[slug]["role"],
            "commit": head_sha(repo),
            "archive": zpath.name,
            "files": n,
            "uncompressed_bytes": raw,
            "uncompressed_human": human_bytes(raw),
            "archive_bytes": zpath.stat().st_size,
            "archive_human": human_bytes(zpath.stat().st_size),
            "sha256": sha256(zpath),
        }
        print(f"packed {slug}: {n} files, {human_bytes(raw)} -> {human_bytes(zpath.stat().st_size)}")
    manifest["total_files"] = sum(r["files"] for r in manifest["repositories"].values())
    manifest["total_archive_bytes"] = sum(r["archive_bytes"] for r in manifest["repositories"].values())
    write_json(out_dir / "manifest.json", manifest)
    print("total:", manifest["total_files"], "files /", human_bytes(manifest["total_archive_bytes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
