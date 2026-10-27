#!/usr/bin/env bash
# Install ScholarForge into any Agent Skills host.
set -euo pipefail
TARGET="${HOME}/.claude/skills/scholar-forge"
MODE="copy"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --link)   MODE="link"; shift ;;
    --help|-h)
      echo "Usage: install.sh [--target DIR] [--link]"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$(dirname "$TARGET")"
if [ "$MODE" = "link" ]; then
  ln -sfn "$SRC" "$TARGET"
  echo "[ok] linked $SRC -> $TARGET"
else
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude '.git/' --exclude '__pycache__/' "$SRC/" "$TARGET/"
  else
    mkdir -p "$TARGET"
    (cd "$SRC" && tar --exclude=.git --exclude=__pycache__ -cf - .) | (cd "$TARGET" && tar -xf -)
  fi
  echo "[ok] copied ScholarForge to $TARGET"
fi

python3 "$TARGET/scripts/scholarforge.py" doctor || true
echo
echo "Skill ready: $TARGET/SKILL.md"
echo "Quick check: python3 $TARGET/scripts/scholarforge.py selftest"
