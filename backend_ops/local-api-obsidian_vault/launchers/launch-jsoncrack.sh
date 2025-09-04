#!/bin/bash

# JSON Crack Launch Script for Obsidian Vault API
# Complete interactive visualization setup

set -e

# Configuration
COMPOSE_FILE="docker-compose.jsoncrack-fixed.yml"
JSONCRACK_URL="http://localhost:3001"
JSON_VIEWER_URL="http://localhost:3003"
VAULT_API_URL="http://localhost:8081"
N8N_URL="http://localhost:5678"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default action
ACTION=${1:-start}
FORCE=${2:-false}
CLEAN=${3:-false}

function print_color() {
    echo -e "${2}${1}${NC}"
}

function check_docker() {
    if ! docker version >/dev/null 2>&1; then
        print_color "❌ Docker is not running. Please start Docker first." $RED
        exit 1
    fi
}

function check_service_health() {
    local url=$1
    local service_name=$2
    
    if curl -s -f "$url" >/dev/null 2>&1; then
        print_color "✅ $service_name is healthy" $GREEN
        return 0
    else
        print_color "❌ $service_name is not responding" $RED
        return 1
    fi
}

function start_services() {
    print_color "🚀 Starting JSON Crack Visualization Services..." $BLUE
    
    check_docker
    
    # Create necessary directories
    print_color "📁 Creating directories..." $YELLOW
    mkdir -p jsoncrack/{data,config,visualizations}
    print_color "  Created: jsoncrack/data" $GREEN
    print_color "  Created: jsoncrack/config" $GREEN
    print_color "  Created: jsoncrack/visualizations" $GREEN
    
    # Start services
    print_color "🐳 Starting Docker services..." $YELLOW
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be ready
    print_color "⏳ Waiting for services to be ready..." $YELLOW
    sleep 10
    
    # Check service health
    print_color "🔍 Checking service health..." $BLUE
    local all_healthy=true
    
    if ! check_service_health "$JSONCRACK_URL" "JSON Crack"; then
        all_healthy=false
    fi
    
    if ! check_service_health "$VAULT_API_URL/health" "Vault API Visual"; then
        all_healthy=false
    fi
    
    if ! check_service_health "$N8N_URL" "n8n Workflows"; then
        all_healthy=false
    fi
    
    if [ "$all_healthy" = true ]; then
        print_color "🎉 All services are running successfully!" $GREEN
        show_service_urls
    else
        print_color "⚠️  Some services may not be fully ready yet. Check logs with: docker-compose -f $COMPOSE_FILE logs" $YELLOW
    fi
}

function stop_services() {
    print_color "🛑 Stopping JSON Crack services..." $BLUE
    docker-compose -f "$COMPOSE_FILE" down
    
    if [ $? -eq 0 ]; then
        print_color "✅ Services stopped successfully" $GREEN
    else
        print_color "❌ Failed to stop services" $RED
    fi
}

function show_service_urls() {
    print_color "\n🌐 Service URLs:" $BLUE
    print_color "  JSON Crack Dashboard:     $JSONCRACK_URL" $GREEN
    print_color "  Vault API Visual:         $VAULT_API_URL" $GREEN
    print_color "  Visualization Dashboard:  $VAULT_API_URL/visualize" $GREEN
    print_color "  n8n Workflows:            $N8N_URL" $GREEN
    print_color "  API Documentation:        $VAULT_API_URL/docs" $GREEN
    print_color "  OpenAPI Schema:           $VAULT_API_URL/openapi.json" $GREEN
    
    print_color "\n📊 Quick Access:" $BLUE
    print_color "  API Endpoints:            $VAULT_API_URL/visualize/api-endpoints" $YELLOW
    print_color "  MCP Tools:                $VAULT_API_URL/visualize/mcp-tools" $YELLOW
    print_color "  Workflows:                $VAULT_API_URL/visualize/workflows" $YELLOW
    print_color "  Vault Structure:          $VAULT_API_URL/visualize/vault-structure" $YELLOW
}

function show_status() {
    print_color "📊 JSON Crack Services Status" $BLUE
    
    local services=(
        "obsidian-jsoncrack:JSON Crack"
        "obsidian-vault-api-visual:Vault API Visual"
        "obsidian-postgres:PostgreSQL"
        "obsidian-redis:Redis"
        "obsidian-n8n:n8n"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r container name <<< "$service_info"
        local status=$(docker ps --filter "name=$container" --format "{{.Status}}" 2>/dev/null || echo "")
        
        if [ -n "$status" ]; then
            print_color "  ✅ $name: $status" $GREEN
        else
            print_color "  ❌ $name: Not running" $RED
        fi
    done
    
    print_color "\n🔗 Quick Links:" $BLUE
    show_service_urls
}

function clean_data() {
    print_color "🧹 Cleaning JSON Crack data..." $YELLOW
    
    # Stop services first
    stop_services
    
    # Remove volumes
    print_color "🗑️  Removing volumes..." $YELLOW
    docker-compose -f "$COMPOSE_FILE" down -v
    
    # Clean directories
    print_color "🗑️  Cleaning directories..." $YELLOW
    rm -rf jsoncrack/{data,config,visualizations}
    print_color "  Removed: jsoncrack/data" $GREEN
    print_color "  Removed: jsoncrack/config" $GREEN
    print_color "  Removed: jsoncrack/visualizations" $GREEN
    
    print_color "✅ Cleanup completed" $GREEN
}

function show_logs() {
    local service=${1:-""}
    
    if [ -n "$service" ]; then
        print_color "📋 Showing logs for $service..." $BLUE
        docker-compose -f "$COMPOSE_FILE" logs -f "$service"
    else
        print_color "📋 Showing logs for all services..." $BLUE
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

function test_visualization() {
    print_color "🧪 Testing JSON Crack visualization..." $BLUE
    
    # Test JSON Crack connection
    if curl -s -f "$JSONCRACK_URL/api/health" >/dev/null 2>&1; then
        print_color "✅ JSON Crack is responding" $GREEN
    else
        print_color "❌ JSON Crack is not responding" $RED
        return 1
    fi
    
    # Test Vault API visualization endpoint
    if curl -s -f "$VAULT_API_URL/visualize/status" >/dev/null 2>&1; then
        print_color "✅ Vault API visualization is working" $GREEN
    else
        print_color "❌ Vault API visualization is not working" $RED
        return 1
    fi
    
    # Open browser to dashboard (Linux)
    if command -v xdg-open >/dev/null 2>&1; then
        print_color "🌐 Opening visualization dashboard..." $BLUE
        xdg-open "$VAULT_API_URL/visualize" &
    elif command -v open >/dev/null 2>&1; then
        # macOS
        print_color "🌐 Opening visualization dashboard..." $BLUE
        open "$VAULT_API_URL/visualize" &
    else
        print_color "🌐 Please open: $VAULT_API_URL/visualize" $YELLOW
    fi
}

function show_help() {
    print_color "JSON Crack Launch Script for Obsidian Vault API" $BLUE
    print_color "Usage: ./launch-jsoncrack.sh [Action] [Options]" $YELLOW
    print_color ""
    print_color "Actions:" $BLUE
    print_color "  start     Start all JSON Crack services" $GREEN
    print_color "  stop      Stop all services" $GREEN
    print_color "  restart   Restart all services" $GREEN
    print_color "  status    Show service status" $GREEN
    print_color "  logs      Show service logs" $GREEN
    print_color "  test      Test visualization functionality" $GREEN
    print_color "  clean     Clean all data" $GREEN
    print_color ""
    print_color "Examples:" $BLUE
    print_color "  ./launch-jsoncrack.sh start" $GREEN
    print_color "  ./launch-jsoncrack.sh status" $GREEN
    print_color "  ./launch-jsoncrack.sh logs jsoncrack" $GREEN
    print_color "  ./launch-jsoncrack.sh clean" $GREEN
}

# Main execution
case "$ACTION" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 5
        start_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "test")
        test_visualization
        ;;
    "clean")
        if [ "$CLEAN" = "true" ]; then
            clean_data
        else
            print_color "⚠️  Use 'clean true' to confirm cleanup" $YELLOW
        fi
        ;;
    *)
        show_help
        ;;
esac
