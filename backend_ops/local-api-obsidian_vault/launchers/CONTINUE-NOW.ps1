#!/usr/bin/env powershell
# CONTINUE-NOW.ps1 - Quick System Launcher

param(
    [switch]$Force,
    [switch]$Status,
    [switch]$Test
)

Write-Host "CONTINUING OBSIDIAN VAULT AI SYSTEM..." -ForegroundColor Green

# Check Docker Desktop
$dockerRunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerRunning) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep 10
}

# Use enhanced docker-compose
$composeFile = "docker-compose.enhanced.yml"

if ($Status) {
    Write-Host "SYSTEM STATUS:" -ForegroundColor Cyan
    docker-compose -f $composeFile ps
    return
}

if ($Test) {
    Write-Host scripts/ING SERVICES..." -ForegroundColor Cyan
    
    # Test key endpoints
    $endpoints = @(
        @{Name="Obsidian API"; URL="http://localhost:27123/health"},
        @{Name=servicesservices/n8n"; URL="http://localhost:5678/healthz"},
        @{Name="Flyde Studio"; URL="http://localhost:3001/health"},
        @{Name="Ollama"; URL="http://localhost:11434/api/tags"},
        @{Name="ChromaDB"; URL="http://localhost:8000/api/v1/heartbeat"}
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.URL -UseBasicParsing -TimeoutSec 5
            Write-Host "OK: $($endpoint.Name)" -ForegroundColor Green
        } catch {
            Write-Host "FAILED: $($endpoint.Name)" -ForegroundColor Red
        }
    }
    return
}

# Stop existing services if Force
if ($Force) {
    Write-Host "Stopping existing services..." -ForegroundColor Yellow
    docker-compose -f $composeFile down
}

# Start core services first
Write-Host "Starting core infrastructure..." -ForegroundColor Cyan
docker-compose -f $composeFile up -d postgres redis

# Wait for databases
Write-Host "Waiting for databases..." -ForegroundColor Yellow
Start-Sleep 15

# Start API services
Write-Host "Starting API services..." -ForegroundColor Cyan
docker-compose -f $composeFile up -d obsidian-api chromadb ollama

# Wait for APIs
Write-Host "Waiting for APIs..." -ForegroundColor Yellow
Start-Sleep 10

# Start automation services
Write-Host "Starting automation services..." -ForegroundColor Cyan
docker-compose -f $composeFile up -d n8n flyde-studio motia-dev

# Start monitoring
Write-Host "Starting monitoring..." -ForegroundColor Cyan
docker-compose -f $composeFile up -d prometheus

# Final status check
Write-Host "SYSTEM LAUNCHED! Checking status..." -ForegroundColor Green
Start-Sleep 5

# Show running services
docker-compose -f $composeFile ps

Write-Host ""
Write-Host "QUICK ACCESS URLS:" -ForegroundColor Cyan
Write-Host "Obsidian API: http://localhost:27123" -ForegroundColor White
Write-Host servicesservices/n8n Workflows: http://localhost:5678" -ForegroundColor White
Write-Host "Flyde Studio: http://localhost:3001" -ForegroundColor White
Write-Host "Motia Dev: http://localhost:3000" -ForegroundColor White
Write-Host "Ollama AI: http://localhost:11434" -ForegroundColor White
Write-Host "ChromaDB: http://localhost:8000" -ForegroundColor White
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor White

Write-Host ""
Write-Host scripts/ COMMANDS:" -ForegroundColor Cyan
Write-Host scripts/ Status: .\CONTINUE-NOW.ps1 -Test" -ForegroundColor White
Write-Host "View Status: .\CONTINUE-NOW.ps1 -Status" -ForegroundColor White
Write-Host "Force Restart: .\CONTINUE-NOW.ps1 -Force" -ForegroundColor White

Write-Host ""
Write-Host "SYSTEM READY FOR DEVELOPMENT!" -ForegroundColor Green