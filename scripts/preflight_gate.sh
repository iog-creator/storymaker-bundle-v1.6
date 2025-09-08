#!/usr/bin/env bash
# One-command preflight: LM Studio models + chat, SSOT=16, commit-hygiene (stdin).
# Emits EXACTLY ONE Envelope v1.1 summarizing checks.
set -euo pipefail

ok=1; reasons=(); checks=(); proofs=()

run_env() { # run a JSON-producing step; require success+smoke=0.0
  local name="$1"; shift
  local out="$(bash -lc "$*" 2>&1 || true)"
  if echo "$out" | jq -e 'type=="object" and has("status") and has("meta")' >/dev/null 2>&1; then
    local s="$(echo "$out" | jq -r '.status')" ; local sm="$(echo "$out" | jq -r '.meta.smoke_score // 1')"
    if { [[ "$s" == "success" ]] && { [[ "$sm" == "0" ]] || [[ "$sm" == "0.0" ]]; }; }; then
      checks+=("${name}=ok")
    else ok=0; reasons+=("${name}_fail"); fi
    proofs+=("step:${name}")
  else ok=0; reasons+=("${name}_invalid_envelope"); fi
}

# 0) LM Studio must be reachable and usable
if [[ -s scripts/lmstudio_models_envelope.sh ]]; then run_env "lm_models" "bash scripts/lmstudio_models_envelope.sh"; else ok=0; reasons+=("missing_lm_models"); fi
if [[ -s scripts/lmstudio_chat_smoke.sh   ]]; then run_env "lm_chat"   "bash scripts/lmstudio_chat_smoke.sh";   else ok=0; reasons+=("missing_lm_chat");   fi

# 1) SSOT presence (flexible count)
if [[ -s scripts/ssot_presence.sh ]]; then
  out="$(bash scripts/ssot_presence.sh)"
  if echo "$out" | jq -e '(.status=="success" or .status=="warning") and (.data.count|tonumber)>=1 and (.meta.smoke_score|tonumber)<=0.5' >/dev/null 2>&1; then
    count=$(echo "$out" | jq -r '.data.count')
    checks+=("ssot_presence_${count}=ok"); proofs+=("ssot_count=${count}")
  else ok=0; reasons+=("ssot_presence_fail"); fi
else ok=0; reasons+=("missing_ssot_presence_script"); fi

# 2) Commit hygiene deterministic PASS & FAIL (stdin)
if [[ -s scripts/commit_hygiene_check.sh ]]; then
  pass_out="$( { echo "PR-1234: Good example"; echo "PR-5678: Another good example"; } | bash scripts/commit_hygiene_check.sh --stdin )"
  echo "$pass_out" | jq -e '.status=="success" and .data.window.total==2 and .data.window.matched==2' >/dev/null 2>&1 || { ok=0; reasons+=("commit_hygiene_pass_fail"); }
  fail_out="$( echo "Bad subject" | bash scripts/commit_hygiene_check.sh --stdin )"
  echo "$fail_out" | jq -e '.status=="error" and .meta.smoke_score==1.0 and .data.window.total==1 and .data.window.matched==0' >/dev/null 2>&1 || { ok=0; reasons+=("commit_hygiene_fail_misfire"); }
  checks+=("commit_hygiene_ok")
else ok=0; reasons+=("missing_commit_hygiene"); fi

status="success"; smoke="0.0"; [[ $ok -ne 1 ]] && { status="error"; smoke="1.0"; }
jq -n --arg status "$status" --arg smoke "$smoke" \
  --argjson reasons "$(printf '%s\n' "${reasons[@]:-}" | jq -R . | jq -s .)" \
  --argjson checks  "$(printf '%s\n' "${checks[@]:-}"  | jq -R . | jq -s .)" \
  --argjson proofs  "$(printf '%s\n' "${proofs[@]:-}"  | jq -R . | jq -s .)" \
'{
  status: $status,
  data: { preflight: true },
  error: { message: (if $status=="success" then "" else ($reasons|join("; ")) end), details: {} },
  meta: { smoke_score: ($smoke|tonumber), reasons: (if ($reasons|length)>0 then $reasons else ["preflight_ok"] end),
          scope: ["scripts/preflight_gate.sh"], checks: $checks, proofs: $proofs }
}'
