#!/usr/bin/env bash
set -euo pipefail
ts="$(date +%Y%m%d_%H%M%S)"
mkdir -p docs/proofs/agentpm
out="docs/proofs/agentpm/narrative_${ts}.json"

>&2 echo "[narrative-proof] hitting Narrative…"
resp="$(curl -sS localhost:8001/narrative/generate/plot \
  -H 'content-type: application/json' \
  -d '{"task":"logline","inputs":{"premise":"A harbor captain faces living fog."}}')"

echo "$resp" | jq '
  {
    ok: ((.data.provider=="groq") and (.data.model|test("llama-3\\.3-70b-versatile")) and (.data.draft|type=="string") and (.data.draft|length>0)),
    provider: .data.provider, model: .data.model,
    draft: (.data.draft|(.[:100] + (if (length>100) then "…" else "" end))),
    meta: {ts: now|todate, endpoint:"narrative:8001"}
  }
' | tee "$out" | jq -e '.ok==true' >/dev/null

>&2 echo "[narrative-proof] wrote $out"
