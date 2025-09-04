# System Overview Launch Script
# Complete system mapping and live data visualization

param(
    [string]$Action = "start",
    [switch]$OpenBrowser,
    [switch]$ShowStats
)

$ErrorActionPreference = "Stop"

# Configuration
$COMPOSE_FILE = "docker-compose.jsoncrack-fixed.yml"
$SYSTEM_OVERVIEW_URL = "http://localhost:8081/system/overview"
$JSON_VIEWER_URL = "http://localhost:3003"
$VAULT_API_URL = "http://localhost:8081"

# Colors for output
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Cyan = "`e[36m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "$Color$Message$Reset"
}

function Start-SystemOverview {
    Write-ColorOutput "🗺️ Starting System Overview Dashboard..." $Blue
    
    # Check if services are running
    Write-ColorOutput "🔍 Checking service status..." $Yellow
    
    $services = @(
        @{Name = "Vault API"; Url = "$VAULT_API_URL/health"},
        @{Name = "JSON Viewer"; Url = $JSON_VIEWER_URL},
        @{Name = "Context Engineering Master"; Url = "http://localhost:3000/health"}
    )
    
    $allRunning = $true
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "  ✅ $($service.Name) is running" $Green
            } else {
                Write-ColorOutput "  ⚠️ $($service.Name) returned status: $($response.StatusCode)" $Yellow
                $allRunning = $false
            }
        } catch {
            Write-ColorOutput "  ❌ $($service.Name) is not responding" $Red
            $allRunning = $false
        }
    }
    
    if (-not $allRunning) {
        Write-ColorOutput "🚀 Starting required services..." $Blue
        & .\launch-jsoncrack.ps1 start
        Start-Sleep -Seconds 10
    }
    
    # Show access information
    Show-SystemOverviewURLs
    
    if ($OpenBrowser) {
        Write-ColorOutput "🌐 Opening System Overview Dashboard..." $Cyan
        Start-Process $SYSTEM_OVERVIEW_URL
    }
}

function Show-SystemOverviewURLs {
    Write-ColorOutput "`n🗺️ System Overview Access Points:" $Blue
    Write-ColorOutput "  📊 System Dashboard:     $SYSTEM_OVERVIEW_URL" $Green
    Write-ColorOutput "  🎨 JSON Viewer:          $JSON_VIEWER_URL" $Green
    Write-ColorOutput "  🔗 Vault API:            $VAULT_API_URL" $Green
    Write-ColorOutput "  📚 API Documentation:    $VAULT_API_URL/docs" $Green
    
    Write-ColorOutput "`n📊 Quick Access Endpoints:" $Blue
    Write-ColorOutput "  📈 System Stats:         $VAULT_API_URL/system/stats" $Yellow
    Write-ColorOutput "  🔧 Service Status:       $VAULT_API_URL/system/services" $Yellow
    Write-ColorOutput "  🔗 All Endpoints:        $VAULT_API_URL/system/endpoints" $Yellow
    Write-ColorOutput "  🛠️ MCP Tools:            $VAULT_API_URL/system/mcp-tools" $Yellow
    Write-ColorOutput "  📋 Data Schemas:         $VAULT_API_URL/system/schemas" $Yellow
    Write-ColorOutput "  🌐 Live Data:            $VAULT_API_URL/system/live-data" $Yellow
    
    Write-ColorOutput "`n🧠 Context Engineering Master:" $Blue
    Write-ColorOutput "  🎨 Interactive Web UI:   http://localhost:3000" $Yellow
    Write-ColorOutput "  🔌 WebSocket:            ws://localhost:3000" $Yellow
    Write-ColorOutput "  📊 API:                  http://localhost:3000/api" $Yellow
    Write-ColorOutput "  🕸️ Knowledge Graph:      http://localhost:3000/api/graph/d3" $Yellow
    Write-ColorOutput "  📋 MCP Servers:          http://localhost:3000/api/mcp/servers" $Yellow
    Write-ColorOutput "  🔧 Health Check:         http://localhost:3000/health" $Yellow
}

function Get-SystemStats {
    Write-ColorOutput "📊 Fetching System Statistics..." $Blue
    
    try {
        $stats = Invoke-RestMethod -Uri "$VAULT_API_URL/system/stats" -Method Get
        $services = Invoke-RestMethod -Uri "$VAULT_API_URL/system/services" -Method Get
        
        Write-ColorOutput "`n📈 System Statistics:" $Blue
        Write-ColorOutput "  🔗 Total Endpoints:     $($stats.total_endpoints)" $Green
        Write-ColorOutput "  🛠️ MCP Tools:           $($stats.total_mcp_tools)" $Green
        Write-ColorOutput "  📋 Data Schemas:        $($stats.total_schemas)" $Green
        Write-ColorOutput "  ⚡ Active Services:     $($stats.active_services)" $Green
        Write-ColorOutput "  ⏱️ System Uptime:       $($stats.uptime)" $Green
        Write-ColorOutput "  💾 Memory Usage:        $($stats.memory_usage)%" $Green
        Write-ColorOutput "  🖥️ CPU Usage:           $($stats.cpu_usage)%" $Green
        
        Write-ColorOutput "`n🔧 Service Status:" $Blue
        foreach ($service in $services.services) {
            $statusColor = if ($service.status -eq "online") { $Green } else { $Red }
            $statusIcon = if ($service.status -eq "online") { "✅" } else { "❌" }
            Write-ColorOutput "  $statusIcon $($service.name): $($service.status)" $statusColor
            if ($service.response_time) {
                Write-ColorOutput "    Response Time: $($service.response_time)ms" $Yellow
            }
        }
        
    } catch {
        Write-ColorOutput "❌ Failed to fetch system stats: $($_.Exception.Message)" $Red
    }
}

function Test-SystemOverview {
    Write-ColorOutput "🧪 Testing System Overview..." $Blue
    
    $tests = @(
        @{Name = "System Overview Page"; Url = $SYSTEM_OVERVIEW_URL},
        @{Name = "System Stats API"; Url = "$VAULT_API_URL/system/stats"},
        @{Name = "Services Status API"; Url = "$VAULT_API_URL/system/services"},
        @{Name = "Endpoints API"; Url = "$VAULT_API_URL/system/endpoints"},
        @{Name = "MCP Tools API"; Url = "$VAULT_API_URL/system/mcp-tools"},
        @{Name = "JSON Viewer"; Url = $JSON_VIEWER_URL}
    )
    
    $passed = 0
    $total = $tests.Count
    
    foreach ($test in $tests) {
        try {
            $response = Invoke-WebRequest -Uri $test.Url -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "  ✅ $($test.Name)" $Green
                $passed++
            } else {
                Write-ColorOutput "  ❌ $($test.Name) - Status: $($response.StatusCode)" $Red
            }
        } catch {
            Write-ColorOutput "  ❌ $($test.Name) - Error: $($_.Exception.Message)" $Red
        }
    }
    
    Write-ColorOutput "`n📊 Test Results: $passed/$total tests passed" $(if ($passed -eq $total) { $Green } else { $Yellow })
    
    if ($passed -eq $total) {
        Write-ColorOutput "🎉 All system overview components are working!" $Green
        Write-ColorOutput "🌐 Open $SYSTEM_OVERVIEW_URL to view the dashboard" $Cyan
    } else {
        Write-ColorOutput "⚠️ Some components need attention. Check the logs above." $Yellow
    }
}

function Show-Help {
    Write-ColorOutput "🗺️ System Overview Launch Script" $Blue
    Write-ColorOutput "Usage: .\launch-system-overview.ps1 [Action] [Options]" $Yellow
    Write-ColorOutput ""
    Write-ColorOutput "Actions:" $Blue
    Write-ColorOutput "  start     Start system overview dashboard" $Green
    Write-ColorOutput "  stats     Show system statistics" $Green
    Write-ColorOutput "  test      Test all system overview components" $Green
    Write-ColorOutput "  urls      Show all access URLs" $Green
    Write-ColorOutput "  help      Show this help message" $Green
    Write-ColorOutput ""
    Write-ColorOutput "Options:" $Blue
    Write-ColorOutput "  -OpenBrowser    Open dashboard in browser" $Yellow
    Write-ColorOutput "  -ShowStats      Show detailed statistics" $Yellow
    Write-ColorOutput ""
    Write-ColorOutput "Examples:" $Blue
    Write-ColorOutput "  .\launch-system-overview.ps1 start -OpenBrowser" $Green
    Write-ColorOutput "  .\launch-system-overview.ps1 stats" $Green
    Write-ColorOutput "  .\launch-system-overview.ps1 test" $Green
}

# Main execution
switch ($Action.ToLower()) {
    "start" {
        Start-SystemOverview
    }
    "stats" {
        Get-SystemStats
    }
    scripts/" {
        Test-SystemOverview
    }
    "urls" {
        Show-SystemOverviewURLs
    }
    "help" {
        Show-Help
    }
    default {
        Show-Help
    }
}
