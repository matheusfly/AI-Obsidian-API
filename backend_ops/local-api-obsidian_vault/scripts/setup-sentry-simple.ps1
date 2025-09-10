# Sentry MCP Simple Setup Script
Write-Host "🚀 Starting Sentry MCP Setup..." -ForegroundColor Green

# Check if Node.js is installed
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Install Sentry MCP packages
Write-Host "📦 Installing Sentry MCP packages..." -ForegroundColor Yellow

Write-Host scripts/ing @sentry/mcp-stdio..." -ForegroundColor Cyan
try {
    npm install -g @sentry/mcp-stdio
    Write-Host "✅ @sentry/mcp-stdio installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Failed to install @sentry/mcp-stdio" -ForegroundColor Yellow
}

Write-Host scripts/ing @sentry/cli..." -ForegroundColor Cyan
try {
    npm install -g @sentry/cli
    Write-Host "✅ @sentry/cli installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Failed to install @sentry/cli" -ForegroundColor Yellow
}

# Create directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow

$directories = @(data/", logs/", datadata/memory", servicesservices/sentry-config")

foreach ($dir in $directories) {
    $dirPath = Join-Path $PSScriptRoot $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

Write-Host "🎉 Sentry MCP setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Get your Sentry credentials from https://sentry.io/settings/auth-tokens/" -ForegroundColor White
Write-Host "2. Update your Cursor mcp.json with Sentry auth token" -ForegroundColor White
Write-Host "3. Copy WARP_SENTRY_MCP_CONFIG.json to Warp settings" -ForegroundColor White
Write-Host "4. Restart Cursor and Warp to load new MCP tools" -ForegroundColor White
Write-Host ""
Write-Host "Happy debugging with Sentry MCP!" -ForegroundColor Green
