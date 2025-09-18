# Real-Time Vault Synchronization System Startup Script
# This script starts the complete real-time synchronization system with monitoring

Write-Host "🚀 Starting Real-Time Vault Synchronization System..." -ForegroundColor Green
Write-Host ""

# Configuration
$VAULT_PATH = "D:\Nomade Milionario"
$API_BASE_URL = "http://localhost:27124"
$API_TOKEN = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
$MCP_SERVER_PORT = "8081"
$DASHBOARD_PORT = "8082"
$SYNC_PORT = "8083"

# Check if required directories exist
if (-not (Test-Path $VAULT_PATH)) {
    Write-Host "❌ Vault path does not exist: $VAULT_PATH" -ForegroundColor Red
    Write-Host "Please update the VAULT_PATH variable in this script." -ForegroundColor Yellow
    exit 1
}

# Check if Obsidian API is running
Write-Host "🔍 Checking Obsidian API connection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$API_BASE_URL/vault/" -Headers @{"Authorization" = "Bearer $API_TOKEN"} -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Obsidian API is running and accessible" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Obsidian API responded with status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Cannot connect to Obsidian API at $API_BASE_URL" -ForegroundColor Red
    Write-Host "Please ensure Obsidian is running with the Local REST API plugin enabled." -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Function to start a service in background
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$Command,
        [string]$WorkingDir = "."
    )
    
    Write-Host "🔄 Starting $ServiceName..." -ForegroundColor Cyan
    
    try {
        $process = Start-Process -FilePath "go" -ArgumentList "run", $Command -WorkingDirectory $WorkingDir -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 2
        
        if (-not $process.HasExited) {
            Write-Host "✅ $ServiceName started successfully (PID: $($process.Id))" -ForegroundColor Green
            return $process
        } else {
            Write-Host "❌ $ServiceName failed to start" -ForegroundColor Red
            return $null
        }
    } catch {
        Write-Host "❌ Failed to start $ServiceName`: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to check if a port is available
function Test-Port {
    param([string]$Port)
    
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, [int]$Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

# Check port availability
Write-Host "🔍 Checking port availability..." -ForegroundColor Cyan
$ports = @($MCP_SERVER_PORT, $DASHBOARD_PORT, $SYNC_PORT)
foreach ($port in $ports) {
    if (-not (Test-Port $port)) {
        Write-Host "⚠️ Port $port is already in use" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Port $port is available" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "📋 Starting Services:" -ForegroundColor Green
Write-Host ""

# Start MCP Server
$mcpServer = Start-Service -ServiceName "MCP Server" -Command "mcp_server_main.go"
if ($mcpServer) {
    Write-Host "   🌐 MCP Server: http://localhost:$MCP_SERVER_PORT" -ForegroundColor White
}

# Start Real-Time Sync Service
$syncService = Start-Service -ServiceName "Real-Time Sync Service" -Command "REAL_TIME_VAULT_SYNC.go"
if ($syncService) {
    Write-Host "   🔄 Real-Time Sync: Active" -ForegroundColor White
}

# Start Monitoring Dashboard
$dashboard = Start-Service -ServiceName "Monitoring Dashboard" -Command "VAULT_MONITORING_DASHBOARD.go"
if ($dashboard) {
    Write-Host "   📊 Monitoring Dashboard: http://localhost:$DASHBOARD_PORT" -ForegroundColor White
}

Write-Host ""
Write-Host "🎯 System Status:" -ForegroundColor Green

# Wait a moment for services to start
Start-Sleep -Seconds 3

# Check service health
$services = @(
    @{Name="MCP Server"; URL="http://localhost:$MCP_SERVER_PORT/health"},
    @{Name="Monitoring Dashboard"; URL="http://localhost:$DASHBOARD_PORT/api/health"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $($service.Name): Healthy" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ $($service.Name): Status $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ $($service.Name): Unhealthy" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🔗 Available Endpoints:" -ForegroundColor Green
Write-Host "   📡 MCP Server: http://localhost:$MCP_SERVER_PORT" -ForegroundColor White
Write-Host "   📊 Monitoring Dashboard: http://localhost:$DASHBOARD_PORT" -ForegroundColor White
Write-Host "   🔄 Real-Time Sync: Active monitoring" -ForegroundColor White
Write-Host "   🧪 Test Suite: Run 'go run REAL_TIME_SYNC_TEST_SUITE.go'" -ForegroundColor White

Write-Host ""
Write-Host "📚 Available Commands:" -ForegroundColor Green
Write-Host "   • Interactive CLI Chat: go run ULTIMATE_INTERACTIVE_CLI_CHAT.go" -ForegroundColor White
Write-Host "   • Run Test Suite: go run REAL_TIME_SYNC_TEST_SUITE.go" -ForegroundColor White
Write-Host "   • View Dashboard: Start browser and go to http://localhost:$DASHBOARD_PORT" -ForegroundColor White

Write-Host ""
Write-Host "⚠️ To stop all services, press Ctrl+C or close this window" -ForegroundColor Yellow
Write-Host ""

# Keep the script running and monitor services
try {
    while ($true) {
        Start-Sleep -Seconds 30
        
        # Check if services are still running
        $runningServices = 0
        if ($mcpServer -and -not $mcpServer.HasExited) { $runningServices++ }
        if ($syncService -and -not $syncService.HasExited) { $runningServices++ }
        if ($dashboard -and -not $dashboard.HasExited) { $runningServices++ }
        
        Write-Host "🔄 System Status: $runningServices/3 services running" -ForegroundColor Cyan
        
        # Check for any service failures
        if ($mcpServer -and $mcpServer.HasExited) {
            Write-Host "❌ MCP Server has stopped unexpectedly" -ForegroundColor Red
        }
        if ($syncService -and $syncService.HasExited) {
            Write-Host "❌ Real-Time Sync Service has stopped unexpectedly" -ForegroundColor Red
        }
        if ($dashboard -and $dashboard.HasExited) {
            Write-Host "❌ Monitoring Dashboard has stopped unexpectedly" -ForegroundColor Red
        }
    }
} catch {
    Write-Host ""
    Write-Host "🛑 Shutting down services..." -ForegroundColor Yellow
    
    # Stop all services
    if ($mcpServer -and -not $mcpServer.HasExited) {
        $mcpServer.Kill()
        Write-Host "   ✅ MCP Server stopped" -ForegroundColor Green
    }
    if ($syncService -and -not $syncService.HasExited) {
        $syncService.Kill()
        Write-Host "   ✅ Real-Time Sync Service stopped" -ForegroundColor Green
    }
    if ($dashboard -and -not $dashboard.HasExited) {
        $dashboard.Kill()
        Write-Host "   ✅ Monitoring Dashboard stopped" -ForegroundColor Green
    }
    
    Write-Host "👋 All services stopped. Goodbye!" -ForegroundColor Green
}
