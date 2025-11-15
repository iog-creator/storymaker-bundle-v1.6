#!/usr/bin/env bash
set -euo pipefail
source ci/_load_env.sh

# check LM Studio models are present
need=( "qwen/qwen3-8b" "qwen/qwen3-4b-thinking-2507" "qwen.qwen3-reranker-0.6b" "text-embedding-qwen3-embedding-0.6b" )
have="$(curl -sS "${OPENAI_API_BASE}/models" | jq -r '.data[].id')"
for m in "${need[@]}"; do
  echo "$have" | grep -qx "$m" || { echo "Missing LM Studio model: $m"; exit 1; }
done

# services up + health
make services.up >/dev/null
for url in \
  "${WORLDCORE_BASE}/health" \
  "${NARRATIVE_BASE}/health" \
  "${ORCHESTRATION_BASE}/healthz"
do
  curl -sfS "$url" >/dev/null || { echo "Not healthy: $url"; exit 1; }
done

echo "preflight ok"
