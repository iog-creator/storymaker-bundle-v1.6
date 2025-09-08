#!/usr/bin/env sh
set -eu
fail(){ echo "NO_MOCKS_ENV_GUARD: $1" >&2; exit 1; }
[ -f .env ] || fail ".env missing"
DISABLE=$(grep -E '^DISABLE_MOCKS=' .env | cut -d= -f2- || true)
MOCKLMS=$(grep -E '^MOCK_LMS=' .env | cut -d= -f2- || true)
[ "${DISABLE:-1}" = "1" ] || fail "DISABLE_MOCKS must be 1"
[ "${MOCKLMS:-0}" = "0" ] || fail "MOCK_LMS must be 0"
echo "NO_MOCKS_ENV_GUARD: OK"
