#!/usr/bin/env bash
# setup-api-keys.sh - Configure API keys for StoryMaker
# This script helps users set up their real API keys safely

set -euo pipefail

echo "🔑 StoryMaker API Key Setup"
echo "=========================="
echo ""

# Check if .env.local already exists
if [[ -f ".env.local" ]]; then
    echo "⚠️  .env.local already exists. Backing up to .env.local.backup"
    cp .env.local .env.local.backup
fi

# Copy .env.local.example to .env.local
if [[ -f ".env.local.example" ]]; then
    cp .env.local.example .env.local
    echo "✅ Created .env.local from template"
else
    # Create .env.local from .env.local if it doesn't exist
    cp .env .env.local
    echo "✅ Created .env.local from .env"
fi

echo ""
echo "📝 Please edit .env.local and add your real API keys:"
echo "   - GROQ_API_KEY: Get from https://console.groq.com/"
echo "   - Other keys as needed"
echo ""
echo "After editing .env.local, run:"
echo "   make verify-all"
echo ""
echo "🔒 Security Notes:"
echo "   - .env.local is gitignored and will never be committed"
echo "   - .env contains dummy values for git safety"
echo "   - Always run 'make verify-all' to verify system status"
echo ""

# Open editor if available
if command -v code >/dev/null 2>&1; then
    echo "Opening .env.local in VS Code..."
    code .env.local
elif command -v nano >/dev/null 2>&1; then
    echo "Opening .env.local in nano..."
    nano .env.local
else
    echo "Please edit .env.local manually with your preferred editor"
fi


