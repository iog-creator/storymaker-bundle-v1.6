#!/bin/bash
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

# Start the narrative service
uv run uvicorn services.narrative.main:app --port 8001 --reload