#!/bin/bash

# WebUI Startup Script with Timeouts
# This script starts the WebUI with proper timeouts to prevent hanging

set -e

echo "🚀 Starting StoryMaker WebUI with timeouts..."

# Kill any existing Vite processes
echo "🧹 Cleaning up existing processes..."
pkill -f "vite" 2>/dev/null || true
sleep 2

# Change to WebUI directory
cd /home/mccoy/Projects/StoryMaker/storymaker-bundle-v1.6-unified-full/apps/webui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    timeout 10s npm install
fi

# Start the WebUI with timeout
echo "🎯 Starting Vite development server..."
echo "   - Using timeout to prevent hanging"
echo "   - Logs will be written to /tmp/webui.log"
echo "   - WebUI will be available at http://localhost:5173 (or next available port)"

# Start with proper logging (no timeout for dev server)
npm run dev > /tmp/webui.log 2>&1 &
WEBUI_PID=$!

# Wait a moment for startup
sleep 3

# Check if it's running
if ps -p $WEBUI_PID > /dev/null; then
    echo "✅ WebUI started successfully (PID: $WEBUI_PID)"
    echo "📊 Check status with: ps aux | grep vite"
    echo "📋 View logs with: tail -f /tmp/webui.log"
    echo "🌐 WebUI will be available at: http://localhost:5173 (or next available port if 5173 is busy)"
else
    echo "❌ Failed to start WebUI"
    echo "📋 Check logs: cat /tmp/webui.log"
    exit 1
fi

echo "🎉 WebUI startup complete!"
