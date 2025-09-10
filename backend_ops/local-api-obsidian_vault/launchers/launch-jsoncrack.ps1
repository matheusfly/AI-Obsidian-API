# JSON Crack Launch Script for Obsidian Vault API
# Complete interactive visualization setup

param(
    [string]$Action = "start",
    [switch]$Force,
    [switch]$Clean,
    [switch]$Status
)

$ErrorActionPreference = "Stop"

# Configuration
$COMPOSE_FILE = "docker-compose.jsoncrack-fixed.yml"
    $JSONCRACK_URL = "http://localhost:3001"
    $JSON_VIEWER_URL = "http://localhost:3003"
    $VAULT_API_URL = "http://localhost:8081"
$N8N_URL = "http://localhost:5678"

# Colors for output
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "$Color$Message$Reset"
}

function Test-DockerRunning {
    try {
        docker version | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Test-ServiceHealth {
    param([string]$Url, [string]$ServiceName)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "✅ $ServiceName is healthy" $Green
            return $true
        }
    } catch {
        Write-ColorOutput "❌ $ServiceName is not responding" $Red
        return $false
    }
    return $false
}

function Start-JSONCrackServices {
    Write-ColorOutput "🚀 Starting JSON Crack Visualization Services..." $Blue
    
    if (-not (Test-DockerRunning)) {
        Write-ColorOutput "❌ Docker is not running. Please start Docker Desktop first." $Red
        exit 1
    }
    
    # Create necessary directories
    Write-ColorOutput "📁 Creating directories..." $Yellow
    $directories = @(
        "jsoncrackdata/",
        "jsoncrackconfig/", 
        "jsoncrack/visualizations"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-ColorOutput "  Created: $dir" $Green
        }
    }
    
    # Start services
    Write-ColorOutput "🐳 Starting Docker services..." $Yellow
    docker-compose -f $COMPOSE_FILE up -d
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Failed to start services" $Red
        exit 1
    }
    
    # Wait for services to be ready
    Write-ColorOutput "⏳ Waiting for services to be ready..." $Yellow
    Start-Sleep -Seconds 10
    
    # Check service health
    Write-ColorOutput "🔍 Checking service health..." $Blue
    $services = @(
        @{Url = $JSONCRACK_URL; Name = "JSON Crack"},
        @{Url = $JSON_VIEWER_URL; Name = "JSON Viewer"},
        @{Url = "$VAULT_API_URL/health"; Name = "Vault API Visual"},
        @{Url = $N8N_URL; Name = servicesservices/n8n Workflows"}
    )
    
    $allHealthy = $true
    foreach ($service in $services) {
        if (-not (Test-ServiceHealth -Url $service.Url -ServiceName $service.Name)) {
            $allHealthy = $false
        }
    }
    
    if ($allHealthy) {
        Write-ColorOutput "🎉 All services are running successfully!" $Green
        Show-ServiceURLs
    } else {
        Write-ColorOutput "⚠️  Some services may not be fully ready yet. Check logs with: docker-compose -f $COMPOSE_FILE logs" $Yellow
    }
}

function Stop-JSONCrackServices {
    Write-ColorOutput "🛑 Stopping JSON Crack services..." $Blue
    docker-compose -f $COMPOSE_FILE down
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Services stopped successfully" $Green
    } else {
        Write-ColorOutput "❌ Failed to stop services" $Red
    }
}

function Show-ServiceURLs {
    Write-ColorOutput "`n🌐 Service URLs:" $Blue
    Write-ColorOutput "  JSON Crack Dashboard:     $JSONCRACK_URL" $Green
    Write-ColorOutput "  JSON Viewer (Backup):     $JSON_VIEWER_URL" $Green
    Write-ColorOutput "  Vault API Visual:         $VAULT_API_URL" $Green
    Write-ColorOutput "  Visualization Dashboard:  $VAULT_API_URL/visualize" $Green
    Write-ColorOutput "  n8n Workflows:            $N8N_URL" $Green
    Write-ColorOutput "  API Documentation:        $VAULT_API_URL/docs" $Green
    Write-ColorOutput "  OpenAPI Schema:           $VAULT_API_URL/openapi.json" $Green
    
    Write-ColorOutput "`n📊 Quick Access:" $Blue
    Write-ColorOutput "  API Endpoints:            $VAULT_API_URL/visualize/api-endpoints" $Yellow
    Write-ColorOutput "  MCP Tools:                $VAULT_API_URL/visualize/mcp-tools" $Yellow
    Write-ColorOutput "  Workflows:                $VAULT_API_URL/visualize/workflows" $Yellow
    Write-ColorOutput "  Vault Structure:          $VAULT_API_URL/visualize/vault-structure" $Yellow
}

function Show-Status {
    Write-ColorOutput "📊 JSON Crack Services Status" $Blue
    
    $services = @(
        @{Name = "JSON Crack"; Url = $JSONCRACK_URL; Container = "obsidian-jsoncrack"},
        @{Name = "Vault API Visual"; Url = "$VAULT_API_URL/health"; Container = "obsidian-vault-api-visual"},
        @{Name = servicesservices/postgresQL"; Url = ""; Container = "obsidian-postgres"},
        @{Name = "Redis"; Url = ""; Container = "obsidian-redis"},
        @{Name = servicesservices/n8n"; Url = $N8N_URL; Container = "obsidian-n8n"}
    )
    
    foreach ($service in $services) {
        $containerStatus = docker ps --filter "name=$($service.Container)" --format "table {{.Status}}" | Select-Object -Skip 1
        
        if ($containerStatus -and $containerStatus -ne "") {
            Write-ColorOutput "  ✅ $($service.Name): $containerStatus" $Green
        } else {
            Write-ColorOutput "  ❌ $($service.Name): Not running" $Red
        }
    }
    
    Write-ColorOutput "`n🔗 Quick Links:" $Blue
    Show-ServiceURLs
}

function Clean-JSONCrackData {
    Write-ColorOutput "🧹 Cleaning JSON Crack data..." $Yellow
    
    # Stop services first
    Stop-JSONCrackServices
    
    # Remove volumes
    Write-ColorOutput "🗑️  Removing volumes..." $Yellow
    docker-compose -f $COMPOSE_FILE down -v
    
    # Clean directories
    $directories = @("jsoncrackdata/", "jsoncrackconfig/", "jsoncrack/visualizations")
    foreach ($dir in $directories) {
        if (Test-Path $dir) {
            Remove-Item -Path $dir -Recurse -Force
            Write-ColorOutput "  Removed: $dir" $Green
        }
    }
    
    Write-ColorOutput "✅ Cleanup completed" $Green
}

function Show-Logs {
    param([string]$Service = "")
    
    if ($Service) {
        Write-ColorOutput "📋 Showing logs for $Service..." $Blue
        docker-compose -f $COMPOSE_FILE logs -f $Service
    } else {
        Write-ColorOutput "📋 Showing logs for all services..." $Blue
        docker-compose -f $COMPOSE_FILE logs -f
    }
}

function Test-Visualization {
    Write-ColorOutput "🧪 Testing JSON Crack visualization..." $Blue
    
    try {
        # Test JSON Crack connection
        $response = Invoke-RestMethod -Uri "$JSONCRACK_URL/api/health" -Method Get
        Write-ColorOutput "✅ JSON Crack is responding" $Green
        
        # Test Vault API visualization endpoint
        $response = Invoke-RestMethod -Uri "$VAULT_API_URL/visualize/status" -Method Get
        Write-ColorOutput "✅ Vault API visualization is working" $Green
        
        # Open browser to dashboard
        Write-ColorOutput "🌐 Opening visualization dashboard..." $Blue
        Start-Process "$VAULT_API_URL/visualize"
        
    } catch {
        Write-ColorOutput "❌ Visualization test failed: $($_.Exception.Message)" $Red
    }
}

# Main execution
switch ($Action.ToLower()) {
    "start" {
        Start-JSONCrackServices
    }
    "stop" {
        Stop-JSONCrackServices
    }
    scripts/" {
        Stop-JSONCrackServices
        Start-Sleep -Seconds 5
        Start-JSONCrackServices
    }
    "status" {
        Show-Status
    }
    logs/" {
        Show-Logs
    }
    scripts/" {
        Test-Visualization
    }
    "clean" {
        if ($Clean) {
            Clean-JSONCrackData
        } else {
            Write-ColorOutput "⚠️  Use -Clean flag to confirm cleanup" $Yellow
        }
    }
    default {
        Write-ColorOutput "JSON Crack Launch Script for Obsidian Vault API" $Blue
        Write-ColorOutput "Usage: .\launch-jsoncrack.ps1 [Action] [Options]" $Yellow
        Write-ColorOutput ""
        Write-ColorOutput "Actions:" $Blue
        Write-ColorOutput "  start     Start all JSON Crack services" $Green
        Write-ColorOutput "  stop      Stop all services" $Green
        Write-ColorOutput "  restart   Restart all services" $Green
        Write-ColorOutput "  status    Show service status" $Green
        Write-ColorOutput "  logs      Show service logs" $Green
        Write-ColorOutput "  test      Test visualization functionality" $Green
        Write-ColorOutput "  clean     Clean all data (use -Clean flag)" $Green
        Write-ColorOutput ""
        Write-ColorOutput "Options:" $Blue
        Write-ColorOutput "  -Force    Force action without confirmation" $Yellow
        Write-ColorOutput "  -Clean    Confirm cleanup action" $Yellow
        Write-ColorOutput ""
        Write-ColorOutput "Examples:" $Blue
        Write-ColorOutput "  .\launch-jsoncrack.ps1 start" $Green
        Write-ColorOutput "  .\launch-jsoncrack.ps1 status" $Green
        Write-ColorOutput "  .\launch-jsoncrack.ps1 logs jsoncrack" $Green
        Write-ColorOutput "  .\launch-jsoncrack.ps1 clean -Clean" $Green
    }
}
