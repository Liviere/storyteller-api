#!/bin/bash

# Celery Management Script for Story Teller API
# Usage: ./celery-setup.sh [start|stop|restart|worker|flower|status|logs]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.celery.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Redis is running
check_redis() {
    if docker-compose -f "$COMPOSE_FILE" ps redis | grep -q "Up"; then
        return 0
    else
        return 1
    fi
}

# Function to start Redis
start_redis() {
    print_status "Starting Redis for Celery..."
    docker-compose -f "$COMPOSE_FILE" up -d redis
    
    # Wait for Redis to be ready
    print_status "Waiting for Redis to be ready..."
    for i in {1..30}; do
        if check_redis && docker-compose -f "$COMPOSE_FILE" exec redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis is ready!"
            return 0
        fi
        sleep 1
    done
    
    print_error "Redis failed to start properly"
    return 1
}

# Function to stop Redis
stop_redis() {
    print_status "Stopping Redis..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "Redis stopped"
}

# Function to start Celery worker
start_worker() {
    if ! check_redis; then
        print_warning "Redis is not running. Starting Redis first..."
        start_redis
    fi
    
    print_status "Starting Celery worker..."
    cd "$PROJECT_DIR"
    
    # Export environment variables
    export CELERY_BROKER_URL="redis://localhost:6379/0"
    export CELERY_RESULT_BACKEND="redis://localhost:6379/1"
    
    # Start worker with appropriate settings
    poetry run celery -A app.celery_app.celery:celery_app worker \
        --loglevel=info \
        --concurrency=4 \
        --queues=default,stories,llm \
        --hostname=worker@%h \
        --max-tasks-per-child=100 \
        --time-limit=300 \
        --soft-time-limit=240
}

# Function to start Flower monitoring
start_flower() {
    if ! check_redis; then
        print_warning "Redis is not running. Starting Redis first..."
        start_redis
    fi
    
    print_status "Starting Flower monitoring on http://localhost:5555"
    cd "$PROJECT_DIR"
    
    # Export environment variables
    export CELERY_BROKER_URL="redis://localhost:6379/0"
    export CELERY_RESULT_BACKEND="redis://localhost:6379/1"
    
    # Start Flower
    poetry run celery -A app.celery_app.celery:celery_app flower \
        --port=5555 \
        --broker_api=redis://localhost:6379/0
}

# Function to show Celery status
show_status() {
    print_status "Checking Celery system status..."
    
    # Check Redis
    if check_redis; then
        print_success "Redis: Running"
    else
        print_error "Redis: Not running"
    fi
    
    # Check workers
    cd "$PROJECT_DIR"
    export CELERY_BROKER_URL="redis://localhost:6379/0"
    export CELERY_RESULT_BACKEND="redis://localhost:6379/1"
    
    if command -v poetry >/dev/null 2>&1; then
        print_status "Active workers:"
        poetry run celery -A app.celery_app.celery:celery_app inspect active 2>/dev/null || print_warning "No workers found or Celery not accessible"
        
        print_status "Registered tasks:"
        poetry run celery -A app.celery_app.celery:celery_app inspect registered 2>/dev/null || print_warning "Could not fetch registered tasks"
    else
        print_warning "Poetry not found. Install poetry to check worker status."
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing Redis logs..."
    docker-compose -f "$COMPOSE_FILE" logs -f redis
}

# Main script logic
case "${1:-help}" in
    start)
        start_redis
        ;;
    stop)
        stop_redis
        ;;
    restart)
        stop_redis
        sleep 2
        start_redis
        ;;
    worker)
        start_worker
        ;;
    flower)
        start_flower
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|*)
        echo "Celery Management Script"
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start      Start Redis for Celery"
        echo "  stop       Stop Redis"
        echo "  restart    Restart Redis"
        echo "  worker     Start Celery worker (requires Redis to be running)"
        echo "  flower     Start Flower monitoring interface"
        echo "  status     Show status of Redis and workers"
        echo "  logs       Show Redis logs"
        echo "  help       Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start           # Start Redis"
        echo "  $0 worker          # Start worker (in foreground)"
        echo "  $0 flower          # Start Flower monitoring"
        echo ""
        echo "For production, run worker and flower in separate terminals or as services."
        ;;
esac
