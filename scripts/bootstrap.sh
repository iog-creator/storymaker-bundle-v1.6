#!/usr/bin/env bash
# bootstrap.sh — One-command setup for StoryMaker
# This script handles everything a new user needs to get started

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables from .env file
if [[ -f .env ]]; then
    set -a
    source .env
    set +a
fi

# Load no-mocks guard after environment is loaded
if [[ -f scripts/lib/no_mocks_guard.sh ]]; then
  # shellcheck disable=SC1091
  source scripts/lib/no_mocks_guard.sh
fi

# Helper functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if port is in use
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Main bootstrap function
bootstrap() {
    log_info "🚀 Starting StoryMaker Bootstrap..."
    
    # Step 1: Check prerequisites
    log_info "Checking prerequisites..."
    
    if ! command_exists docker; then
        log_error "Docker is required but not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists curl; then
        log_error "curl is required but not installed. Please install curl first."
        exit 1
    fi
    
    if ! command_exists jq; then
        log_error "jq is required but not installed. Please install jq first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
    
    # Step 2: Check LM Studio or mock mode
    log_info "Checking AI integration..."

    # Check LM Studio availability
    log_info "Checking LM Studio connection..."

    if ! curl -s http://127.0.0.1:1234/v1/models >/dev/null 2>&1; then
        log_error "LM Studio is not running or not accessible on port 1234"
        log_info "Please:"
        log_info "1. Open LM Studio"
        log_info "2. Load a chat model (e.g., qwen/qwen3-4b-2507)"
        log_info "3. Start the server"
        log_info "5. Run this script again"
        exit 1
    fi

    # Check if models are loaded
    model_count=$(curl -s http://127.0.0.1:1234/v1/models | jq '.data | length' 2>/dev/null || echo "0")
    if [ "$model_count" -eq 0 ]; then
        log_error "No models loaded in LM Studio"
        log_info "Please load at least one chat model in LM Studio"
        exit 1
    fi

    log_success "LM Studio is running with $model_count models"
    
    # Step 3: Setup database
    log_info "Setting up database..."
    
    if ! docker compose ps db | grep -q "Up"; then
        log_info "Starting database..."
        docker compose up -d db redis minio
        sleep 5
    fi
    
    log_success "Database is running"
    
    # Step 4: Run migrations
    log_info "Running database migrations..."
    
    if command_exists uv; then
        uv venv --clear && uv pip install psycopg[binary]
        POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker uv run python scripts/db_migrate.py sql/001_init.sql
    else
        log_warning "uv not found, using pip"
        pip install psycopg[binary]
        POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker python scripts/db_migrate.py sql/001_init.sql
    fi
    
    log_success "Database migrations completed"
    
    # Step 5: Start services
    log_info "Starting StoryMaker services..."
    
    # Kill any existing services on our ports
    for port in 8000 8001 8002 8003 8004; do
        if port_in_use "$port"; then
            log_info "Stopping existing service on port $port"
            bash scripts/kill_by_port.sh "$port" || true
        fi
    done
    
    # Start services
    log_info "Starting worldcore service..."
    POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker REDIS_URL=redis://localhost:6379 bash scripts/start_service.sh worldcore 8000 "uv run uvicorn services.worldcore.main:app --port 8000 --reload" &
    
    log_info "Starting narrative service..."
    POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker REDIS_URL=redis://localhost:6379 bash scripts/start_service.sh narrative 8001 "uv run uvicorn services.narrative.main:app --port 8001 --reload" &
    
    log_info "Starting screenplay service..."
    POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker REDIS_URL=redis://localhost:6379 bash scripts/start_service.sh screenplay 8002 "uv run uvicorn services.screenplay.main:app --port 8002 --reload" &
    
    log_info "Starting media service..."
    POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker REDIS_URL=redis://localhost:6379 bash scripts/start_service.sh media 8003 "uv run uvicorn services.media.main:app --port 8003 --reload" &
    
    log_info "Starting interact service..."
    POSTGRES_DSN=postgresql://story:story@localhost:5432/storymaker REDIS_URL=redis://localhost:6379 bash scripts/start_service.sh interact 8004 "uv run uvicorn services.interact.main:app --port 8004 --reload" &
    
    # Wait for services to start
    log_info "Waiting for services to start..."
    sleep 10
    
    # Step 6: Verify services
    log_info "Verifying services..."
    
    failed_services=()
    for port in 8000 8001 8002 8003 8004; do
        if curl -s http://localhost:$port/health >/dev/null 2>&1; then
            log_success "Service on port $port is healthy"
        else
            log_error "Service on port $port is not responding"
            failed_services+=("$port")
        fi
    done
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_error "Some services failed to start: ${failed_services[*]}"
        log_info "Check the logs with: docker compose logs"
        exit 1
    fi
    
    # Step 7: Final verification
    log_info "Running final verification..."

    if curl -s http://127.0.0.1:1234/v1/models | jq -e '.data | length > 0' >/dev/null 2>&1; then
        log_success "LM Studio integration verified"
    else
        log_error "LM Studio integration failed"
        exit 1
    fi
    
    # Success!
    echo ""
    log_success "🎉 StoryMaker is ready!"
    echo ""
    log_info "Access points:"
    log_info "• Web UI: http://localhost:3000"
    log_info "• API: http://localhost:8000-8004"
    echo ""
    log_info "Useful commands:"
    log_info "• make status    - Check service status"
    log_info "• make restart   - Restart all services"
    log_info "• make stop      - Stop all services"
    log_info "• make logs      - View service logs"
    echo ""
}

# Handle command line arguments
case "${1:-bootstrap}" in
    "bootstrap"|"start")
        bootstrap
        ;;
    "stop")
        log_info "Stopping StoryMaker services..."
        for port in 8000 8001 8002 8003 8004; do
            bash scripts/kill_by_port.sh "$port" || true
        done
        docker compose down
        log_success "All services stopped"
        ;;
    "status")
        log_info "Checking StoryMaker status..."
        echo ""
        echo "LM Studio:"
        if curl -s http://127.0.0.1:1234/v1/models >/dev/null 2>&1; then
            model_count=$(curl -s http://127.0.0.1:1234/v1/models | jq '.data | length' 2>/dev/null || echo "0")
            log_success "Running with $model_count models"
        else
            log_error "Not running"
        fi
        echo ""
        echo "Database:"
        if docker compose ps db | grep -q "Up"; then
            log_success "Running"
        else
            log_error "Not running"
        fi
        echo ""
        echo "Services:"
        for port in 8000 8001 8002 8003 8004; do
            if curl -s http://localhost:$port/health >/dev/null 2>&1; then
                log_success "Port $port: Healthy"
            else
                log_error "Port $port: Not responding"
            fi
        done
        ;;
    "help")
        echo "StoryMaker Bootstrap Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start StoryMaker (default)"
        echo "  stop     - Stop all services"
        echo "  status   - Check service status"
        echo "  help     - Show this help"
        echo ""
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
