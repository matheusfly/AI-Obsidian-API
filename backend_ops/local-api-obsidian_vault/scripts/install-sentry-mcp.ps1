# Sentry MCP Installation Script
Write-Host "Starting Sentry MCP Setup..." -ForegroundColor Green

# Check Node.js
Write-Host scripts/ing prerequisites..." -ForegroundColor Yellow
try {
    node --version
    Write-Host "Node.js found" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install packages
Write-Host scripts/ing Sentry MCP packages..." -ForegroundColor Yellow

Write-Host scripts/ing @sentry/mcp-stdio..." -ForegroundColor Cyan
npm install -g @sentry/mcp-stdio

Write-Host scripts/ing @sentry/cli..." -ForegroundColor Cyan
npm install -g @sentry/cli

# Create directories
Write-Host scripts/ing directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path data/" -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path logs/" -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path datadata/memory" -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path servicesservices/sentry-config" -Force -ErrorAction SilentlyContinue

Write-Host "Sentry MCP setup completed!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Get your Sentry credentials from https://sentry.io/settings/auth-tokens/" -ForegroundColor White
Write-Host "2. Update your Cursor mcp.json with Sentry auth token" -ForegroundColor White
Write-Host "3. Copy WARP_SENTRY_MCP_CONFIG.json to Warp settings" -ForegroundColor White
Write-Host "4. Restart Cursor and Warp to load new MCP tools" -ForegroundColor White
