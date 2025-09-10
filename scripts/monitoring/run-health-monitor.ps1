# Run System Health Monitor - Active Health Monitoring and Auto-Fixing
# Executes system health monitoring with real-time analysis

Write-Host "🏥 RUNNING SYSTEM HEALTH MONITOR - ACTIVE MONITORING" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Start mock MCP servers
Write-Host "🔧 Starting Mock MCP Servers..." -ForegroundColor Yellow
python scripts/start_mock_mcp_servers.py
Start-Sleep -Seconds 3

# Run health monitoring tests
Write-Host "🧪 Running System Health Monitor..." -ForegroundColor Cyan
npx playwright test --config=playwright.config.cjs --grep "Health Monitor" --reporter=list

Write-Host "✅ HEALTH MONITORING COMPLETED!" -ForegroundColor Green
Write-Host "📊 System health report generated" -ForegroundColor Blue
