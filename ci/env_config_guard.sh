#!/usr/bin/env bash
set -eu

# Load environment
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
source "$ROOT_DIR/ci/_load_env.sh"

fail(){ echo "ENV_CONFIG_GUARD: $1" >&2; exit 1; }

[ -f .env ] || fail ".env missing"
grep -Eq '^OPENAI_API_BASE=' .env || fail "OPENAI_API_BASE missing"
grep -Eq '^OPENAI_API_KEY='  .env || fail "OPENAI_API_KEY missing"
grep -Eq '^CHAT_MODEL_PRIMARY=' .env || fail "CHAT_MODEL_PRIMARY missing"
grep -Eq '^EMBEDDING_MODEL=' .env || fail "EMBEDDING_MODEL missing"
grep -Eq '^EMBEDDING_DIMS='  .env || fail "EMBEDDING_DIMS missing"
grep -Eq '^GROQ_API_KEY='    .env || fail "GROQ_API_KEY missing"
grep -Eq '^GROQ_MODEL='      .env || fail "GROQ_MODEL missing"
echo "ENV_CONFIG_GUARD: OK"
