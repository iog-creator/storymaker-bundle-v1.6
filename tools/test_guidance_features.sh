#!/bin/bash
# Test script for PR-S007 Persistent Guidance features

echo "🧪 Testing StoryMaker Persistent Guidance Features (PR-S007)"
echo "=========================================================="

# Check if API server is running
echo "1. Checking API server..."
if curl -s http://localhost:8700/api/ssot/status > /dev/null 2>&1; then
    echo "   ✅ API server is running on port 8700"
else
    echo "   ❌ API server not running. Start with: node tools/server/api.js"
    exit 1
fi

# Test guidance endpoints
echo "2. Testing guidance computation endpoints..."
endpoints=(
    "/api/lm/models"
    "/api/groq/model" 
    "/api/ssot/status"
    "/api/proofs/summary"
)

for endpoint in "${endpoints[@]}"; do
    response=$(curl -s "http://localhost:8700${endpoint}?cb=${Date.now()}")
    if echo "$response" | grep -q '"ok":true\|"ok":false'; then
        echo "   ✅ $endpoint responding"
    else
        echo "   ⚠️  $endpoint response: $response"
    fi
done

echo ""
echo "🎯 New Features Available:"
echo "   • Persistent Guidance panel (right side) - shows what to do next"
echo "   • Persistent Notifications (bottom of guidance) - saved in localStorage"
echo "   • Legend modal (press H) - explains all tiles and keybindings"
echo "   • Always-visible keybar (bottom) - quick reference"
echo "   • Action buttons in guidance - click to fix issues"
echo ""
echo "🔧 Guidance Features:"
echo "   • Computes next actions from live system state"
echo "   • LM Studio issues → Checklist button"
echo "   • Groq issues → Checklist button"  
echo "   • SSOT drift → Emit rules button"
echo "   • QA guard failures → Open latest proof button"
echo ""
echo "📱 Persistent Notifications:"
echo "   • Survives page refresh/restart"
echo "   • Timestamped entries"
echo "   • Color-coded (green/yellow/red)"
echo "   • Clear button to reset"
echo ""
echo "🚀 To test the full dashboard:"
echo "   1. Start API: node tools/server/api.js"
echo "   2. Start dashboard: make ui.live"
echo "   3. Open: http://localhost:8080/web_dashboard.html"
echo "   4. Look for guidance panel on the right"
echo "   5. Press H for legend"
echo "   6. Click action buttons in guidance"
echo ""
echo "🧪 Test scenarios:"
echo "   • Create drift: echo 'test' >> docs/SSOT/DRIFT_LOG.md"
echo "   • Emit rules: make -s rules.emit"
echo "   • Check guidance updates automatically"
echo "   • Check notifications persist after refresh"
