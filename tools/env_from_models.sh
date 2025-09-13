#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
lock="$root/docs/SSOT/models.lock.json"

command -v jq >/dev/null 2>&1 || { echo "::error ::jq not found"; exit 1; }
jq -e . "$lock" >/dev/null

export CHAT_MODEL_PRIMARY=$(jq -r .chat_primary "$lock")
export CHAT_MODEL_REASON=$(jq -r .chat_reason  "$lock")
export EMBEDDING_MODEL=$(jq -r .embedding     "$lock")
export RERANKER_MODEL=$(jq -r .reranker       "$lock")
export EMBEDDING_DIMS=$(jq -r .dims           "$lock")

cat >"$root/.env.generated" <<EOF
# GENERATED from docs/SSOT/models.lock.json
CHAT_MODEL_PRIMARY=$CHAT_MODEL_PRIMARY
CHAT_MODEL_REASON=$CHAT_MODEL_REASON
EMBEDDING_MODEL=$EMBEDDING_MODEL
RERANKER_MODEL=$RERANKER_MODEL
EMBEDDING_DIMS=$EMBEDDING_DIMS
EOF

agentws="$root/.agentpm_workspace"
mkdir -p "$agentws"
cat >"$agentws/.env.generated" <<EOF
# GENERATED from docs/SSOT/models.lock.json
AGENTPM_LM_DEFAULT_MODEL=$CHAT_MODEL_PRIMARY
AGENTPM_LM_REASON_MODEL=$CHAT_MODEL_REASON
AGENTPM_LM_EMBEDDING_MODEL=$EMBEDDING_MODEL
AGENTPM_RERANKER_MODEL=$RERANKER_MODEL
AGENTPM_GRAPH_EMBEDDING_DIMENSIONS=$EMBEDDING_DIMS
EOF

echo "envs rendered: .env.generated | .agentpm_workspace/.env.generated"


