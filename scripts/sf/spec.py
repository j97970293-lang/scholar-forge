"""Validate SKILL.md against the Agent Skills open specification.

Stdlib only. The spec (agentskills.io/specification, consulted 2026-10-28) fixes:
  name 1-64 chars, lowercase a-z/0-9/hyphen, no leading/trailing/doubled hyphen,
  must match the parent directory name;
  description 1-1024 chars, non-empty, no XML tags, states what AND when;
  compatibility <= 500 chars; metadata is a map of string -> string;
  allowed-tools is a space-separated string; body < 500 lines / ~5000 tokens;
  file references are kept one level deep from SKILL.md.

This validator is deliberately conservative about things it cannot prove: it
reports advisories instead of guessing.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .util import ROOT, read_text

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
XML_RE = re.compile(r"<[A-Za-z/][^>]*>")
LINK_RE = re.compile(r"(?:references|scripts|templates|config|data|assets)/[A-Za-z0-9._/-]+")


def frontmatter(text: str) -> Dict[str, Any]:
    """Tiny frontmatter reader for the subset of YAML the spec uses."""
    if not text.startswith("---"):
        raise ValueError("SKILL.md must start with a YAML frontmatter block")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md frontmatter is not closed by ---")
    out: Dict[str, Any] = {}
    current: Optional[str] = None
    for raw in parts[1].splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line[:1].isspace()
        if ":" not in line:
            continue
        key, _, val = line.strip().partition(":")
        val = val.strip()
        if val in ("|", ">", "|-", ">-", "|+", ">+"):
            raise ValueError("Block-scalar YAML is not supported by this stdlib subset validator; use quoted single-line values or skills-ref")
        if indented and current:
            out[current][key] = _scalar(val)
        elif not val and line.endswith(":"):
            current = key
            out[current] = {}
        else:
            current = None
            if val.startswith("{") and val.endswith("}"):
                inner: Dict[str, Any] = {}
                for bit in val[1:-1].split(","):
                    if ":" in bit:
                        k, _, v = bit.partition(":")
                        inner[k.strip()] = _scalar(v.strip())
                out[key] = inner
            else:
                out[key] = _scalar(val)
    return out


def _scalar(value: str) -> Any:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    if value in ("true", "false", "True", "False", "TRUE", "FALSE"):
        return value.lower() == "true"
    if value.lower() in ("null", "~"):
        return None
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?", value):
        return float(value)
    if value.startswith("[") and value.endswith("]"):
        return [x.strip().strip("'\"") for x in value[1:-1].split(",") if x.strip()]
    return value


def _check(name: str, ok: bool, detail: str, severity: str = "error") -> Dict[str, Any]:
    return {"name": name, "ok": bool(ok), "severity": severity, "detail": detail}


def validate(root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(root) if root else ROOT
    skill = root / "SKILL.md"
    checks: List[Dict[str, Any]] = []
    if not skill.is_file():
        return {"ok": False, "checks": [_check("SKILL.md exists", False, str(skill))],
                "errors": 1, "warnings": 0}
    text = read_text(skill)
    try:
        fm = frontmatter(text)
    except ValueError as exc:
        return {"ok": False, "checks": [_check("frontmatter", False, str(exc))],
                "errors": 1, "warnings": 0}

    name = str(fm.get("name", ""))
    checks.append(_check("name present", bool(name) and isinstance(fm.get("name"), str), repr(name)))
    checks.append(_check("name <= 64 chars", len(name) <= 64, f"{len(name)} chars"))
    checks.append(_check("name lowercase kebab-case", bool(NAME_RE.match(name)) and "--" not in name,
                         "a-z, 0-9, single hyphens only"))
    checks.append(_check("name matches directory", name == root.name,
                         f"name={name!r}, dir={root.name!r}"))

    desc = str(fm.get("description", ""))
    checks.append(_check("description non-empty", isinstance(fm.get("description"), str) and bool(desc.strip()), f"{len(desc)} chars"))
    checks.append(_check("description <= 1024 chars", 1 <= len(desc) <= 1024,
                         f"{len(desc)} chars (spec max 1024)"))
    checks.append(_check("description has no XML tags", not XML_RE.search(desc), "no XML markup"))

    compat = str(fm.get("compatibility", "")) if fm.get("compatibility") else ""
    if compat:
        checks.append(_check("compatibility <= 500 chars", len(compat) <= 500, f"{len(compat)} chars"))

    meta = fm.get("metadata")
    if meta is not None:
        bad = [k for k, v in (meta.items() if isinstance(meta, dict) else []) if not isinstance(v, str)]
        checks.append(_check("metadata is map of strings", isinstance(meta, dict) and not bad,
                             "non-string metadata values: " + (", ".join(map(str, bad)) or "none")))
    tools = fm.get("allowed-tools")
    if tools is not None:
        checks.append(_check("allowed-tools is a string", isinstance(tools, str),
                             "space-separated string"))

    body = text.split("---", 2)[2]
    lines = len(body.splitlines())
    tokens = len(body) // 4
    checks.append(_check("body < 500 lines", lines < 500, f"{lines} lines"))
    checks.append(_check("body ~< 5000 tokens", tokens <= 5000, f"~{tokens} tokens (char/4 estimate)",
                         "warning"))

    refs = sorted((root / "references").glob("*.md"))
    checks.append(_check("references/ populated", len(refs) > 0, f"{len(refs)} playbooks"))
    mentioned = set(m.rstrip(".,;:`)]") for m in LINK_RE.findall(text))
    missing = sorted(m for m in mentioned
                     if "." in m.rsplit("/", 1)[-1] and not (root / m).exists())
    checks.append(_check("referenced paths resolve", not missing,
                         "unresolved: " + (", ".join(missing[:6]) or "none")))
    nested = []
    for r in refs:
        for m in re.finditer(r"references/([A-Za-z0-9._-]+\.md)", read_text(r)):
            nested.append(r.name)
            break
    checks.append(_check("references one level deep", not nested,
                         "files linking to other references: " + (", ".join(sorted(set(nested))) or "none"),
                         "warning"))
    for d in ("scripts", "templates", "config"):
        checks.append(_check(f"{d}/ exists", (root / d).is_dir(), str(root / d)))

    errors = sum(1 for c in checks if c["severity"] == "error" and not c["ok"])
    warnings = sum(1 for c in checks if c["severity"] == "warning" and not c["ok"])
    return {"ok": errors == 0, "errors": errors, "warnings": warnings,
            "checks": checks, "spec": "https://agentskills.io/specification"}


def to_markdown(report: Dict[str, Any]) -> str:
    L = ["# Agent Skills spec validation", "",
         f"Result: **{'PASS' if report['ok'] else 'FAIL'}** — {report['errors']} errors, "
         f"{report['warnings']} advisories", "",
         "| Check | Status | Detail |", "|---|---|---|"]
    for c in report["checks"]:
        mark = "ok" if c["ok"] else ("WARN" if c["severity"] == "warning" else "FAIL")
        L.append(f"| {c['name']} | {mark} | {c['detail']} |")
    L += ["", "Spec: " + report.get("spec", "https://agentskills.io/specification")]
    return "\n".join(L) + "\n"
