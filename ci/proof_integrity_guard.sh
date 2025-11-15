#!/usr/bin/env bash
set -euo pipefail
source ci/_load_env.sh
bash ci/preflight_cross.sh >/dev/null

rid="$(uuidgen)"
body='{"world_id":"verify","premise":"A courier steals time","structure":"harmon_8","max_beats":8,"mode":"harmon_8"}'
resp="$(curl -sS "${NARRATIVE_BASE}/api/v1/narrative/outline" \
  -H "Content-Type: application/json" -H "X-Request-Id: '"$rid"'" -d "$body")"

echo "$resp" | jq -e '.proof.path and .proof.sha256 and .meta.provider' >/dev/null
p="$(echo "$resp" | jq -r .proof.path)"
h="$(echo "$resp" | jq -r .proof.sha256)"

# Use single-source canonicalizer (Python) for both response and file
hr="$(echo "$resp" | ci/json_hash.py)"
test -f "$p" || { echo "missing proof file: $p"; exit 1; }
hf="$(jq -r . "$p" | ci/json_hash.py)"

if [ "$h" != "$hr" ] || [ "$h" != "$hf" ]; then
  echo "❌ proof integrity mismatch"
  echo "expected: $h"
  echo "resp:     $hr"
  echo "file:     $hf"
  echo "— resp canon (no .proof) —" > /tmp/resp.canon.json
  echo "$resp" | jq 'del(.proof)' | jq -S -c > /tmp/resp.canon.json
  echo "— file canon (no .proof) —" > /tmp/file.canon.json
  jq 'del(.proof)' "$p" | jq -S -c > /tmp/file.canon.json
  echo "diff (resp vs file, canonized, context 1):"
  diff -u --label RESP /tmp/resp.canon.json --label FILE /tmp/file.canon.json || true
  exit 1
fi

echo "✅ proof integrity ok: $h"