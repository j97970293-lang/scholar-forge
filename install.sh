#!/usr/bin/env bash
# Install ScholarForge into any Agent Skills host.
#
# Copy mode produces a LEAN skill folder: only the files an agent needs at
# runtime. Build tools, reports and the upstream archives stay
# in the repository. `--link` links the whole repository for development.
set -euo pipefail
TARGET="${HOME}/.claude/skills/scholar-forge"
MODE="copy"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --link)   MODE="link"; shift ;;
    --help|-h)
      echo "Usage: install.sh [--target DIR] [--link]"
      echo "The target directory name must be exactly 'scholar-forge' (Agent Skills spec)."
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

if [ "$(basename "$TARGET")" != "scholar-forge" ]; then
  echo "Target directory must be named scholar-forge (Agent Skills spec)." >&2; exit 2
fi
mkdir -p "$(dirname "$TARGET")"
if [ "$MODE" = "link" ]; then
  ln -sfn "$SRC" "$TARGET"
  echo "[ok] linked $SRC -> $TARGET (development mode, full repository)"
else
  mkdir -p "$TARGET"
  for item in SKILL.md LICENSE NOTICE.md references scripts templates config data tests evals; do
    if [ -d "$SRC/$item" ]; then
      mkdir -p "$TARGET/$item"
      if command -v rsync >/dev/null 2>&1; then
        rsync -a --exclude '__pycache__/' --exclude '*.pyc' "$SRC/$item/" "$TARGET/$item/"
      else
        (cd "$SRC" && tar --exclude=__pycache__ --exclude='*.pyc' -cf - "$item") \
          | (cd "$TARGET" && tar -xf -)
      fi
    elif [ -f "$SRC/$item" ]; then
      cp -f "$SRC/$item" "$TARGET/$item"
    fi
  done
  echo "[ok] copied lean skill to $TARGET"
fi

python3 "$TARGET/scripts/scholarforge.py" doctor
python3 "$TARGET/scripts/scholarforge.py" validate
echo
echo "Skill ready: $TARGET/SKILL.md"
echo "Quick check: python3 $TARGET/scripts/scholarforge.py selftest"
