#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
lock="$root/docs/SSOT/models.lock.json"

command -v jq >/dev/null 2>&1 || { echo "::error ::jq not found"; exit 1; }
jq -e . "$lock" >/dev/null

exp_chat=$(jq -r .chat_primary "$lock")
exp_reason=$(jq -r .chat_reason "$lock")
exp_embed=$(jq -r .embedding "$lock")
exp_rank=$(jq -r .reranker "$lock")
exp_dims=$(jq -r .dims "$lock")

check_env () {
  local f="$1"; local err=0
  [ -f "$f" ] || { echo "::error ::missing $f"; return 1; }
  # shellcheck disable=SC1090
  source "$f"
  [ "${CHAT_MODEL_PRIMARY:-$AGENTPM_LM_DEFAULT_MODEL}" = "$exp_chat" ]    || { echo "::error ::chat mismatch in $f"; err=1; }
  [ "${CHAT_MODEL_REASON:-$AGENTPM_LM_REASON_MODEL}" = "$exp_reason" ]    || { echo "::error ::reason mismatch in $f"; err=1; }
  [ "${EMBEDDING_MODEL:-$AGENTPM_LM_EMBEDDING_MODEL}" = "$exp_embed" ]    || { echo "::error ::embedding mismatch in $f"; err=1; }
  [ "${RERANKER_MODEL:-$AGENTPM_RERANKER_MODEL}" = "$exp_rank" ]          || { echo "::error ::reranker mismatch in $f"; err=1; }
  [ "${EMBEDDING_DIMS:-$AGENTPM_GRAPH_EMBEDDING_DIMENSIONS}" = "$exp_dims" ] || { echo "::error ::dims mismatch in $f"; err=1; }
  return $err
}

ok=0; total=0
for f in \
  "$root/.env.generated" \
  "$root/.env.local" \
  "$root/.agentpm_workspace/.env.generated" \
  "$root/.agentpm_workspace/.env.local"
do
  [ -f "$f" ] || continue
  total=$((total+1))
  if check_env "$f"; then ok=$((ok+1)); fi
done

echo "models_guard: $ok/$total envs match lock"
[ $ok -eq $total ] || exit 1
