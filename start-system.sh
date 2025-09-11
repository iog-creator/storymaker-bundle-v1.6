#!/bin/bash
# StoryMaker System Startup Script
# Starts all services needed for the complete system

set -e

echo "🚀 Starting StoryMaker System..."

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f mock_story_services 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 2

# Start mock services
echo "🔧 Starting mock services..."
cd /home/mccoy/Projects/StoryMaker/storymaker-bundle-v1.6-unified-full
TROPE_MAX=10 PYTHONPATH=. python3 scripts/mock_story_services.py &
MOCK_PID=$!
echo "Mock services PID: $MOCK_PID"

# Wait for mock services to be ready
echo "⏳ Waiting for mock services..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:8900/health >/dev/null 2>&1; then
        echo "✅ Mock services ready"
        break
    fi
    echo "   Attempt $i/10..."
    sleep 2
done

# Start web UI
echo "🌐 Starting web UI..."
cd apps/webui
npm run dev &
WEB_PID=$!
echo "Web UI PID: $WEB_PID"

# Wait for web UI to be ready
echo "⏳ Waiting for web UI..."
for i in {1..10}; do
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo "✅ Web UI ready at http://localhost:5173"
        break
    fi
    echo "   Attempt $i/10..."
    sleep 2
done

echo ""
echo "🎉 StoryMaker System is running!"
echo "   Web UI: http://localhost:5173"
echo "   Mock Services: http://127.0.0.1:8900"
echo "   Mermaid Diagram: Integrated in the UI"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running and handle cleanup
trap 'echo "🛑 Stopping services..."; kill $MOCK_PID $WEB_PID 2>/dev/null || true; exit 0' INT
wait
