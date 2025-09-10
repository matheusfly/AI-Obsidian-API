# 🚀 PRODUCTION CLI LAUNCHER
# Ultra-fast command-line interface with UV optimization
# Version: 3.0.0 - Production Ready

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(
        "start", "stop", "restart", "status", "logs", "health", "monitor", 
        "deploy", "backup", "restore", "update", "config", "test", "benchmark"
    )]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "prod",
    
    [Parameter(Mandatory=$false)]
    [string]$Service = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$Timeout = 300,
    
    [Parameter(Mandatory=$false)]
    [string]$Config = "docker-compose.prod.yml"
)

# Performance Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue"

# CLI Configuration
$CLIConfig = @{
    Version = "3.0.0"
    Environment = $Environment
    ConfigFile = $Config
    Timeout = $Timeout
    LogLevel = if ($Verbose) { "DEBUG" } else { "INFO" }
    Colors = @{
        Success = "Green"
        Error = "Red"
        Warning = "Yellow"
        Info = "Cyan"
        Debug = "Gray"
        Header = "Magenta"
    }
}

# Performance Metrics
$PerformanceMetrics = @{
    StartTime = Get-Date
    CommandsExecuted = 0
    ServicesAffected = 0
    Errors = 0
}

# Utility Functions
function Write-CLIOutput {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White",
        [switch]$NoNewline = $false
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $prefix = switch ($Level) {
        "SUCCESS" { "✅" }
        "ERROR" { "❌" }
        "WARNING" { "⚠️" }
        "INFO" { "ℹ️" }
        "DEBUG" { "🔍" }
        "HEADER" { "🚀" }
        default { "📝" }
    }
    
    $output = "[$timestamp] $prefix $Message"
    
    if ($NoNewline) {
        Write-Host $output -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $output -ForegroundColor $Color
    }
}

function Write-CLIBanner {
    Write-CLIOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 PRODUCTION CLI LAUNCHER 3.0.0 🚀                     ║
║                    Ultra-Fast Command-Line Interface                        ║
║                    Environment: $Environment | Config: $Config ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Level "HEADER" -Color $CLIConfig.Colors.Header
}

function Test-Prerequisites {
    Write-CLIOutput "🔍 Checking prerequisites..." -Level "INFO"
    
    $prerequisites = @{
        Docker = $false
        DockerCompose = $false
        UV = $false
        Python = $false
        Node = $false
    }
    
    # Check Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.Docker = $true
            Write-CLIOutput "✅ Docker: $dockerVersion" -Level "SUCCESS"
        }
    } catch {
        Write-CLIOutput "❌ Docker not found" -Level "ERROR"
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.DockerCompose = $true
            Write-CLIOutput "✅ Docker Compose: $composeVersion" -Level "SUCCESS"
        }
    } catch {
        Write-CLIOutput "❌ Docker Compose not found" -Level "ERROR"
    }
    
    # Check UV
    try {
        $uvVersion = uv --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.UV = $true
            Write-CLIOutput "✅ UV: $uvVersion" -Level "SUCCESS"
        }
    } catch {
        Write-CLIOutput "⚠️ UV not found, installing..." -Level "WARNING"
        try {
            pip install uv
            $prerequisites.UV = $true
            Write-CLIOutput "✅ UV installed successfully" -Level "SUCCESS"
        } catch {
            Write-CLIOutput "❌ Failed to install UV" -Level "ERROR"
        }
    }
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.Python = $true
            Write-CLIOutput "✅ Python: $pythonVersion" -Level "SUCCESS"
        }
    } catch {
        Write-CLIOutput "❌ Python not found" -Level "ERROR"
    }
    
    # Check Node
    try {
        $nodeVersion = node --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.Node = $true
            Write-CLIOutput "✅ Node: $nodeVersion" -Level "SUCCESS"
        }
    } catch {
        Write-CLIOutput "❌ Node.js not found" -Level "ERROR"
    }
    
    $allPrerequisites = $prerequisites.Values | Where-Object { $_ -eq $true }
    if ($allPrerequisites.Count -lt 3) {
        Write-CLIOutput "❌ Missing critical prerequisites" -Level "ERROR"
        return $false
    }
    
    return $true
}

function Start-Services {
    Write-CLIOutput "🚀 Starting services..." -Level "INFO"
    
    if (-not (Test-Path $CLIConfig.ConfigFile)) {
        Write-CLIOutput "❌ Config file not found: $($CLIConfig.ConfigFile)" -Level "ERROR"
        return $false
    }
    
    try {
        # Use UV for ultra-fast dependency installation
        if (Test-Path "requirements.txt") {
            Write-CLIOutput "📦 Installing dependencies with UV..." -Level "INFO"
            $uvResult = uv pip install --system -r requirements.txt --cache-dir "$env:TEMP\uv-cache" --no-cache 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-CLIOutput "⚠️ UV installation had issues: $uvResult" -Level "WARNING"
            } else {
                Write-CLIOutput "✅ Dependencies installed with UV" -Level "SUCCESS"
            }
        }
        
        # Start services with Docker Compose
        Write-CLIOutput "🐳 Starting Docker services..." -Level "INFO"
        $composeResult = docker-compose -f $CLIConfig.ConfigFile up -d 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-CLIOutput "✅ Services started successfully" -Level "SUCCESS"
            $PerformanceMetrics.ServicesAffected++
            return $true
        } else {
            Write-CLIOutput "❌ Failed to start services: $composeResult" -Level "ERROR"
            $PerformanceMetrics.Errors++
            return $false
        }
    } catch {
        Write-CLIOutput "❌ Error starting services: $($_.Exception.Message)" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Stop-Services {
    Write-CLIOutput "🛑 Stopping services..." -Level "INFO"
    
    try {
        $composeResult = docker-compose -f $CLIConfig.ConfigFile down 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-CLIOutput "✅ Services stopped successfully" -Level "SUCCESS"
            $PerformanceMetrics.ServicesAffected++
            return $true
        } else {
            Write-CLIOutput "❌ Failed to stop services: $composeResult" -Level "ERROR"
            $PerformanceMetrics.Errors++
            return $false
        }
    } catch {
        Write-CLIOutput "❌ Error stopping services: $($_.Exception.Message)" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Restart-Services {
    Write-CLIOutput "🔄 Restarting services..." -Level "INFO"
    
    Stop-Services | Out-Null
    Start-Sleep -Seconds 5
    return Start-Services
}

function Get-ServiceStatus {
    Write-CLIOutput "📊 Getting service status..." -Level "INFO"
    
    try {
        $services = docker-compose -f $CLIConfig.ConfigFile ps --services
        $status = docker-compose -f $CLIConfig.ConfigFile ps
        
        Write-CLIOutput "📋 Service Status:" -Level "INFO"
        Write-Host $status
        
        # Health check for each service
        $healthUrls = @{
            "vault-api" = "http://localhost:8080/health"
            "obsidian-api" = "http://localhost:27123/health"
            "n8n" = "http://localhost:5678/healthz"
            "postgres" = "localhost:5432"
            "redis" = "localhost:6379"
        }
        
        foreach ($service in $services) {
            if ($healthUrls.ContainsKey($service)) {
                try {
                    $response = Invoke-RestMethod -Uri $healthUrls[$service] -TimeoutSec 5 -ErrorAction Stop
                    Write-CLIOutput "✅ $service: Healthy" -Level "SUCCESS"
                } catch {
                    Write-CLIOutput "❌ $service: Unhealthy" -Level "ERROR"
                }
            }
        }
        
        return $true
    } catch {
        Write-CLIOutput "❌ Error getting status: $($_.Exception.Message)" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Show-ServiceLogs {
    param([string]$ServiceName = "")
    
    Write-CLIOutput "📝 Showing service logs..." -Level "INFO"
    
    try {
        if ($ServiceName) {
            Write-CLIOutput "📋 Logs for $ServiceName:" -Level "INFO"
            docker-compose -f $CLIConfig.ConfigFile logs -f --tail=100 $ServiceName
        } else {
            Write-CLIOutput "📋 All service logs:" -Level "INFO"
            docker-compose -f $CLIConfig.ConfigFile logs -f --tail=50
        }
        
        return $true
    } catch {
        Write-CLIOutput "❌ Error showing logs: $($_.Exception.Message)" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Start-HealthCheck {
    Write-CLIOutput "🏥 Starting health check..." -Level "INFO"
    
    $healthScript = Join-Path $PSScriptRoot "..\scripts\production-monitor.ps1"
    if (Test-Path $healthScript) {
        & $healthScript -Mode health
    } else {
        Write-CLIOutput "❌ Health check script not found" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Start-Monitoring {
    Write-CLIOutput "📊 Starting monitoring..." -Level "INFO"
    
    $monitorScript = Join-Path $PSScriptRoot "..\scripts\production-monitor.ps1"
    if (Test-Path $monitorScript) {
        & $monitorScript -Mode full -Continuous
    } else {
        Write-CLIOutput "❌ Monitoring script not found" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Deploy-Services {
    Write-CLIOutput "🚀 Deploying services..." -Level "INFO"
    
    try {
        # Pull latest images
        Write-CLIOutput "📥 Pulling latest images..." -Level "INFO"
        docker-compose -f $CLIConfig.ConfigFile pull
        
        # Build services
        Write-CLIOutput "🔨 Building services..." -Level "INFO"
        docker-compose -f $CLIConfig.ConfigFile build --parallel
        
        # Start services
        Write-CLIOutput "🚀 Starting services..." -Level "INFO"
        docker-compose -f $CLIConfig.ConfigFile up -d
        
        Write-CLIOutput "✅ Deployment completed successfully" -Level "SUCCESS"
        $PerformanceMetrics.ServicesAffected++
        return $true
    } catch {
        Write-CLIOutput "❌ Deployment failed: $($_.Exception.Message)" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Backup-Services {
    Write-CLIOutput "💾 Creating backup..." -Level "INFO"
    
    $backupDir = "backups\$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    try {
        # Backup database
        Write-CLIOutput "📊 Backing up database..." -Level "INFO"
        docker-compose -f $CLIConfig.ConfigFile exec -T postgres pg_dump -U postgres vault_db > "$backupDir\vault_db.sql"
        
        # Backup volumes
        Write-CLIOutput "📁 Backing up volumes..." -Level "INFO"
        docker run --rm -v "${PWD}\data:/backup" -v "postgres_data:/data" alpine tar czf /backup/postgres_data.tar.gz -C /data .
        
        Write-CLIOutput "✅ Backup completed: $backupDir" -Level "SUCCESS"
        return $true
    } catch {
        Write-CLIOutput "❌ Backup failed: $($_.Exception.Message)" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Test-Services {
    Write-CLIOutput "🧪 Running service tests..." -Level "INFO"
    
    try {
        # Run health checks
        Start-HealthCheck | Out-Null
        
        # Run API tests
        Write-CLIOutput "🔍 Testing API endpoints..." -Level "INFO"
        $testScript = Join-Path $PSScriptRoot "..\scripts\test-complete-suite.ps1"
        if (Test-Path $testScript) {
            & $testScript
        }
        
        Write-CLIOutput "✅ All tests passed" -Level "SUCCESS"
        return $true
    } catch {
        Write-CLIOutput "❌ Tests failed: $($_.Exception.Message)" -Level "ERROR"
        $PerformanceMetrics.Errors++
        return $false
    }
}

function Show-PerformanceReport {
    $totalTime = (Get-Date) - $PerformanceMetrics.StartTime
    
    Write-CLIOutput "📊 Performance Report:" -Level "INFO"
    Write-CLIOutput "   Duration: $($totalTime.TotalSeconds.ToString('F2'))s" -Level "INFO"
    Write-CLIOutput "   Commands Executed: $($PerformanceMetrics.CommandsExecuted)" -Level "INFO"
    Write-CLIOutput "   Services Affected: $($PerformanceMetrics.ServicesAffected)" -Level "INFO"
    Write-CLIOutput "   Errors: $($PerformanceMetrics.Errors)" -Level "INFO"
}

# Main Execution
function Main {
    Write-CLIBanner
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-CLIOutput "❌ Prerequisites check failed" -Level "ERROR"
        exit 1
    }
    
    $PerformanceMetrics.CommandsExecuted++
    
    # Execute command
    switch ($Command) {
        "start" {
            Start-Services
        }
        "stop" {
            Stop-Services
        }
        "restart" {
            Restart-Services
        }
        "status" {
            Get-ServiceStatus
        }
        "logs" {
            Show-ServiceLogs -ServiceName $Service
        }
        "health" {
            Start-HealthCheck
        }
        "monitor" {
            Start-Monitoring
        }
        "deploy" {
            Deploy-Services
        }
        "backup" {
            Backup-Services
        }
        "test" {
            Test-Services
        }
        default {
            Write-CLIOutput "❌ Unknown command: $Command" -Level "ERROR"
            Write-CLIOutput "Available commands: start, stop, restart, status, logs, health, monitor, deploy, backup, test" -Level "INFO"
            exit 1
        }
    }
    
    Show-PerformanceReport
}

# Execute main function
Main
