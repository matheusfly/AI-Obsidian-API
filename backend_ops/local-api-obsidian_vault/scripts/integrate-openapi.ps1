# 🚀 OpenAPI Renderer Plugin Integration Script
# This script integrates the backend system with the Obsidian OpenAPI renderer plugin

param(
    [string]$Action = "full",
    [switch]$Force = $false,
    [switch]$Verbose = $false
)

# Color definitions
$GREEN = "Green"
$BLUE = "Blue"
$YELLOW = "Yellow"
$RED = "Red"
$WHITE = "White"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $colors = @{
        "Green" = "Green"; "Blue" = "Blue"; "Yellow" = "Yellow"
        "Red" = "Red"; "White" = "White"; "Cyan" = "Cyan"
    }
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Start-DockerDesktop {
    Write-ColorOutput "🐳 Starting Docker Desktop..." $BLUE
    
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-ColorOutput "✅ Docker Desktop started" $GREEN
    } else {
        Write-ColorOutput "❌ Docker Desktop not found at $dockerPath" $RED
        return $false
    }
    
    # Wait for Docker to be ready
    Write-ColorOutput "⏳ Waiting for Docker to be ready..." $YELLOW
    $timeout = 120
    $elapsed = 0
    
    do {
        Start-Sleep -Seconds 5
        $elapsed += 5
        if (Test-DockerRunning) {
            Write-ColorOutput "✅ Docker is ready" $GREEN
            return $true
        }
        Write-ColorOutput "⏳ Still waiting... ($elapsed/$timeout seconds)" $YELLOW
    } while ($elapsed -lt $timeout)
    
    Write-ColorOutput "❌ Docker failed to start within $timeout seconds" $RED
    return $false
}

function Initialize-Environment {
    Write-ColorOutput "🔧 Initializing environment configuration..." $BLUE
    
    $envFile = ".env"
    if (-not (Test-Path $envFile) -or $Force) {
        $envContent = @"
# Obsidian Configuration
OBSIDIAN_API_KEY=obsidian_secure_key_2024
OBSIDIAN_VAULT_PATH=/mnt/d/Nomade Milionario

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=secure_n8n_password_2024
N8N_ENCRYPTION_KEY=32_character_encryption_key_here

# Database Configuration
POSTGRES_USER=obsidian_user
POSTGRES_PASSWORD=secure_postgres_password_2024
POSTGRES_NON_ROOT_USER=obsidian_app
POSTGRES_NON_ROOT_PASSWORD=secure_app_password_2024

# Redis Configuration
REDIS_PASSWORD=secure_redis_password_2024

# Grafana Configuration
GRAFANA_USER=admin
GRAFANA_PASSWORD=secure_grafana_password_2024

# AI Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
OLLAMA_MODEL=llama3.1:8b
"@
        
        $envContent | Out-File -FilePath $envFile -Encoding UTF8
        Write-ColorOutput "✅ Environment file created: $envFile" $GREEN
    } else {
        Write-ColorOutput "ℹ️ Environment file already exists: $envFile" $YELLOW
    }
}

function Start-BackendServices {
    Write-ColorOutput "🚀 Starting backend services..." $BLUE
    
    try {
        # Start all services
        docker-compose up -d
        
        # Wait for services to be ready
        Write-ColorOutput "⏳ Waiting for services to be ready..." $YELLOW
        Start-Sleep -Seconds 30
        
        # Check service status
        $services = docker-compose ps --services
        $healthyServices = 0
        $totalServices = $services.Count
        
        foreach ($service in $services) {
            $status = docker-compose ps --format "table {{.Service}}\t{{.Status}}" | Select-String $service
            if ($status -match "Up") {
                $healthyServices++
                Write-ColorOutput "✅ $service is running" $GREEN
            } else {
                Write-ColorOutput "❌ $service is not running" $RED
            }
        }
        
        Write-ColorOutput "📊 Services Status: $healthyServices/$totalServices healthy" $BLUE
        
        if ($healthyServices -eq $totalServices) {
            Write-ColorOutput "🎉 All services are running!" $GREEN
            return $true
        } else {
            Write-ColorOutput "⚠️ Some services are not running properly" $YELLOW
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ Failed to start services: $($_.Exception.Message)" $RED
        return $false
    }
}

function Test-APIEndpoints {
    Write-ColorOutput "🔍 Testing API endpoints..." $BLUE
    
    $endpoints = @(
        @{Name="Vault API Health"; URL="http://localhost:8080/health"},
        @{Name="Vault API OpenAPI"; URL="http://localhost:8080/openapi.json"},
        @{Name="Obsidian API"; URL="http://localhost:27123/vault/info"},
        @{Name=servicesservices/n8n API"; URL="http://localhost:5678/healthz"}
    )
    
    $healthyEndpoints = 0
    $totalEndpoints = $endpoints.Count
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-RestMethod -Uri $endpoint.URL -TimeoutSec 10 -ErrorAction Stop
            Write-ColorOutput "✅ $($endpoint.Name) is responding" $GREEN
            $healthyEndpoints++
        }
        catch {
            Write-ColorOutput "❌ $($endpoint.Name) is not responding: $($_.Exception.Message)" $RED
        }
    }
    
    Write-ColorOutput "📊 API Status: $healthyEndpoints/$totalEndpoints endpoints healthy" $BLUE
    return $healthyEndpoints -eq $totalEndpoints
}

function Configure-Plugin {
    Write-ColorOutput "🔌 Configuring OpenAPI renderer plugin..." $BLUE
    
    $pluginConfigPath = "D:\Nomade Milionario\.obsidian\plugins\openapi-renderer\config.json"
    
    if (Test-Path $pluginConfigPath) {
        Write-ColorOutput "✅ Plugin configuration already exists" $GREEN
    } else {
        Write-ColorOutput "❌ Plugin configuration not found at: $pluginConfigPath" $RED
        Write-ColorOutput "Please ensure the OpenAPI renderer plugin is installed in Obsidian" $YELLOW
        return $false
    }
    
    # Test plugin configuration
    try {
        $config = Get-Content $pluginConfigPath | ConvertFrom-Json
        Write-ColorOutput "✅ Plugin configuration is valid JSON" $GREEN
        
        foreach ($endpoint in $config.apiEndpoints) {
            Write-ColorOutput "🔗 Configured endpoint: $($endpoint.name)" $BLUE
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "❌ Plugin configuration is invalid: $($_.Exception.Message)" $RED
        return $false
    }
}

function Show-IntegrationStatus {
    Write-ColorOutput "📊 Integration Status Report" $BLUE
    Write-ColorOutput ("=" * 50) $BLUE
    
    # Docker status
    if (Test-DockerRunning) {
        Write-ColorOutput "🐳 Docker: ✅ Running" $GREEN
    } else {
        Write-ColorOutput "🐳 Docker: ❌ Not running" $RED
    }
    
    # Environment file
    if (Test-Path ".env") {
        Write-ColorOutput "🔧 Environment: ✅ Configured" $GREEN
    } else {
        Write-ColorOutput "🔧 Environment: ❌ Missing" $RED
    }
    
    # Services status
    try {
        $services = docker-compose ps --format "table {{.Service}}\t{{.Status}}"
        Write-ColorOutput "🚀 Services:" $BLUE
        $services | ForEach-Object { Write-ColorOutput "   $_" $WHITE }
    }
    catch {
        Write-ColorOutput "🚀 Services: ❌ Cannot check status" $RED
    }
    
    # API endpoints
    Write-ColorOutput "🌐 API Endpoints:" $BLUE
    Write-ColorOutput "   Vault API: http://localhost:8080" $WHITE
    Write-ColorOutput "   Obsidian API: http://localhost:27123" $WHITE
    Write-ColorOutput "   n8n Workflows: http://localhost:5678" $WHITE
    Write-ColorOutput "   Grafana: http://localhost:3000" $WHITE
    
    # Plugin status
    $pluginPath = "D:\Nomade Milionario\.obsidian\plugins\openapi-renderer"
    if (Test-Path $pluginPath) {
        Write-ColorOutput "🔌 Plugin: ✅ Installed" $GREEN
    } else {
        Write-ColorOutput "🔌 Plugin: ❌ Not found" $RED
    }
}

function Show-Usage {
    Write-ColorOutput "🚀 OpenAPI Renderer Plugin Integration Script" $BLUE
    Write-ColorOutput ("=" * 50) $BLUE
    Write-ColorOutput ""
    Write-ColorOutput "Usage: .\integrate-openapi.ps1 [Action] [Options]" $WHITE
    Write-ColorOutput ""
    Write-ColorOutput "Actions:" $YELLOW
    Write-ColorOutput "  full        - Complete integration (default)" $WHITE
    Write-ColorOutput "  docker      - Start Docker Desktop only" $WHITE
    Write-ColorOutput "  services    - Start backend services only" $WHITE
    Write-ColorOutput "  test        - Test API endpoints only" $WHITE
    Write-ColorOutput "  plugin      - Configure plugin only" $WHITE
    Write-ColorOutput "  status      - Show integration status" $WHITE
    Write-ColorOutput ""
    Write-ColorOutput "Options:" $YELLOW
    Write-ColorOutput "  -Force      - Force recreation of configuration files" $WHITE
    Write-ColorOutput "  -Verbose    - Show detailed output" $WHITE
    Write-ColorOutput ""
    Write-ColorOutput "Examples:" $YELLOW
    Write-ColorOutput "  .\integrate-openapi.ps1" $WHITE
    Write-ColorOutput "  .\integrate-openapi.ps1 -Action docker" $WHITE
    Write-ColorOutput "  .\integrate-openapi.ps1 -Action status" $WHITE
    Write-ColorOutput "  .\integrate-openapi.ps1 -Force" $WHITE
}

# Main execution
Write-ColorOutput "🚀 OpenAPI Renderer Plugin Integration" $BLUE
Write-ColorOutput ("=" * 50) $BLUE

switch ($Action.ToLower()) {
    "full" {
        Write-ColorOutput "🔄 Starting full integration process..." $BLUE
        
        # Step 1: Check Docker
        if (-not (Test-DockerRunning)) {
            if (-not (Start-DockerDesktop)) {
                Write-ColorOutput "❌ Failed to start Docker Desktop" $RED
                exit 1
            }
        }
        
        # Step 2: Initialize environment
        Initialize-Environment
        
        # Step 3: Start services
        if (-not (Start-BackendServices)) {
            Write-ColorOutput "❌ Failed to start backend services" $RED
            exit 1
        }
        
        # Step 4: Test endpoints
        if (-not (Test-APIEndpoints)) {
            Write-ColorOutput "⚠️ Some API endpoints are not responding" $YELLOW
        }
        
        # Step 5: Configure plugin
        Configure-Plugin
        
        Write-ColorOutput "🎉 Integration completed!" $GREEN
        Show-IntegrationStatus
    }
    
    "docker" {
        if (-not (Test-DockerRunning)) {
            Start-DockerDesktop
        } else {
            Write-ColorOutput "✅ Docker is already running" $GREEN
        }
    }
    
    "services" {
        if (-not (Test-DockerRunning)) {
            Write-ColorOutput "❌ Docker is not running. Please start Docker first." $RED
            exit 1
        }
        
        Initialize-Environment
        Start-BackendServices
    }
    
    scripts/" {
        Test-APIEndpoints
    }
    
    "plugin" {
        Configure-Plugin
    }
    
    "status" {
        Show-IntegrationStatus
    }
    
    "help" {
        Show-Usage
    }
    
    default {
        Write-ColorOutput "❌ Unknown action: $Action" $RED
        Show-Usage
        exit 1
    }
}

Write-ColorOutput "✅ Script completed successfully!" $GREEN
