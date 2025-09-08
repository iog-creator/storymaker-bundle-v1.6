#!/bin/bash
# Simple StoryMaker startup script - bypasses AgentPM integration

echo "=== Starting StoryMaker Services ==="

# Set environment variables directly
export POSTGRES_DSN="postgresql://story:story@localhost:5432/storymaker"
export REDIS_URL="redis://localhost:6380"

# Check if dependencies are installed
if ! command -v uvicorn &> /dev/null; then
    echo "Installing dependencies..."
    uv pip install -r requirements-dev.txt
fi

# Start WorldCore service
echo "Starting WorldCore service on port 8000..."
uvicorn services.worldcore.main:app --port 8000 --host 127.0.0.1 &

# Wait a moment for service to start
sleep 3

# Test the service
echo "Testing WorldCore service..."
curl -s http://127.0.0.1:8000/health || echo "Service not responding"

echo "=== StoryMaker startup complete ==="
