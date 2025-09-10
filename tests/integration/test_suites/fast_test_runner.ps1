# =============================================================================
# ⚡ FAST TEST RUNNER - MCP LANGSMITH INTEGRATION
# =============================================================================
# Ultra-fast test execution with minimal overhead
# =============================================================================

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

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

Write-Host "⚡ FAST TEST RUNNER - MCP LANGSMITH INTEGRATION" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Kill existing processes
Write-Host "🔄 Stopping existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Start servers in parallel
Write-Host "🚀 Starting servers in parallel..." -ForegroundColor Green

$jobs = @()

# Start MCP Integration Server
$jobs += Start-Job -ScriptBlock {
    $env:LANGSMITH_API_KEY = $using:Config.LangSmithAPIKey
    $env:LANGSMITH_PROJECT = $using:Config.LangSmithProject
    python mcp_tools/mcp_integration_server.py
}

# Start Observability Server
$jobs += Start-Job -ScriptBlock {
    $env:LANGSMITH_API_KEY = $using:Config.LangSmithAPIKey
    $env:LANGSMITH_PROJECT = $using:Config.LangSmithProject
    python mcp_tools/http_observability_server.py
}

# Start Debug Dashboard
$jobs += Start-Job -ScriptBlock {
    $env:LANGSMITH_API_KEY = $using:Config.LangSmithAPIKey
    $env:LANGSMITH_PROJECT = $using:Config.LangSmithProject
    python mcp_tools/mcp_debug_dashboard.py
}

# Wait for servers to start
Write-Host "⏳ Waiting for servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Quick health checks
Write-Host "`n🔍 RUNNING FAST HEALTH CHECKS" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

$healthChecks = @(
    @{ Name = "MCP Integration"; Url = "http://127.0.0.1:$($Config.MCPIntegrationPort)/health" },
    @{ Name = "Observability"; Url = "http://127.0.0.1:$($Config.ObservabilityPort)/health" },
    @{ Name = "Debug Dashboard"; Url = "http://127.0.0.1:$($Config.DebugDashboardPort)/health" }
)

$healthyCount = 0
foreach ($check in $healthChecks) {
    try {
        $response = Invoke-RestMethod -Uri $check.Url -Method Get -TimeoutSec 5
        if ($response.status -eq "healthy") {
            Write-Host "✅ $($check.Name): HEALTHY" -ForegroundColor Green
            $healthyCount++
        } else {
            Write-Host "⚠️ $($check.Name): $($response.status)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ $($check.Name): ERROR" -ForegroundColor Red
    }
}

# Fast MCP tool call test
Write-Host "`n🔧 TESTING MCP TOOL CALL" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

try {
    $payload = @{
        server_name = "observability-mcp"
        tool_name = "create_trace_event"
        arguments = @{
            event_type = "fast_test"
            message = "Fast test execution"
            level = "info"
            metadata = @{
                source = "fast_test_runner"
                timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            }
        }
    } | ConvertTo-Json -Depth 10

    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$($Config.MCPIntegrationPort)/mcp/call" -Method Post -Body $payload -ContentType "application/json" -TimeoutSec 10

    if ($response.success) {
        Write-Host "✅ MCP Tool Call: SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "⚠️ MCP Tool Call: $($response.error)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ MCP Tool Call: $($_.Exception.Message)" -ForegroundColor Red
}

# Fast LangSmith test
Write-Host "`n📊 TESTING LANGSMITH INTEGRATION" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

try {
    $langsmithTest = @"
import langsmith
from langsmith import Client
import os

os.environ['LANGSMITH_API_KEY'] = '$($Config.LangSmithAPIKey)'
os.environ['LANGSMITH_PROJECT'] = '$($Config.LangSmithProject)'

try:
    client = Client()
    runs = list(client.list_runs(project_name='$($Config.LangSmithProject)', limit=3))
    print(f"SUCCESS: {len(runs)} runs found")
    for i, run in enumerate(runs):
        print(f"  {i+1}. {run.name} - {run.status}")
except Exception as e:
    print(f"ERROR: {str(e)}")
"@

    $result = python -c $langsmithTest 2>&1
    if ($result -match "SUCCESS:") {
        Write-Host "✅ LangSmith: $result" -ForegroundColor Green
    } else {
        Write-Host "❌ LangSmith: $result" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ LangSmith Test Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Fast trace retrieval test
Write-Host "`n📋 TESTING TRACE RETRIEVAL" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$($Config.ObservabilityPort)/traces" -Method Get -TimeoutSec 5
    Write-Host "✅ Trace Retrieval: $($response.Count) traces found" -ForegroundColor Green
} catch {
    Write-Host "❌ Trace Retrieval: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n📊 FAST TEST SUMMARY" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Magenta
Write-Host "✅ Healthy Services: $healthyCount/3" -ForegroundColor White
Write-Host "🌐 Service URLs:" -ForegroundColor White
Write-Host "   MCP Integration: http://127.0.0.1:$($Config.MCPIntegrationPort)" -ForegroundColor Gray
Write-Host "   Observability:   http://127.0.0.1:$($Config.ObservabilityPort)" -ForegroundColor Gray
Write-Host "   Debug Dashboard: http://127.0.0.1:$($Config.DebugDashboardPort)" -ForegroundColor Gray
Write-Host "   LangSmith:       https://smith.langchain.com/project/9d0b2020-2853-467c-a6b7-038830616919" -ForegroundColor Gray

if ($healthyCount -eq 3) {
    Write-Host "`n🎉 ALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Some services need attention" -ForegroundColor Yellow
}

Write-Host "`nPress any key to stop services and exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Write-Host "`n🔄 Stopping services..." -ForegroundColor Yellow
$jobs | Stop-Job
$jobs | Remove-Job
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
