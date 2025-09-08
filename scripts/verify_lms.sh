#!/usr/bin/env bash
set -euo pipefail
ts="$(date +%Y%m%d_%H%M%S)"
mkdir -p docs/proofs/agentpm
out="docs/proofs/agentpm/lmstudio_${ts}.json"

>&2 echo "[lmstudio-proof] listing models…"
resp="$(curl -sS ${OPENAI_API_BASE:-http://127.0.0.1:1234/v1}/models)"

echo "$resp" | jq --arg endpoint "${OPENAI_API_BASE:-http://127.0.0.1:1234/v1}" '
  {
    ok: (.data|type=="array" and (..|.id? // empty | tostring | test("qwen|embedding";"i"))),
    meta: {ts: now|todate, endpoint: $endpoint}
  }
' | tee "$out" | jq -e '.ok==true' >/dev/null

>&2 echo "[lmstudio-proof] wrote $out"