#!/usr/bin/env bash
set -euo pipefail

svc="${1:-}"
port="${2:-}"
cmd="${3:-}"

if [[ -z "$svc" || -z "$port" || -z "$cmd" ]]; then
  echo "usage: start_service.sh <name> <port> <command...>" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
if "$script_dir/port_in_use.sh" "$port"; then
  echo "SKIP: $svc (port $port busy)" >&2
  exit 0
fi

echo "START: $svc on :$port"
nohup bash -lc "$cmd" >/dev/null 2>&1 &
disown || true
exit 0



