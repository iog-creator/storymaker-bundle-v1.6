#!/usr/bin/env bash
set -euo pipefail
ROOT=docs/proofs/agentpm
fail(){ echo "PROOFS_LINT: $1" >&2; exit 1; }
[ -d "$ROOT" ] || exit 0
command -v jq >/dev/null 2>&1 || { echo "jq not found; skipping JSON validation"; exit 0; }
while IFS= read -r -d '' f; do
  [ "$(stat -c%s "$f")" -le 524288 ] || fail "$f >512KB"
  jq -e . "$f" >/dev/null || fail "$f is not valid JSON"
done < <(find "$ROOT" -type f -name '*.json' -print0)
echo "PROOFS_LINT: OK"
