#!/usr/bin/env python3
"""Build deterministic ScholarForge full and installable-skill ZIPs, stdlib only.

    python3 tools/package_release.py --output /path/outside/the/repository

Archives contain no .git, credentials, bytecode or runtime output. They include
per-file SHA-256 manifests. Full-source and curated upstream policies remain
separate. Upstream ZIP hashes are verified before building. No upstream code is
executed. Hash integrity is not a secret or malware scan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
from pathlib import Path
from typing import Dict
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
STAMP = (2026, 10, 28, 0, 0, 0)
ROOT_FILES = (
    ".gitignore", "00-LISEZ-MOI.md", "README.md", "SKILL.md", "LICENSE", "NOTICE.md",
    "CITATION.cff", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", "Makefile",
    "install.sh", "install.ps1",
)
FULL_DIRS = (".github", "references", "scripts", "templates", "config", "data", "tests",
             "evals", "examples", "tools", "upstream", "docs")
LEAN_DIRS = ("references", "scripts", "templates", "config", "data", "tests", "evals")
LEAN_FILES = ("00-LISEZ-MOI.md", "README.md", "SKILL.md", "LICENSE", "NOTICE.md", "CITATION.cff",
              "CHANGELOG.md")
SKIP = {".git", "__pycache__", ".cache", ".pytest_cache", "node_modules", ".venv"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select(directories, files) -> Dict[str, Path]:
    selected = {name: ROOT / name for name in files if (ROOT / name).is_file()}
    for folder in directories:
        for path in (ROOT / folder).rglob("*"):
            if (not path.is_file() or path.is_symlink() or any(p in SKIP for p in path.parts)
                    or path.suffix in (".pyc", ".pyo") or path.name == ".DS_Store"):
                continue
            selected[path.relative_to(ROOT).as_posix()] = path
    return dict(sorted(selected.items()))


def verify_upstream() -> int:
    count = 0
    for relative in ("upstream/manifest.json", "upstream/v2/manifest.json"):
        path = ROOT / relative
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for entry in manifest["repositories"].values():
            archive = path.parent / entry["archive"]
            if sha256(archive) != entry["sha256"]:
                raise ValueError("Upstream SHA-256 mismatch: " + str(archive))
            count += 1
    return count


def info(name: str, executable: bool = False, stored: bool = False) -> ZipInfo:
    item = ZipInfo(name, STAMP)
    item.create_system = 3
    item.external_attr = ((stat.S_IFREG | (0o755 if executable else 0o644)) << 16)
    item.compress_type = ZIP_STORED if stored else ZIP_DEFLATED
    return item


def build(path: Path, selected: Dict[str, Path], top_level: bool = False) -> Dict[str, object]:
    hashes = {name: sha256(file) for name, file in selected.items()}
    manifest = "".join(f"{digest}  {name}\n" for name, digest in hashes.items())
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        if top_level:
            for name in ("00-LISEZ-MOI.md", "README.md", "CHANGELOG.md"):
                z.writestr(info(name), selected[name].read_bytes())
        for name, file in selected.items():
            executable = name == "install.sh" or bool(file.stat().st_mode & stat.S_IXUSR)
            z.writestr(info("scholar-forge/" + name, executable, file.suffix == ".zip"), file.read_bytes())
        z.writestr(info("scholar-forge/SHA256SUMS.txt"), manifest.encode("utf-8"))
    with ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            raise ValueError("ZIP CRC check failed: " + bad)
    tree_digest = hashlib.sha256(manifest.encode("utf-8")).hexdigest()
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path),
            "source_files": len(selected), "source_tree_sha256": tree_digest}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT.parent)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("Output must be outside the source tree (avoid recursive packaging).")
    output.mkdir(parents=True, exist_ok=True)
    version = re.search(r'__version__\s*=\s*"([^"]+)"',
                        (ROOT / "scripts/sf/cli.py").read_text(encoding="utf-8")).group(1)
    upstream_count = verify_upstream()
    full = build(output / ("scholar-forge-" + version + ".zip"), select(FULL_DIRS, ROOT_FILES), True)
    lean = build(output / "scholar-forge-skill.zip", select(LEAN_DIRS, LEAN_FILES))
    manifest = {"version": version, "upstream_archives_verified": upstream_count,
                "archive_timestamp_policy": "fixed 2026-10-28 for reproducibility; not a file modification date",
                "archives": [full, lean]}
    (output / "release-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "SHA256SUMS.txt").write_text("".join(f"{r['sha256']}  {r['name']}\n" for r in (full, lean)), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
