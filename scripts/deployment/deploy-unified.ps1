#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Ultra-fast deployment script for Data Vault Obsidian unified container
.DESCRIPTION
    Deploys everything in a single container with UV optimization for maximum speed
#>

param(
    [switch]$Build,
    [switch]$Up,
    [switch]$Down,
    [switch]$Logs,
    [switch]$Status,
    [switch]$Clean,
    [switch]$Test
)

# Colors for output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Cyan = "`e[36m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "${Color}${Message}${Reset}"
}

function Show-Header {
    Write-ColorOutput "🚀 Data Vault Obsidian - Unified Container Deployment" $Cyan
    Write-ColorOutput "Single container with Data Pipeline + Observability Stack" $Yellow
    Write-ColorOutput "Using UV for ultra-fast Python package installation" $Yellow
    Write-ColorOutput "=================================================" $Cyan
}

function Build-Unified {
    Write-ColorOutput "🔨 Building unified container with UV optimization..." $Yellow
    
    # Enable BuildKit for maximum speed
    $env:DOCKER_BUILDKIT = "1"
    $env:COMPOSE_DOCKER_CLI_BUILD = "1"
    
    # Build with parallel processing and cache
    docker-compose -f docker-compose.unified.yml build --parallel --no-cache
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Unified container built successfully!" $Green
    } else {
        Write-ColorOutput "❌ Build failed!" $Red
        exit 1
    }
}

function Start-Unified {
    Write-ColorOutput "🚀 Starting unified container..." $Yellow
    
    # Start all services
    docker-compose -f docker-compose.unified.yml up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Unified container started!" $Green
        Start-Sleep -Seconds 10
        Show-Status
        Test-Services
    } else {
        Write-ColorOutput "❌ Failed to start unified container!" $Red
        exit 1
    }
}

function Stop-Unified {
    Write-ColorOutput "🛑 Stopping unified container..." $Yellow
    docker-compose -f docker-compose.unified.yml down
    Write-ColorOutput "✅ Unified container stopped!" $Green
}

function Show-Status {
    Write-ColorOutput "📊 Service Status:" $Blue
    docker-compose -f docker-compose.unified.yml ps
}

function Show-Logs {
    Write-ColorOutput "📋 Unified container logs:" $Blue
    docker-compose -f docker-compose.unified.yml logs -f data-vault-obsidian
}

function Test-Services {
    Write-ColorOutput "🧪 Testing all service endpoints..." $Yellow
    
    # Test data-pipeline health
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8003/health" -TimeoutSec 10
        Write-ColorOutput "✅ Data Pipeline: $($response.status)" $Green
    } catch {
        Write-ColorOutput "❌ Data Pipeline: Not responding" $Red
    }
    
    # Test ChromaDB
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/heartbeat" -TimeoutSec 10
        Write-ColorOutput "✅ ChromaDB: Running" $Green
    } catch {
        Write-ColorOutput "❌ ChromaDB: Not responding" $Red
    }
    
    # Test Grafana
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10
        Write-ColorOutput "✅ Grafana: Running (admin/admin123)" $Green
    } catch {
        Write-ColorOutput "❌ Grafana: Not responding" $Red
    }
    
    # Test Prometheus
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -TimeoutSec 10
        Write-ColorOutput "✅ Prometheus: Running" $Green
    } catch {
        Write-ColorOutput "❌ Prometheus: Not responding" $Red
    }
    
    Write-ColorOutput "`n🌐 Access URLs:" $Cyan
    Write-ColorOutput "  Data Pipeline API: http://localhost:8003" $Reset
    Write-ColorOutput "  Grafana Dashboard: http://localhost:3000 (admin/admin123)" $Reset
    Write-ColorOutput "  Prometheus: http://localhost:9090" $Reset
    Write-ColorOutput "  ChromaDB: http://localhost:8001" $Reset
}

function Clean-Environment {
    Write-ColorOutput "🧹 Cleaning up environment..." $Yellow
    
    # Stop and remove containers
    docker-compose -f docker-compose.unified.yml down -v
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    Write-ColorOutput "✅ Environment cleaned!" $Green
}

# Main execution
Show-Header

if ($Build) {
    Build-Unified
}

if ($Up) {
    if ($Build) {
        Build-Unified
    }
    Start-Unified
}

if ($Down) {
    Stop-Unified
}

if ($Logs) {
    Show-Logs
}

if ($Status) {
    Show-Status
}

if ($Test) {
    Test-Services
}

if ($Clean) {
    Clean-Environment
}

# Default action if no parameters
if (-not ($Build -or $Up -or $Down -or $Logs -or $Status -or $Test -or $Clean)) {
    Write-ColorOutput "Usage examples:" $Yellow
    Write-ColorOutput "  .\scripts\deploy-unified.ps1 -Build -Up    # Build and start unified container" $Reset
    Write-ColorOutput "  .\scripts\deploy-unified.ps1 -Up           # Start unified container" $Reset
    Write-ColorOutput "  .\scripts\deploy-unified.ps1 -Status       # Show status" $Reset
    Write-ColorOutput "  .\scripts\deploy-unified.ps1 -Logs         # Show logs" $Reset
    Write-ColorOutput "  .\scripts\deploy-unified.ps1 -Test         # Test all services" $Reset
    Write-ColorOutput "  .\scripts\deploy-unified.ps1 -Clean        # Clean environment" $Reset
}

