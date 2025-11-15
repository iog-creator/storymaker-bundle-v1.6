#!/usr/bin/env bash
# config_guard.sh — fail-closed validation of SSOT config.
set -euo pipefail

req_vars=(OPENAI_API_BASE OPENAI_API_KEY DATABASE_URL EMBEDDING_DIMS CHAT_MODEL EMBEDDING_MODEL)
missing=()
for v in "${req_vars[@]}"; do
  [[ -n "${!v:-}" ]] || missing+=("$v")
done

# Local-first hard rule (with mock support for development)
if [[ "${OPENAI_API_BASE:-}" != "http://127.0.0.1:1234/v1" ]] && [[ "${MOCK_LMS:-}" != "1" ]]; then
  echo "[config_guard] ERROR: OPENAI_API_BASE must be http://127.0.0.1:1234/v1 (local-first)." >&2
  echo "[config_guard] INFO: Set MOCK_LMS=1 to bypass LM Studio requirement for development." >&2
  exit 1
fi

# Embedding dims contract (pgvector schema)
if [[ "${EMBEDDING_DIMS:-}" != "1024" ]]; then
  echo "[config_guard] ERROR: EMBEDDING_DIMS must be 1024 to match pgvector schema." >&2
  exit 1
fi

if ((${#missing[@]})); then
  printf '[config_guard] ERROR: Missing required vars in .env: %s\n' "${missing[*]}" >&2
  exit 1
fi
