#!/bin/bash
# no_mocks_guard.sh — Universal mock detection and blocking
# This script MUST be sourced early in every service launcher
set -euo pipefail

# Universal kill-switch: if DISABLE_MOCKS=1, mocks are forbidden
if [[ "${DISABLE_MOCKS:-0}" = "1" ]]; then
  if [[ "${MOCK_LMS:-0}" != "0" ]]; then
    echo "[NO-MOCKS GUARD] MOCK_LMS=${MOCK_LMS} but DISABLE_MOCKS=1 — refusing to start." >&2
    echo "[NO-MOCKS GUARD] Mocks are illegal in this project. Set MOCK_LMS=0 and ensure LM Studio is running." >&2
    exit 2
  fi
fi

# Deny "mock" response providers at runtime too
if env | grep -qi '\bmock\b'; then
  echo "[NO-MOCKS GUARD] Found 'mock' in environment — refusing to start." >&2
  echo "[NO-MOCKS GUARD] Mocks are illegal in this project. Remove all mock environment variables." >&2
  exit 2
fi

# Verify required real services are configured
if [[ -z "${GROQ_API_KEY:-}" ]]; then
  echo "[NO-MOCKS GUARD] GROQ_API_KEY is required — refusing to start." >&2
  echo "[NO-MOCKS GUARD] Creative generation requires real Groq API key." >&2
  exit 2
fi

if [[ "${OPENAI_API_BASE:-}" != "http://127.0.0.1:1234/v1" ]]; then
  echo "[NO-MOCKS GUARD] OPENAI_API_BASE must be http://127.0.0.1:1234/v1 — refusing to start." >&2
  echo "[NO-MOCKS GUARD] Embeddings/reranking requires real LM Studio." >&2
  exit 2
fi

echo "[NO-MOCKS GUARD] ✅ All mock checks passed — real services only" >&2
