#!/usr/bin/env bash
set -euo pipefail
# Create workspace symlink to canonical proofs
mkdir -p .agentpm_workspace/docs
rm -rf .agentpm_workspace/docs/proofs
ln -s ../../docs/proofs/agentpm .agentpm_workspace/docs/proofs
echo "✅ workspace: linked .agentpm_workspace/docs/proofs → ../../docs/proofs/agentpm"
