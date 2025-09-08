#!/usr/bin/env bash
# verify_live.sh — REAL end-to-end go-live gate (no mocks).
# Orchestrates: no-bypass -> LM Studio (models/chat) -> DB wait/health
# -> SSOT ingest -> embeddings upsert -> graph extract -> KNN -> graph paths
# Emits ONE Envelope v1.1 rollup.

# Self-healing bootstrap: re-invoke through run.sh if not already loaded
if [[ -z "${RUN_SH:-}" ]]; then
  exec bash "$(dirname "$0")/run.sh" "$0" "$@"
fi

set -euo pipefail

# >>> NEW: normalize DB env from DATABASE_URL so all child steps inherit correct PG* <<<
if [[ -f scripts/lib/db_url_env.sh ]]; then
  # shellcheck source=/dev/null
  . scripts/lib/db_url_env.sh
fi
# <<< NEW >>>

have(){ command -v "$1" >/dev/null 2>&1; }

emit(){
  local status="$1"; shift
  local smoke="$1"; shift
  local data_json="$1"; shift
  local reasons_json="$1"; shift
  local checks_json="$1"; shift
  local proofs_json="$1"; shift
  jq -n --arg status "$status" --arg smoke "$smoke" \
    --argjson data "$data_json" --argjson reasons "$reasons_json" \
    --argjson checks "$checks_json" --argjson proofs "$proofs_json" \
'{
  status: $status,
  data: $data,
  error: { message: (if $status=="success" then "" else ($reasons | join("; ")) end), details: {} },
  meta: { smoke_score: ($smoke|tonumber),
          reasons: (if ($reasons|length>0) then $reasons else ["verify_live_ok"] end),
          scope: ["scripts/verify_live.sh"], checks: $checks, proofs: $proofs }
}'
}


# Tools
for t in jq curl psql python3; do
  have "$t" || { emit "error" "1.0" '{}' "$(jq -n --arg t "$t" '["missing_tool:"+$t]')" '[]' '[]'; exit 0; }
done

checks=(); reasons=(); proofs=()
STEP_TIMEOUT="${STEP_TIMEOUT:-0}" # seconds; 0 disables timeout
twrap(){
  # run with optional timeout if available
  if [[ "$STEP_TIMEOUT" -gt 0 ]] && command -v timeout >/dev/null 2>&1; then
    timeout -s TERM "${STEP_TIMEOUT}s" bash -lc "$*"
  else
    bash -lc "$*"
  fi
}

run_step(){
  local name="$1"; shift
  local cmd="$*"
  local out env_status env_smoke
  out="$(twrap "$cmd" 2>/dev/null | jq -c 'if type=="object" then . elif type=="array" then .[0] else . end' 2>/dev/null || true)"
  if [[ -z "${out// }" ]]; then
    reasons+=("no_output:$name"); checks+=("fail:$name"); return 1
  fi
  env_status="$(printf '%s' "$out" | jq -r '.status // empty' 2>/dev/null || true)"
  env_smoke="$(printf '%s' "$out" | jq -r '.meta.smoke_score // empty' 2>/dev/null || true)"
  if [[ "$env_status" == "success" && ( "$env_smoke" == "0" || "$env_smoke" == "0.0" ) ]]; then
    checks+=("ok:$name"); proofs+=("$name"); return 0
  else
    local msg="$(printf '%s' "$out" | jq -r '.error.message // "unknown_error"' 2>/dev/null || true)"
    reasons+=("step_failed:$name:$msg"); checks+=("fail:$name"); return 1
  fi
}

# 0) Local-first
run_step "no_bypass" "bash scripts/no_bypass_gate.sh"

# 1) LM Studio
run_step "lm_models" "bash scripts/lmstudio_models_envelope.sh"
run_step "lm_chat"   "bash scripts/lmstudio_chat_smoke.sh"

# 2) DB gates
: "${TIMEOUT_SEC:=60}"
run_step "db_wait"   "TIMEOUT_SEC=$TIMEOUT_SEC bash scripts/db_wait.sh"
run_step "db_health" "bash scripts/db_health.sh"

# 3) Ingest (fixed to use \copy FROM file)
run_step "ssot_ingest" "bash scripts/ingest_ssot.sh"

# 4) Embeddings / Graph / Retrieval
run_step "embed_upsert"  "bash scripts/embed_upsert.sh"
run_step "graph_extract" "python3 scripts/graph_extract.py"
run_step "knn_smoke"     "bash scripts/knn_smoke.sh"
run_step "graph_paths"   "bash scripts/graph_paths.sh"

# Optional
if [[ -s scripts/embed_report.sh ]]; then
  run_step "embed_report" "bash scripts/embed_report.sh" || true
fi

# Embedding rows sanity
# Respect DATABASE_URL first
if [[ -n "${DATABASE_URL:-}" ]]; then
  CONN="$DATABASE_URL"
else
  CONN="host=${PGHOST:-127.0.0.1} port=${PGPORT:-5432} user=${PGUSER:-postgres} dbname=${PGDATABASE:-agentpm}"
fi
emb_rows="$(psql -At "$CONN" -c "SELECT count(*) FROM kb_chunks WHERE doc_id LIKE 'SSOT/%' AND embedding IS NOT NULL;" 2>/dev/null || echo "")"

critical=(no_bypass lm_models lm_chat db_wait db_health ssot_ingest embed_upsert knn_smoke graph_extract graph_paths)
failed=0
for c in "${critical[@]}"; do
  printf '%s\n' "${checks[@]}" | grep -q "^ok:$c$" || { failed=1; reasons+=("critical_failed:"+$c); }
done

data="$(jq -n \
  --argjson checks "$(printf '%s\n' "${checks[@]}" | jq -R . | jq -s .)" \
  --argjson proofs "$(printf '%s\n' "${proofs[@]}" | jq -R . | jq -s .)" \
  --arg emb_rows "${emb_rows:-0}" \
  '{emb_rows: ( ($emb_rows|tonumber) // 0 ), checks:$checks, proofs:$proofs }')"

if [[ "$failed" -eq 0 && "${emb_rows:-0}" != "0" ]]; then
  emit "success" "0.0" "$data" "$(jq -n '[]')" "$(printf '%s\n' "${checks[@]}" | jq -R . | jq -s .)" "$(printf '%s\n' "${proofs[@]}" | jq -R . | jq -s .)"
else
  emit "error" "1.0" "$data" "$(printf '%s\n' "${reasons[@]}" | jq -R . | jq -s .)" "$(printf '%s\n' "${checks[@]}" | jq -R . | jq -s .)" "$(printf '%s\n' "${proofs[@]}" | jq -R . | jq -s .)"
fi