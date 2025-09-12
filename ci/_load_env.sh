#!/usr/bin/env bash
set -euo pipefail
# Pick one: .env.local > .env
ENV_FILE="${ENV_FILE:-}"
for f in ".env.local" ".env"; do
  [ -z "${ENV_FILE}" ] && [ -f "$f" ] && ENV_FILE="$f"
done
if [ -n "${ENV_FILE}" ] && [ -f "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
fi
