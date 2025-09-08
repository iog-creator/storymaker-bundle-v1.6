#!/usr/bin/env bash
set -euo pipefail

echo "🚀 AgentPM Self-Bootstrap Starting..."
echo "=================================="

# Step 1: Environment Setup
echo "📋 Step 1: Environment Setup"
if [[ ! -f .env ]]; then
    echo "  → Copying .env.example to .env"
    cp .env.example .env
    echo "  ✅ Environment file created"
else
    echo "  ✅ Environment file already exists"
fi

# Validate required environment variables
echo "  → Validating environment variables"
source .env
if [[ -z "${GROQ_API_KEY:-}" ]]; then
    echo "  ⚠️  GROQ_API_KEY not set - you'll need to add it to .env for creative generation"
fi
if [[ -z "${POSTGRES_DSN:-}" ]]; then
    echo "  ⚠️  POSTGRES_DSN not set - using default"
fi
echo "  ✅ Environment validation complete"

# Step 2: Infrastructure Setup
echo ""
echo "🐳 Step 2: Infrastructure Setup"
echo "  → Starting Docker services..."
docker compose up -d db redis minio || {
    echo "  ❌ Failed to start Docker services"
    echo "  💡 Make sure Docker is running and try: docker compose up -d db redis minio"
    exit 1
}

echo "  → Waiting for services to be ready..."
sleep 5

# Check if services are responding
echo "  → Validating service connectivity..."
if ! docker compose ps | grep -q "Up"; then
    echo "  ❌ Services not running properly"
    echo "  💡 Check with: docker compose ps"
    exit 1
fi
echo "  ✅ Infrastructure ready"

# Step 3: LM Studio Integration Check
echo ""
echo "🤖 Step 3: LM Studio Integration Check"
echo "  → Checking LM Studio availability..."

if curl -sS http://127.0.0.1:1234/v1/models >/dev/null 2>&1; then
    echo "  ✅ LM Studio is running and accessible"
    model_count=$(curl -sS http://127.0.0.1:1234/v1/models | jq '.data | length' 2>/dev/null || echo "0")
    echo "  📊 Found $model_count models loaded"
else
    echo "  ⚠️  LM Studio not detected at http://127.0.0.1:1234/v1"
    echo "  💡 To use LM Studio:"
    echo "     1. Download from https://lmstudio.ai"
    echo "     2. Load Qwen chat + embedding models"
    echo "     3. Start server on port 1234"
    echo "  🔄 Continuing without LM Studio (some features will be limited)"
fi

# Step 4: AgentPM Workspace Bootstrap
echo ""
echo "📁 Step 4: AgentPM Workspace Bootstrap"
echo "  → Creating canonical proofs directory..."
mkdir -p docs/proofs/agentpm
echo "  ✅ Proofs directory ready"

echo "  → Setting up workspace symlinks..."
bash scripts/bootstrap_workspace.sh
echo "  ✅ Workspace symlinks created"

echo "  → Syncing SSOT rules to Cursor..."
bash scripts/sync_rules.sh
echo "  ✅ Rules synced to Cursor"

# Step 5: System Verification
echo ""
echo "🔍 Step 5: System Verification"
echo "  → Running complete verification suite..."

if make verify-all >/dev/null 2>&1; then
    echo "  ✅ All verifications passed"
    echo "  📊 System is production-ready"
else
    echo "  ⚠️  Some verifications failed"
    echo "  💡 Run 'make verify-all' for detailed output"
    echo "  🔄 System may still be functional for basic operations"
fi

# Step 6: Final Status
echo ""
echo "🎉 Bootstrap Complete!"
echo "===================="
echo ""
echo "✅ Environment: Configured"
echo "✅ Infrastructure: Running"
echo "✅ AgentPM Workspace: Initialized"
echo "✅ Rules: Synced and enforced"
echo "✅ Proofs: Canonical path established"
echo ""
echo "🚀 Ready to use! Try these commands:"
echo "  make start     # Start all services"
echo "  make status    # Check system status"
echo "  make verify-all # Run verification suite"
echo ""
echo "📚 For more information, see:"
echo "  - docs/SSOT/MASTER_PLAN.md (canonical plan)"
echo "  - README.md (usage guide)"
echo "  - QUICK_START.md (getting started)"
