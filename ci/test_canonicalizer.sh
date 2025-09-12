#!/usr/bin/env bash
set -euo pipefail
# Same digest whether .proof is present or not.
sample='{"data":{"x":1,"y":[2,3]},"proof":{"sha256":"X","path":"/tmp/x","format":"canon-v1"}}'
no_proof='{"data":{"x":1,"y":[2,3]}}'
a="$(echo "$sample"   | ci/json_hash.py)"
b="$(echo "$no_proof" | ci/json_hash.py)"
[ "$a" = "$b" ] || { echo "canonicalizer drift"; exit 1; }
echo "canonicalizer ok: $a"