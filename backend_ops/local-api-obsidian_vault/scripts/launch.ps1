# Obsidian Vault AI System - PowerShell Launch Script
# Complete backend system launcher with interactive CLI

param(
    [string]$Action = "start",
    [switch]$Interactive = $false,
    [switch]$Verbose = $false,
    [switch]$SkipHealthCheck = $false
)

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    Magenta = "Magenta"
    White = "White"
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Write-Banner {
    Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 OBSIDIAN VAULT AI SYSTEM 🚀                           ║
║                         Backend Operations Center                            ║
║                              Version 2.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Color "Cyan"
}

function Test-Prerequisites {
    Write-ColorOutput "🔍 Checking prerequisites..." -Color "Blue"
    
    $issues = @()
    $warnings = @()
    
    # Check Docker Desktop
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-ColorOutput "✅ Docker: $dockerVersion" -Color "Green"
            
            # Check if Docker Desktop is actually running
            try {
                $dockerInfo = docker info 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "✅ Docker Desktop: Running" -Color "Green"
                } else {
                    $warnings += "Docker Desktop not running - will attempt to start"
                }
            } catch {
                $warnings += "Docker Desktop not accessible - will attempt to start"
            }
        } else {
            $issues += "Docker not found - please install Docker Desktop"
        }
    } catch {
        $issues += "Docker not accessible - please install Docker Desktop"
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($composeVersion) {
            Write-ColorOutput "✅ Docker Compose: $composeVersion" -Color "Green"
        } else {
            $issues += "Docker Compose not found"
        }
    } catch {
        $issues += "Docker Compose not accessible"
    }
    
    # Check .env file
    if (Test-Path ".env") {
        Write-ColorOutput "✅ Environment file found" -Color "Green"
    } else {
        $issues += ".env file not found (copy from .env.example)"
    }
    
    # Check vault path
    $vaultPath = "D:\Nomade Milionario"
    if (Test-Path $vaultPath) {
        $noteCount = (Get-ChildItem -Path $vaultPath -Filter "*.md" -Recurse).Count
        Write-ColorOutput "✅ Vault accessible: $noteCount markdown files found" -Color "Green"
    } else {
        $issues += "Vault path not accessible: $vaultPath"
    }
    
    # Check WSL mount
    $wslPath = "/mnt/d/Nomade Milionario"
    try {
        $wslCheck = wsl test -d "$wslPath" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ WSL mount accessible" -Color "Green"
        } else {
            $issues += "WSL mount not accessible: $wslPath"
        }
    } catch {
        Write-ColorOutput "⚠️  WSL check skipped (WSL not available)" -Color "Yellow"
    }
    
    if ($warnings.Count -gt 0) {
        Write-ColorOutput "⚠️  Warnings found:" -Color "Yellow"
        foreach ($warning in $warnings) {
            Write-ColorOutput "   • $warning" -Color "Yellow"
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-ColorOutput "❌ Prerequisites check failed:" -Color "Red"
        foreach ($issue in $issues) {
            Write-ColorOutput "   • $issue" -Color "Red"
        }
        return $false
    }
    
    Write-ColorOutput "✅ All prerequisites satisfied!" -Color "Green"
    return $true
}

function Start-DockerDesktop {
    Write-ColorOutput "🐳 Starting Docker Desktop..." -Color "Blue"
    
    # Check if Docker Desktop is already running
    try {
        docker info | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Docker Desktop is already running" -Color "Green"
            return $true
        }
    } catch {
        # Docker Desktop not running, continue with startup
    }
    
    # Try to start Docker Desktop
    $dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerDesktopPath) {
        Write-ColorOutput "🚀 Launching Docker Desktop..." -Color "Blue"
        Start-Process -FilePath $dockerDesktopPath -WindowStyle Hidden
        
        # Wait for Docker Desktop to start
        Write-ColorOutput "⏳ Waiting for Docker Desktop to start..." -Color "Yellow"
        $maxWait = 120 # 2 minutes
        $waited = 0
        
        while ($waited -lt $maxWait) {
            try {
                docker info | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "✅ Docker Desktop is ready!" -Color "Green"
                    return $true
                }
            } catch {
                # Still starting
            }
            
            Start-Sleep -Seconds 5
            $waited += 5
            Write-ColorOutput "   Still waiting... ($waited/$maxWait seconds)" -Color "Yellow"
        }
        
        Write-ColorOutput "❌ Docker Desktop failed to start within $maxWait seconds" -Color "Red"
        return $false
    } else {
        Write-ColorOutput "❌ Docker Desktop not found at: $dockerDesktopPath" -Color "Red"
        Write-ColorOutput "💡 Please install Docker Desktop for Windows" -Color "Yellow"
        return $false
    }
}

function Start-Services {
    Write-ColorOutput "🚀 Starting Obsidian Vault AI System..." -Color "Blue"
    
    # Ensure Docker Desktop is running
    if (-not (Start-DockerDesktop)) {
        Write-ColorOutput "❌ Cannot start services without Docker Desktop" -Color "Red"
        return
    }
    
    # Pull latest images
    Write-ColorOutput "📦 Pulling latest Docker images..." -Color "Blue"
    docker-compose pull
    
    # Build custom services
    Write-ColorOutput "🔨 Building custom services..." -Color "Blue"
    docker-compose build
    
    # Start services
    Write-ColorOutput "🎯 Starting all services..." -Color "Blue"
    docker-compose up -d
    
    if (-not $SkipHealthCheck) {
        Start-Sleep -Seconds 10
        Test-ServiceHealth
    }
    
    Show-AccessPoints
    Show-QuickCommands
}

function Stop-Services {
    Write-ColorOutput "🛑 Stopping Obsidian Vault AI System..." -Color "Yellow"
    docker-compose down
    Write-ColorOutput "✅ All services stopped" -Color "Green"
}

function Restart-Services {
    Write-ColorOutput "🔄 Restarting Obsidian Vault AI System..." -Color "Blue"
    docker-compose restart
    Start-Sleep -Seconds 10
    Test-ServiceHealth
}

function Test-ServiceHealth {
    Write-ColorOutput "🔍 Checking service health..." -Color "Blue"
    
    $services = @(
        @{Name="Vault API"; URL="http://localhost:8080/health"; Port=8080},
        @{Name="Obsidian API"; URL="http://localhost:27123/health"; Port=27123},
        @{Name=servicesservices/n8n"; URL="http://localhost:5678/health"; Port=5678},
        @{Name="Grafana"; URL="http://localhost:3000/api/health"; Port=3000}
    )
    
    foreach ($service in $services) {
        $maxAttempts = 10
        $attempt = 1
        $healthy = $false
        
        while ($attempt -le $maxAttempts -and -not $healthy) {
            try {
                $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-ColorOutput "✅ $($service.Name) is healthy" -Color "Green"
                    $healthy = $true
                } else {
                    Write-ColorOutput "⏳ $($service.Name) - attempt $attempt/$maxAttempts..." -Color "Yellow"
                }
            } catch {
                Write-ColorOutput "⏳ $($service.Name) - attempt $attempt/$maxAttempts..." -Color "Yellow"
            }
            
            if (-not $healthy) {
                Start-Sleep -Seconds 3
                $attempt++
            }
        }
        
        if (-not $healthy) {
            Write-ColorOutput "❌ $($service.Name) health check failed" -Color "Red"
        }
    }
}

function Show-ServiceStatus {
    Write-ColorOutput "📊 Service Status:" -Color "Blue"
    docker-compose ps
    
    Write-ColorOutput "`n🔌 Port Status:" -Color "Blue"
    $ports = @(8080, 27123, 5678, 3000, 9090, 6379, 5432)
    foreach ($port in $ports) {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
        $status = if ($connection) { "✅ OPEN" } else { "❌ CLOSED" }
        $color = if ($connection) { "Green" } else { "Red" }
        Write-ColorOutput "   Port $port`: $status" -Color $color
    }
}

function Show-AccessPoints {
    Write-ColorOutput @"

🌐 System Access Points:
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Access Points                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🔗 Vault API:        http://localhost:8080                                 │
│ 📚 API Docs:         http://localhost:8080/docs                            │
│ 🔄 n8n Workflows:    http://localhost:5678                                 │
│ 📝 Obsidian API:     http://localhost:27123                                │
│ 📊 Grafana:          http://localhost:3000                                 │
│ 📈 Prometheus:       http://localhost:9090                                 │
│ 🌐 Nginx Proxy:      http://localhost                                      │
└─────────────────────────────────────────────────────────────────────────────┘
"@ -Color "Cyan"
}

function Show-QuickCommands {
    Write-ColorOutput @"

🧪 Quick Test Commands:
┌─────────────────────────────────────────────────────────────────────────────┐
│ # Test API status                                                           │
│ curl http://localhost:8080/                                                 │
│                                                                             │
│ # Test health check                                                         │
│ curl http://localhost:8080/health                                           │
│                                                                             │
│ # List MCP tools                                                            │
│ curl http://localhost:8080/api/v1/mcp/tools                                 │
│                                                                             │
│ # PowerShell API test                                                       │
│ Invoke-RestMethod -Uri "http://localhost:8080/health"                       │
└─────────────────────────────────────────────────────────────────────────────┘
"@ -Color "Yellow"
}

function Show-Logs {
    param([string]$Service = "")
    
    if ($Service) {
        Write-ColorOutput "📋 Showing logs for $Service..." -Color "Blue"
        docker-compose logs -f $Service
    } else {
        Write-ColorOutput "📋 Showing all service logs..." -Color "Blue"
        docker-compose logs -f
    }
}

function Test-API {
    Write-ColorOutput "🧪 Testing API endpoints..." -Color "Blue"
    
    $tests = @(
        @{Name="Root Endpoint"; URL="http://localhost:8080/"},
        @{Name="Health Check"; URL="http://localhost:8080/health"},
        @{Name="MCP Tools"; URL="http://localhost:8080/api/v1/mcp/tools"},
        @{Name="API Docs"; URL="http://localhost:8080/docs"}
    )
    
    foreach ($test in $tests) {
        try {
            $response = Invoke-RestMethod -Uri $test.URL -TimeoutSec 10
            Write-ColorOutput "✅ $($test.Name): OK" -Color "Green"
            if ($Verbose) {
                Write-ColorOutput "   Response: $($response | ConvertTo-Json -Depth 2)" -Color "White"
            }
        } catch {
            Write-ColorOutput "❌ $($test.Name): FAILED - $($_.Exception.Message)" -Color "Red"
        }
    }
}

function Show-MCPTools {
    Write-ColorOutput "🛠️  Available MCP Tools:" -Color "Blue"
    
    try {
        $tools = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools" -TimeoutSec 10
        
        foreach ($tool in $tools.tools) {
            Write-ColorOutput "📋 $($tool.name)" -Color "Cyan"
            Write-ColorOutput "   Description: $($tool.description)" -Color "White"
            if ($Verbose -and $tool.parameters) {
                Write-ColorOutput "   Parameters: $($tool.parameters | ConvertTo-Json -Depth 2)" -Color "Gray"
            }
            Write-Host ""
        }
        
        Write-ColorOutput "Total tools available: $($tools.total)" -Color "Green"
    } catch {
        Write-ColorOutput "❌ Failed to fetch MCP tools: $($_.Exception.Message)" -Color "Red"
    }
}

function Start-InteractiveCLI {
    Write-Banner
    Write-ColorOutput "🎮 Interactive CLI Mode - Type 'help' for commands" -Color "Green"
    
    while ($true) {
        Write-Host "`nObsidian-AI> " -NoNewline -ForegroundColor "Cyan"
        $command = Read-Host
        
        switch ($command.ToLower().Trim()) {
            "help" {
                Write-ColorOutput @"

📋 Available Commands:
┌─────────────────────────────────────────────────────────────────────────────┐
│ System Control:                                                             │
│   start          - Start all services                                      │
│   stop           - Stop all services                                       │
│   restart        - Restart all services                                    │
│   status         - Show service status                                     │
│   health         - Check service health                                    │
│                                                                             │
│ Information:                                                                │
│   access         - Show access points                                      │
│   logs [service] - Show logs (optional service name)                       │
│   test           - Test API endpoints                                       │
│   tools          - Show MCP tools                                          │
│   endpoints      - Show API endpoints                                      │
│                                                                             │
│ Utilities:                                                                  │
│   clear          - Clear screen                                            │
│   verbose        - Toggle verbose mode                                     │
│   exit/quit      - Exit CLI                                                │
└─────────────────────────────────────────────────────────────────────────────┘
"@ -Color "Yellow"
            }
            "start" { Start-Services }
            "stop" { Stop-Services }
            scripts/" { Restart-Services }
            "status" { Show-ServiceStatus }
            "health" { Test-ServiceHealth }
            "access" { Show-AccessPoints }
            logs/" { Show-Logs }
            scripts/" { Test-API }
            "tools" { Show-MCPTools }
            "endpoints" { Show-APIEndpoints }
            "clear" { Clear-Host; Write-Banner }
            "verbose" { 
                $Verbose = -not $Verbose
                Write-ColorOutput "Verbose mode: $(if($Verbose){'ON'}else{'OFF'})" -Color "Yellow"
            }
            {$_ -match "^logs\s+(.+)"} {
                $service = $matches[1]
                Show-Logs -Service $service
            }
            {$_ -in @("exit", "quit", "q")} {
                Write-ColorOutput "👋 Goodbye!" -Color "Green"
                return
            }
            "" { continue }
            default {
                Write-ColorOutput "❌ Unknown command: $command" -Color "Red"
                Write-ColorOutput "💡 Type 'help' for available commands" -Color "Yellow"
            }
        }
    }
}

function Show-APIEndpoints {
    Write-ColorOutput @"

📡 API Endpoints Reference:
┌─────────────────────────────────────────────────────────────────────────────┐
│ Core Vault API (http://localhost:8080):                                    │
│   GET    /                           - Root endpoint                       │
│   GET    /health                     - Health check                        │
│   GET    /docs                       - API documentation                   │
│                                                                             │
│ Note Management:                                                            │
│   GET    /api/v1/notes               - List notes                          │
│   POST   /api/v1/notes               - Create note                         │
│   GET    /api/v1/notes/{path}        - Read note                           │
│   PUT    /api/v1/notes/{path}        - Update note                         │
│   DELETE /api/v1/notes/{path}        - Delete note                         │
│                                                                             │
│ Search & AI:                                                               │
│   POST   /api/v1/search              - Search notes                        │
│   POST   /api/v1/ai/process          - AI processing                       │
│                                                                             │
│ MCP Tools:                                                                  │
│   GET    /api/v1/mcp/tools           - List MCP tools                      │
│   POST   /api/v1/mcp/tools/call      - Call MCP tool                       │
│   GET    /api/v1/mcp/resources       - List MCP resources                  │
│                                                                             │
│ Workflows:                                                                  │
│   GET    /api/v1/workflows           - List workflows                      │
│   POST   /api/v1/workflows/trigger   - Trigger workflow                    │
│                                                                             │
│ System:                                                                     │
│   GET    /api/v1/sync/status         - Sync status                         │
│   POST   /api/v1/batch               - Batch operations                    │
│   WS     /ws                         - WebSocket updates                   │
└─────────────────────────────────────────────────────────────────────────────┘

📝 Obsidian Direct API (http://localhost:27123):
┌─────────────────────────────────────────────────────────────────────────────┐
│   GET    /vault/info                 - Vault information                   │
│   GET    scripts/les                      - List files                          │
│   GET    scripts/les/{path}               - Read file                           │
│   POST   scripts/les                      - Create file                         │
│   PUT    scripts/les/{path}               - Update file                         │
│   DELETE scripts/les/{path}               - Delete file                         │
│   POST   /vault/search               - Search vault                        │
└─────────────────────────────────────────────────────────────────────────────┘
"@ -Color "Cyan"
}

# Main execution logic
try {
    if ($Interactive) {
        Start-InteractiveCLI
        exit 0
    }
    
    Write-Banner
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-ColorOutput "❌ Prerequisites check failed. Please fix the issues above." -Color "Red"
        exit 1
    }
    
    switch ($Action.ToLower()) {
        "start" { Start-Services }
        "stop" { Stop-Services }
        scripts/" { Restart-Services }
        "status" { Show-ServiceStatus }
        "health" { Test-ServiceHealth }
        scripts/" { Test-API }
        "tools" { Show-MCPTools }
        logs/" { Show-Logs }
        "interactive" { Start-InteractiveCLI }
        default {
            Write-ColorOutput "❌ Unknown action: $Action" -Color "Red"
            Write-ColorOutput "Available actions: start, stop, restart, status, health, test, tools, logs, interactive" -Color "Yellow"
            exit 1
        }
    }
    
} catch {
    Write-ColorOutput "❌ Script execution failed: $($_.Exception.Message)" -Color "Red"
    exit 1
}