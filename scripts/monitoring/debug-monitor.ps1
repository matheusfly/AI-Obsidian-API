# Debug Monitor - Active Debugging with Issue Detection
# Continuously monitors tests and detects common issues

Write-Host "🐛 DEBUG MONITOR - ACTIVE ISSUE DETECTION" -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Red
Write-Host ""

# Function to detect common issues
function Detect-Issues {
    param([string]$LogOutput)
    
    $issues = @()
    
    # Check for connection errors
    if ($LogOutput -match "ERR_CONNECTION_REFUSED") {
        $issues += "🔴 Connection Refused - Service not running"
    }
    
    # Check for timeout errors
    if ($LogOutput -match "timeout") {
        $issues += "⏰ Timeout Error - Service response too slow"
    }
    
    # Check for memory issues
    if ($LogOutput -match "out of memory") {
        $issues += "💾 Memory Error - Insufficient memory"
    }
    
    # Check for port conflicts
    if ($LogOutput -match "port.*already in use") {
        $issues += "🔌 Port Conflict - Port already occupied"
    }
    
    # Check for test failures
    if ($LogOutput -match "failed.*tests") {
        $issues += "❌ Test Failures - Some tests are failing"
    }
    
    # Check for performance issues
    if ($LogOutput -match "response time.*[0-9]{3,}ms") {
        $issues += "🐌 Performance Issue - High response times"
    }
    
    return $issues
}

# Function to run tests with issue detection
function Run-TestsWithDebugging {
    Write-Host "🧪 Running tests with active debugging..." -ForegroundColor Cyan
    Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host "=" * 60 -ForegroundColor Gray
    
    # Start mock servers
    Write-Host "🔧 Starting Mock MCP Servers..." -ForegroundColor Yellow
    $mockOutput = python scripts/start_mock_mcp_servers.py 2>&1
    Write-Host $mockOutput -ForegroundColor Gray
    Start-Sleep -Seconds 3
    
    # Run tests and capture output
    Write-Host "🧪 Running All Tests..." -ForegroundColor Cyan
    $testOutput = npx playwright test --config=playwright.config.cjs --reporter=list 2>&1
    
    # Display test output
    Write-Host $testOutput -ForegroundColor White
    
    # Detect issues
    $issues = Detect-Issues -LogOutput $testOutput
    
    if ($issues.Count -gt 0) {
        Write-Host "🚨 ISSUES DETECTED:" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "  $issue" -ForegroundColor Red
        }
    } else {
        Write-Host "✅ No issues detected!" -ForegroundColor Green
    }
    
    Write-Host "=" * 60 -ForegroundColor Gray
    Write-Host ""
    
    return $issues
}

# Function to check system status
function Check-SystemStatus {
    Write-Host "🔍 System Status Check..." -ForegroundColor Yellow
    
    # Check if mock servers are running
    $ports = @(6379, 8001, 9001)
    foreach ($port in $ports) {
        try {
            $connection = Test-NetConnection -ComputerName "127.0.0.1" -Port $port -WarningAction SilentlyContinue
            if ($connection.TcpTestSucceeded) {
                Write-Host "✅ Port $port: Open" -ForegroundColor Green
            } else {
                Write-Host "❌ Port $port: Closed" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Port $port: Error checking" -ForegroundColor Red
        }
    }
    
    # Check Node.js processes
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    Write-Host "📊 Node.js Processes: $($nodeProcesses.Count)" -ForegroundColor Blue
    
    # Check Python processes
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    Write-Host "🐍 Python Processes: $($pythonProcesses.Count)" -ForegroundColor Blue
    
    Write-Host ""
}

# Main debugging loop
Write-Host "Starting Debug Monitor..." -ForegroundColor Red
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
Write-Host ""

$cycleCount = 0
$totalIssues = 0
$startTime = Get-Date

try {
    while ($true) {
        $cycleCount++
        Write-Host "🐛 DEBUG CYCLE #$cycleCount" -ForegroundColor Magenta
        Write-Host "Started: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
        
        # Check system status
        Check-SystemStatus
        
        # Run tests with debugging
        $issues = Run-TestsWithDebugging
        $totalIssues += $issues.Count
        
        # Show cycle summary
        $elapsed = (Get-Date) - $startTime
        Write-Host "📊 Debug Summary:" -ForegroundColor Cyan
        Write-Host "  - Cycles Completed: $cycleCount" -ForegroundColor White
        Write-Host "  - Issues This Cycle: $($issues.Count)" -ForegroundColor White
        Write-Host "  - Total Issues Found: $totalIssues" -ForegroundColor White
        Write-Host "  - Total Runtime: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor White
        Write-Host ""
        
        # Wait before next cycle
        Write-Host "⏳ Waiting 60 seconds before next debug cycle..." -ForegroundColor Yellow
        Start-Sleep -Seconds 60
        
        Write-Host "🐛 Starting next debug cycle..." -ForegroundColor Magenta
        Write-Host ""
    }
} catch {
    Write-Host "🛑 Debug Monitor stopped by user" -ForegroundColor Red
    Write-Host "📊 Final Debug Summary:" -ForegroundColor Cyan
    Write-Host "  - Total Cycles: $cycleCount" -ForegroundColor White
    Write-Host "  - Total Issues Found: $totalIssues" -ForegroundColor White
    Write-Host "  - Total Runtime: $(((Get-Date) - $startTime).ToString('hh\:mm\:ss'))" -ForegroundColor White
    Write-Host "✅ Debug session ended" -ForegroundColor Green
}
