#!/bin/bash
# Debug script to test run.sh without hanging

echo "=== DEBUG: Testing run.sh ==="
echo "Current directory: $(pwd)"
echo "Environment variables:"
echo "MOCK_LMS: ${MOCK_LMS:-not set}"
echo "OPENAI_API_BASE: ${OPENAI_API_BASE:-not set}"

echo "=== Testing run.sh with timeout ==="
timeout 5 bash -c 'source scripts/run.sh bash -lc "echo test"' || echo "TIMEOUT after 5 seconds"

echo "=== Testing direct script execution ==="
timeout 5 bash scripts/run.sh bash -lc "echo direct test" || echo "DIRECT TIMEOUT after 5 seconds"

echo "=== Testing config guard directly ==="
timeout 5 bash scripts/lib/config_guard.sh || echo "CONFIG GUARD TIMEOUT after 5 seconds"

echo "=== Debug complete ==="
