#!/bin/bash

# Test Environment Management Script for Story Teller API
# Usage: ./test-setup.sh [command]

set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    source .env
fi

# Set default test port values if not defined in .env
TEST_MYSQL_PORT=${TEST_MYSQL_HOST_PORT:-3307}
TEST_REDIS_PORT=${TEST_REDIS_HOST_PORT:-6380}

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
    echo "  init                   Start full test environment (MySQL + Redis + Celery worker)"
    echo "  init-integration       Start MySQL test database only"
    echo "  stop                   Stop test environment"
    echo "  clean                  Stop test environment (no persistent data to remove)"
    echo "  test                   Run all tests (unit + integration + e2e)"
    echo "  test-unit              Run fast unit tests"
    echo "  test-integration       Run integration tests"
    echo "  test-e2e               Run Celery integration tests"
    echo "  status                 Show test environment status"
    echo "  logs                   Show test environment logs"
    echo "  help                   Show this help message"
    echo ""
    echo "Suggested workflow:"
    echo "  $0 init-full           # Basic MySQL test DB"
    echo "  $0 test                # Run Celery integration tests"
    echo "  $0 stop                # Stop test environment"
    echo "  $0 clean               # Clean up test environment"
    echo ""
    echo "Test databases run on different ports:"
    echo "  - MySQL: localhost:$TEST_MYSQL_PORT (vs ${MYSQL_HOST_PORT:-3306} for dev)"
    echo "  - Redis: localhost:$TEST_REDIS_PORT (vs ${REDIS_HOST_PORT:-6379} for dev)"
}

start_integration() {
    print_status "Starting MySQL test database..."
    docker-compose -f "$TEST_COMPOSE_FILE" up -d mysql-test
    
    print_status "Waiting for MySQL test database to be ready..."
    for i in {1..30}; do
        if docker-compose -f "$TEST_COMPOSE_FILE" exec mysql-test mysqladmin ping -h "localhost" --silent 2>/dev/null; then
            print_success "MySQL test database is ready!"
            echo ""
            echo "Test Database Info:"
            echo "  Host: localhost:$TEST_MYSQL_PORT"
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

run_unit_tests() {
    print_status "Running fast unit tests..."
    
    # Fast tests use SQLite and don't require any infrastructure
    poetry run pytest -m "unit" -v
}

run_integration_tests() {
    print_status "Running tests with MySQL test database..."
    
    # Check if MySQL test is running
    if ! docker-compose -f "$TEST_COMPOSE_FILE" ps mysql-test | grep -q "Up"; then
        print_warning "MySQL test database not running. Starting it..."
        start_integration
    fi
    
    export TESTING="true"
    export TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:$TEST_MYSQL_PORT/storyteller_test"
    
    poetry run pytest tests/ -v -m "integration"
}

run_e2e_tests() {
    print_status "Running e2e tests..."
    
    # Check if Celery environment is running (Redis + Worker)
    if ! docker-compose -f "$TEST_COMPOSE_FILE" ps redis-test | grep -q "Up" || \
       ! docker-compose -f "$TEST_COMPOSE_FILE" ps worker-test | grep -q "Up"; then
        print_warning "Test environment not fully running. Starting it..."
        start_full
        
        # Wait for worker to be ready
        print_status "Waiting for Celery worker to be ready..."
        sleep 15
    fi
    
    export TESTING="true"
    export TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:$TEST_MYSQL_PORT/storyteller_test"
    export CELERY_BROKER_URL="redis://localhost:$TEST_REDIS_PORT/0"
    export CELERY_RESULT_BACKEND="redis://localhost:$TEST_REDIS_PORT/1"
    
    poetry run pytest -m e2e -v
}

run_all_tests() {
    print_status "Running all tests..."
    
    # Check if Celery environment is running (Redis + Worker)
    if ! docker-compose -f "$TEST_COMPOSE_FILE" ps redis-test | grep -q "Up" || \
       ! docker-compose -f "$TEST_COMPOSE_FILE" ps worker-test | grep -q "Up"; then
        print_warning "Test environment not fully running. Starting it..."
        start_full
        
        # Wait for worker to be ready
        print_status "Waiting for Celery worker to be ready..."
        sleep 15
    fi
    
    export TESTING="true"
    export TEST_DATABASE_URL="mysql+mysqlconnector://test_user:test_pass@localhost:$TEST_MYSQL_PORT/storyteller_test"
    export CELERY_BROKER_URL="redis://localhost:$TEST_REDIS_PORT/0"
    export CELERY_RESULT_BACKEND="redis://localhost:$TEST_REDIS_PORT/1"
    
    poetry run pytest -v
}

show_status() {
    print_status "Test environment status:"
    docker-compose -f "$TEST_COMPOSE_FILE" ps
    echo ""
    
    # Check which services are running
    if docker-compose -f "$TEST_COMPOSE_FILE" ps mysql-test | grep -q "Up"; then
        print_success "✅ MySQL test database: Running (port $TEST_MYSQL_PORT)"
    else
        print_warning "❌ MySQL test database: Not running"
    fi
    
    if docker-compose -f "$TEST_COMPOSE_FILE" ps redis-test 2>/dev/null | grep -q "Up"; then
        print_success "✅ Redis test database: Running (port $TEST_REDIS_PORT)"
    else
        print_warning "❌ Redis test database: Not running"
    fi
    
    if docker-compose -f "$TEST_COMPOSE_FILE" ps worker-test 2>/dev/null | grep -q "Up"; then
        print_success "✅ Celery worker test: Running"
    else
        print_warning "❌ Celery worker test: Not running"
    fi
}

show_logs() {
    print_status "Showing test environment logs..."
    docker-compose -f "$TEST_COMPOSE_FILE" logs -f
}

# Main script logic
case "${1:-help}" in
    init-integration)
        start_integration
        ;;
    init)
        start_full
        ;;
    stop)
        stop_environment
        ;;
    clean)
        clean_environment
        ;;
    test)
        run_all_tests
        ;;
    test-unit)
        run_unit_tests
        ;;
    test-integration)
        run_integration_tests
        ;;
    test-e2e)
        run_e2e_tests
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
