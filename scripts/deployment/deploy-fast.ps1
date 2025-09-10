#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Fast deployment script for Data Vault Obsidian with UV optimization
.DESCRIPTION
    Deploys the entire observability stack with optimized build performance
    using UV for ultra-fast Python package installation.
#>

param(
    [switch]$Build,
    [switch]$Up,
    [switch]$Down,
    [switch]$Logs,
    [switch]$Status,
    [switch]$Clean,
    [string]$Service = ""
)

# Colors for output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "${Color}${Message}${Reset}"
}

function Show-Header {
    Write-ColorOutput "🚀 Data Vault Obsidian - Fast Deployment" $Blue
    Write-ColorOutput "Using UV for ultra-fast Python package installation" $Yellow
    Write-ColorOutput "=================================================" $Blue
}

function Build-Services {
    Write-ColorOutput "🔨 Building services with UV optimization..." $Yellow
    
    # Enable BuildKit for faster builds
    $env:DOCKER_BUILDKIT = "1"
    $env:COMPOSE_DOCKER_CLI_BUILD = "1"
    
    # Build with parallel processing
    docker-compose build --parallel --no-cache
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Build completed successfully!" $Green
    } else {
        Write-ColorOutput "❌ Build failed!" $Red
        exit 1
    }
}

function Start-Services {
    Write-ColorOutput "🚀 Starting all services..." $Yellow
    
    # Start services in dependency order
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ All services started!" $Green
        Show-Status
    } else {
        Write-ColorOutput "❌ Failed to start services!" $Red
        exit 1
    }
}

function Stop-Services {
    Write-ColorOutput "🛑 Stopping all services..." $Yellow
    docker-compose down
    Write-ColorOutput "✅ All services stopped!" $Green
}

function Show-Status {
    Write-ColorOutput "📊 Service Status:" $Blue
    docker-compose ps
}

function Show-Logs {
    if ($Service) {
        Write-ColorOutput "📋 Logs for $Service:" $Blue
        docker-compose logs -f $Service
    } else {
        Write-ColorOutput "📋 All service logs:" $Blue
        docker-compose logs -f
    }
}

function Clean-Environment {
    Write-ColorOutput "🧹 Cleaning up environment..." $Yellow
    
    # Stop and remove containers
    docker-compose down -v
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    Write-ColorOutput "✅ Environment cleaned!" $Green
}

function Test-Services {
    Write-ColorOutput "🧪 Testing service endpoints..." $Yellow
    
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
        Write-ColorOutput "✅ Grafana: Running" $Green
    } catch {
        Write-ColorOutput "❌ Grafana: Not responding" $Red
    }
}

# Main execution
Show-Header

if ($Build) {
    Build-Services
}

if ($Up) {
    if ($Build) {
        Build-Services
    }
    Start-Services
    Start-Sleep -Seconds 5
    Test-Services
}

if ($Down) {
    Stop-Services
}

if ($Logs) {
    Show-Logs
}

if ($Status) {
    Show-Status
}

if ($Clean) {
    Clean-Environment
}

# Default action if no parameters
if (-not ($Build -or $Up -or $Down -or $Logs -or $Status -or $Clean)) {
    Write-ColorOutput "Usage examples:" $Yellow
    Write-ColorOutput "  .\scripts\deploy-fast.ps1 -Build          # Build all services" $Reset
    Write-ColorOutput "  .\scripts\deploy-fast.ps1 -Up             # Start all services" $Reset
    Write-ColorOutput "  .\scripts\deploy-fast.ps1 -Build -Up      # Build and start" $Reset
    Write-ColorOutput "  .\scripts\deploy-fast.ps1 -Status         # Show status" $Reset
    Write-ColorOutput "  .\scripts\deploy-fast.ps1 -Logs -Service data-pipeline  # Show logs" $Reset
    Write-ColorOutput "  .\scripts\deploy-fast.ps1 -Clean          # Clean environment" $Reset
}
