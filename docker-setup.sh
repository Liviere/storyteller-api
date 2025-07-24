#!/bin/bash

# Story Teller Docker Setup Script
# This script helps set up and run the application with MySQL using Docker

set -e

echo "=== Story Teller Docker Setup ==="

# Load environment variables if .env exists
if [ -f .env ]; then
    source .env
fi

# Set default port values if not defined in .env
APP_PORT=${APP_HOST_PORT:-8080}
MYSQL_PORT=${MYSQL_HOST_PORT:-3306}
PHPMYADMIN_PORT=${PHPMYADMIN_HOST_PORT:-8081}
REDIS_PORT=${REDIS_HOST_PORT:-6379}
FLOWER_PORT=${FLOWER_HOST_PORT:-5555}
REDIS_UI_PORT=${REDIS_UI_HOST_PORT:-8082}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is available
check_port_available() {
    local port=$1
    if command -v nc >/dev/null 2>&1; then
        ! nc -z localhost $port >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        ! netstat -tuln 2>/dev/null | grep -q ":$port "
    else
        # Fallback: assume port is available
        return 0
    fi
}

# Function to find an available port starting from a base port
find_available_port() {
    local base_port=$1
    local port=$base_port
    while ! check_port_available $port; do
        port=$((port + 1))
    done
    echo $port
}

# Function to validate port configuration
validate_ports() {
    local ports_to_check=(
        "APP_PORT:$APP_PORT"
        "MYSQL_PORT:$MYSQL_PORT" 
        "PHPMYADMIN_PORT:$PHPMYADMIN_PORT"
        "REDIS_PORT:$REDIS_PORT"
        "FLOWER_PORT:$FLOWER_PORT"
        "REDIS_UI_PORT:$REDIS_UI_PORT"
    )
    
    local conflicts=()
    for port_info in "${ports_to_check[@]}"; do
        local service_name="${port_info%%:*}"
        local port="${port_info##*:}"
        if ! check_port_available $port; then
            conflicts+=("$service_name:$port")
        fi
    done
    
    if [ ${#conflicts[@]} -gt 0 ]; then
        print_warning "Port conflicts detected:"
        for conflict in "${conflicts[@]}"; do
            local service="${conflict%%:*}"
            local port="${conflict##*:}"
            echo "  - $service (port $port) is already in use"
        done
        echo ""
        print_warning "You can either:"
        echo "  1. Stop services using these ports"
        echo "  2. Edit .env file to use different ports"
        echo "  3. Use auto-port-assignment with: $0 start --auto-ports"
        return 1
    fi
    return 0
}

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_status ".env file created. Please review and modify if needed."
fi

# Create logs directory
mkdir -p logs

# Function to show help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start        Start default services (MySQL only)"
    echo "  infrastructure Start infrastructure only (MySQL + Redis + Tools) - for local development"
    echo "  tools        Start services with development tools (phpMyAdmin + Redis UI)"
    echo "  celery       Start Celery infrastructure (MySQL + Redis + Flower) - for local development"
    echo "  dev          Start development infrastructure (MySQL + Redis + monitoring) - run API/worker locally"
    echo "  full         Start all infrastructure services (phpMyAdmin + Redis UI + Flower)"
    echo "  production   Start production services (App + Worker)"
    echo "  all          Start all services (complete setup)"
    echo "  stop         Stop all services"
    echo "  restart      Restart all services"
    echo "  build        Build application image"
    echo "  logs         Show application logs"
    echo "  mysql        Connect to MySQL database"
    echo "  migrate      Migrate data from SQLite to MySQL"
    echo "  clean        Stop services and remove all data"
    echo "  status       Show status of all services"
    echo "  help         Show this help message"
    echo ""
    echo "Profile Examples:"
    echo "  $0 start                    # Default: MySQL only (matches docker-compose up -d)"
    echo "  $0 infrastructure           # Infrastructure only: MySQL + Redis + Tools"
    echo "  $0 celery                   # Celery infrastructure: MySQL + Redis + Flower"
    echo "  $0 dev                      # Development: Infrastructure + monitoring (recommended)"
    echo "  $0 full                     # All infrastructure: phpMyAdmin + Redis UI + Flower"
    echo "  $0 production               # Production: App + Worker (matches --profile production)"
    echo "  $0 all                      # Everything: Production + Tools + Monitoring"
    echo ""
    echo "Port Configuration:"
    echo "  Ports are configured via .env file. Current settings:"
    echo "  - API: $APP_PORT"
    echo "  - MySQL: $MYSQL_PORT" 
    echo "  - phpMyAdmin: $PHPMYADMIN_PORT"
    echo "  - Redis: $REDIS_PORT"
    echo "  - Flower: $FLOWER_PORT"
    echo "  - Redis UI: $REDIS_UI_PORT"
    echo ""
    echo "Development workflow:"
    echo "  1. Run: $0 dev              # Start infrastructure"
    echo "  2. Run API locally: poetry run uvicorn main:app --reload --port $APP_PORT"
    echo "  3. Run worker locally: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
    echo ""
    echo "Available at:"
    echo "  - API: http://localhost:$APP_PORT (local or container)"
    echo "  - API Docs: http://localhost:$APP_PORT/docs"
    echo "  - phpMyAdmin: http://localhost:$PHPMYADMIN_PORT (with dev/infrastructure/production)"
    echo "  - Flower: http://localhost:$FLOWER_PORT (with dev/production)"
    echo "  - Redis UI: http://localhost:$REDIS_UI_PORT (with dev/infrastructure/production)"
}

# Function to start basic services
start_services() {
    print_status "Starting default services (MySQL only)..."
    
    # Validate ports before starting
    if ! validate_ports; then
        print_error "Port validation failed. Please resolve conflicts before starting services."
        return 1
    fi
    
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "Default services started successfully!"
        echo ""
        echo "Services running:"
        echo "  - MySQL database on port $MYSQL_PORT"
        echo ""
        echo "To add API, run: docker-compose up -d --profile production"
        echo "To add tools, run: docker-compose up -d --profile tools"
        echo "To view logs: $0 logs"
        echo "To stop services: $0 stop"
    else
        print_error "Failed to start services. Check logs with: docker-compose logs"
    fi
}

# Function to start services with Celery infrastructure only
start_infrastructure() {
    print_status "Starting infrastructure only (MySQL + Redis + Tools)..."
    docker-compose --profile infrastructure up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Infrastructure started successfully!"
    echo ""
    echo "Infrastructure URLs:"
    echo "  - phpMyAdmin: http://localhost:$PHPMYADMIN_PORT"
    echo "  - Redis UI: http://localhost:$REDIS_UI_PORT"
    echo ""
    echo "Now you can run locally:"
    echo "  - API: poetry run uvicorn main:app --reload --port $APP_PORT"
    echo "  - Worker: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
}

# Function to start services with development tools
start_with_tools() {
    print_status "Starting services with development tools (MySQL + Redis + Tools)..."
    docker-compose --profile tools up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Services with tools started successfully!"
    echo ""
    echo "Infrastructure URLs:"
    echo "  - phpMyAdmin: http://localhost:$PHPMYADMIN_PORT"
    echo "  - Redis UI: http://localhost:$REDIS_UI_PORT"
    echo ""
    echo "Now you can run locally:"
    echo "  - API: poetry run uvicorn main:app --reload --port $APP_PORT"
    echo "  - Worker: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
}

# Function to start development environment  
start_development() {
    print_status "Starting development infrastructure (MySQL + Redis + monitoring)..."
    docker-compose --profile tools --profile monitoring up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Development infrastructure started successfully!"
    echo ""
    echo "Infrastructure URLs:"
    echo "  - phpMyAdmin: http://localhost:$PHPMYADMIN_PORT"
    echo "  - Redis UI: http://localhost:$REDIS_UI_PORT"
    echo "  - Flower monitoring: http://localhost:$FLOWER_PORT"
    echo ""
    echo "Now run your applications locally:"
    echo "  - API: poetry run uvicorn main:app --reload --port $APP_PORT"
    echo "  - Worker: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
    echo ""
    echo "This gives you full development flexibility with infrastructure support!"
}

# Function to start Celery infrastructure
start_celery() {
    print_status "Starting Celery infrastructure (MySQL + Redis + Flower)..."
    docker-compose --profile celery up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Celery infrastructure started successfully!"
    echo ""
    echo "Infrastructure URLs:"
    echo "  - Flower monitoring: http://localhost:$FLOWER_PORT"
    echo ""
    echo "Now run your applications locally:"
    echo "  - API: poetry run uvicorn main:app --reload --port $APP_PORT"
    echo "  - Worker: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
}

# Function to start all infrastructure services
start_full() {
    print_status "Starting all infrastructure services (full profile)..."
    docker-compose --profile full up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "All infrastructure services started successfully!"
    echo ""
    echo "Infrastructure URLs:"
    echo "  - phpMyAdmin: http://localhost:$PHPMYADMIN_PORT"
    echo "  - Redis UI: http://localhost:$REDIS_UI_PORT"
    echo "  - Flower monitoring: http://localhost:$FLOWER_PORT"
    echo ""
    echo "Now run your applications locally:"
    echo "  - API: poetry run uvicorn main:app --reload --port $APP_PORT"
    echo "  - Worker: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
}

# Function to start production services
start_production() {
    print_status "Starting production services (App + Worker)..."
    docker-compose --profile production up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    print_status "Production services started successfully!"
    echo ""
    echo "Application URLs:"
    echo "  - API: http://localhost:$APP_PORT"
    echo "  - API Docs: http://localhost:$APP_PORT/docs"
    echo ""
    echo "Production setup running:"
    echo "  - MySQL database"
    echo "  - FastAPI application"
    echo "  - Celery worker"
    echo ""
    echo "To add tools, run: docker-compose up -d --profile tools"
    echo "To add monitoring, run: docker-compose up -d --profile monitoring"
    echo "For full setup, use: $0 all"
}

# Function to start all services (everything)
start_all() {
    print_status "Starting all services (complete setup)..."
    docker-compose --profile production --profile tools --profile monitoring up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    print_status "All services started successfully!"
    echo ""
    echo "Application URLs:"
    echo "  - API: http://localhost:$APP_PORT"
    echo "  - API Docs: http://localhost:$APP_PORT/docs"
    echo "  - phpMyAdmin: http://localhost:$PHPMYADMIN_PORT"
    echo "  - Redis UI: http://localhost:$REDIS_UI_PORT"
    echo "  - Flower monitoring: http://localhost:$FLOWER_PORT"
    echo ""
    echo "Complete stack is running!"
}

# Function to show status
show_status() {
    print_status "Service status:"
    docker-compose ps
    echo ""
    print_status "Running profiles:"
    
    # Check which services are running to determine active profiles
    local has_app=$(docker-compose ps app | grep -q "Up" && echo "yes" || echo "no")
    local has_worker=$(docker-compose ps celery-worker | grep -q "Up" && echo "yes" || echo "no") 
    local has_redis=$(docker-compose ps redis | grep -q "Up" && echo "yes" || echo "no")
    local has_tools=$(docker-compose ps phpmyadmin | grep -q "Up" && echo "yes" || echo "no")
    local has_flower=$(docker-compose ps flower | grep -q "Up" && echo "yes" || echo "no")
    
    if [[ "$has_app" == "yes" && "$has_worker" == "yes" ]]; then
        echo "  ✅ Production profile active (Full containerized setup)"
    elif [[ "$has_redis" == "yes" && "$has_tools" == "yes" && "$has_flower" == "yes" && "$has_app" == "no" ]]; then
        echo "  ✅ Development profile active (Infrastructure + monitoring - run API/worker locally)"
    elif [[ "$has_redis" == "yes" && "$has_tools" == "yes" && "$has_app" == "no" ]]; then
        echo "  ✅ Infrastructure profile active (MySQL + Redis + Tools - run API/worker locally)"
    elif [[ "$has_app" == "yes" && "$has_redis" == "no" ]]; then
        echo "  ✅ Basic profile active (MySQL + FastAPI only)"
    else
        echo "  ℹ️ Custom configuration active"
    fi
    
    if [[ "$has_redis" == "no" && ("$has_app" == "no" || "$has_worker" == "no") ]]; then
        echo ""
        echo "💡 For development, try:"
        echo "   ./docker-setup.sh dev     # Infrastructure + monitoring (recommended)"
        echo "   Run API locally: poetry run uvicorn main:app --reload --port 8080"
        echo "   Run worker locally: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_status "Services stopped."
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    docker-compose restart
    print_status "Services restarted."
}

# Function to build application
build_app() {
    print_status "Building application image..."
    docker-compose build app
    print_status "Build completed."
}

# Function to show logs
show_logs() {
    docker-compose logs -f app
}

# Function to connect to MySQL
connect_mysql() {
    print_status "Connecting to MySQL..."
    docker-compose exec mysql mysql -u storyteller_user -p storyteller
}

# Function to run migration
run_migration() {
    print_status "Running data migration..."
    
    # Check if SQLite database exists
    if [ ! -f "stories.db" ]; then
        print_warning "No SQLite database found. Nothing to migrate."
        return
    fi
    
    # Start MySQL service if not running
    if ! docker-compose ps mysql | grep -q "Up"; then
        print_status "Starting MySQL service..."
        docker-compose up -d mysql
        print_status "Waiting for MySQL to be ready..."
        sleep 15
    fi
    
    # Run migration script
    python3 migrate_to_mysql.py
}

# Function to clean everything
clean_all() {
    print_warning "This will stop all services and remove all data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v
        docker system prune -f
        print_status "Cleanup completed."
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to auto-assign available ports
auto_assign_ports() {
    print_status "Auto-assigning available ports..."
    
    APP_PORT=$(find_available_port $APP_PORT)
    MYSQL_PORT=$(find_available_port $MYSQL_PORT)
    PHPMYADMIN_PORT=$(find_available_port $PHPMYADMIN_PORT)
    REDIS_PORT=$(find_available_port $REDIS_PORT)
    FLOWER_PORT=$(find_available_port $FLOWER_PORT)
    REDIS_UI_PORT=$(find_available_port $REDIS_UI_PORT)
    
    # Export for docker-compose
    export APP_HOST_PORT=$APP_PORT
    export MYSQL_HOST_PORT=$MYSQL_PORT
    export PHPMYADMIN_HOST_PORT=$PHPMYADMIN_PORT
    export REDIS_HOST_PORT=$REDIS_PORT
    export FLOWER_HOST_PORT=$FLOWER_PORT
    export REDIS_UI_HOST_PORT=$REDIS_UI_PORT
    
    print_status "Assigned ports:"
    echo "  - API: $APP_PORT"
    echo "  - MySQL: $MYSQL_PORT"
    echo "  - phpMyAdmin: $PHPMYADMIN_PORT"
    echo "  - Redis: $REDIS_PORT"
    echo "  - Flower: $FLOWER_PORT"
    echo "  - Redis UI: $REDIS_UI_PORT"
    echo ""
}

# Main script logic
case "${1:-}" in
    start)
        # Check for auto-ports flag
        if [[ "${2:-}" == "--auto-ports" ]]; then
            auto_assign_ports
        fi
        start_services
        ;;
    infrastructure)
        if [[ "${2:-}" == "--auto-ports" ]]; then
            auto_assign_ports
        fi
        start_infrastructure
        ;;
    tools)
        if [[ "${2:-}" == "--auto-ports" ]]; then
            auto_assign_ports
        fi
        start_with_tools
        ;;
    celery)
        if [[ "${2:-}" == "--auto-ports" ]]; then
            auto_assign_ports
        fi
        start_celery
        ;;
    dev|development)
        if [[ "${2:-}" == "--auto-ports" ]]; then
            auto_assign_ports
        fi
        start_development
        ;;
    full)
        if [[ "${2:-}" == "--auto-ports" ]]; then
            auto_assign_ports
        fi
        start_full
        ;;
    production)
        if [[ "${2:-}" == "--auto-ports" ]]; then
            auto_assign_ports
        fi
        start_production
        ;;
    all)
        if [[ "${2:-}" == "--auto-ports" ]]; then
            auto_assign_ports
        fi
        start_all
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    build)
        build_app
        ;;
    logs)
        show_logs
        ;;
    mysql)
        connect_mysql
        ;;
    migrate)
        run_migration
        ;;
    clean)
        clean_all
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        print_error "No command provided."
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
