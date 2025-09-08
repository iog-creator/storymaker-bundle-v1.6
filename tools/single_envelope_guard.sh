#!/usr/bin/env bash
# single_envelope_guard.sh
# Purpose: Ensure pipeline yields EXACTLY ONE Envelope v1.1 JSON object.
# Behavior:
#  - If stdin is a JSON object => pass through (compact).
#  - If stdin is a JSON array  => emit first element (compact).
#  - Otherwise                 => emit ONE error envelope (compact).
set -euo pipefail

read -r -d '' INPUT || true

emit_err() {
  local msg="${1:-invalid input}"
  jq -c -n --arg m "$msg" '{
    status:"error",
    data:{},
    error:{message:$m,details:{}},
    meta:{smoke_score:1.0,reasons:["single_envelope_guard"],scope:["tools/single_envelope_guard.sh"],checks:[],proofs:[]}
  }'
}

if jq -e 'type=="object"' >/dev/null 2>&1 <<<"$INPUT"; then
  jq -c . <<<"$INPUT"
elif jq -e 'type=="array" and (length>=1)' >/dev/null 2>&1 <<<"$INPUT"; then
  jq -c '.[0]' <<<"$INPUT"
else
  emit_err "input is not a JSON object or non-empty array"
fi