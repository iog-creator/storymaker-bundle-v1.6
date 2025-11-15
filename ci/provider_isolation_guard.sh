#!/usr/bin/env bash
set -euo pipefail
# break LM Studio; Narrative should still pass, QA should fail
export OPENAI_API_BASE_ORIG="${OPENAI_API_BASE:-}"
export OPENAI_API_BASE="http://127.0.0.1:9999/v1"

set +e
narr=$(curl -sS -o /dev/null -w "%{http_code}" \
  "${NARRATIVE_BASE:-http://127.0.0.1:8001}/api/v1/narrative/outline" \
  -H 'Content-Type: application/json' -d '{"world_id":"x","premise":"y","structure":"harmon_8"}')
qa=$(curl -sS -o /dev/null -w "%{http_code}" \
  "${WORLDCORE_BASE:-http://127.0.0.1:8000}/api/v1/qa/trope-budget" \
  -H 'Content-Type: application/json' -d '{"draft":"x","cap":10}')
set -e

# Narrative must be 200, QA must be 5xx
[ "$narr" -eq 200 ] || { echo "Narrative fell over when LM Studio broke"; exit 1; }
[ "$qa" -ge 500 ] || { echo "QA did not fail-closed when LM Studio broke"; exit 1; }

export OPENAI_API_BASE="$OPENAI_API_BASE_ORIG"