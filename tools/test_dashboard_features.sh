#!/bin/bash
# Test script for interactive dashboard features

echo "🧪 Testing StoryMaker Interactive Dashboard Features"
echo "=================================================="

# Check if API server is running
echo "1. Checking API server..."
if curl -s http://localhost:8700/api/ssot/status > /dev/null 2>&1; then
    echo "   ✅ API server is running on port 8700"
else
    echo "   ❌ API server not running. Start with: node tools/server/api.js"
    exit 1
fi

# Test autosync endpoint
echo "2. Testing autosync endpoint..."
response=$(curl -s -X POST http://localhost:8700/api/actions/autosync)
if echo "$response" | grep -q '"ok":true'; then
    echo "   ✅ Autosync endpoint working"
else
    echo "   ⚠️  Autosync endpoint response: $response"
fi

# Test rules.emit endpoint
echo "3. Testing rules.emit endpoint..."
response=$(curl -s -X POST http://localhost:8700/api/actions/rules.emit)
if echo "$response" | grep -q '"ok":true'; then
    echo "   ✅ Rules.emit endpoint working"
else
    echo "   ⚠️  Rules.emit endpoint response: $response"
fi

# Test proofs endpoint
echo "4. Testing proofs endpoint..."
response=$(curl -s http://localhost:8700/api/proofs/summary)
if echo "$response" | grep -q '"ok":true'; then
    echo "   ✅ Proofs endpoint working"
else
    echo "   ⚠️  Proofs endpoint response: $response"
fi

# Test SSOT status endpoint
echo "5. Testing SSOT status endpoint..."
response=$(curl -s http://localhost:8700/api/ssot/status)
if echo "$response" | grep -q '"ok":true'; then
    echo "   ✅ SSOT status endpoint working"
else
    echo "   ⚠️  SSOT status endpoint response: $response"
fi

echo ""
echo "🎯 Interactive Features Available:"
echo "   • Click 'SSOT Rules (.mdc)' tile → Opens details modal"
echo "   • Click 'Envelopes & Proofs' tile → Opens latest proof JSON"
echo "   • Click 'Docs Autosync' tile → Runs autosync action"
echo "   • Smart notifications for drift, out-of-date docs, QA failures"
echo "   • Toast notifications for all actions"
echo ""
echo "🚀 To test the full dashboard:"
echo "   1. Start API: node tools/server/api.js"
echo "   2. Start dashboard: make ui.live"
echo "   3. Open: http://localhost:8080/web_dashboard.html"
echo "   4. Click tiles and watch for toasts/modals!"
