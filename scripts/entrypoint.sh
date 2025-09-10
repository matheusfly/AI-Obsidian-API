#!/bin/bash
set -e

echo "🚀 Starting Data Vault Obsidian - Unified Container"
echo "=================================================="

# Create necessary directories
mkdir -p /prometheus
mkdir -p /var/lib/grafana
mkdir -p /var/log/supervisor

# Set permissions
chown -R grafana:grafana /var/lib/grafana 2>/dev/null || true

# Wait for ChromaDB to be ready (if external)
if [ ! -z "$CHROMA_URL" ]; then
    echo "⏳ Waiting for ChromaDB to be ready..."
    until curl -f $CHROMA_URL/api/v2/heartbeat 2>/dev/null; do
        echo "ChromaDB not ready, waiting..."
        sleep 2
    done
    echo "✅ ChromaDB is ready!"
fi

# Start all services with supervisor
echo "🔧 Starting all services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
