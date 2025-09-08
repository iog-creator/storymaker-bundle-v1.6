#!/usr/bin/env bash
# db_url_env.sh — source this to normalize PG* from $DATABASE_URL.
# Safe to source multiple times. No external deps required (uses python if present).

set -euo pipefail

# If DEBUG_DB=1, echo resolved connection details to stderr
_debug_db() {
  if [[ "${DEBUG_DB:-0}" == "1" ]]; then
    echo "[db_url_env] PGHOST=${PGHOST:-} PGPORT=${PGPORT:-} PGUSER=${PGUSER:-} PGDATABASE=${PGDATABASE:-}" >&2
  fi
}

# If DATABASE_URL is set, parse and export PG* so psql/pg_isready pick them up.
if [[ -n "${DATABASE_URL:-}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    eval "$(
      python3 - <<'PY'
import os, urllib.parse
u = urllib.parse.urlparse(os.environ["DATABASE_URL"])
user = u.username or "postgres"
password = u.password or ""
host = u.hostname or "127.0.0.1"
port = str(u.port or 5432)
db = (u.path[1:] if u.path.startswith("/") else (u.path or "postgres")) or "postgres"
print(f'export PGUSER="{user}"')
print(f'export PGPASSWORD="{password}"')
print(f'export PGHOST="{host}"')
print(f'export PGPORT="{port}"')
print(f'export PGDATABASE="{db}"')
PY
    )"
  else
    # Minimal sed fallback (covers the common shape)
    export PGUSER="${PGUSER:-$(echo "$DATABASE_URL" | sed -n 's#.*://\([^:/@]*\).*#\1#p')}"
    export PGPASSWORD="${PGPASSWORD:-$(echo "$DATABASE_URL" | sed -n 's#.*://[^:]*:\([^@]*\)@.*#\1#p')}"
    export PGHOST="${PGHOST:-$(echo "$DATABASE_URL" | sed -n 's#.*://[^@]*@\([^:/]*\).*#\1#p')}"
    export PGPORT="${PGPORT:-$(echo "$DATABASE_URL" | sed -n 's#.*://[^@]*@[^:]*:\([0-9]\+\).*#\1#p')}"
    export PGDATABASE="${PGDATABASE:-$(echo "$DATABASE_URL" | sed -n 's#.*/\([^/?]*\).*#\1#p')}"
    : "${PGUSER:=postgres}" ; : "${PGHOST:=127.0.0.1}" ; : "${PGPORT:=5432}" ; : "${PGDATABASE:=postgres}"
  fi
fi

# Helper: run psql against URL if present, otherwise use PG* envs
db_psql() {
  if [[ -n "${DATABASE_URL:-}" ]]; then
    psql "$DATABASE_URL" "$@"
  else
    psql -h "${PGHOST:-127.0.0.1}" -p "${PGPORT:-5432}" -U "${PGUSER:-postgres}" -d "${PGDATABASE:-postgres}" "$@"
  fi
}

_debug_db
