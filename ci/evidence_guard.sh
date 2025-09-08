#!/bin/bash
# evidence_guard.sh — Require proof of real endpoints used in verification
set -euo pipefail
exec 3>&1 1>&2  # from here: stdout→stderr; use FD3 when you truly need JSON to stdout

echo "🔍 Checking for evidence of real service usage..."

# Check that proofs directory exists
test -d docs/proofs/agentpm || { echo "❌ No proofs generated"; exit 1; }

# LM Studio evidence: look for local OpenAI-compatible endpoint in any JSON
grep -r '127\.0\.0\.1:1234\|OpenAI API\|"openai/v1/models"' docs/proofs/agentpm/ >/dev/null || {
  echo "❌ Missing LM Studio endpoint evidence in proofs"; exit 1; }

# Groq creative evidence: Narrative proof with provider=groq
grep -r '"provider"\s*:\s*"groq"' docs/proofs/agentpm/ >/dev/null || {
  echo "❌ Missing Groq provider evidence in proofs"; exit 1; }

echo "✅ Evidence ok in proofs directory"
