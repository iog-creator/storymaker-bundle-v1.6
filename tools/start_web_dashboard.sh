#!/bin/bash
# Start the web dashboard with API server

echo "Starting StoryMaker Web Dashboard..."

# Start API server in background
echo "Starting API server on port 8700..."
node tools/server/api.js &
API_PID=$!

# Wait a moment for API server to start
sleep 2

# Start web server for dashboard
echo "Starting web server on port 8080..."
cd tools
python3 -m http.server 8080 &
WEB_PID=$!

echo ""
echo "✅ Web Dashboard is running!"
echo "🌐 Open: http://localhost:8080/web_dashboard.html"
echo "🔧 API: http://localhost:8700"
echo ""
echo "Hotkeys:"
echo "  E - Emit rules"
echo "  P - Open latest proof"
echo "  L - LM Studio checklist"
echo "  G - Groq checklist"
echo "  Q - Quit"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $API_PID $WEB_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
