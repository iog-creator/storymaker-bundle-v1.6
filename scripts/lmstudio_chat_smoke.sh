#!/usr/bin/env bash
# lmstudio_chat_smoke.sh — Test LM Studio chat functionality

# Test LM Studio chat
API_BASE="${OPENAI_API_BASE:-http://127.0.0.1:1234/v1}"
API_KEY="${OPENAI_API_KEY:-lm-studio}"
MODEL="${CHAT_MODEL:-}"

# Get first available model if not specified
if [[ -z "$MODEL" ]]; then
    models_response=$(curl -sS -m 4 -H "Authorization: Bearer $API_KEY" "$API_BASE/models" 2>/dev/null || echo '{"data":[]}')
    MODEL=$(echo "$models_response" | jq -r '.data[0].id // empty' 2>/dev/null)
fi

if [[ -z "$MODEL" ]]; then
    echo '{"status":"error","data":{},"error":{"message":"No chat model available"},"meta":{"smoke_score":1.0,"reasons":["no_model"],"scope":["lmstudio_chat"],"checks":[],"proofs":[]}}'
    exit 1
fi

# Test chat
payload=$(jq -n --arg model "$MODEL" \
    '{model:$model,temperature:0,max_tokens:8,messages:[{"role":"user","content":"ping"}]}')

response=$(curl -sS -m 8 -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" \
    -d "$payload" "$API_BASE/chat/completions" 2>/dev/null || echo '{}')

answer=$(echo "$response" | jq -r '.choices[0].message.content // empty' 2>/dev/null)

if [[ -n "$answer" ]]; then
    echo "{\"status\":\"success\",\"data\":{\"response\":\"$answer\",\"model\":\"$MODEL\"},\"error\":{\"message\":\"\"},\"meta\":{\"smoke_score\":0.0,\"reasons\":[\"chat_working\"],\"scope\":[\"lmstudio_chat\"],\"checks\":[\"response_ok\"],\"proofs\":[\"lm_studio_chat\"]}}"
else
    echo '{"status":"error","data":{},"error":{"message":"Chat test failed"},"meta":{"smoke_score":1.0,"reasons":["chat_failed"],"scope":["lmstudio_chat"],"checks":[],"proofs":[]}}'
fi
