#!/usr/bin/env bash
# lmstudio_models_envelope.sh — Check LM Studio models availability
# Supports mock mode for development when LM Studio is not available

if [[ "${MOCK_LMS:-}" == "1" ]]; then
    # Mock mode - return success without hitting LM Studio
    echo '{"status":"success","data":{"count":1,"models":["mock-model"]},"error":{"message":""},"meta":{"smoke_score":0.0,"reasons":["mock_mode"],"scope":["lmstudio_models"],"checks":["mock"],"proofs":["mock"]}}'
    exit 0
fi

# Real mode - check LM Studio
API_BASE="${OPENAI_API_BASE:-http://127.0.0.1:1234/v1}"
API_KEY="${OPENAI_API_KEY:-lm-studio}"

# Check if LM Studio is reachable
if ! curl -sS -m 4 -H "Authorization: Bearer $API_KEY" "$API_BASE/models" >/dev/null 2>&1; then
    echo '{"status":"error","data":{},"error":{"message":"LM Studio not reachable"},"meta":{"smoke_score":1.0,"reasons":["lm_studio_unreachable"],"scope":["lmstudio_models"],"checks":[],"proofs":[]}}'
    exit 1
fi

# Get models list
models_response=$(curl -sS -m 8 -H "Authorization: Bearer $API_KEY" "$API_BASE/models" 2>/dev/null || echo '{"data":[]}')

# Count models
count=$(echo "$models_response" | jq -r '.data | length' 2>/dev/null || echo "0")

if [[ "$count" -gt 0 ]]; then
    models_json=$(echo "$models_response" | jq -c '.data[].id' 2>/dev/null | jq -s . || echo '[]')
    echo "{\"status\":\"success\",\"data\":{\"count\":$count,\"models\":$models_json},\"error\":{\"message\":\"\"},\"meta\":{\"smoke_score\":0.0,\"reasons\":[\"models_found\"],\"scope\":[\"lmstudio_models\"],\"checks\":[\"count_ok\"],\"proofs\":[\"lm_studio_models\"]}}"
else
    echo '{"status":"error","data":{"count":0},"error":{"message":"No models loaded in LM Studio"},"meta":{"smoke_score":1.0,"reasons":["no_models"],"scope":["lmstudio_models"],"checks":[],"proofs":[]}}'
fi
