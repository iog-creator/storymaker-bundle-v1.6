#!/usr/bin/env bash
set -euo pipefail
# DEPRECATED NOTE: This wrapper only delegates to Python canonicalizer.
# No jq fallback is allowed.
# Usage: cat envelope.json | ci/json_hash.sh

if command -v python3 >/dev/null 2>&1; then
  exec python3 ci/json_hash.py
fi
echo "::error ::python3 not found; canonicalizer unavailable" >&2
exit 90
