#!/usr/bin/env bash
set -euo pipefail
bash ci/preflight.sh

W="${WORLDCORE_BASE:-http://127.0.0.1:8000}/api/v1"

draft="In a dystopian future where memories are currency, a young woman discovers she can remember everything. She must navigate a world where forgetting is survival, but remembering is revolution. The story follows her journey as she uncovers the truth about her past and the system that controls society. Along the way, she meets a mysterious stranger who claims to know her true identity, and together they must fight against the oppressive regime that has been erasing history itself."
cap=10

resp=$(curl -sS "$W/qa/trope-budget" -H 'Content-Type: application/json' \
  -d "{\"draft\":\"$draft\",\"cap\":$cap}")

jq -e '
  .status=="ok" and .meta.provider=="lm-studio" and
  (.meta.latency_ms|tonumber) >= 0 and
  (.data.used|tonumber) >= 1 and
  (.data.notes|length) >= 1
' >/dev/null <<<"$resp" || {
  echo "QA trope-budget failed validation:"
  echo "$resp" | jq .
  exit 1
}
echo "qa_nonempty_guard ok"
