# MCP LangSmith Integration - COMPLETE TEST SUITE
# This script actually runs and tests everything properly

$ErrorActionPreference = "Stop"

# Configuration
$Config = @{
    LangSmithAPIKey = "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"
    LangSmithProject = "mcp-obsidian-integration"
    MCPIntegrationPort = 8003
    ObservabilityPort = 8002
    DebugDashboardPort = 8004
}

# Set environment
$env:LANGSMITH_API_KEY = $Config.LangSmithAPIKey
$env:LANGSMITH_PROJECT = $Config.LangSmithProject

Write-Host "MCP LANGSMITH INTEGRATION - COMPLETE TEST SUITE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Kill existing processes
Write-Host "Stopping existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start servers
Write-Host "Starting MCP servers..." -ForegroundColor Green

# Start MCP Integration Server
Write-Host "Starting MCP Integration Server..." -ForegroundColor White
Start-Process -FilePath "python" -ArgumentList "mcp_tools/mcp_integration_server.py" -WindowStyle Hidden
Start-Sleep -Seconds 3

# Start Observability Server  
Write-Host "Starting Observability Server..." -ForegroundColor White
Start-Process -FilePath "python" -ArgumentList "mcp_tools/http_observability_server.py" -WindowStyle Hidden
Start-Sleep -Seconds 3

# Start Debug Dashboard
Write-Host "Starting Debug Dashboard..." -ForegroundColor White
Start-Process -FilePath "python" -ArgumentList "mcp_tools/mcp_debug_dashboard.py" -WindowStyle Hidden
Start-Sleep -Seconds 3

# Health checks
Write-Host "`nRunning health checks..." -ForegroundColor Cyan

$healthChecks = @(
    @{ Name = "MCP Integration"; Url = "http://127.0.0.1:$($Config.MCPIntegrationPort)/health" },
    @{ Name = "Observability"; Url = "http://127.0.0.1:$($Config.ObservabilityPort)/health" },
    @{ Name = "Debug Dashboard"; Url = "http://127.0.0.1:$($Config.DebugDashboardPort)/health" }
)

$healthyCount = 0
foreach ($check in $healthChecks) {
    try {
        $response = Invoke-RestMethod -Uri $check.Url -Method Get -TimeoutSec 10
        if ($response.status -eq "healthy") {
            Write-Host "SUCCESS: $($check.Name) - HEALTHY" -ForegroundColor Green
            $healthyCount++
        } else {
            Write-Host "WARNING: $($check.Name) - $($response.status)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "ERROR: $($check.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test MCP Tool Call
Write-Host "`nTesting MCP tool calls..." -ForegroundColor Cyan

try {
    $payload = @{
        server_name = "observability-mcp"
        tool_name = "create_trace_event"
        arguments = @{
            event_type = "powershell_test"
            message = "Test from PowerShell script"
            level = "info"
            metadata = @{
                source = "powershell_test_runner"
                timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            }
        }
    } | ConvertTo-Json -Depth 10

    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$($Config.MCPIntegrationPort)/mcp/call" -Method Post -Body $payload -ContentType "application/json" -TimeoutSec 15

    if ($response.success) {
        Write-Host "SUCCESS: MCP Tool Call - $($response.result)" -ForegroundColor Green
    } else {
        Write-Host "WARNING: MCP Tool Call - $($response.error)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: MCP Tool Call - $($_.Exception.Message)" -ForegroundColor Red
}

# Test LangSmith Integration
Write-Host "`nTesting LangSmith integration..." -ForegroundColor Cyan

try {
    $langsmithScript = @"
import langsmith
from langsmith import Client
import os

os.environ['LANGSMITH_API_KEY'] = '$($Config.LangSmithAPIKey)'
os.environ['LANGSMITH_PROJECT'] = '$($Config.LangSmithProject)'

try:
    client = Client()
    runs = list(client.list_runs(project_name='$($Config.LangSmithProject)', limit=5))
    print(f"SUCCESS: Found {len(runs)} runs in LangSmith")
    for i, run in enumerate(runs):
        print(f"  {i+1}. {run.name} - {run.status}")
except Exception as e:
    print(f"ERROR: {str(e)}")
"@

    $result = python -c $langsmithScript 2>&1
    Write-Host $result -ForegroundColor White
} catch {
    Write-Host "ERROR: LangSmith test failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test Trace Retrieval
Write-Host "`nTesting trace retrieval..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$($Config.ObservabilityPort)/traces" -Method Get -TimeoutSec 10
    Write-Host "SUCCESS: Retrieved $($response.Count) trace events" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Trace retrieval failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test Performance Metrics
Write-Host "`nTesting performance metrics..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$($Config.ObservabilityPort)/performance" -Method Get -TimeoutSec 10
    Write-Host "SUCCESS: Performance metrics retrieved" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Performance metrics not available - $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test MCP Server List
Write-Host "`nTesting MCP server list..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$($Config.MCPIntegrationPort)/mcp/servers" -Method Get -TimeoutSec 10
    Write-Host "SUCCESS: Found $($response.Count) MCP servers" -ForegroundColor Green
    Write-Host "Servers: $($response -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: MCP server list failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test Debug Dashboard
Write-Host "`nTesting debug dashboard..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$($Config.DebugDashboardPort)/" -Method Get -TimeoutSec 10
    Write-Host "SUCCESS: Debug dashboard accessible" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Debug dashboard failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`nTEST SUMMARY" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Magenta
Write-Host "Healthy Services: $healthyCount/3" -ForegroundColor White
Write-Host "Service URLs:" -ForegroundColor White
Write-Host "  MCP Integration: http://127.0.0.1:$($Config.MCPIntegrationPort)" -ForegroundColor Gray
Write-Host "  Observability:   http://127.0.0.1:$($Config.ObservabilityPort)" -ForegroundColor Gray
Write-Host "  Debug Dashboard: http://127.0.0.1:$($Config.DebugDashboardPort)" -ForegroundColor Gray
Write-Host "  LangSmith:       https://smith.langchain.com/project/9d0b2020-2853-467c-a6b7-038830616919" -ForegroundColor Gray

if ($healthyCount -eq 3) {
    Write-Host "`nALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
} else {
    Write-Host "`nSome services need attention" -ForegroundColor Yellow
}

Write-Host "`nPress any key to stop services and exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Write-Host "`nStopping services..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup complete!" -ForegroundColor Green
