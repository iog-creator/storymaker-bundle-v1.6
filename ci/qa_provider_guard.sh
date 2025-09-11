#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
fail=0
for f in docs/proofs/agentpm/qa_*.json; do
  provider=$(jq -r '.meta.provider // empty' "$f" || true)
  if [[ "$provider" != "lm-studio" ]]; then
    echo "[qa-guard] $f: provider must be 'lm-studio'"; fail=1
  fi
done
exit $fail
