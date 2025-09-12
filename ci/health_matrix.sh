#!/usr/bin/env bash
set -euo pipefail
source ci/_load_env.sh

O="${ORCH_HEALTH_OVERRIDE:-}"
detect() {
  for p in /healthz /api/v1/health /health; do
    curl -sfS "${ORCHESTRATION_BASE}${p}" >/dev/null && { echo "${ORCHESTRATION_BASE}${p}"; return; }
  done
  echo ""
}
ORCH="${O:-$(detect)}"

declare -a urls=(
  "${WORLDCORE_BASE}/health"
  "${NARRATIVE_BASE}/api/v1/health"
  "${NARRATIVE_BASE}/health"
)
[ -n "$ORCH" ] && urls+=("$ORCH")

ok=0
echo "— health matrix —"
for u in "${urls[@]}"; do
  if curl -sfS "$u" >/dev/null; then
    printf "✅ %s\n" "$u"; ok=$((ok+1))
  else
    printf "❌ %s\n" "$u"
  fi
done
need="${REQ_OK:-3}"
echo "OK: $ok / ${#urls[@]}  (need ≥ $need)"
[ "$ok" -ge "$need" ]

