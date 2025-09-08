#!/bin/bash
# Mock LM Studio chat check for development

if [[ "${MOCK_LMS:-}" == "1" ]]; then
    echo '{"status":"success","data":{"response":"pong"},"error":{"message":""},"meta":{"smoke_score":0.0,"reasons":["mock_mode"],"scope":["lmstudio_chat"],"checks":["mock"],"proofs":["mock"]}}'
else
    echo '{"status":"error","data":{},"error":{"message":"LM Studio not available"},"meta":{"smoke_score":1.0,"reasons":["lm_studio_unavailable"],"scope":["lmstudio_chat"],"checks":[],"proofs":[]}}'
fi
