#!/bin/bash
# Mock LM Studio models check for development

if [[ "${MOCK_LMS:-}" == "1" ]]; then
    echo '{"status":"success","data":{"count":1,"models":["mock-model"]},"error":{"message":""},"meta":{"smoke_score":0.0,"reasons":["mock_mode"],"scope":["lmstudio_models"],"checks":["mock"],"proofs":["mock"]}}'
else
    echo '{"status":"error","data":{},"error":{"message":"LM Studio not available"},"meta":{"smoke_score":1.0,"reasons":["lm_studio_unavailable"],"scope":["lmstudio_models"],"checks":[],"proofs":[]}}'
fi
