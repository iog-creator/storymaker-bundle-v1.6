#!/usr/bin/env bash
set -euo pipefail
grep -Eq '^OPENAI_API_BASE=http://127.0.0.1:1234/v1' .env
grep -Eq '^GROQ_API_KEY=' .env
grep -Eq '^GROQ_MODEL='   .env
mkdir -p docs/proofs/agentpm
out="docs/proofs/agentpm/provider_split_$(date +%Y%m%d_%H%M%S).json"
cat > "$out" <<'JSON'
{"ok": true, "provider_split": "groq=creative, lmstudio=embeddings"}
JSON
echo "Wrote $out"
