#!/usr/bin/env bash
# install.sh — One-command installation for StoryMaker
# This script handles everything needed to get StoryMaker running

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🚀 StoryMaker Installation Script"
echo "================================="
echo ""

# Check if we're in the right directory
if [ ! -f "Makefile" ] || [ ! -f "scripts/bootstrap.sh" ]; then
    log_error "This script must be run from the StoryMaker root directory"
    log_info "Make sure you're in the folder containing Makefile and scripts/"
    exit 1
fi

# Check prerequisites
log_info "Checking prerequisites..."

# Check for required commands
missing_commands=()

if ! command -v docker >/dev/null 2>&1; then
    missing_commands+=("docker")
fi

if ! command -v curl >/dev/null 2>&1; then
    missing_commands+=("curl")
fi

if ! command -v jq >/dev/null 2>&1; then
    missing_commands+=("jq")
fi

if [ ${#missing_commands[@]} -gt 0 ]; then
    log_error "Missing required commands: ${missing_commands[*]}"
    echo ""
    log_info "Please install the missing commands:"
    for cmd in "${missing_commands[@]}"; do
        case "$cmd" in
            "docker")
                log_info "  Docker: https://docs.docker.com/get-docker/"
                ;;
            "curl")
                log_info "  curl: Usually pre-installed on most systems"
                ;;
            "jq")
                log_info "  jq: https://stedolan.github.io/jq/download/"
                ;;
        esac
    done
    exit 1
fi

log_success "All prerequisites are installed"

# Check if LM Studio is running
log_info "Checking LM Studio..."
if curl -s http://127.0.0.1:1234/v1/models >/dev/null 2>&1; then
    model_count=$(curl -s http://127.0.0.1:1234/v1/models | jq '.data | length' 2>/dev/null || echo "0")
    if [ "$model_count" -gt 0 ]; then
        log_success "LM Studio is running with $model_count models"
    else
        log_warning "LM Studio is running but no models are loaded"
        log_info "Please load a model in LM Studio and try again"
        exit 1
    fi
else
    log_warning "LM Studio is not running"
    echo ""
    log_info "Please:"
    log_info "1. Download LM Studio from https://lmstudio.ai"
    log_info "2. Install and open LM Studio"
    log_info "3. Load a chat model (e.g., qwen/qwen3-4b-2507)"
    log_info "4. Start the server (should show port 1234)"
    log_info "5. Run this script again"
    echo ""
    exit 1
fi

# Make scripts executable
log_info "Setting up scripts..."
chmod +x scripts/*.sh
log_success "Scripts are ready"

# Run the bootstrap
log_info "Starting StoryMaker..."
echo ""
bash scripts/bootstrap.sh start

echo ""
log_success "🎉 StoryMaker installation complete!"
echo ""
log_info "Next steps:"
log_info "1. Open your web browser"
log_info "2. Go to: http://localhost:3000"
log_info "3. Start creating!"
echo ""
log_info "Useful commands:"
log_info "• make status  - Check if everything is running"
log_info "• make stop    - Stop StoryMaker"
log_info "• make restart - Restart StoryMaker"
echo ""
log_info "For help, see:"
log_info "• README.md - Technical documentation"
log_info "• USER_GUIDE.md - For writers and authors"
log_info "• QUICK_START.md - Quick reference"
