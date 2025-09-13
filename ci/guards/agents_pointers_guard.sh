#!/usr/bin/env bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
ws="$root/.agentpm_workspace"
err=0
shopt -s globstar nullglob
for f in "$ws"/**/AGENTS.md; do
  # Must be a pointer stub
  if ! head -n1 "$f" | grep -q '^# Pointer: Single Source of Truth'; then
    echo "::error ::$f is not a pointer stub (run: make agents.pointers)"
    err=1
  fi
done
[ $err -eq 0 ] && echo "agents_pointers_guard: OK" || exit 1
