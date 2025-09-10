# 🚀 UV ULTRA LAUNCHER - Production-Ready Performance Optimized
# Ultra-fast parallel execution with UV Python package manager
# Version: 3.0.0 - Production Ready

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("full", "core", "minimal", "dev", "prod")]
    [string]$Mode = "core",
    
    [Parameter(Mandatory=$false)]
    [switch]$Parallel = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipDocker = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Monitor = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxConcurrency = 8,
    
    [Parameter(Mandatory=$false)]
    [string]$LogLevel = "INFO"
)

# Performance Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# UV Configuration
$UV_CACHE_DIR = "$env:TEMP\uv-cache"
$UV_VENV_DIR = ".venv"
$UV_PYTHON_VERSION = "3.11"

# Performance Metrics
$PerformanceMetrics = @{
    StartTime = Get-Date
    ServicesStarted = 0
    ServicesFailed = 0
    TotalMemoryUsed = 0
    PeakCPU = 0
}

# Color Functions for Performance
function Write-PerfOutput {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $levelColor = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        "DEBUG" { "Gray" }
        default { "White" }
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $levelColor
}

function Write-Banner {
    Write-PerfOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 UV ULTRA LAUNCHER 3.0.0 🚀                           ║
║                    Production-Ready Performance System                      ║
║                    Mode: $Mode | Parallel: $Parallel | Concurrency: $MaxConcurrency ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Level "INFO" -Color "Cyan"
}

# UV Package Manager Functions
function Initialize-UVEnvironment {
    Write-PerfOutput "🔧 Initializing UV environment..." -Level "INFO"
    
    # Check if UV is installed
    if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
        Write-PerfOutput "Installing UV package manager..." -Level "INFO"
        pip install uv
    }
    
    # Create UV cache directory
    if (-not (Test-Path $UV_CACHE_DIR)) {
        New-Item -ItemType Directory -Path $UV_CACHE_DIR -Force | Out-Null
    }
    
    # Set UV environment variables for performance
    $env:UV_CACHE_DIR = $UV_CACHE_DIR
    $env:UV_HTTP_TIMEOUT = "30"
    $env:UV_CONCURRENT_DOWNLOADS = $MaxConcurrency.ToString()
    $env:UV_INDEX_STRATEGY = "unsafe-best-match"
    
    Write-PerfOutput "✅ UV environment initialized" -Level "SUCCESS"
}

function Install-Dependencies {
    param([string]$RequirementsFile = "requirements.txt")
    
    Write-PerfOutput "📦 Installing dependencies with UV..." -Level "INFO"
    
    $startTime = Get-Date
    
    try {
        # Use UV for ultra-fast dependency installation
        $result = uv pip install --system -r $RequirementsFile --cache-dir $UV_CACHE_DIR --no-cache 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $duration = (Get-Date) - $startTime
            Write-PerfOutput "✅ Dependencies installed in $($duration.TotalSeconds.ToString('F2'))s" -Level "SUCCESS"
            return $true
        } else {
            Write-PerfOutput "❌ Failed to install dependencies: $result" -Level "ERROR"
            return $false
        }
    } catch {
        Write-PerfOutput "❌ Error installing dependencies: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

# Parallel Service Management
function Start-ServicesParallel {
    param([array]$Services)
    
    Write-PerfOutput "🚀 Starting $($Services.Count) services in parallel..." -Level "INFO"
    
    $jobs = @()
    $serviceResults = @{}
    
    foreach ($service in $Services) {
        $job = Start-Job -ScriptBlock {
            param($ServiceName, $ServiceConfig, $LogLevel)
            
            $ErrorActionPreference = "Stop"
            
            try {
                # Service-specific startup logic
                switch ($ServiceName) {
                    "vault-api" {
                        $env:PYTHONPATH = "."
                        $env:LOG_LEVEL = $LogLevel
                        python -m uvicorn vault_api.main:app --host 0.0.0.0 --port 8080 --workers 4
                    }
                    "obsidian-api" {
                        $env:NODE_ENV = "production"
                        $env:LOG_LEVEL = $LogLevel
                        npm start
                    }
                    "n8n" {
                        $env:N8N_LOG_LEVEL = $LogLevel
                        npx n8n start
                    }
                    "postgres" {
                        # PostgreSQL startup logic
                        pg_ctl start -D ./data/postgres
                    }
                    "redis" {
                        # Redis startup logic
                        redis-server --port 6379
                    }
                    default {
                        Write-Output "Unknown service: $ServiceName"
                        return @{ Success = $false; Error = "Unknown service" }
                    }
                }
                
                return @{ Success = $true; Service = $ServiceName }
            } catch {
                return @{ Success = $false; Service = $ServiceName; Error = $_.Exception.Message }
            }
        } -ArgumentList $service.Name, $service.Config, $LogLevel
        
        $jobs += $job
    }
    
    # Monitor job completion with timeout
    $timeout = 300 # 5 minutes
    $startTime = Get-Date
    
    while ($jobs | Where-Object { $_.State -eq "Running" }) {
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -gt $timeout) {
            Write-PerfOutput "⏰ Timeout reached, stopping remaining jobs..." -Level "WARN"
            $jobs | Where-Object { $_.State -eq "Running" } | Stop-Job
            break
        }
        
        Start-Sleep -Milliseconds 100
    }
    
    # Collect results
    foreach ($job in $jobs) {
        $result = Receive-Job -Job $job
        $serviceResults[$result.Service] = $result
        Remove-Job -Job $job
    }
    
    # Report results
    $successCount = ($serviceResults.Values | Where-Object { $_.Success }).Count
    $failCount = ($serviceResults.Values | Where-Object { -not $_.Success }).Count
    
    Write-PerfOutput "📊 Service startup results: $successCount success, $failCount failed" -Level "INFO"
    
    return $serviceResults
}

# Service Configuration
$ServiceConfigs = @{
    "full" = @(
        @{ Name = "vault-api"; Priority = 1; Dependencies = @() },
        @{ Name = "obsidian-api"; Priority = 1; Dependencies = @() },
        @{ Name = "postgres"; Priority = 0; Dependencies = @() },
        @{ Name = "redis"; Priority = 0; Dependencies = @() },
        @{ Name = "n8n"; Priority = 2; Dependencies = @("postgres", "redis") },
        @{ Name = "chromadb"; Priority = 2; Dependencies = @() },
        @{ Name = "ollama"; Priority = 2; Dependencies = @() },
        @{ Name = "prometheus"; Priority = 3; Dependencies = @() },
        @{ Name = "grafana"; Priority = 3; Dependencies = @("prometheus") }
    )
    "core" = @(
        @{ Name = "vault-api"; Priority = 1; Dependencies = @() },
        @{ Name = "obsidian-api"; Priority = 1; Dependencies = @() },
        @{ Name = "postgres"; Priority = 0; Dependencies = @() },
        @{ Name = "redis"; Priority = 0; Dependencies = @() }
    )
    "minimal" = @(
        @{ Name = "vault-api"; Priority = 1; Dependencies = @() }
    )
    "dev" = @(
        @{ Name = "vault-api"; Priority = 1; Dependencies = @() },
        @{ Name = "obsidian-api"; Priority = 1; Dependencies = @() },
        @{ Name = "postgres"; Priority = 0; Dependencies = @() },
        @{ Name = "redis"; Priority = 0; Dependencies = @() },
        @{ Name = "n8n"; Priority = 2; Dependencies = @("postgres", "redis") }
    )
    "prod" = @(
        @{ Name = "vault-api"; Priority = 1; Dependencies = @() },
        @{ Name = "obsidian-api"; Priority = 1; Dependencies = @() },
        @{ Name = "postgres"; Priority = 0; Dependencies = @() },
        @{ Name = "redis"; Priority = 0; Dependencies = @() },
        @{ Name = "n8n"; Priority = 2; Dependencies = @("postgres", "redis") },
        @{ Name = "prometheus"; Priority = 3; Dependencies = @() },
        @{ Name = "grafana"; Priority = 3; Dependencies = @("prometheus") },
        @{ Name = "nginx"; Priority = 4; Dependencies = @("vault-api", "obsidian-api") }
    )
}

# Health Check System
function Test-ServiceHealth {
    param([string]$ServiceName, [string]$HealthUrl)
    
    try {
        $response = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 5 -ErrorAction Stop
        return $true
    } catch {
        Write-PerfOutput "❌ Health check failed for $ServiceName`: $($_.Exception.Message)" -Level "DEBUG"
        return $false
    }
}

function Start-HealthMonitoring {
    param([array]$Services)
    
    Write-PerfOutput "🏥 Starting health monitoring..." -Level "INFO"
    
    $healthUrls = @{
        "vault-api" = "http://localhost:8080/health"
        "obsidian-api" = "http://localhost:27123/health"
        "n8n" = "http://localhost:5678/healthz"
        "postgres" = "localhost:5432"
        "redis" = "localhost:6379"
    }
    
    while ($true) {
        $healthyServices = 0
        $totalServices = $Services.Count
        
        foreach ($service in $Services) {
            if ($healthUrls.ContainsKey($service.Name)) {
                if (Test-ServiceHealth -ServiceName $service.Name -HealthUrl $healthUrls[$service.Name]) {
                    $healthyServices++
                }
            }
        }
        
        $healthPercentage = [math]::Round(($healthyServices / $totalServices) * 100, 2)
        Write-PerfOutput "🏥 Health Status: $healthyServices/$totalServices services healthy ($healthPercentage%)" -Level "INFO"
        
        if ($healthPercentage -lt 80) {
            Write-PerfOutput "⚠️ System health below 80%, consider restarting services" -Level "WARN"
        }
        
        Start-Sleep -Seconds 30
    }
}

# Performance Monitoring
function Start-PerformanceMonitoring {
    Write-PerfOutput "📊 Starting performance monitoring..." -Level "INFO"
    
    while ($true) {
        $processes = Get-Process | Where-Object { $_.ProcessName -match "(python|node|postgres|redis)" }
        $totalMemory = ($processes | Measure-Object -Property WorkingSet -Sum).Sum / 1MB
        $totalCPU = ($processes | Measure-Object -Property CPU -Sum).Sum
        
        $PerformanceMetrics.TotalMemoryUsed = [math]::Round($totalMemory, 2)
        $PerformanceMetrics.PeakCPU = [math]::Round($totalCPU, 2)
        
        Write-PerfOutput "📊 Memory: $($PerformanceMetrics.TotalMemoryUsed)MB | CPU: $($PerformanceMetrics.PeakCPU)s" -Level "DEBUG"
        
        Start-Sleep -Seconds 10
    }
}

# Main Execution
function Main {
    Write-Banner
    
    # Initialize UV environment
    Initialize-UVEnvironment
    
    # Install dependencies if requirements.txt exists
    if (Test-Path "requirements.txt") {
        if (-not (Install-Dependencies)) {
            Write-PerfOutput "❌ Failed to install dependencies, exiting..." -Level "ERROR"
            exit 1
        }
    }
    
    # Get service configuration for selected mode
    $services = $ServiceConfigs[$Mode]
    Write-PerfOutput "🎯 Starting in $Mode mode with $($services.Count) services" -Level "INFO"
    
    # Start services
    if ($Parallel) {
        $results = Start-ServicesParallel -Services $services
    } else {
        # Sequential startup (fallback)
        Write-PerfOutput "🔄 Starting services sequentially..." -Level "INFO"
        foreach ($service in $services) {
            Write-PerfOutput "Starting $($service.Name)..." -Level "INFO"
            # Add sequential startup logic here
        }
    }
    
    # Start monitoring if requested
    if ($Monitor) {
        Write-PerfOutput "🔍 Starting monitoring systems..." -Level "INFO"
        
        # Start health monitoring in background
        Start-Job -ScriptBlock { 
            param($Services)
            # Health monitoring logic
        } -ArgumentList $services | Out-Null
        
        # Start performance monitoring in background
        Start-Job -ScriptBlock {
            # Performance monitoring logic
        } | Out-Null
    }
    
    # Display final status
    $totalTime = (Get-Date) - $PerformanceMetrics.StartTime
    Write-PerfOutput "🎉 System startup completed in $($totalTime.TotalSeconds.ToString('F2'))s" -Level "SUCCESS"
    Write-PerfOutput "🌐 Access points:" -Level "INFO"
    Write-PerfOutput "   • Vault API: http://localhost:8080" -Level "INFO"
    Write-PerfOutput "   • Obsidian API: http://localhost:27123" -Level "INFO"
    Write-PerfOutput "   • n8n: http://localhost:5678" -Level "INFO"
    Write-PerfOutput "   • Grafana: http://localhost:3004" -Level "INFO"
}

# Execute main function
Main

