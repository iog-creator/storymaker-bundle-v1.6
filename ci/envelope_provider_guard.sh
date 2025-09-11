#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
fail=0
for f in docs/proofs/agentpm/narrative_*.json docs/proofs/agentpm/narrative_outline_*.json; do
  provider=$(jq -r '.meta.provider // empty' "$f" || true)
  if [[ "$provider" != "groq" ]]; then
    echo "[provider-guard] $f: provider must be 'groq'"; fail=1
  fi
done
exit $fail
