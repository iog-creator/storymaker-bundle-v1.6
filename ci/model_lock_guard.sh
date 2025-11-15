#!/usr/bin/env bash
# model_lock_guard.sh — fail-closed validation of exact model IDs per SSOT v1.2
set -euo pipefail

# Load environment
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
source "$ROOT_DIR/ci/_load_env.sh"

req() { test -n "${!1:-}" || { echo "Missing $1"; exit 1; }; }

req GROQ_MODEL;            test "$GROQ_MODEL" = "llama-3.3-70b-versatile" || exit 1
req CHAT_MODEL_PRIMARY;    test "$CHAT_MODEL_PRIMARY" = "qwen/qwen3-8b" || exit 1
req CHAT_MODEL_REASON;     test "$CHAT_MODEL_REASON" = "qwen/qwen3-4b-thinking-2507" || exit 1
req EMBEDDING_MODEL;       test "$EMBEDDING_MODEL" = "text-embedding-qwen3-embedding-0.6b" || exit 1
req EMBEDDING_DIMS;        test "$EMBEDDING_DIMS" = "1024" || exit 1
req RERANKER_MODEL;        test "$RERANKER_MODEL" = "qwen.qwen3-reranker-0.6b" || exit 1
req OPENAI_API_BASE;       curl -sf "$OPENAI_API_BASE/models" >/dev/null || exit 1
test "${DISABLE_MOCKS:-}" = "1" && test "${MOCK_LMS:-}" = "0" || exit 1
echo "model_lock_guard: OK"
