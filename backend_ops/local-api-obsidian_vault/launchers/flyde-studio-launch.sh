#!/bin/bash
# 🎨 Flyde Studio Quick Launch Script
# One-click launch of Flyde Studio with custom configuration

# Default configuration
PORT=${1:-3001}
HOST=${2:-localhost}
CONFIG=${3:-"./flyde.config.js"}

echo "🎨 Launching Flyde Studio..."
echo "📍 Port: $PORT"
echo "🌐 Host: $HOST"
echo "⚙️  Config: $CONFIG"

# Check if config exists
if [ ! -f "$CONFIG" ]; then
    echo "⚠️  Config file not found, using defaults"
    npx flyde studio --port $PORT --host $HOST --open
else
    npx flyde studio --config $CONFIG --port $PORT --host $HOST --open
fi
