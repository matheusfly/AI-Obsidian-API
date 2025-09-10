#!/bin/bash

# Obsidian Vault AI System - Start Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

log "🚀 Starting Obsidian Vault AI System..."

# Check if .env exists
if [ ! -f .env ]; then
    error ".env file not found. Please run setup.sh first or copy .env.example to .env"
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    error "Docker is not running. Please start Docker Desktop."
fi

# Check if docker-compose.yml exists
if [ ! -f docker-compose.yml ]; then
    error "docker-compose.yml not found. Please ensure you're in the correct directory."
fi

# Pull latest images
log "📦 Pulling latest Docker images..."
docker-compose pull

# Build custom services
log "🔨 Building custom services..."
docker-compose build

# Start services
log "🎯 Starting services..."
docker-compose up -d

# Wait for services to be ready
log "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
log "🔍 Checking service health..."

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            log "✅ $service_name is healthy"
            return 0
        fi
        
        log "⏳ Waiting for $service_name (attempt $attempt/$max_attempts)..."
        sleep 5
        ((attempt++))
    done
    
    warn "❌ $service_name health check failed after $max_attempts attempts"
    return 1
}

# Check each service
check_service "Vault API" "http://localhost:8080/health"
check_service "Obsidian API" "http://localhost:27123/health"
check_service "n8n" "http://localhost:5678/health"

# Display service status
log "📊 Service Status:"
docker-compose ps

# Display access information
log "🌐 System Access Points:"
echo -e "${BLUE}┌─────────────────────────────────────────────────────────┐${NC}"
echo -e "${BLUE}│                    Access Points                       │${NC}"
echo -e "${BLUE}├─────────────────────────────────────────────────────────┤${NC}"
echo -e "${BLUE}│ Vault API:      http://localhost:8080                  │${NC}"
echo -e "${BLUE}│ API Docs:       http://localhost:8080/docs             │${NC}"
echo -e "${BLUE}│ n8n Workflows:  http://localhost:5678                  │${NC}"
echo -e "${BLUE}│ Obsidian API:   http://localhost:27123                 │${NC}"
echo -e "${BLUE}│ Monitoring:     http://localhost:3000 (if enabled)     │${NC}"
echo -e "${BLUE}└─────────────────────────────────────────────────────────┘${NC}"

# Display quick test commands
log "🧪 Quick Test Commands:"
echo -e "${YELLOW}# Test API status:${NC}"
echo "curl http://localhost:8080/"
echo ""
echo -e "${YELLOW}# Test health check:${NC}"
echo "curl http://localhost:8080/health"
echo ""
echo -e "${YELLOW}# List notes (requires API key):${NC}"
echo "curl -H \"Authorization: Bearer your_api_key\" http://localhost:8080/api/v1/notes"

# Check for common issues
log "🔧 System Diagnostics:"

# Check vault path
VAULT_PATH="/mnt/d/Nomade Milionario"
if [ -d "$VAULT_PATH" ]; then
    log "✅ Vault path accessible: $VAULT_PATH"
    NOTE_COUNT=$(find "$VAULT_PATH" -name "*.md" 2>/dev/null | wc -l)
    log "📝 Found $NOTE_COUNT markdown files in vault"
else
    warn "❌ Vault path not accessible: $VAULT_PATH"
    warn "Please check your WSL mount or update OBSIDIAN_VAULT_PATH in .env"
fi

# Check ports
log "🔌 Port Status:"
for port in 8080 5678 27123; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        log "✅ Port $port is in use"
    else
        warn "❌ Port $port is not in use"
    fi
done

# Display logs command
log "📋 To view logs, run:"
echo "docker-compose logs -f"

# Display stop command
log "🛑 To stop the system, run:"
echo "./scripts/stop.sh"

log "🎉 System startup complete!"
log "📚 Check QUICK_START_GUIDE.md for API usage examples"
log "📖 Check DAILY_OPERATIONS_MANUAL.md for daily operations"

# Final status check
if docker-compose ps | grep -q "Up"; then
    log "✅ System is running successfully!"
    exit 0
else
    error "❌ Some services failed to start. Check logs with: docker-compose logs"
fi