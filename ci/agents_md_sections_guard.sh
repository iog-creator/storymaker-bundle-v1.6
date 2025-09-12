#!/usr/bin/env bash
set -euo pipefail
ok=0; bad=0
for f in $(git ls-files '**/AGENTS.md'); do
  if rg -q '^# Purpose' "$f" && rg -q '^# Entrypoints & Commands' "$f" && rg -q '^# Interfaces' "$f"; then
    ok=$((ok+1))
  else
    echo "::error ::$f missing required headings (# Purpose / # Entrypoints & Commands / # Interfaces)"
    bad=$((bad+1))
  fi
done
echo "AGENTS.md ok: $ok  bad: $bad"
exit $bad
