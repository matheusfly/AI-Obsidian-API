# Active Monitor - Continuous Test Execution with Live Log Watching
# Continuously runs tests and monitors logs for debugging

Write-Host "👀 ACTIVE MONITOR - CONTINUOUS TESTING WITH LIVE LOGS" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""

# Function to run tests with detailed logging
function Run-TestsWithLogs {
    param([string]$TestType = "all")
    
    Write-Host "🧪 Running $TestType tests with live monitoring..." -ForegroundColor Cyan
    Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host "=" * 60 -ForegroundColor Gray
    
    # Start mock servers
    Write-Host "🔧 Starting Mock MCP Servers..." -ForegroundColor Yellow
    python scripts/start_mock_mcp_servers.py
    Start-Sleep -Seconds 3
    
    # Run tests with detailed output
    if ($TestType -eq "all") {
        npx playwright test --config=playwright.config.cjs --reporter=list
    } else {
        npx playwright test --config=playwright.config.cjs --grep $TestType --reporter=list
    }
    
    Write-Host "=" * 60 -ForegroundColor Gray
    Write-Host "✅ Test cycle completed at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
    Write-Host ""
}

# Function to monitor system health
function Monitor-SystemHealth {
    Write-Host "🏥 System Health Check..." -ForegroundColor Yellow
    
    # Check MCP server health
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -TimeoutSec 5
        Write-Host "✅ MCP Server: Healthy" -ForegroundColor Green
    } catch {
        Write-Host "❌ MCP Server: Unreachable" -ForegroundColor Red
    }
    
    # Check memory usage
    $memory = Get-Process -Name "node" -ErrorAction SilentlyContinue | Measure-Object WorkingSet -Sum
    if ($memory) {
        $memoryMB = [math]::Round($memory.Sum / 1MB, 2)
        Write-Host "💾 Memory Usage: $memoryMB MB" -ForegroundColor Blue
    }
    
    Write-Host ""
}

# Main monitoring loop
Write-Host "Starting Active Monitor..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

$cycleCount = 0
$startTime = Get-Date

try {
    while ($true) {
        $cycleCount++
        Write-Host "🔄 MONITORING CYCLE #$cycleCount" -ForegroundColor Magenta
        Write-Host "Started: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
        
        # Run tests
        Run-TestsWithLogs -TestType "all"
        
        # Monitor system health
        Monitor-SystemHealth
        
        # Show cycle summary
        $elapsed = (Get-Date) - $startTime
        Write-Host "📊 Cycle Summary:" -ForegroundColor Cyan
        Write-Host "  - Cycles Completed: $cycleCount" -ForegroundColor White
        Write-Host "  - Total Runtime: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor White
        Write-Host "  - Average Cycle Time: $([math]::Round($elapsed.TotalSeconds / $cycleCount, 2))s" -ForegroundColor White
        Write-Host ""
        
        # Wait before next cycle
        Write-Host "⏳ Waiting 30 seconds before next cycle..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        Write-Host "🔄 Starting next monitoring cycle..." -ForegroundColor Magenta
        Write-Host ""
    }
} catch {
    Write-Host "🛑 Active Monitor stopped by user" -ForegroundColor Red
    Write-Host "📊 Final Summary:" -ForegroundColor Cyan
    Write-Host "  - Total Cycles: $cycleCount" -ForegroundColor White
    Write-Host "  - Total Runtime: $(((Get-Date) - $startTime).ToString('hh\:mm\:ss'))" -ForegroundColor White
    Write-Host "✅ Monitoring session ended" -ForegroundColor Green
}
