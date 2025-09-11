#!/bin/bash
# PR-0034 - Narrative Groq Hardening Startup Script

cd /home/mccoy/Projects/StoryMaker/storymaker-bundle-v1.6-unified-full

# Set environment variables (load from .env or environment)
if [ -f .env ]; then
    source .env
fi

# Default model if not set
export GROQ_MODEL=${GROQ_MODEL:-llama-3.3-70b-versatile}

# Check if API key is set
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY not set. Please set it in .env or environment."
    exit 1
fi

echo "🚀 Starting Narrative Service with Groq Hardening (PR-0034)"
echo "Environment:"
echo "  GROQ_API_KEY: ${GROQ_API_KEY:0:10}..."
echo "  GROQ_MODEL: $GROQ_MODEL"
echo

# Test the implementation first
echo "🔧 Testing implementation..."
python3 test_narrative_groq.py
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Fix the issues before starting the service."
    exit 1
fi

echo
echo "✅ Tests passed. Starting service..."

# Start the service
uv run uvicorn services.narrative.main_new:app --host 127.0.0.1 --port 8001 --log-level info