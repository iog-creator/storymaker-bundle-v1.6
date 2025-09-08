#!/usr/bin/env sh
set -eu
fail(){ echo "PROVIDER_SPLIT_GUARD: $1" >&2; exit 1; }
[ -f .env ] || fail ".env missing"
grep -Eq '^GROQ_API_KEY=' .env || fail "Need GROQ_API_KEY for narrative"
grep -Eq '^GROQ_MODEL='   .env || fail "Need GROQ_MODEL for narrative"
grep -Eq '^OPENAI_API_BASE=http://127.0.0.1:1234/v1' .env || \
  fail "OPENAI_API_BASE must point to LM Studio for embeddings/rerank"
echo "PROVIDER_SPLIT_GUARD: OK"
