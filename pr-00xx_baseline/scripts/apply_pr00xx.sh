#!/usr/bin/env bash
set -euo pipefail
echo "Applying PR-00XX baseline into repo root..."
shopt -s dotglob || true

# Copy dirs/files into current directory
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cp -R "$SRC/ci" .
mkdir -p docs/SSOT/rules
cp -R "$SRC/docs/SSOT/rules/"* docs/SSOT/rules/
mkdir -p scripts
cp -f "$SRC/scripts/sync_rules.sh" scripts/
cp -f "$SRC/scripts/smoke_provider_split.sh" scripts/
cp -f "$SRC/scripts/proofs_lint.sh" scripts/
mkdir -p .githooks
cp -f "$SRC/.githooks/pre-commit" .githooks/
mkdir -p .github/workflows
cp -f "$SRC/.github/workflows/verify.yml" .github/workflows/
# Append Makefile rules
if ! grep -q "guards:" Makefile 2>/dev/null; then
  cat "$SRC/MAKEFILE_APPEND.txt" >> Makefile
  echo "Appended Makefile targets."
else
  echo "Makefile already has guard targets; skipping append."
fi
chmod +x ci/*.sh scripts/*.sh .githooks/pre-commit || true
echo "Done. Next:"
echo "  1) Append ENV_EXAMPLE_APPEND.env to your .env.example"
echo "  2) Insert README_INSERT_PROOFS.md block into README.md"
echo "  3) Enable local git hook: git config core.hooksPath .githooks"
echo "  4) Run: make rules-sync verify"
