#!/usr/bin/env bash
set -euo pipefail
# One-liner for drift detection - run this if proof hashes ever drift again

RID=$(uuidgen)
RESP=$(curl -sS "$NARRATIVE_BASE/api/v1/narrative/outline" \
  -H "Content-Type: application/json" -H "X-Request-Id: $RID" \
  -d '{"world_id":"verify","premise":"A courier steals time","structure":"harmon_8","max_beats":8,"mode":"harmon_8"}')

echo "=== HASH COMPARISON ==="
echo "expected: $(echo "$RESP" | jq -r .proof.sha256)"
echo "resp:     $(echo "$RESP" | ci/json_hash.py)"
echo "file:     $(jq -r .proof.path <<<"$RESP" | xargs cat | ci/json_hash.py)"

echo ""
echo "=== CANONICAL DIFF ==="
echo "$RESP" | jq 'del(.proof)' | jq -S -c > /tmp/resp.canon.json
jq -r .proof.path <<<"$RESP" | xargs jq 'del(.proof)' | jq -S -c > /tmp/file.canon.json
diff -u --label RESP /tmp/resp.canon.json --label FILE /tmp/file.canon.json || true
