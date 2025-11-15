#!/bin/bash

# System Status Check Script with Timeouts
# This script checks all StoryMaker services with proper timeouts

set -e

echo "🔍 StoryMaker System Status Check"
echo "=================================="

# Check WebUI
echo "🌐 WebUI Status:"
if ss -tlnp | grep ":5173 " > /dev/null; then
    echo "   ✅ WebUI running on port 5173"
    echo "   🔗 URL: http://localhost:5173"
    
    # Test WebUI with timeout
    if curl -s --max-time 2 "http://localhost:5173/" > /dev/null 2>&1; then
        echo "   ✅ WebUI responding to requests"
    else
        echo "   ⚠️  WebUI not responding to requests"
    fi
else
    echo "   ❌ WebUI not running on port 5173"
fi

echo ""

# Check Backend Services
echo "🔧 Backend Services Status:"
SERVICES=("8000:worldcore" "8001:narrative" "8002:screenplay" "8003:media" "8004:interact")

for service in "${SERVICES[@]}"; do
    PORT=$(echo $service | cut -d: -f1)
    NAME=$(echo $service | cut -d: -f2)
    
    if ss -tlnp | grep ":$PORT " > /dev/null; then
        echo "   ✅ $NAME service running on port $PORT"
        
        # Test service with timeout
        if curl -s --max-time 2 "http://localhost:$PORT/docs" > /dev/null 2>&1; then
            echo "      ✅ $NAME responding to requests"
        else
            echo "      ⚠️  $NAME not responding to requests"
        fi
    else
        echo "   ❌ $NAME service not running on port $PORT"
    fi
done

echo ""

# Check LM Studio
echo "🤖 LM Studio Status:"
if ps aux | grep -i lmstudio | grep -v grep > /dev/null; then
    echo "   ✅ LM Studio process running"
    
    # Test LM Studio API with timeout
    if curl -s --max-time 2 "http://127.0.0.1:1234/v1/models" > /dev/null 2>&1; then
        echo "   ✅ LM Studio API responding"
    else
        echo "   ⚠️  LM Studio API not responding"
    fi
else
    echo "   ❌ LM Studio not running"
fi

echo ""

# Check Database
echo "🗄️  Database Status:"
if ss -tlnp | grep ":5432 " > /dev/null; then
    echo "   ✅ PostgreSQL running on port 5432"
else
    echo "   ❌ PostgreSQL not running on port 5432"
fi

echo ""
echo "🎯 Quick Access URLs:"
echo "   WebUI: http://localhost:5173"
echo "   WorldCore API: http://localhost:8000/docs"
echo "   Narrative API: http://localhost:8001/docs"
echo "   Screenplay API: http://localhost:8002/docs"
echo "   Media API: http://localhost:8003/docs"
echo "   Interact API: http://localhost:8004/docs"

echo ""
echo "📋 Useful Commands:"
echo "   View WebUI logs: tail -f /tmp/webui.log"
echo "   Check processes: ps aux | grep -E '(vite|uvicorn|lmstudio)'"
echo "   Restart WebUI: ./start_webui_with_timeout.sh"
echo "   Check ports: ss -tlnp | grep -E ':(5173|5174|5175|8000|8001|8002|8003|8004)'"

echo ""
echo "✅ Status check complete!"
