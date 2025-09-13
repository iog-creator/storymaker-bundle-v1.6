#!/usr/bin/env bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
venv="$root/.venv"

[ -x "$venv/bin/python" ] || { echo "::error ::missing $venv/bin/python (run: make venv.ensure)"; exit 1; }

ipath="$("$venv/bin/python" - <<'PY'
import sys, os
print(sys.executable)
PY
)"

case "$ipath" in
  "$venv"/*) echo "venv_guard: interpreter bound to .venv ✔ ($ipath)";;
  *) echo "::error ::interpreter not in .venv ($ipath)"; exit 1;;
esac

# Sanity: prevent global pip usage
out="$("$venv/bin/pip" -V || true)"
case "$out" in
  *"/.venv/"*) echo "venv_guard: pip bound to .venv ✔";;
  *) echo "::error ::pip is not from .venv"; exit 1;;
esac

echo "venv_guard: OK"


