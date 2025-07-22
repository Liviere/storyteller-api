#!/bin/bash

# Test Environment Management Script for Story Teller API
# Usage: ./test-setup.sh [command]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_COMPOSE_FILE="$PROJECT_DIR/docker-compose.test.yml"

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

show_help() {
    echo "Test Environment Management Script"
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start        Start MySQL test database only"
    echo "  celery       Start MySQL + Redis for Celery integration tests"
    echo "  full         Start full test environment"
    echo "  stop         Stop test environment"
    echo "  clean        Stop test environment (no persistent data to remove)"
    echo "  test         Run tests with MySQL"
    echo "  test-celery  Run Celery integration tests"
    echo "  status       Show test environment status"
    echo "  logs         Show test environment logs"
    echo "  help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Basic MySQL test DB"
    echo "  $0 celery                   # + Redis for Celery tests"
    echo "  $0 test-celery              # Run Celery integration tests"
    echo ""
    echo "Test databases run on different ports:"
    echo "  - MySQL: localhost:3307 (vs 3306 for dev)"
    echo "  - Redis: localhost:6380 (vs 6379 for dev)"
}

start_basic() {
    print_status "Starting MySQL test database..."
    docker-compose -f "$TEST_COMPOSE_FILE" up -d mysql-test
    
    print_status "Waiting for MySQL test database to be ready..."
    for i in {1..30}; do
        if docker-compose -f "$TEST_COMPOSE_FILE" exec mysql-test mysqladmin ping -h "localhost" --silent 2>/dev/null; then
            print_success "MySQL test database is ready!"
            echo ""
            echo "Test Database Info:"
            echo "  Host: localhost:3307"
            echo "  Database: storyteller_test"
            echo "  User: test_user"
            echo "  Password: test_pass"
            echo ""
            echo "Run tests with: $0 test"
            return 0
        fi
        sleep 2
    done
    
    print_error "MySQL test database failed to start"
    return 1
}

start_with_celery() {
    print_status "Starting test environment with Celery..."
    docker-compose -f "$TEST_COMPOSE_FILE" --profile celery up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_success "Test environment with Celery ready!"
    echo ""
    echo "Test Environment Info:"
    echo "  MySQL: localhost:3307"
    echo "  Redis: localhost:6380"
    echo ""
    echo "Run Celery tests with: $0 test-celery"
}

start_full() {
    print_status "Starting full test environment..."
    docker-compose -f "$TEST_COMPOSE_FILE" --profile full up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_success "Full test environment ready!"
}

stop_environment() {
    print_status "Stopping test environment..."
    docker-compose -f "$TEST_COMPOSE_FILE" down
    print_success "Test environment stopped."
}

clean_environment() {
    print_status "Stopping test environment and removing containers..."
    docker-compose -f "$TEST_COMPOSE_FILE" down
    print_success "Test environment cleaned (no persistent data to remove)."
}

run_tests() {
    print_status "Running tests with MySQL test database..."
    
    # Check if MySQL test is running
    if ! docker-compose -f "$TEST_COMPOSE_FILE" ps mysql-test | grep -q "Up"; then
        print_warning "MySQL test database not running. Starting it..."
        start_basic
    fi
    
    export TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:3307/storyteller_test"
    poetry run pytest tests/ -v
}

run_celery_tests() {
    print_status "Running Celery integration tests..."
    
    # Check if Redis test is running
    if ! docker-compose -f "$TEST_COMPOSE_FILE" ps redis-test | grep -q "Up"; then
        print_warning "Test environment with Celery not running. Starting it..."
        start_with_celery
    fi
    
    export TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:3307/storyteller_test"
    export CELERY_BROKER_URL="redis://localhost:6380/0"
    export CELERY_RESULT_BACKEND="redis://localhost:6380/1"
    
    poetry run pytest -m celery_integration -v
}

show_status() {
    print_status "Test environment status:"
    docker-compose -f "$TEST_COMPOSE_FILE" ps
    echo ""
    
    # Check which services are running
    if docker-compose -f "$TEST_COMPOSE_FILE" ps mysql-test | grep -q "Up"; then
        print_success "✅ MySQL test database: Running (port 3307)"
    else
        print_warning "❌ MySQL test database: Not running"
    fi
    
    if docker-compose -f "$TEST_COMPOSE_FILE" ps redis-test 2>/dev/null | grep -q "Up"; then
        print_success "✅ Redis test database: Running (port 6380)"
    else
        print_warning "❌ Redis test database: Not running"
    fi
}

show_logs() {
    print_status "Showing test environment logs..."
    docker-compose -f "$TEST_COMPOSE_FILE" logs -f
}

# Main script logic
case "${1:-help}" in
    start)
        start_basic
        ;;
    celery)
        start_with_celery
        ;;
    full)
        start_full
        ;;
    stop)
        stop_environment
        ;;
    clean)
        clean_environment
        ;;
    test)
        run_tests
        ;;
    test-celery)
        run_celery_tests
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|*)
        show_help
        ;;
esac
