# Watch Mode - Continuous Test Execution
# Runs tests in watch mode for continuous development

Write-Host "👀 WATCH MODE - CONTINUOUS TESTING" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Start mock MCP servers
Write-Host "🔧 Starting Mock MCP Servers..." -ForegroundColor Yellow
python scripts/start_mock_mcp_servers.py
Start-Sleep -Seconds 3

# Run tests in watch mode
Write-Host "🧪 Running Tests in Watch Mode..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop watching" -ForegroundColor Yellow
npx playwright test --config=playwright.config.cjs --reporter=list --watch

Write-Host "✅ WATCH MODE STOPPED!" -ForegroundColor Green
