#!/usr/bin/env bash
# ssot_v1_2_self_test.sh — validate SSOT v1.2 compliance end-to-end
set -euo pipefail

# Load environment
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
source "$ROOT_DIR/ci/_load_env.sh"

NARRATIVE_BASE="${NARRATIVE_BASE:-http://127.0.0.1:8001}"
WORLDCORE_BASE="${WORLDCORE_BASE:-http://127.0.0.1:8000}"

echo "🧪 SSOT v1.2 Self-Test: Validating end-to-end compliance..."

# Test 1: Narrative v1 endpoint with v1.2 envelope
echo "1. Testing /api/v1/narrative/outline (v1.2 envelope + Groq provider)..."
NARRATIVE_RESPONSE=$(curl -s -X POST "$NARRATIVE_BASE/api/v1/narrative/outline" \
  -H "Content-Type: application/json" \
  -d '{"premise": "A detective discovers that the victim was actually the killer all along", "world_id": "test-ssot-v1.2", "mode": "hero_journey"}')

# Validate v1.2 envelope structure
echo "$NARRATIVE_RESPONSE" | jq -e '.status == "ok"' || { echo "❌ Narrative status not 'ok'"; exit 1; }
echo "$NARRATIVE_RESPONSE" | jq -e '.data' || { echo "❌ Narrative missing 'data' field"; exit 1; }
echo "$NARRATIVE_RESPONSE" | jq -e '.meta.provider == "groq"' || { echo "❌ Narrative provider not 'groq'"; exit 1; }
echo "$NARRATIVE_RESPONSE" | jq -e '.meta.model == "llama-3.3-70b-versatile"' || { echo "❌ Narrative model not 'llama-3.3-70b-versatile'"; exit 1; }
echo "$NARRATIVE_RESPONSE" | jq -e '.meta.api_version == "v1.2"' || { echo "❌ Narrative missing api_version v1.2"; exit 1; }
echo "$NARRATIVE_RESPONSE" | jq -e '.meta.role == "creative"' || { echo "❌ Narrative role not 'creative'"; exit 1; }

# Check proof was written
PROOF_ID=$(echo "$NARRATIVE_RESPONSE" | jq -r '.meta.proof.id // empty')
if [ -n "$PROOF_ID" ]; then
  PROOF_PATH="docs/proofs/agentpm/$PROOF_ID"
  [ -f "$PROOF_PATH" ] || { echo "❌ Proof file not written: $PROOF_PATH"; exit 1; }
  echo "✅ Proof written: $PROOF_PATH"
else
  echo "❌ No proof ID in response"
  exit 1
fi

echo "✅ Narrative v1.2 envelope validation passed"

# Test 2: Embed endpoint with dims:1024 validation
echo "2. Testing /api/v1/search/embed (dims:1024 + LM Studio provider)..."
EMBED_RESPONSE=$(curl -s -X POST "$WORLDCORE_BASE/api/v1/search/embed" \
  -H "Content-Type: application/json" \
  -d '{"text": "test embedding", "model": "text-embedding-qwen3-embedding-0.6b"}')

# Validate dims:1024
echo "$EMBED_RESPONSE" | jq -e '.data.dims == 1024' || { echo "❌ Embed dims not 1024"; exit 1; }
echo "$EMBED_RESPONSE" | jq -e '.meta.provider == "lm-studio"' || { echo "❌ Embed provider not 'lm-studio'"; exit 1; }
echo "$EMBED_RESPONSE" | jq -e '.data.embedding | length == 1024' || { echo "❌ Embedding vector length not 1024"; exit 1; }

echo "✅ Embed dims:1024 validation passed"

# Test 3: Rerank endpoint with sorted scores
echo "3. Testing /api/v1/search/rerank (sorted scores + LM Studio provider)..."
RERANK_RESPONSE=$(curl -s -X POST "$WORLDCORE_BASE/api/v1/search/rerank" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "candidates": [{"id": "doc1", "text": "This is document 1"}, {"id": "doc2", "text": "This is document 2"}, {"id": "doc3", "text": "This is document 3"}], "k": 3}')

# Validate sorted scores
echo "$RERANK_RESPONSE" | jq -e '.data.top_k | length > 0' || { echo "❌ Rerank no results"; exit 1; }
echo "$RERANK_RESPONSE" | jq -e '.meta.provider == "lm-studio"' || { echo "❌ Rerank provider not 'lm-studio'"; exit 1; }

# Check scores are sorted (descending)
SCORES=$(echo "$RERANK_RESPONSE" | jq -r '.data.top_k[].score')
if [ -n "$SCORES" ]; then
  SORTED_SCORES=$(echo "$SCORES" | sort -nr)
  if [ "$SCORES" != "$SORTED_SCORES" ]; then
    echo "❌ Rerank scores not sorted in descending order"
    exit 1
  fi
fi

echo "✅ Rerank sorted scores validation passed"

echo ""
echo "🎉 SSOT v1.2 Self-Test: ALL TESTS PASSED"
echo "   ✅ Narrative v1.2 envelope with Groq provider"
echo "   ✅ Embed dims:1024 with LM Studio provider"  
echo "   ✅ Rerank sorted scores with LM Studio provider"
echo "   ✅ Proof generation working"
echo ""
echo "🚀 SSOT v1.2: VERIFIED"
