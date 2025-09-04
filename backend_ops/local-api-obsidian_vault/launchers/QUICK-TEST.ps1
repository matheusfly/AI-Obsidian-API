# Quick Test & Launch Script
param(
    [switch]$SkipDocker,
    [switch]$TestOnly
)

Write-Host "🚀 Obsidian Vault AI System - Quick Test & Launch" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Function to check if Docker Desktop is running
function Test-DockerRunning {
    try {
        docker version | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to start Docker Desktop
function Start-DockerDesktop {
    Write-Host "🐳 Starting Docker Desktop..." -ForegroundColor Yellow
    
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-Host "⏳ Waiting for Docker Desktop to start..." -ForegroundColor Yellow
        
        $timeout = 60
        $elapsed = 0
        while (-not (Test-DockerRunning) -and $elapsed -lt $timeout) {
            Start-Sleep -Seconds 2
            $elapsed += 2
            Write-Host "." -NoNewline -ForegroundColor Yellow
        }
        
        if (Test-DockerRunning) {
            Write-Host "`n✅ Docker Desktop is running!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "`n❌ Docker Desktop failed to start within $timeout seconds" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ Docker Desktop not found at $dockerPath" -ForegroundColor Red
        return $false
    }
}

# Check Docker status
if (-not $SkipDocker) {
    if (-not (Test-DockerRunning)) {
        if (-not (Start-DockerDesktop)) {
            Write-Host "❌ Cannot proceed without Docker Desktop" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✅ Docker Desktop is already running" -ForegroundColor Green
    }
}

# Test basic connectivity
Write-Host "`n🔍 Running System Tests..." -ForegroundColor Cyan

# Test 1: Check vault path
$vaultPath = "D:\Nomade Milionario"
if (Test-Path $vaultPath) {
    Write-Host "✅ Vault path accessible: $vaultPath" -ForegroundColor Green
} else {
    Write-Host "❌ Vault path not found: $vaultPath" -ForegroundColor Red
}

# Test 2: Check environment file
if (Test-Path ".env") {
    Write-Host "✅ Environment file found" -ForegroundColor Green
} else {
    Write-Host "❌ Environment file missing" -ForegroundColor Red
}

# Test 3: Check docker-compose file
if (Test-Path "docker-compose.yml") {
    Write-Host "✅ Docker Compose file found" -ForegroundColor Green
} else {
    Write-Host "❌ Docker Compose file missing" -ForegroundColor Red
}

if ($TestOnly) {
    Write-Host "`n✅ Test completed!" -ForegroundColor Green
    exit 0
}

# Launch the system
Write-Host "`n🚀 Launching Obsidian Vault AI System..." -ForegroundColor Cyan

try {
    # Stop any existing containers
    Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
    docker-compose down --remove-orphans 2>$null

    # Start the system
    Write-Host "🚀 Starting services..." -ForegroundColor Yellow
    docker-compose up -d

    # Wait a moment for services to initialize
    Start-Sleep -Seconds 10

    # Check service status
    Write-Host "`n📊 Service Status:" -ForegroundColor Cyan
    docker-compose ps

    Write-Host "`n🌐 Access Points:" -ForegroundColor Cyan
    Write-Host "• Obsidian API: http://localhost:27123" -ForegroundColor White
    Write-Host "• n8n Workflows: http://localhost:5678" -ForegroundColor White
    Write-Host "• Vault API: http://localhost:8080" -ForegroundColor White
    Write-Host "• Grafana: http://localhost:3000" -ForegroundColor White
    Write-Host "• ChromaDB: http://localhost:8000" -ForegroundColor White

    Write-Host "`n✅ System launched successfully!" -ForegroundColor Green
    Write-Host "Run docker-compose logs -f to view logs" -ForegroundColor Gray

} catch {
    Write-Host "❌ Error launching system: $_" -ForegroundColor Red
    exit 1
}