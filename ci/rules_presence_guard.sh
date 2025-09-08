#!/usr/bin/env sh
set -eu
fail(){ echo "RULES_PRESENCE_GUARD: $1" >&2; exit 1; }
[ -d docs/SSOT/rules ] || fail "docs/SSOT/rules missing"
CNT=$(find docs/SSOT/rules -maxdepth 1 -name '*.mdc' | wc -l | tr -d ' ')
[ "$CNT" -ge 5 ] || fail "Need >=5 .mdc rule files (found $CNT)"
[ -d .cursor/rules ] || fail ".cursor/rules missing (sync needed)"
echo "RULES_PRESENCE_GUARD: OK"
