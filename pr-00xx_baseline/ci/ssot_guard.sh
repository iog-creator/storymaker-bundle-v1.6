#!/usr/bin/env sh
set -eu
fail(){ echo "SSOT_GUARD: $1" >&2; exit 1; }
[ -d docs/SSOT ] || fail "docs/SSOT missing"
REQ="MASTER_PLAN.md ASBUILT.md MANUAL.md VALIDATION_PROTOCOL.md"
for f in $REQ; do [ -f "docs/SSOT/$f" ] || fail "Missing docs/SSOT/$f"; done
echo "SSOT_GUARD: OK"
