#!/usr/bin/env bash
set -euo pipefail

port="${1:-}"
if [[ -z "${port}" ]]; then
  echo "usage: port_in_use.sh <port>" >&2
  exit 2
fi

# Try ss, fallback to lsof, then nc
if command -v ss >/dev/null 2>&1; then
  if ss -ltnp 2>/dev/null | awk '{print $4}' | grep -Eq "[:\.]${port}$"; then
    exit 0
  else
    exit 1
  fi
elif command -v lsof >/dev/null 2>&1; then
  if lsof -i TCP:"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
    exit 0
  else
    exit 1
  fi
else
  if nc -z localhost "${port}" >/dev/null 2>&1; then
    exit 0
  else
    exit 1
  fi
fi



