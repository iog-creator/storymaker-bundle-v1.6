#!/usr/bin/env bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
venv="$root/.venv"
py="${PYTHON_BIN:-python3}"

if [ ! -x "$venv/bin/python" ]; then
  echo "::notice ::creating venv at $venv"
  "$py" -m venv "$venv"
fi

# Ensure pip is available and upgrade to avoid old pip/setuptools annoyances
if ! "$venv/bin/python" -m pip --version >/dev/null 2>&1; then
  echo "::notice ::installing pip in venv"
  "$venv/bin/python" -m ensurepip --upgrade
fi
"$venv/bin/python" -m pip install --upgrade pip > /dev/null

# Force Cursor/VS Code to use this interpreter + env in the integrated terminal
mkdir -p "$root/.vscode"
cat > "$root/.vscode/settings.json" <<'JSON'
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.venvPath": "${workspaceFolder}",
  "python.analysis.venvPath": "${workspaceFolder}",
  "terminal.integrated.env.linux": {
    "VIRTUAL_ENV": "${workspaceFolder}/.venv",
    "PATH": "${workspaceFolder}/.venv/bin:${env:PATH}",
    "PIP_REQUIRE_VIRTUALENV": "1"
  },
  "terminal.integrated.env.osx": {
    "VIRTUAL_ENV": "${workspaceFolder}/.venv",
    "PATH": "${workspaceFolder}/.venv/bin:${env:PATH}",
    "PIP_REQUIRE_VIRTUALENV": "1"
  },
  "terminal.integrated.env.windows": {
    "VIRTUAL_ENV": "${workspaceFolder}\\.venv",
    "Path": "${workspaceFolder}\\.venv\\Scripts;${env:Path}",
    "PIP_REQUIRE_VIRTUALENV": "1"
  }
}
JSON

# Pip local policy (prevents accidental global installs)
mkdir -p "$root/pip"
cat > "$root/pip/pip.conf" <<'INI'
[global]
require-virtualenv = true
disable-pip-version-check = true
INI

echo "venv_lock: OK → .venv + .vscode/settings.json + pip policy"
