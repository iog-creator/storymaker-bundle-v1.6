#!/usr/bin/env sh
set -eu
fail(){ echo "PROOFS_PATH_GUARD: $1" >&2; exit 1; }
ROOT=docs/proofs/agentpm
[ -d "$ROOT" ] || fail "$ROOT missing"
BAD=$(git ls-files | grep -E '(^|/)proofs(/|$)' | grep -v "^$ROOT" || true)
[ -z "$BAD" ] || fail "Proofs found outside $ROOT: \n$BAD"
echo "PROOFS_PATH_GUARD: OK"
