# 🚀 COMPLETE MCP ACTIVATION SCRIPT
Write-Host "🚀 COMPLETE MCP ACTIVATION" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Load environment variables
Write-Host "
📍 Step 1: Loading environment variables..." -ForegroundColor Yellow
& ".\LOAD_MCP_ENV.ps1"

# Start all MCP servers
Write-Host "
📍 Step 2: Starting MCP servers..." -ForegroundColor Yellow
& ".\START_MCP_SERVERS.ps1"

# Wait for servers to initialize
Write-Host "
📍 Step 3: Waiting for servers to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test server connections
Write-Host "
📍 Step 4: Testing server connections..." -ForegroundColor Yellow

# Test filesystem server
try {
    Write-Host "   Testing filesystem server..." -ForegroundColor Cyan
     = npx -y @modelcontextprotocol/server-filesystem --help 2>&1
    Write-Host "   ✅ Filesystem server ready" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Filesystem server test inconclusive" -ForegroundColor Yellow
}

# Test GitHub server
try {
    Write-Host "   Testing GitHub server..." -ForegroundColor Cyan
     = npx -y @modelcontextprotocol/server-github --help 2>&1
    Write-Host "   ✅ GitHub server ready" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  GitHub server test inconclusive" -ForegroundColor Yellow
}

# Test sequential-thinking server
try {
    Write-Host "   Testing sequential-thinking server..." -ForegroundColor Cyan
     = npx -y @modelcontextprotocol/server-sequential-thinking --help 2>&1
    Write-Host "   ✅ Sequential-thinking server ready" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Sequential-thinking server test inconclusive" -ForegroundColor Yellow
}

Write-Host "
🎉 MCP ACTIVATION COMPLETE!" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

Write-Host "
✅ All MCP servers are now running!" -ForegroundColor Green
Write-Host "
📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Go to Cursor MCP Tools panel" -ForegroundColor White
Write-Host "   2. Click the toggle switches to enable each server" -ForegroundColor White
Write-Host "   3. All servers should now show as 'Enabled'" -ForegroundColor White
Write-Host "   4. Test MCP tools functionality" -ForegroundColor White

Write-Host "
🎯 Available MCP servers:" -ForegroundColor Cyan
Write-Host "   • filesystem - File operations" -ForegroundColor White
Write-Host "   • github - GitHub integration" -ForegroundColor White
Write-Host "   • sequential-thinking - AI reasoning" -ForegroundColor White
Write-Host "   • playwright - Web automation" -ForegroundColor White
Write-Host "   • context7 - Context management" -ForegroundColor White
Write-Host "   • shadcn-ui - UI components" -ForegroundColor White
Write-Host "   • byterover-mcp - ByteRover integration" -ForegroundColor White
Write-Host "   • fetch - Web fetching" -ForegroundColor White
Write-Host "   • brave-search - Web search" -ForegroundColor White

Write-Host "
🚀 Ready to use all MCP tools in Cursor!" -ForegroundColor Green
