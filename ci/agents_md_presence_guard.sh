#!/usr/bin/env bash
set -euo pipefail

# Directories that must have AGENTS.md if they contain code/build files
PATTERN='(py|ts|tsx|js|go|rs|java|cs)$|(^Makefile$)|(^pyproject\.toml$)|(^package\.json$)'

missing=0
for d in $(git ls-files | grep -E "$PATTERN" | xargs -n1 dirname | sort -u); do
  # allow exceptions (leaf asset dirs etc.)
  case "$d" in
    docs/*|node_modules/*|.git/*) continue ;;
  esac
  if [ ! -f "$d/AGENTS.md" ]; then
    echo "::error ::Missing AGENTS.md in $d"
    missing=1
  fi
done
exit $missing
