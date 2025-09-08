#!/usr/bin/env bash
set -euo pipefail

port="${1:-}"
if [[ -z "${port}" ]]; then
  echo "usage: kill_by_port.sh <port>" >&2
  exit 2
fi

kill_pids(){
  local pids="$1"
  [[ -z "$pids" ]] && return 0
  echo "$pids" | xargs -r kill -TERM || true
  sleep 0.5
  echo "$pids" | xargs -r kill -KILL || true
}

if command -v lsof >/dev/null 2>&1; then
  pids=$(lsof -t -i TCP:"${port}" -sTCP:LISTEN || true)
  kill_pids "$pids"
elif command -v ss >/dev/null 2>&1; then
  pids=$(ss -ltnp 2>/dev/null | awk -v p=":$port$" '$4 ~ p {print $7}' | sed -E 's/.*pid=([0-9]+),.*/\1/' | sort -u)
  kill_pids "$pids"
else
  echo "WARN: neither lsof nor ss available; cannot kill by port" >&2
  exit 0
fi


