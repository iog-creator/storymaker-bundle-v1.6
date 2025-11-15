#!/bin/bash
set -euo pipefail

# Envelope Conformance Guard
# Asserts SSOT v1.2 envelope, role/provider/model, and non-empty payloads

echo "🔍 Testing envelope conformance and payload validation..."

RID=$(uuidgen)
baseN=${NARRATIVE_BASE:-http://127.0.0.1:8001}/api/v1
baseW=${WORLDCORE_BASE:-http://127.0.0.1:8000}/api/v1

# Test 1: Narrative outline with SSOT v1.2 validation
echo "  📝 Testing narrative outline envelope..."
resp=$(curl -sS -H "X-Request-Id: $RID" -H "Content-Type: application/json" \
  -d '{"world_id":"ssot-guard","premise":"A courier steals time","structure":"harmon_8","max_beats":8,"mode":"hero_journey"}' \
  "$baseN/narrative/outline")

echo "$resp" | jq -e '
  .status=="ok" and
  .meta.api_version=="v1.2" and
  .meta.provider=="groq" and
  .meta.role=="creative" and
  (.data.beats|length)>=6 and
  ([.data.beats[].id]|unique|length)==(.data.beats|length) and
  (.data.beats[]|.description|length)>0
'

echo "  ✅ Narrative outline envelope validation passed"

# Test 2: QA trope budget with non-empty data validation
echo "  🎭 Testing QA trope budget envelope..."
qa1=$(curl -sS -H "X-Request-Id: $RID" -H "Content-Type: application/json" \
  -d '{"draft":"Hook, promise and plant are present.","cap":10}' \
  "$baseW/qa/trope-budget")

echo "$qa1" | jq -e '
  .status=="ok" and 
  .meta.provider=="lm-studio" and
  (.data.used|type)=="number" and 
  (.data.cap==10) and
  (.data.notes|type)=="array" and
  (.data.notes|length)>0 and
  (.data.used>0)
'

echo "  ✅ QA trope budget envelope validation passed"

# Test 3: QA promise payoff with non-empty ledger validation
echo "  🎯 Testing QA promise payoff envelope..."
qa2=$(curl -sS -H "X-Request-Id: $RID" -H "Content-Type: application/json" \
  -d '{"draft":"Chekhov gun setup without payoff"}' \
  "$baseW/qa/promise-payoff")

echo "$qa2" | jq -e '
  .status=="ok" and 
  .meta.provider=="lm-studio" and
  .meta.role=="retrieval" and
  (.data.ledger|type)=="array" and
  (.data.ledger|length)>0
'

echo "  ✅ QA promise payoff envelope validation passed"

# Test 4: Embeddings with dimension validation
echo "  🔢 Testing embeddings envelope..."
emb=$(curl -sS -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-qwen3-embedding-0.6b","input":"test embedding"}' \
  "$baseW/embeddings")

echo "$emb" | jq -e '
  .status=="ok" and
  .meta.provider=="lm-studio" and
  .meta.role=="retrieval" and
  (.data.embedding|length)==1024 and
  ([.data.embedding[]|type]=="number") and
  ([.data.embedding[]|.!=0]|any)
'

echo "  ✅ Embeddings envelope validation passed"

# Test 5: Rerank with sorting validation
echo "  🔄 Testing rerank envelope..."
rerank=$(curl -sS -H "Content-Type: application/json" \
  -d '{"query":"test query","candidates":["candidate 1","candidate 2","candidate 3"],"top_k":3}' \
  "$baseW/search/rerank")

echo "$rerank" | jq -e '
  .status=="ok" and
  .meta.provider=="lm-studio" and
  .meta.role=="retrieval" and
  (.data.results|length)==3 and
  ([.data.results[].score] | . == (sort_by(-.) | .))
'

echo "  ✅ Rerank envelope validation passed"

echo "🎉 All envelope conformance tests passed!"
