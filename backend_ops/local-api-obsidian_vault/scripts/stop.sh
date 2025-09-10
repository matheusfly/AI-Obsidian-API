#!/bin/bash

# Obsidian Vault AI System - Stop Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

log "🛑 Stopping Obsidian Vault AI System..."

# Check if docker-compose.yml exists
if [ ! -f docker-compose.yml ]; then
    error "docker-compose.yml not found. Please ensure you're in the correct directory."
fi

# Stop services gracefully
log "⏹️  Stopping services..."
docker-compose stop

# Remove containers
log "🗑️  Removing containers..."
docker-compose down

# Display final status
log "📊 Final Status:"
docker-compose ps

log "✅ System stopped successfully!"
log "💡 To start again, run: ./scripts/start.sh"