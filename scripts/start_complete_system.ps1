# Complete MCP System Startup Script
# This script starts the MCP server and then launches the interactive chat

Write-Host "🚀 STARTING COMPLETE MCP SYSTEM" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check if Go is available
try {
    $goVersion = go version
    Write-Host "✅ Go detected: $goVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Go not found. Please install Go first." -ForegroundColor Red
    exit 1
}

# Start MCP Server in background
Write-Host "🔧 Starting MCP Server..." -ForegroundColor Yellow
Start-Process -FilePath "go" -ArgumentList "run", "mcp_server_main.go" -WindowStyle Hidden

# Wait for server to start
Write-Host "⏳ Waiting for MCP server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if server is running
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8081/health" -Method GET -ErrorAction Stop
    Write-Host "✅ MCP Server is healthy!" -ForegroundColor Green
    Write-Host "📊 Server Status: $($healthCheck.status)" -ForegroundColor Cyan
    Write-Host "🔧 Version: $($healthCheck.version)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ MCP Server failed to start or is not responding" -ForegroundColor Red
    Write-Host "💡 Trying to start server in foreground..." -ForegroundColor Yellow
    
    # Start server in foreground
    Start-Process -FilePath "go" -ArgumentList "run", "mcp_server_main.go" -WindowStyle Normal
    exit 1
}

# Start Interactive Chat
Write-Host "🎯 Starting Interactive MCP Chat..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Launch interactive chat
go run interactive_mcp_chat.go
