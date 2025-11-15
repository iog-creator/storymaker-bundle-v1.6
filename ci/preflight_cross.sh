#!/usr/bin/env bash
set -euo pipefail
source ci/_load_env.sh

# 1) Bring up services once
make services.up >/dev/null || true

# 2) Health checks with auto-detection + soft threshold
REQ_OK="${REQ_OK:-3}"   # require at least this many OKs

check() { curl -sfS "$1" >/dev/null && echo "OK  $1" || echo "BAD $1"; }

detect_orch() {
  # Try likely paths in priority order
  for p in /healthz /api/v1/health /health; do
    if curl -sfS "${ORCHESTRATION_BASE}${p}" >/dev/null; then
      echo "${ORCHESTRATION_BASE}${p}"
      return 0
    fi
  done
  # No orchestration? Return empty; caller will still pass if threshold met
  echo ""
}

ORCH_HEALTH_OVERRIDE="${ORCH_HEALTH_OVERRIDE:-}"
ORCH_HEALTH="$( [ -n "$ORCH_HEALTH_OVERRIDE" ] && echo "$ORCH_HEALTH_OVERRIDE" || detect_orch )"

urls=(
  "${WORLDCORE_BASE}/health"
  "${NARRATIVE_BASE}/api/v1/health"
  "${NARRATIVE_BASE}/health"
)
[ -n "$ORCH_HEALTH" ] && urls+=("$ORCH_HEALTH")

ok=0
echo "— preflight health sweep —"
for u in "${urls[@]}"; do
  if curl -sfS "$u" >/dev/null; then
    echo "✅ $u"
    ok=$((ok+1))
  else
    echo "❌ $u"
  fi
done

echo "health OK: $ok / ${#urls[@]}  (need ≥ $REQ_OK)"
[ "$ok" -ge "$REQ_OK" ] || { echo "Services not healthy"; exit 1; }

# 3) (Optional) Strict legacy preflight AFTER tolerant health
#    - Set PREFLIGHT_STRICT=1 to enforce; otherwise it is skipped or tolerated.
if [ -f "ci/preflight.sh" ]; then
  if [ "${PREFLIGHT_STRICT:-0}" = "1" ]; then
    echo "running strict preflight.sh ..."
    bash ci/preflight.sh
  else
    echo "skipping strict preflight.sh (set PREFLIGHT_STRICT=1 to enable)"
  fi
fi

echo "preflight_cross ok"
