#!/usr/bin/env bash
# retrieval_smoke_guard.sh — validate retrieval endpoints return dims:1024 and proper provider
set -euo pipefail

# Load environment
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
source "$ROOT_DIR/ci/_load_env.sh"

WORLDCORE_BASE="${WORLDCORE_BASE:-http://127.0.0.1:8000}"

echo "Testing retrieval endpoints..."

# Test embed endpoint
echo "Testing /api/v1/search/embed..."
embed_resp=$(curl -s -X POST "${WORLDCORE_BASE}/api/v1/search/embed" \
  -H "Content-Type: application/json" \
  -d '{"text": "test embedding text"}')

# Validate dims:1024
dims=$(echo "$embed_resp" | jq -r '.data.dims // empty')
if [[ "$dims" != "1024" ]]; then
  echo "RETRIEVAL_SMOKE_GUARD: FAIL - Expected dims:1024, got: $dims"
  exit 1
fi

# Validate provider
provider=$(echo "$embed_resp" | jq -r '.meta.provider // empty')
if [[ "$provider" != "lm-studio" ]]; then
  echo "RETRIEVAL_SMOKE_GUARD: FAIL - Expected provider:lm-studio, got: $provider"
  exit 1
fi

# Test rerank endpoint
echo "Testing /api/v1/search/rerank..."
rerank_resp=$(curl -s -X POST "${WORLDCORE_BASE}/api/v1/search/rerank" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "candidates": [{"text": "candidate 1"}, {"text": "candidate 2"}], "k": 2}')

# Validate provider
provider=$(echo "$rerank_resp" | jq -r '.meta.provider // empty')
if [[ "$provider" != "lm-studio" ]]; then
  echo "RETRIEVAL_SMOKE_GUARD: FAIL - Expected provider:lm-studio, got: $provider"
  exit 1
fi

echo "RETRIEVAL_SMOKE_GUARD: OK"
