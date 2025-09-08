#!/usr/bin/env sh
set -eu
mkdir -p .cursor/rules
cp -f docs/SSOT/rules/*.mdc .cursor/rules/
echo "Rules synced to .cursor/rules/"
