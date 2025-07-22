#!/bin/bash

# Story Teller Docker Setup Script
# This script helps set up and run the application with MySQL using Docker

set -e

echo "=== Story Teller Docker Setup ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    echo "  start        Start basic services (MySQL + FastAPI)"
    echo "  infrastructure Start infrastructure only (MySQL + Redis + Tools) - for local development"
    echo "  tools        Start services with development tools (phpMyAdmin + Redis UI)"
    echo "  dev          Start development infrastructure (MySQL + Redis + monitoring) - run API/worker locally"
    echo "  production   Start all services (full production setup)"
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
    echo "  $0 start                    # Basic: MySQL + FastAPI (quick demo)"
    echo "  $0 dev                      # Infrastructure: MySQL + Redis + monitoring (recommended for development)"
    echo "  $0 infrastructure           # Infrastructure only: MySQL + Redis + Tools"
    echo "  $0 production               # Everything in containers (production-like setup)"
    echo ""
    echo "Development workflow:"
    echo "  1. Run: $0 dev              # Start infrastructure"
    echo "  2. Run API locally: poetry run uvicorn main:app --reload --port 8080"
    echo "  3. Run worker locally: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
    echo ""
    echo "Available at:"
    echo "  - API: http://localhost:8080 (local or container)"
    echo "  - API Docs: http://localhost:8080/docs"
    echo "  - phpMyAdmin: http://localhost:8081 (with dev/infrastructure/production)"
    echo "  - Flower: http://localhost:5555 (with dev/production)"
    echo "  - Redis UI: http://localhost:8082 (with dev/infrastructure/production)"
}

# Function to start basic services
start_services() {
    print_status "Starting basic services (MySQL + FastAPI)..."
    docker-compose up -d mysql app
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "Basic services started successfully!"
        echo ""
        echo "Application URLs:"
        echo "  - API: http://localhost:8080"
        echo "  - API Docs: http://localhost:8080/docs"
        echo ""
        echo "To add Celery: $0 celery"
        echo "To add tools: $0 tools"
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
    echo "  - phpMyAdmin: http://localhost:8081"
    echo "  - Redis UI: http://localhost:8082"
    echo ""
    echo "Now you can run locally:"
    echo "  - API: poetry run uvicorn main:app --reload --port 8080"
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
    echo "  - phpMyAdmin: http://localhost:8081"
    echo "  - Redis UI: http://localhost:8082"
    echo "  - Flower monitoring: http://localhost:5555"
    echo ""
    echo "Now run your applications locally:"
    echo "  - API: poetry run uvicorn main:app --reload --port 8080"
    echo "  - Worker: poetry run celery -A app.celery_app.celery:celery_app worker --loglevel=info"
    echo ""
    echo "This gives you full development flexibility with infrastructure support!"
}

# Function to start all services (production-like)
start_production() {
    print_status "Starting all services (production setup)..."
    docker-compose --profile production --profile tools --profile monitoring up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    print_status "All services started successfully!"
    echo ""
    echo "Application URLs:"
    echo "  - API: http://localhost:8080"
    echo "  - API Docs: http://localhost:8080/docs"
    echo "  - phpMyAdmin: http://localhost:8081"
    echo "  - Redis UI: http://localhost:8082"
    echo "  - Flower monitoring: http://localhost:5555"
    echo ""
    echo "Complete production stack is running!"
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

# Main script logic
case "${1:-}" in
    start)
        start_services
        ;;
    infrastructure)
        start_infrastructure
        ;;
    tools)
        start_with_tools
        ;;
    dev|development)
        start_development
        ;;
    production)
        start_production
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
