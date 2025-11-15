#!/bin/bash
set -euo pipefail

# Embedding Dimension Guard
# Asserts length==1024, not-all-zeros, cross-input diversity

echo "🔢 Testing embedding dimension invariants..."

baseW=${WORLDCORE_BASE:-http://127.0.0.1:8000}/api/v1

# Test 1: Generate embeddings for different texts
echo "  📊 Generating embeddings for diversity test..."
one=$(curl -sS -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-qwen3-embedding-0.6b","input":"alpha"}' \
  "$baseW/embeddings")

two=$(curl -sS -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-qwen3-embedding-0.6b","input":"beta"}' \
  "$baseW/embeddings")

three=$(curl -sS -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-qwen3-embedding-0.6b","input":"gamma"}' \
  "$baseW/embeddings")

# Test 2: Validate dimension length
echo "  📏 Validating embedding dimensions..."
len1=$(echo "$one" | jq '.data.embedding|length')
len2=$(echo "$two" | jq '.data.embedding|length')
len3=$(echo "$three" | jq '.data.embedding|length')

if [ "$len1" -ne 1024 ] || [ "$len2" -ne 1024 ] || [ "$len3" -ne 1024 ]; then
  echo "❌ Embedding dimension mismatch: $len1, $len2, $len3 (expected 1024)"
  exit 1
fi

echo "  ✅ All embeddings have correct 1024 dimensions"

# Test 3: Validate non-zero values
echo "  🔍 Validating non-zero values..."
sumabs1=$(echo "$one" | jq '[.data.embedding[]|abs]|add')
sumabs2=$(echo "$two" | jq '[.data.embedding[]|abs]|add')
sumabs3=$(echo "$three" | jq '[.data.embedding[]|abs]|add')

if (( $(echo "$sumabs1 == 0" | bc -l) )) || (( $(echo "$sumabs2 == 0" | bc -l) )) || (( $(echo "$sumabs3 == 0" | bc -l) )); then
  echo "❌ Found zero-sum embeddings: $sumabs1, $sumabs2, $sumabs3"
  exit 1
fi

echo "  ✅ All embeddings contain non-zero values"

# Test 4: Validate cross-input diversity
echo "  🌈 Validating cross-input diversity..."
python3 - <<'PY'
import json
import sys
import numpy as np

# Parse embeddings
one = json.load(sys.stdin)
two = json.load(sys.stdin)
three = json.load(sys.stdin)

emb1 = np.array(one['data']['embedding'])
emb2 = np.array(two['data']['embedding'])
emb3 = np.array(three['data']['embedding'])

# Check for identical embeddings (should be different)
if np.allclose(emb1, emb2, atol=1e-6):
    print("❌ Embeddings 1 and 2 are identical")
    sys.exit(1)

if np.allclose(emb1, emb3, atol=1e-6):
    print("❌ Embeddings 1 and 3 are identical")
    sys.exit(1)

if np.allclose(emb2, emb3, atol=1e-6):
    print("❌ Embeddings 2 and 3 are identical")
    sys.exit(1)

# Check for reasonable diversity (cosine similarity should be < 0.99)
cos_sim_12 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
cos_sim_13 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
cos_sim_23 = np.dot(emb2, emb3) / (np.linalg.norm(emb2) * np.linalg.norm(emb3))

if cos_sim_12 > 0.99 or cos_sim_13 > 0.99 or cos_sim_23 > 0.99:
    print(f"❌ Embeddings too similar: {cos_sim_12:.4f}, {cos_sim_13:.4f}, {cos_sim_23:.4f}")
    sys.exit(1)

print("  ✅ Embeddings show proper diversity")
PY

echo "  ✅ Cross-input diversity validation passed"

# Test 5: Validate embedding range and distribution
echo "  📈 Validating embedding range and distribution..."
python3 - <<'PY'
import json
import sys
import numpy as np

# Parse embeddings
one = json.load(sys.stdin)
two = json.load(sys.stdin)
three = json.load(sys.stdin)

emb1 = np.array(one['data']['embedding'])
emb2 = np.array(two['data']['embedding'])
emb3 = np.array(three['data']['embedding'])

# Check for reasonable range (not all values the same)
for i, emb in enumerate([emb1, emb2, emb3], 1):
    if np.std(emb) < 0.001:
        print(f"❌ Embedding {i} has no variance (std: {np.std(emb):.6f})")
        sys.exit(1)
    
    if np.min(emb) == np.max(emb):
        print(f"❌ Embedding {i} has identical values")
        sys.exit(1)

print("  ✅ Embeddings have proper variance and range")
PY

echo "  ✅ Embedding range and distribution validation passed"

echo "🎉 All embedding dimension tests passed!"
