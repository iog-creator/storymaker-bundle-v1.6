#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
bad=(.cursor/rules/*.md)
[ ${#bad[@]} -eq 0 ] || { printf "::error ::unexpected .md in .cursor/rules/: %s\n" "${bad[@]}"; exit 1; }
echo "rules_no_md_guard: OK"


