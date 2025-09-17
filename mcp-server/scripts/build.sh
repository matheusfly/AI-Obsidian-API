#!/bin/bash

# MCP Server Build Script
echo "Building MCP Server..."

# Create build directory
mkdir -p build

# Build the server
echo "Compiling server binary..."
go build -o build/mcp-server ./cmd/server

if [ $? -eq 0 ]; then
    echo "✅ Build successful! Binary created at: build/mcp-server"
    echo "📁 Binary size: $(du -h build/mcp-server | cut -f1)"
else
    echo "❌ Build failed!"
    exit 1
fi

# Create Windows batch file for easy execution
cat > build/run-server.bat << 'EOF'
@echo off
echo Starting MCP Server...
echo Make sure Obsidian is running with Local REST API plugin enabled
echo Make sure Ollama is running on localhost:11434
echo.
mcp-server.exe
pause
EOF

echo "✅ Build script completed!"
echo "🚀 To run the server:"
echo "   Windows: cd build && run-server.bat"
echo "   Linux/Mac: ./build/mcp-server"

