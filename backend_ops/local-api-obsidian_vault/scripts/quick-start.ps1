# Quick Start Script for Obsidian Vault AI System
# Handles Docker Desktop startup and service initialization

param(
    [switch]$Force = $false,
    [switch]$SkipDocker = $false,
    [switch]$Verbose = $false,
    [switch]$ShowLogs = $false,
    [switch]$LightSpeed = $false,
    [string]$Service = ""
)

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"
$BLUE = "Blue"
$CYAN = "Cyan"
$WHITE = "White"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Banner {
    Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 OBSIDIAN VAULT AI SYSTEM 🚀                           ║
║                         Quick Start Launcher                                 ║
║                              Version 2.1.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Color "Cyan"
}

function Test-DockerDesktop {
    Write-ColorOutput "🐳 Checking Docker Desktop status..." -Color "Blue"
    
    try {
        $dockerInfo = docker info 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Docker Desktop is running" -Color "Green"
            return $true
        } else {
            Write-ColorOutput "❌ Docker Desktop is not running" -Color "Red"
            return $false
        }
    } catch {
        Write-ColorOutput "❌ Docker Desktop is not accessible" -Color "Red"
        return $false
    }
}

function Start-DockerDesktop {
    Write-ColorOutput "🚀 Starting Docker Desktop..." -Color "Blue"
    
    $dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (-not (Test-Path $dockerDesktopPath)) {
        Write-ColorOutput "❌ Docker Desktop not found at: $dockerDesktopPath" -Color "Red"
        Write-ColorOutput "💡 Please install Docker Desktop for Windows" -Color "Yellow"
        return $false
    }
    
    # Check if already running
    if (Test-DockerDesktop) {
        return $true
    }
    
    Write-ColorOutput "🚀 Launching Docker Desktop..." -Color "Blue"
    Start-Process -FilePath $dockerDesktopPath -WindowStyle Hidden
    
    # Wait for Docker Desktop to start
    Write-ColorOutput "⏳ Waiting for Docker Desktop to start (this may take 1-2 minutes)..." -Color "Yellow"
    $maxWait = 180 # 3 minutes
    $waited = 0
    
    while ($waited -lt $maxWait) {
        if (Test-DockerDesktop) {
            Write-ColorOutput "✅ Docker Desktop is ready!" -Color "Green"
            return $true
        }
        
        Start-Sleep -Seconds 10
        $waited += 10
        Write-ColorOutput "   Still waiting... ($waited/$maxWait seconds)" -Color "Yellow"
    }
    
    Write-ColorOutput "❌ Docker Desktop failed to start within $maxWait seconds" -Color "Red"
    Write-ColorOutput "💡 Please start Docker Desktop manually and try again" -Color "Yellow"
    return $false
}

function Test-Environment {
    Write-ColorOutput "🔍 Checking environment configuration..." -Color "Blue"
    
    $issues = @()
    
    # Check .env file
    if (-not (Test-Path ".env")) {
        $issues += ".env file not found"
    } else {
        Write-ColorOutput "✅ Environment file found" -Color "Green"
    }
    
    # Check vault path
    $vaultPath = "D:\Nomade Milionario"
    if (Test-Path $vaultPath) {
        $noteCount = (Get-ChildItem -Path $vaultPath -Filter "*.md" -Recurse -ErrorAction SilentlyContinue).Count
        Write-ColorOutput "✅ Vault accessible: $noteCount markdown files found" -Color "Green"
    } else {
        $issues += "Vault path not accessible: $vaultPath"
    }
    
    if ($issues.Count -gt 0) {
        Write-ColorOutput "⚠️  Environment issues found:" -Color "Yellow"
        foreach ($issue in $issues) {
            Write-ColorOutput "   • $issue" -Color "Yellow"
        }
        return $false
    }
    
    return $true
}

function Start-Services {
    Write-ColorOutput "🚀 Starting backend services..." -Color "Blue"

    if ($LightSpeed) {
        Write-ColorOutput "⚡ Light Speed mode enabled: optimizing build and starting core stack" -Color "Yellow"
        # Enable BuildKit + parallel builds
        $env:DOCKER_BUILDKIT = "1"
        $env:COMPOSE_DOCKER_CLI_BUILD = "1"

        # Build only local images we actually need for core
        Write-ColorOutput "🔨 Building core services in parallel (obsidian-api, vault-api)..." -Color "Blue"
        $buildResult = docker-compose build --parallel obsidian-api vault-api 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "❌ Build failed:" -Color "Red"
            Write-ColorOutput "$buildResult" -Color "Red"
            return $false
        }

        # Start minimal stack (Compose will bring up dependencies automatically)
        Write-ColorOutput "🎯 Starting core services..." -Color "Blue"
        $startResult = docker-compose up -d obsidian-api vault-api postgres redis n8n chromadb ollama 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "❌ Failed to start core services:" -Color "Red"
            Write-ColorOutput "$startResult" -Color "Red"
            return $false
        }

        Write-ColorOutput "✅ Core services started!" -Color "Green"
        return $true
    }
    
    # Standard (full) flow
    Write-ColorOutput "📦 Pulling latest images..." -Color "Blue"
    $pullResult = docker-compose pull 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "⚠️  Image pull had issues, but continuing..." -Color "Yellow"
        Write-ColorOutput "Pull output: $pullResult" -Color "Gray"
    }
    
    Write-ColorOutput "🔨 Building services..." -Color "Blue"
    $buildResult = docker-compose build 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Build failed:" -Color "Red"
        Write-ColorOutput "$buildResult" -Color "Red"
        return $false
    }
    
    Write-ColorOutput "🎯 Starting all services..." -Color "Blue"
    $startResult = docker-compose up -d 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Services started successfully!" -Color "Green"
        return $true
    } else {
        Write-ColorOutput "❌ Failed to start services:" -Color "Red"
        Write-ColorOutput "$startResult" -Color "Red"
        return $false
    }
}

function Test-Services {
    Write-ColorOutput "🔍 Testing service health..." -Color "Blue"
    
$services = @(
        @{Name="Vault API"; URL="http://localhost:8085/health"; Port=8085},
        @{Name="Obsidian API"; URL="http://localhost:27123/health"; Port=27123},
        @{Name="n8n"; URL="http://localhost:5678/"; Port=5678}
    )
    
    $healthy = 0
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "✅ $($service.Name) is healthy" -Color "Green"
                $healthy++
            } else {
                Write-ColorOutput "⚠️  $($service.Name) responded with status $($response.StatusCode)" -Color "Yellow"
            }
        } catch {
            Write-ColorOutput "❌ $($service.Name) is not responding" -Color "Red"
        }
    }
    
    return $healthy
}

function Show-InteractiveLogs {
    Write-ColorOutput "📋 Starting interactive logs..." -Color "Blue"
    Write-ColorOutput "Press Ctrl+C to stop viewing logs" -Color "Yellow"
    
    # Show logs for all services
    docker-compose logs -f
}

function Show-ServiceLogs {
    param([string]$Service = "")
    
    if ($Service) {
        Write-ColorOutput "📋 Showing logs for $Service..." -Color "Blue"
        docker-compose logs -f $Service
    } else {
        Write-ColorOutput "📋 Available services:" -Color "Blue"
        docker-compose ps --services | ForEach-Object {
            Write-ColorOutput "  • $_" -Color "White"
        }
        Write-ColorOutput "`nUsage: Show-ServiceLogs -Service 'service-name'" -Color "Yellow"
    }
}

function Show-Status {
    Write-ColorOutput @"

🌐 System Access Points:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔗 Vault API:        http://localhost:8085                                 │
│ 📚 API Docs:         http://localhost:8085/docs                            │
│ 🔄 n8n Workflows:    http://localhost:5678                                 │
│ 📝 Obsidian API:     http://localhost:27123                                │
│ 📊 Grafana:          http://localhost:3004                                 │
│ 📈 Prometheus:       http://localhost:9090                                 │
└─────────────────────────────────────────────────────────────────────────────┘

🧪 Quick Test Commands:
┌─────────────────────────────────────────────────────────────────────────────┐
│ # Test API health                                                           │
│ Invoke-RestMethod -Uri "http://localhost:8080/health"                       │
│                                                                             │
│ # Test OpenAPI spec                                                         │
│ Invoke-RestMethod -Uri "http://localhost:8080/openapi.json"                 │
│                                                                             │
│ # View service logs                                                         │
│ docker-compose logs -f vault-api                                            │
│                                                                             │
│ # View all logs interactively                                               │
│ .\scripts\quick-start.ps1 -ShowLogs                                         │
└─────────────────────────────────────────────────────────────────────────────┘
"@ -Color "Cyan"
}

# Main execution
try {
    Write-Banner
    
    # Handle log viewing
    if ($ShowLogs) {
        if ($Service) {
            Show-ServiceLogs -Service $Service
        } else {
            Show-InteractiveLogs
        }
        exit 0
    }
    
    # Check environment
    if (-not (Test-Environment)) {
        Write-ColorOutput "⚠️  Environment issues detected, but continuing..." -Color "Yellow"
    }
    
    # Handle Docker Desktop
    if (-not $SkipDocker) {
        if (-not (Start-DockerDesktop)) {
            Write-ColorOutput "❌ Cannot proceed without Docker Desktop" -Color "Red"
            Write-ColorOutput "💡 Please start Docker Desktop manually and run this script again" -Color "Yellow"
            exit 1
        }
    }
    
    # Start services
    if (Start-Services) {
        Write-ColorOutput "⏳ Waiting for services to initialize..." -Color "Yellow"
        Start-Sleep -Seconds 15
        
        $healthyServices = Test-Services
        if ($healthyServices -gt 0) {
            Write-ColorOutput "🎉 System is ready! $healthyServices services are healthy." -Color "Green"
            Show-Status
        } else {
            Write-ColorOutput "⚠️  Services started but health checks failed" -Color "Yellow"
            Write-ColorOutput "💡 Check logs with: .\scripts\quick-start.ps1 -ShowLogs" -Color "Yellow"
            Show-Status
        }
    } else {
        Write-ColorOutput "❌ Failed to start services" -Color "Red"
        Write-ColorOutput "💡 Check Docker Desktop is running and try again" -Color "Yellow"
        Write-ColorOutput "💡 View logs with: .\scripts\quick-start.ps1 -ShowLogs" -Color "Yellow"
        exit 1
    }
    
} catch {
    Write-ColorOutput "❌ Script execution failed: $($_.Exception.Message)" -Color "Red"
    exit 1
}
