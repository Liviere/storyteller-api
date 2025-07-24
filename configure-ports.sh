#!/bin/bash

# Port Configuration Management Script
# This script helps configure and validate port settings for the Story Teller application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

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

# Function to find next available port
find_available_port() {
    local base_port=$1
    local port=$base_port
    while ! check_port_available $port; do
        port=$((port + 1))
    done
    echo $port
}

# Function to read current port configuration
read_current_config() {
    if [ -f .env ]; then
        source .env
    fi
    
    # Set defaults if not defined
    APP_HOST_PORT=${APP_HOST_PORT:-8080}
    MYSQL_HOST_PORT=${MYSQL_HOST_PORT:-3306}
    PHPMYADMIN_HOST_PORT=${PHPMYADMIN_HOST_PORT:-8081}
    REDIS_HOST_PORT=${REDIS_HOST_PORT:-6379}
    FLOWER_HOST_PORT=${FLOWER_HOST_PORT:-5555}
    REDIS_UI_HOST_PORT=${REDIS_UI_HOST_PORT:-8082}
    TEST_MYSQL_HOST_PORT=${TEST_MYSQL_HOST_PORT:-3307}
    TEST_REDIS_HOST_PORT=${TEST_REDIS_HOST_PORT:-6380}
}

# Function to display current configuration
show_current_config() {
    read_current_config
    
    echo "=== Current Port Configuration ==="
    echo ""
    echo "Main Services:"
    printf "  %-15s %s" "FastAPI:" "$APP_HOST_PORT"
    if check_port_available $APP_HOST_PORT; then
        echo -e " ${GREEN}✓ Available${NC}"
    else
        echo -e " ${RED}✗ In Use${NC}"
    fi
    
    printf "  %-15s %s" "MySQL:" "$MYSQL_HOST_PORT"
    if check_port_available $MYSQL_HOST_PORT; then
        echo -e " ${GREEN}✓ Available${NC}"
    else
        echo -e " ${RED}✗ In Use${NC}"
    fi
    
    printf "  %-15s %s" "Redis:" "$REDIS_HOST_PORT"
    if check_port_available $REDIS_HOST_PORT; then
        echo -e " ${GREEN}✓ Available${NC}"
    else
        echo -e " ${RED}✗ In Use${NC}"
    fi
    
    echo ""
    echo "Development Tools:"
    printf "  %-15s %s" "phpMyAdmin:" "$PHPMYADMIN_HOST_PORT"
    if check_port_available $PHPMYADMIN_HOST_PORT; then
        echo -e " ${GREEN}✓ Available${NC}"
    else
        echo -e " ${RED}✗ In Use${NC}"
    fi
    
    printf "  %-15s %s" "Redis UI:" "$REDIS_UI_HOST_PORT"
    if check_port_available $REDIS_UI_HOST_PORT; then
        echo -e " ${GREEN}✓ Available${NC}"
    else
        echo -e " ${RED}✗ In Use${NC}"
    fi
    
    printf "  %-15s %s" "Flower:" "$FLOWER_HOST_PORT"
    if check_port_available $FLOWER_HOST_PORT; then
        echo -e " ${GREEN}✓ Available${NC}"
    else
        echo -e " ${RED}✗ In Use${NC}"
    fi
    
    echo ""
    echo "Test Environment:"
    printf "  %-15s %s" "MySQL Test:" "$TEST_MYSQL_HOST_PORT"
    if check_port_available $TEST_MYSQL_HOST_PORT; then
        echo -e " ${GREEN}✓ Available${NC}"
    else
        echo -e " ${RED}✗ In Use${NC}"
    fi
    
    printf "  %-15s %s" "Redis Test:" "$TEST_REDIS_HOST_PORT"
    if check_port_available $TEST_REDIS_HOST_PORT; then
        echo -e " ${GREEN}✓ Available${NC}"
    else
        echo -e " ${RED}✗ In Use${NC}"
    fi
    echo ""
}

# Function to auto-fix port conflicts
auto_fix_ports() {
    print_status "Auto-fixing port conflicts..."
    read_current_config
    
    local updated=false
    local new_env_content=""
    local assigned_ports=()
    
    # Read existing .env and preserve non-port settings
    if [ -f .env ]; then
        new_env_content=$(grep -v "^APP_HOST_PORT\|^MYSQL_HOST_PORT\|^PHPMYADMIN_HOST_PORT\|^REDIS_HOST_PORT\|^FLOWER_HOST_PORT\|^REDIS_UI_HOST_PORT\|^TEST_MYSQL_HOST_PORT\|^TEST_REDIS_HOST_PORT" .env || true)
    fi
    
    # Function to find next available port that's not in assigned_ports
    # This function only finds the port, assignment is done outside
    find_next_available_port() {
        local base_port=$1
        local port=$base_port
        while ! check_port_available $port || [[ " ${assigned_ports[@]} " =~ " $port " ]]; do
            port=$((port + 1))
        done
        echo $port
    }
    
    # Check and fix each port, updating assigned_ports after each assignment
    if ! check_port_available $APP_HOST_PORT; then
        APP_HOST_PORT=$(find_next_available_port $APP_HOST_PORT)
        assigned_ports+=($APP_HOST_PORT)
        updated=true
        print_info "FastAPI port changed to: $APP_HOST_PORT"
    else
        assigned_ports+=($APP_HOST_PORT)
    fi
    
    if ! check_port_available $MYSQL_HOST_PORT; then
        MYSQL_HOST_PORT=$(find_next_available_port $MYSQL_HOST_PORT)
        assigned_ports+=($MYSQL_HOST_PORT)
        updated=true
        print_info "MySQL port changed to: $MYSQL_HOST_PORT"
    else
        assigned_ports+=($MYSQL_HOST_PORT)
    fi
    
    if ! check_port_available $REDIS_HOST_PORT; then
        REDIS_HOST_PORT=$(find_next_available_port $REDIS_HOST_PORT)
        assigned_ports+=($REDIS_HOST_PORT)
        updated=true
        print_info "Redis port changed to: $REDIS_HOST_PORT"
    else
        assigned_ports+=($REDIS_HOST_PORT)
    fi
    
    if ! check_port_available $PHPMYADMIN_HOST_PORT; then
        PHPMYADMIN_HOST_PORT=$(find_next_available_port $PHPMYADMIN_HOST_PORT)
        assigned_ports+=($PHPMYADMIN_HOST_PORT)
        updated=true
        print_info "phpMyAdmin port changed to: $PHPMYADMIN_HOST_PORT"
    else
        assigned_ports+=($PHPMYADMIN_HOST_PORT)
    fi
    
    if ! check_port_available $REDIS_UI_HOST_PORT; then
        REDIS_UI_HOST_PORT=$(find_next_available_port $REDIS_UI_HOST_PORT)
        assigned_ports+=($REDIS_UI_HOST_PORT)
        updated=true
        print_info "Redis UI port changed to: $REDIS_UI_HOST_PORT"
    else
        assigned_ports+=($REDIS_UI_HOST_PORT)
    fi
    
    if ! check_port_available $FLOWER_HOST_PORT; then
        FLOWER_HOST_PORT=$(find_next_available_port $FLOWER_HOST_PORT)
        assigned_ports+=($FLOWER_HOST_PORT)
        updated=true
        print_info "Flower port changed to: $FLOWER_HOST_PORT"
    else
        assigned_ports+=($FLOWER_HOST_PORT)
    fi
    
    # For test ports, ensure they don't conflict with main ports
    if ! check_port_available $TEST_MYSQL_HOST_PORT || [[ " ${assigned_ports[@]} " =~ " $TEST_MYSQL_HOST_PORT " ]]; then
        TEST_MYSQL_HOST_PORT=$(find_next_available_port $TEST_MYSQL_HOST_PORT)
        assigned_ports+=($TEST_MYSQL_HOST_PORT)
        updated=true
        print_info "Test MySQL port changed to: $TEST_MYSQL_HOST_PORT"
    else
        assigned_ports+=($TEST_MYSQL_HOST_PORT)
    fi
    
    if ! check_port_available $TEST_REDIS_HOST_PORT || [[ " ${assigned_ports[@]} " =~ " $TEST_REDIS_HOST_PORT " ]]; then
        TEST_REDIS_HOST_PORT=$(find_next_available_port $TEST_REDIS_HOST_PORT)
        assigned_ports+=($TEST_REDIS_HOST_PORT)
        updated=true
        print_info "Test Redis port changed to: $TEST_REDIS_HOST_PORT"
    else
        assigned_ports+=($TEST_REDIS_HOST_PORT)
    fi
    
    if [ "$updated" = true ]; then
        # Update .env file
        {
            echo "$new_env_content"
            echo ""
            echo "# Port Configuration (Auto-updated)"
            echo "APP_HOST_PORT=$APP_HOST_PORT"
            echo "MYSQL_HOST_PORT=$MYSQL_HOST_PORT"
            echo "PHPMYADMIN_HOST_PORT=$PHPMYADMIN_HOST_PORT"
            echo "REDIS_HOST_PORT=$REDIS_HOST_PORT"
            echo "FLOWER_HOST_PORT=$FLOWER_HOST_PORT"
            echo "REDIS_UI_HOST_PORT=$REDIS_UI_HOST_PORT"
            echo "TEST_MYSQL_HOST_PORT=$TEST_MYSQL_HOST_PORT"
            echo "TEST_REDIS_HOST_PORT=$TEST_REDIS_HOST_PORT"
        } > .env.tmp && mv .env.tmp .env
        
        print_status "Port configuration updated in .env file"
    else
        print_status "No port conflicts found - no changes needed"
    fi
}

# Function to reset ports to defaults
reset_to_defaults() {
    print_warning "This will reset all ports to default values!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Preserve non-port settings
        local new_env_content=""
        if [ -f .env ]; then
            new_env_content=$(grep -v "^APP_HOST_PORT\|^MYSQL_HOST_PORT\|^PHPMYADMIN_HOST_PORT\|^REDIS_HOST_PORT\|^FLOWER_HOST_PORT\|^REDIS_UI_HOST_PORT\|^TEST_MYSQL_HOST_PORT\|^TEST_REDIS_HOST_PORT" .env || true)
        fi
        
        {
            echo "$new_env_content"
            echo ""
            echo "# Port Configuration (Reset to defaults)"
            echo "APP_HOST_PORT=8080"
            echo "MYSQL_HOST_PORT=3306"
            echo "PHPMYADMIN_HOST_PORT=8081"
            echo "REDIS_HOST_PORT=6379"
            echo "FLOWER_HOST_PORT=5555"
            echo "REDIS_UI_HOST_PORT=8082"
            echo "TEST_MYSQL_HOST_PORT=3307"
            echo "TEST_REDIS_HOST_PORT=6380"
        } > .env.tmp && mv .env.tmp .env
        
        print_status "Ports reset to defaults"
    else
        print_status "Reset cancelled"
    fi
}

# Function to show help
show_help() {
    echo "Port Configuration Management"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  show      Show current port configuration and availability"
    echo "  fix       Auto-fix port conflicts by finding available ports"
    echo "  reset     Reset all ports to default values"
    echo "  validate  Check for port conflicts without fixing"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 show      # Display current configuration"
    echo "  $0 fix       # Auto-resolve any port conflicts"
    echo "  $0 reset     # Reset to default ports"
}

# Function to validate ports only
validate_ports() {
    read_current_config
    local conflicts=()
    
    local ports=(
        "FastAPI:$APP_HOST_PORT"
        "MySQL:$MYSQL_HOST_PORT"
        "phpMyAdmin:$PHPMYADMIN_HOST_PORT"
        "Redis:$REDIS_HOST_PORT"
        "Flower:$FLOWER_HOST_PORT"
        "Redis UI:$REDIS_UI_HOST_PORT"
        "MySQL Test:$TEST_MYSQL_HOST_PORT"
        "Redis Test:$TEST_REDIS_HOST_PORT"
    )
    
    for port_info in "${ports[@]}"; do
        local service="${port_info%%:*}"
        local port="${port_info##*:}"
        if ! check_port_available $port; then
            conflicts+=("$service:$port")
        fi
    done
    
    if [ ${#conflicts[@]} -gt 0 ]; then
        print_error "Port conflicts detected:"
        for conflict in "${conflicts[@]}"; do
            local service="${conflict%%:*}"
            local port="${conflict##*:}"
            echo "  - $service (port $port) is already in use"
        done
        echo ""
        echo "Run '$0 fix' to auto-resolve conflicts"
        return 1
    else
        print_status "All ports are available - no conflicts detected"
        return 0
    fi
}

# Main script logic
case "${1:-show}" in
    show)
        show_current_config
        ;;
    fix)
        auto_fix_ports
        ;;
    reset)
        reset_to_defaults
        ;;
    validate)
        validate_ports
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
