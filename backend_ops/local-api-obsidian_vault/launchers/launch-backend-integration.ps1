# 🚀 Backend Integration Launch Script (PowerShell)
# Complete backend system with Flyde & Motia integration

param(
    [string]$Mode = "development",
    [switch]$Test,
    [switch]$Production,
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Status,
    [switch]$Logs,
    [switch]$Help
)

# Color definitions
$Colors = @{
    Green = "Green"
    Blue = "Blue"
    Yellow = "Yellow"
    Red = "Red"
    Magenta = "Magenta"
    Cyan = "Cyan"
    White = "White"
}

function Show-Banner {
    Write-Host "🚀 Backend Integration Launch System" -ForegroundColor $Colors.Magenta
    Write-Host "====================================" -ForegroundColor $Colors.Magenta
    Write-Host "Complete backend with Flyde & Motia integration" -ForegroundColor $Colors.White
    Write-Host ""
}

function Show-Help {
    Write-Host "📚 Available Commands:" -ForegroundColor $Colors.Yellow
    Write-Host ""
    Write-Host "🚀 LAUNCH COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\launch-backend-integration.ps1                    # Launch in development mode" -ForegroundColor $Colors.Cyan
    Write-Host "  .\launch-backend-integration.ps1 -Production        # Launch in production mode" -ForegroundColor $Colors.Cyan
    Write-Host "  .\launch-backend-integration.ps1 -Test              # Launch with testing profile" -ForegroundColor $Colors.Cyan
    Write-Host ""
    Write-Host "🔧 MANAGEMENT COMMANDS:" -ForegroundColor $Colors.Green
    Write-Host "  .\launch-backend-integration.ps1 -Stop              # Stop all services" -ForegroundColor $Colors.Cyan
    Write-Host "  .\launch-backend-integration.ps1 -Restart           # Restart all services" -ForegroundColor $Colors.Cyan
    Write-Host "  .\launch-backend-integration.ps1 -Status            # Show service status" -ForegroundColor $Colors.Cyan
    Write-Host "  .\launch-backend-integration.ps1 -Logs              # Show service logs" -ForegroundColor $Colors.Cyan
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "🔍 Checking Prerequisites..." -ForegroundColor $Colors.Green
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker: $dockerVersion" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor $Colors.Red
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker compose version
        Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "❌ Docker Compose not found. Please install Docker Compose." -ForegroundColor $Colors.Red
        exit 1
    }
    
    # Check if .env file exists
    if (Test-Path ".env") {
        Write-Host "✅ Environment file found" -ForegroundColor $Colors.Green
    } else {
        Write-Host "⚠️  Environment file not found. Creating default..." -ForegroundColor $Colors.Yellow
        Create-DefaultEnv
    }
    
    # Check if projects exist
    if (Test-Path "flyde-project") {
        Write-Host "✅ Flyde project found" -ForegroundColor $Colors.Green
    } else {
        Write-Host "⚠️  Flyde project not found. Creating..." -ForegroundColor $Colors.Yellow
        .\plugins.ps1 setup flyde flyde-project
    }
    
    if (Test-Path "motia-project") {
        Write-Host "✅ Motia project found" -ForegroundColor $Colors.Green
    } else {
        Write-Host "⚠️  Motia project not found. Creating..." -ForegroundColor $Colors.Yellow
        .\plugins.ps1 setup motia motia-project
    }
    
    Write-Host ""
}

function Create-DefaultEnv {
    $envContent = @"
# Backend Integration Environment Variables
# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password_123
POSTGRES_NON_ROOT_USER=n8n_user
POSTGRES_NON_ROOT_PASSWORD=n8n_password_123

# Redis Configuration
REDIS_PASSWORD=redis_password_123

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=admin_password_123
N8N_ENCRYPTION_KEY=your_encryption_key_here

# Obsidian API Configuration
OBSIDIAN_API_KEY=your_obsidian_api_key_here

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=grafana_password_123

# Security
JWT_SECRET=your_jwt_secret_here
API_SECRET=your_api_secret_here
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Default .env file created. Please update with your actual values." -ForegroundColor $Colors.Green
}

function Start-Services {
    param([string]$ComposeFile = "docker-compose.enhanced.yml")
    
    Write-Host "🚀 Starting Backend Services..." -ForegroundColor $Colors.Green
    Write-Host "Using compose file: $ComposeFile" -ForegroundColor $Colors.Blue
    
    # Build and start services
    try {
        if ($Test) {
            Write-Host "🧪 Starting with testing profile..." -ForegroundColor $Colors.Yellow
            docker compose -f $ComposeFile --profile testing up -d --build
        } else {
            docker compose -f $ComposeFile up -d --build
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Services started successfully!" -ForegroundColor $Colors.Green
        } else {
            Write-Host "❌ Failed to start services" -ForegroundColor $Colors.Red
            exit 1
        }
    } catch {
        Write-Host "❌ Error starting services: $($_.Exception.Message)" -ForegroundColor $Colors.Red
        exit 1
    }
    
    # Wait for services to be ready
    Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor $Colors.Yellow
    Start-Sleep -Seconds 10
    
    # Check service health
    Check-ServiceHealth
}

function Stop-Services {
    Write-Host "🛑 Stopping Backend Services..." -ForegroundColor $Colors.Green
    
    try {
        docker compose -f docker-compose.enhanced.yml down
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Services stopped successfully!" -ForegroundColor $Colors.Green
        } else {
            Write-Host "❌ Failed to stop services" -ForegroundColor $Colors.Red
        }
    } catch {
        Write-Host "❌ Error stopping services: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
}

function Restart-Services {
    Write-Host "🔄 Restarting Backend Services..." -ForegroundColor $Colors.Green
    
    Stop-Services
    Start-Sleep -Seconds 5
    Start-Services
}

function Check-ServiceHealth {
    Write-Host "🏥 Checking Service Health..." -ForegroundColor $Colors.Green
    
    $services = @(
        @{ Name = "Obsidian API"; Container = servicesservices/obsidian-api" },
        @{ Name = "Flyde Studio"; Container = "flyde-studio" },
        @{ Name = "Motia Dev"; Container = "motia-dev" },
        @{ Name = servicesservices/n8n"; Container = servicesservices/n8n" },
        @{ Name = servicesservices/postgresQL"; Container = servicesservices/postgres" },
        @{ Name = "Redis"; Container = "redis" },
        @{ Name = "Ollama"; Container = "ollama" },
        @{ Name = "ChromaDB"; Container = "chromadb" },
        @{ Name = "Vault API"; Container = servicesservices/vault-api" },
        @{ Name = "Prometheus"; Container = "prometheus" },
        @{ Name = "Grafana"; Container = "grafana" },
        @{ Name = servicesservices/nginx"; Container = servicesservices/nginx" }
    )
    
    foreach ($service in $services) {
        try {
            $status = docker inspect --format='{{.State.Status}}' $service.Container 2>$null
            if ($status -eq "running") {
                Write-Host "  ✅ $($service.Name): Running" -ForegroundColor $Colors.Green
            } else {
                Write-Host "  ❌ $($service.Name): $status" -ForegroundColor $Colors.Red
            }
        } catch {
            Write-Host "  ❌ $($service.Name): Not found" -ForegroundColor $Colors.Red
        }
    }
    Write-Host ""
}

function Show-ServiceStatus {
    Write-Host "📊 Service Status:" -ForegroundColor $Colors.Yellow
    Write-Host "=================" -ForegroundColor $Colors.Yellow
    
    try {
        docker compose -f docker-compose.enhanced.yml ps
    } catch {
        Write-Host "❌ Error getting service status" -ForegroundColor $Colors.Red
    }
    
    Write-Host ""
    Check-ServiceHealth
}

function Show-ServiceLogs {
    Write-Host "📋 Service Logs:" -ForegroundColor $Colors.Yellow
    Write-Host "===============" -ForegroundColor $Colors.Yellow
    
    $services = @(servicesservices/obsidian-api", "flyde-studio", "motia-dev", servicesservices/n8n", servicesservices/vault-api")
    
    foreach ($service in $services) {
        Write-Host "📄 Logs for ${service}:" -ForegroundColor $Colors.Cyan
        try {
            docker logs --tail 10 $service
        } catch {
            Write-Host "❌ No logs available for $service" -ForegroundColor $Colors.Red
        }
        Write-Host ""
    }
}

function Run-IntegrationTests {
    Write-Host "🧪 Running Integration Tests..." -ForegroundColor $Colors.Green
    
    try {
        .\backend-integration-test.ps1 -Integration -Performance -Security
    } catch {
        Write-Host "❌ Integration tests failed" -ForegroundColor $Colors.Red
    }
}

function Show-ServiceUrls {
    Write-Host "🌐 Service URLs:" -ForegroundColor $Colors.Yellow
    Write-Host "===============" -ForegroundColor $Colors.Yellow
    
    $urls = @(
        @{ Name = "Obsidian API"; Url = "http://localhost:27123" },
        @{ Name = "Flyde Studio"; Url = "http://localhost:3001" },
        @{ Name = "Motia Dev Server"; Url = "http://localhost:3000" },
        @{ Name = servicesservices/n8n Workflows"; Url = "http://localhost:5678" },
        @{ Name = "Vault API"; Url = "http://localhost:8080" },
        @{ Name = "Ollama AI"; Url = "http://localhost:11434" },
        @{ Name = "ChromaDB"; Url = "http://localhost:8000" },
        @{ Name = "Prometheus"; Url = "http://localhost:9090" },
        @{ Name = "Grafana"; Url = "http://localhost:3000" },
        @{ Name = servicesservices/nginx Proxy"; Url = "http://localhost" }
    )
    
    foreach ($url in $urls) {
        Write-Host "  🔗 $($url.Name): $($url.Url)" -ForegroundColor $Colors.Cyan
    }
    Write-Host ""
}

function Optimize-Performance {
    Write-Host "⚡ Performance Optimization..." -ForegroundColor $Colors.Green
    
    # Increase Docker memory limits
    Write-Host "🔧 Optimizing Docker settings..." -ForegroundColor $Colors.Blue
    
    # Set environment variables for better performance
    $env:DOCKER_BUILDKIT = "1"
    $env:COMPOSE_DOCKER_CLI_BUILD = "1"
    
    # Enable Docker BuildKit for faster builds
    Write-Host "✅ Docker BuildKit enabled" -ForegroundColor $Colors.Green
    
    # Set Node.js optimization flags
    $env:NODE_OPTIONS = "--max-old-space-size=4096"
    Write-Host "✅ Node.js memory limit increased" -ForegroundColor $Colors.Green
    
    Write-Host ""
}

# Main execution
Show-Banner

if ($Help) {
    Show-Help
} elseif ($Stop) {
    Stop-Services
} elseif ($Restart) {
    Restart-Services
} elseif ($Status) {
    Show-ServiceStatus
} elseif ($Logs) {
    Show-ServiceLogs
} else {
    # Launch services
    Test-Prerequisites
    
    if ($Production) {
        Write-Host "🏭 Production Mode" -ForegroundColor $Colors.Yellow
        Optimize-Performance
        Start-Services "docker-compose.enhanced.yml"
    } else {
        Write-Host "🔧 Development Mode" -ForegroundColor $Colors.Yellow
        Start-Services "docker-compose.enhanced.yml"
    }
    
    if ($Test) {
        Run-IntegrationTests
    }
    
    Show-ServiceUrls
    
    Write-Host "🎉 Backend Integration System Ready!" -ForegroundColor $Colors.Green
    Write-Host "Use '.\launch-backend-integration.ps1 -Status' to check service status" -ForegroundColor $Colors.Cyan
    Write-Host "Use '.\launch-backend-integration.ps1 -Logs' to view service logs" -ForegroundColor $Colors.Cyan
    Write-Host "Use '.\launch-backend-integration.ps1 -Stop' to stop all services" -ForegroundColor $Colors.Cyan
}
