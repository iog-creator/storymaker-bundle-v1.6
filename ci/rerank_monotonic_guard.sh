#!/bin/bash
set -euo pipefail

# Rerank Monotonic Guard
# Asserts result list is sorted desc; p95 latency budget < 800ms

echo "🔄 Testing rerank monotonic ordering and latency..."

baseW=${WORLDCORE_BASE:-http://127.0.0.1:8000}/api/v1

# Test 1: Basic rerank with monotonic ordering
echo "  📊 Testing basic rerank ordering..."
start=$(date +%s%3N)
resp=$(curl -sS -H "Content-Type: application/json" \
  -d '{"query":"test query","candidates":["candidate 1","candidate 2","candidate 3","candidate 4","candidate 5"],"top_k":5}' \
  "$baseW/search/rerank")
dur=$(( $(date +%s%3N) - start ))

echo "$resp" | jq -e '
  .status=="ok" and 
  .meta.provider=="lm-studio" and
  .meta.role=="retrieval" and
  (.data.results|length)==5 and
  ([.data.results[].score] | . == (sort_by(-.) | .))
'

echo "  ✅ Basic rerank ordering validation passed"

# Test 2: Latency budget validation
echo "  ⏱️  Testing latency budget..."
if [ "$dur" -gt 800 ]; then
  echo "❌ Rerank latency exceeded budget: ${dur}ms > 800ms"
  exit 1
fi

echo "  ✅ Latency budget validation passed (${dur}ms)"

# Test 3: Score range validation
echo "  📈 Testing score range validation..."
echo "$resp" | jq -e '
  (.data.results[]|.score|type)=="number" and
  (.data.results[]|.score)>=0 and
  (.data.results[]|.score)<=1
'

echo "  ✅ Score range validation passed"

# Test 4: Multiple rerank requests for stability
echo "  🔄 Testing rerank stability across multiple requests..."
for i in {1..5}; do
  start=$(date +%s%3N)
  resp_i=$(curl -sS -H "Content-Type: application/json" \
    -d "{\"query\":\"test query $i\",\"candidates\":[\"candidate 1\",\"candidate 2\",\"candidate 3\"],\"top_k\":3}" \
    "$baseW/search/rerank")
  dur_i=$(( $(date +%s%3N) - start ))
  
  echo "$resp_i" | jq -e '
    .status=="ok" and
    (.data.results|length)==3 and
    ([.data.results[].score] | . == (sort_by(-.) | .))
  '
  
  if [ "$dur_i" -gt 800 ]; then
    echo "❌ Rerank latency exceeded budget on request $i: ${dur_i}ms > 800ms"
    exit 1
  fi
done

echo "  ✅ Rerank stability validation passed"

# Test 5: Edge case - single candidate
echo "  🎯 Testing edge case - single candidate..."
start=$(date +%s%3N)
resp_single=$(curl -sS -H "Content-Type: application/json" \
  -d '{"query":"test query","candidates":["single candidate"],"top_k":1}' \
  "$baseW/search/rerank")
dur_single=$(( $(date +%s%3N) - start ))

echo "$resp_single" | jq -e '
  .status=="ok" and
  (.data.results|length)==1 and
  (.data.results[0].score|type)=="number"
'

echo "  ✅ Single candidate edge case validation passed"

# Test 6: Edge case - empty candidates
echo "  🚫 Testing edge case - empty candidates..."
start=$(date +%s%3N)
resp_empty=$(curl -sS -H "Content-Type: application/json" \
  -d '{"query":"test query","candidates":[],"top_k":0}' \
  "$baseW/search/rerank")
dur_empty=$(( $(date +%s%3N) - start ))

echo "$resp_empty" | jq -e '
  .status=="ok" and
  (.data.results|length)==0
'

echo "  ✅ Empty candidates edge case validation passed"

# Test 7: Score consistency validation
echo "  🔍 Testing score consistency..."
python3 - <<'PY'
import json
import sys
import numpy as np

# Parse the main response
resp = json.load(sys.stdin)

results = resp['data']['results']
scores = [r['score'] for r in results]

# Check that scores are properly ordered (descending)
if scores != sorted(scores, reverse=True):
    print("❌ Scores are not properly ordered")
    sys.exit(1)

# Check that scores have reasonable variance (not all identical)
if len(set(scores)) == 1 and len(scores) > 1:
    print("❌ All scores are identical")
    sys.exit(1)

# Check that scores are in valid range [0, 1]
if not all(0 <= s <= 1 for s in scores):
    print(f"❌ Scores out of range: {scores}")
    sys.exit(1)

print("  ✅ Score consistency validation passed")
PY

echo "  ✅ Score consistency validation passed"

echo "🎉 All rerank monotonic tests passed!"
