#!/usr/bin/env bash
# run.sh — strict SSOT loader: source .env, normalize DB, guard, then exec the command.
set -euo pipefail

# Set sentinel to indicate we're running through the loader
export RUN_SH=1

# 1) Load .env as SSOT (required)
if [[ ! -f .env ]]; then
  echo "Missing .env (copy from .env.example first)" >&2
  exit 1
fi
set -a; source ./.env; set +a

# 2) Normalize DB env from DATABASE_URL (PGHOST/PGPORT/PGUSER/PGDATABASE)
if [[ -f scripts/lib/db_url_env.sh ]]; then
  # shellcheck disable=SC1091
  source scripts/lib/db_url_env.sh
fi

# 3) No-mocks guard: enforce real services only (MUST be first)
if [[ -f scripts/lib/no_mocks_guard.sh ]]; then
  # shellcheck disable=SC1091
  source scripts/lib/no_mocks_guard.sh
fi

# 4) Guard: validate required variables & local-first
if [[ -f scripts/lib/config_guard.sh ]]; then
  # shellcheck disable=SC1091
  source scripts/lib/config_guard.sh
fi

# 5) Policy gates (keep a few quick ones)
[[ "${OPENAI_API_BASE}" == "http://127.0.0.1:1234/v1" ]] || {
  echo "OPENAI_API_BASE must be local" >&2
  exit 1
}
[[ "${EMBEDDING_DIMS:-}" == "1024" ]] || { echo "EMBEDDING_DIMS must be 1024"; exit 1; }

# 6) Run the requested command under this normalized env
exec "$@"
