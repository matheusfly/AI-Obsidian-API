Write-Host "Obsidian Vault AI System - Quick Test" -ForegroundColor Cyan

# Test Docker
try {
    docker version | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 30
}

# Test vault path
if (Test-Path "D:\Nomade Milionario") {
    Write-Host "Vault path OK" -ForegroundColor Green
} else {
    Write-Host "Vault path missing" -ForegroundColor Red
}

# Test config files
if (Test-Path ".env") {
    Write-Host "Environment file OK" -ForegroundColor Green
} else {
    Write-Host "Environment file missing" -ForegroundColor Red
}

# Launch system
Write-Host "Launching system..." -ForegroundColor Yellow
docker-compose down --remove-orphans
docker-compose up -d

Start-Sleep -Seconds 15
docker-compose ps

Write-Host "System launched! Access points:" -ForegroundColor Green
Write-Host "- Obsidian API: http://localhost:27123"
Write-Host "- n8n: http://localhost:5678"
Write-Host "- Vault API: http://localhost:8080"
Write-Host "- Grafana: http://localhost:3000"