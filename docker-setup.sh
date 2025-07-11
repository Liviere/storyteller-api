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
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     Start all services (MySQL + FastAPI)"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  build     Build the application image"
    echo "  logs      Show application logs"
    echo "  mysql     Connect to MySQL CLI"
    echo "  migrate   Run data migration from SQLite"
    echo "  clean     Stop services and remove volumes (WARNING: deletes data)"
    echo "  help      Show this help message"
    echo ""
}

# Function to start services
start_services() {
    print_status "Starting services..."
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "Services started successfully!"
        echo ""
        echo "Application URLs:"
        echo "  - FastAPI: http://localhost:8080"
        echo "  - API Docs: http://localhost:8080/docs"
        echo "  - phpMyAdmin: http://localhost:8081"
        echo ""
        echo "To view logs: $0 logs"
        echo "To stop services: $0 stop"
    else
        print_error "Failed to start services. Check logs with: docker-compose logs"
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
    help|--help|-h)
        show_help
        ;;
    "")
        print_error "No option provided."
        show_help
        exit 1
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
