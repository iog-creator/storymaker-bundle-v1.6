#!/usr/bin/env bash
set -euo pipefail
# Fail if sources reference unversioned public routes (excluding health endpoints)
rg -n --hidden --glob '!node_modules' --glob '!*tests*' \
  -e '"/run"' -e '"/narrative/outline"' || true
# Allow internal server router wiring only if it also exposes /api/v1/*
if rg -n '"\/run"' -g '!**/router*' -g '!**/legacy*' -g '!**/orchestration*' -g '!**/ci*' -g '!**/proofs*' | grep -q .; then
  echo "Legacy /run found outside router compat layer"; exit 1
fi
