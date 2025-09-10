#!/bin/bash
# 🚀 Flyde Quick Setup Script
# Copy and paste this entire script to set up Flyde in seconds!

echo "🚀 Setting up Flyde Development Environment..."

# Create project directory
PROJECT_NAME=${1:-"flyde-project"}
mkdir -p $PROJECT_NAME && cd $PROJECT_NAME

# Initialize npm project
npm init -y

# Install Flyde dependencies
echo "📦 Installing Flyde dependencies..."
npm install @flyde/loader @flyde/nodes @flyde/runtime

# Install development dependencies
npm install --save-dev @flyde/cli @flyde/studio

# Create basic project structure
mkdir -p flows nodes tests examples

# Create sample flow
cat > flows/hello-world.flyde << 'EOF'
imports: {}
node:
  instances:
    - id: start
      nodeId: InlineValue
      config:
        type: { type: string, value: "string" }
        value: { type: string, value: "Hello, Flyde!" }
    - id: output
      nodeId: Log
      config:
        message: "{{value}}"
  connections:
    - from: { insId: start, pinId: value }
      to: { insId: output, pinId: message }
EOF

# Create package.json scripts
cat >> package.json << 'EOF'
  "scripts": {
    "dev": "flyde studio --port 3001 --open",
    "build": "flyde build --output dist/",
    "test": "flyde test",
    "run": "flyde run flows/hello-world.flyde"
  }
EOF

# Create flyde.config.js
cat > flyde.config.js << 'EOF'
module.exports = {
  flowsDir: './flows',
  nodesDir: './nodes',
  outputDir: './dist',
  devServer: {
    port: 3001,
    host: 'localhost',
    open: true
  },
  build: {
    minify: true,
    sourcemap: true
  }
}
EOF

echo "✅ Flyde environment setup complete!"
echo "🎯 Quick commands:"
echo "  npm run dev     - Launch Flyde Studio"
echo "  npm run build   - Build flows"
echo "  npm run test    - Run tests"
echo "  npm run run     - Execute hello-world flow"
