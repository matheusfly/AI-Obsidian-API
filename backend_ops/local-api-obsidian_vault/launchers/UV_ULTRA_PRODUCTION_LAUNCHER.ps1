# 🚀 UV ULTRA PRODUCTION LAUNCHER
# Ultra-fast, production-ready server with UV optimization
# Version: 3.0.0 - Maximum Performance

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory=$false)]
    [switch]$UltraFast = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Testing = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Monitoring = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8080,
    
    [Parameter(Mandatory=$false)]
    [int]$Workers = 0,
    
    [Parameter(Mandatory=$false)]
    [string]$VaultPath = "D:\Nomade Milionario",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# Performance Configuration
$PerfConfig = @{
    Environment = $Environment
    Port = $Port
    VaultPath = $VaultPath
    UltraFast = $UltraFast
    Testing = $Testing
    Monitoring = $Monitoring
    Verbose = $Verbose
    Workers = if ($Workers -gt 0) { $Workers } else { if ($Environment -eq "production") { 4 } else { 1 } }
    Threads = if ($Environment -eq "production") { 8 } else { 2 }
    MemoryLimit = if ($Environment -eq "production") { "2G" } else { "512M" }
    Timeout = if ($Environment -eq "production") { 300 } else { 60 }
}

# UV Configuration
$UVConfig = @{
    PythonVersion = "3.11"
    CacheDir = "./python-env/cache"
    LockFile = "./python-env/uv-lock/uv.lock"
    RequirementsFile = "./python-env/requirements/production.txt"
    VirtualEnv = "./python-env/.venv"
    IndexUrl = "https://pypi.org/simple"
    ExtraIndexUrl = @("https://download.pytorch.org/whl/cpu")
}

# Service Configuration
$ServiceConfig = @{
    VaultAPI = @{
        Port = $PerfConfig.Port
        Host = "0.0.0.0"
        Workers = $PerfConfig.Workers
        Threads = $PerfConfig.Threads
        MemoryLimit = $PerfConfig.MemoryLimit
        Timeout = $PerfConfig.Timeout
    }
    ObsidianAPI = @{
        Port = 27123
        Host = "0.0.0.0"
    }
    Database = @{
        PostgresPort = 5432
        RedisPort = 6379
    }
    Monitoring = @{
        PrometheusPort = 9090
        GrafanaPort = 3004
    }
}

# Color output functions
function Write-UVOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $prefix = switch ($Level) {
        "SUCCESS" { "✅" }
        "ERROR" { "❌" }
        "WARNING" { "⚠️" }
        "INFO" { "ℹ️" }
        "DEBUG" { "🔍" }
        "PERF" { "⚡" }
        "UV" { "🚀" }
        default { "📝" }
    }
    
    $output = "[$timestamp] $prefix $Message"
    Write-Host $output -ForegroundColor $Color
}

function Write-UVBanner {
    Write-UVOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 UV ULTRA PRODUCTION LAUNCHER 🚀                       ║
║                         Version 3.0.0 - Maximum Performance                ║
║                    Environment: $($PerfConfig.Environment) | Port: $($PerfConfig.Port) ║
║                    Ultra Fast: $($PerfConfig.UltraFast) | Workers: $($PerfConfig.Workers) ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Level "UV" -Color "Magenta"
}

function Test-Prerequisites {
    Write-UVOutput "🔍 Checking prerequisites..." -Level "INFO"
    
    $prerequisites = @{
        Python = $false
        UV = $false
        Docker = $false
        VaultAccess = $false
        PortAvailable = $false
    }
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.Python = $true
            Write-UVOutput "✅ Python: $pythonVersion" -Level "SUCCESS"
        }
    } catch {
        Write-UVOutput "❌ Python not found" -Level "ERROR"
    }
    
    # Check UV
    try {
        $uvVersion = uv --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.UV = $true
            Write-UVOutput "✅ UV: $uvVersion" -Level "SUCCESS"
        } else {
            Write-UVOutput "⚠️ UV not found, installing..." -Level "WARNING"
            pip install uv
            $prerequisites.UV = $true
        }
    } catch {
        Write-UVOutput "❌ Failed to install UV" -Level "ERROR"
    }
    
    # Check Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.Docker = $true
            Write-UVOutput "✅ Docker: $dockerVersion" -Level "SUCCESS"
        }
    } catch {
        Write-UVOutput "❌ Docker not found" -Level "ERROR"
    }
    
    # Check Vault Access
    if (Test-Path $PerfConfig.VaultPath) {
        $prerequisites.VaultAccess = $true
        Write-UVOutput "✅ Vault accessible: $($PerfConfig.VaultPath)" -Level "SUCCESS"
    } else {
        Write-UVOutput "❌ Vault not accessible: $($PerfConfig.VaultPath)" -Level "ERROR"
    }
    
    # Check Port Availability
    try {
        $portTest = Test-NetConnection -ComputerName localhost -Port $PerfConfig.Port -InformationLevel Quiet -WarningAction SilentlyContinue
        if (-not $portTest) {
            $prerequisites.PortAvailable = $true
            Write-UVOutput "✅ Port $($PerfConfig.Port) available" -Level "SUCCESS"
        } else {
            Write-UVOutput "⚠️ Port $($PerfConfig.Port) in use" -Level "WARNING"
        }
    } catch {
        Write-UVOutput "⚠️ Could not check port availability" -Level "WARNING"
    }
    
    $allPrerequisites = $prerequisites.Values | Where-Object { $_ -eq $true }
    if ($allPrerequisites.Count -lt 3) {
        Write-UVOutput "❌ Missing critical prerequisites" -Level "ERROR"
        return $false
    }
    
    return $true
}

function Initialize-UVEnvironment {
    Write-UVOutput "🔧 Initializing UV environment..." -Level "UV"
    
    # Create UV directories
    $uvDirs = @(
        $UVConfig.CacheDir,
        "./python-env/uv-lock",
        "./python-env/requirements",
        "./python-env/wheels"
    )
    
    foreach ($dir in $uvDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-UVOutput "Created directory: $dir" -Level "DEBUG"
        }
    }
    
    # Create UV virtual environment
    if (-not (Test-Path $UVConfig.VirtualEnv)) {
        Write-UVOutput "🏗️ Creating UV virtual environment..." -Level "UV"
        $uvCreateResult = uv venv $UVConfig.VirtualEnv --python $UVConfig.PythonVersion 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-UVOutput "✅ UV virtual environment created" -Level "SUCCESS"
        } else {
            Write-UVOutput "❌ Failed to create UV virtual environment: $uvCreateResult" -Level "ERROR"
            return $false
        }
    } else {
        Write-UVOutput "✅ UV virtual environment already exists" -Level "SUCCESS"
    }
    
    # Install dependencies with UV
    Write-UVOutput "📦 Installing dependencies with UV..." -Level "UV"
    
    $uvInstallArgs = @(
        "pip", "install",
        "--system",
        "-r", $UVConfig.RequirementsFile,
        "--cache-dir", $UVConfig.CacheDir,
        "--index-url", $UVConfig.IndexUrl
    )
    
    if ($PerfConfig.UltraFast) {
        $uvInstallArgs += @("--no-deps", "--only-binary=:all:")
        Write-UVOutput "⚡ Ultra-fast mode: using pre-compiled wheels only" -Level "PERF"
    }
    
    $uvInstallResult = & uv $uvInstallArgs 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-UVOutput "✅ Dependencies installed successfully" -Level "SUCCESS"
    } else {
        Write-UVOutput "❌ Failed to install dependencies: $uvInstallResult" -Level "ERROR"
        return $false
    }
    
    # Verify installation
    Write-UVOutput "🔍 Verifying installation..." -Level "DEBUG"
    $verifyResult = uv run python -c "import fastapi, uvicorn; print('Core dependencies verified')" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-UVOutput "✅ Installation verified" -Level "SUCCESS"
    } else {
        Write-UVOutput "⚠️ Installation verification failed: $verifyResult" -Level "WARNING"
    }
    
    return $true
}

function Start-UVOptimizedServices {
    Write-UVOutput "🚀 Starting UV-optimized services..." -Level "UV"
    
    # Start Vault API with UV
    Write-UVOutput "📡 Starting Vault API..." -Level "INFO"
    
    $vaultAPIArgs = @(
        "run", "python", "services/vault-api/main.py",
        "--host", $ServiceConfig.VaultAPI.Host,
        "--port", $ServiceConfig.VaultAPI.Port,
        "--workers", $ServiceConfig.VaultAPI.Workers
    )
    
    if ($PerfConfig.Environment -eq "production") {
        $vaultAPIArgs += @("--production", "--log-level", "info")
    } else {
        $vaultAPIArgs += @("--reload", "--log-level", "debug")
    }
    
    if ($PerfConfig.UltraFast) {
        $vaultAPIArgs += @("--loop", "uvloop", "--http", "httptools")
        Write-UVOutput "⚡ Ultra-fast mode: using uvloop and httptools" -Level "PERF"
    }
    
    # Set environment variables
    $env:VAULT_PATH = $PerfConfig.VaultPath
    $env:ENVIRONMENT = $PerfConfig.Environment
    $env:UV_CACHE_DIR = $UVConfig.CacheDir
    $env:PYTHONPATH = (Get-Location).Path
    
    Write-UVOutput "Command: uv $($vaultAPIArgs -join ' ')" -Level "DEBUG"
    
    # Start Vault API in background
    $vaultAPIJob = Start-Job -Name "VaultAPI" -ScriptBlock {
        param($Args, $WorkingDir)
        Set-Location $WorkingDir
        & uv $Args
    } -ArgumentList $vaultAPIArgs, (Get-Location).Path
    
    # Wait for Vault API to be ready
    Write-UVOutput "⏳ Waiting for Vault API to be ready..." -Level "INFO"
    $maxWait = 60
    $waited = 0
    
    while ($waited -lt $maxWait) {
        try {
            $healthResponse = Invoke-RestMethod -Uri "http://localhost:$($ServiceConfig.VaultAPI.Port)/health" -TimeoutSec 5 -ErrorAction Stop
            if ($healthResponse.status -eq "healthy") {
                Write-UVOutput "✅ Vault API is ready" -Level "SUCCESS"
                break
            }
        } catch {
            # Service not ready yet
        }
        
        Start-Sleep -Seconds 2
        $waited += 2
        Write-UVOutput "⏳ Waiting... ($waited/$maxWait seconds)" -Level "DEBUG"
    }
    
    if ($waited -ge $maxWait) {
        Write-UVOutput "⚠️ Vault API may not be fully ready" -Level "WARNING"
    }
    
    # Start Obsidian API if needed
    if (Test-Path "services/obsidian-api") {
        Write-UVOutput "📚 Starting Obsidian API..." -Level "INFO"
        
        $obsidianAPIJob = Start-Job -Name "ObsidianAPI" -ScriptBlock {
            param($WorkingDir, $VaultPath, $Port)
            Set-Location $WorkingDir
            $env:VAULT_PATH = $VaultPath
            Set-Location "services/obsidian-api"
            npm start
        } -ArgumentList (Get-Location).Path, $PerfConfig.VaultPath, $ServiceConfig.ObsidianAPI.Port
    }
    
    # Start monitoring if requested
    if ($PerfConfig.Monitoring) {
        Write-UVOutput "📊 Starting monitoring services..." -Level "INFO"
        
        $monitoringJob = Start-Job -Name "Monitoring" -ScriptBlock {
            param($WorkingDir, $Environment)
            Set-Location $WorkingDir
            & "production/monitoring/production-monitor.ps1" -Environment $Environment
        } -ArgumentList (Get-Location).Path, $PerfConfig.Environment
    }
    
    return @{
        VaultAPI = $vaultAPIJob
        ObsidianAPI = if (Test-Path "services/obsidian-api") { $obsidianAPIJob } else { $null }
        Monitoring = if ($PerfConfig.Monitoring) { $monitoringJob } else { $null }
    }
}

function Start-TestingSuite {
    Write-UVOutput "🧪 Starting comprehensive testing suite..." -Level "INFO"
    
    $testArgs = @(
        "run", "python", "-m", "pytest",
        "testing/",
        "-v",
        "--cov=services/vault-api",
        "--cov-report=html:testing/reports/coverage-html",
        "--cov-report=xml:testing/reports/coverage.xml",
        "--cov-report=term-missing",
        "--junitxml=testing/reports/junit.xml"
    )
    
    if ($PerfConfig.Environment -eq "production") {
        $testArgs += @("--benchmark-only", "--benchmark-save=performance")
    }
    
    if ($PerfConfig.UltraFast) {
        $testArgs += @("-x", "--tb=short", "--maxfail=5")
        Write-UVOutput "⚡ Ultra-fast testing mode enabled" -Level "PERF"
    }
    
    Write-UVOutput "Command: uv $($testArgs -join ' ')" -Level "DEBUG"
    
    $testResult = & uv $testArgs 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-UVOutput "✅ All tests passed" -Level "SUCCESS"
    } else {
        Write-UVOutput "❌ Some tests failed: $testResult" -Level "ERROR"
    }
    
    return $LASTEXITCODE -eq 0
}

function Show-SystemStatus {
    Write-UVOutput "📊 System Status Report" -Level "INFO"
    Write-UVOutput "======================" -Level "INFO"
    
    # Check UV environment
    if (Test-Path $UVConfig.VirtualEnv) {
        Write-UVOutput "✅ UV Environment: Ready" -Level "SUCCESS"
    } else {
        Write-UVOutput "❌ UV Environment: Not initialized" -Level "ERROR"
    }
    
    # Check Vault API
    try {
        $vaultResponse = Invoke-RestMethod -Uri "http://localhost:$($ServiceConfig.VaultAPI.Port)/health" -TimeoutSec 5
        Write-UVOutput "✅ Vault API: $($vaultResponse.status)" -Level "SUCCESS"
    } catch {
        Write-UVOutput "❌ Vault API: Not accessible" -Level "ERROR"
    }
    
    # Check Obsidian API
    try {
        $obsidianResponse = Invoke-RestMethod -Uri "http://localhost:$($ServiceConfig.ObsidianAPI.Port)/health" -TimeoutSec 5
        Write-UVOutput "✅ Obsidian API: $($obsidianResponse.status)" -Level "SUCCESS"
    } catch {
        Write-UVOutput "⚠️ Obsidian API: Not accessible" -Level "WARNING"
    }
    
    # Show performance metrics
    Write-UVOutput "⚡ Performance Configuration:" -Level "PERF"
    Write-UVOutput "  Workers: $($ServiceConfig.VaultAPI.Workers)" -Level "PERF"
    Write-UVOutput "  Threads: $($ServiceConfig.VaultAPI.Threads)" -Level "PERF"
    Write-UVOutput "  Memory Limit: $($ServiceConfig.VaultAPI.MemoryLimit)" -Level "PERF"
    Write-UVOutput "  Timeout: $($ServiceConfig.VaultAPI.Timeout)s" -Level "PERF"
    
    # Show access URLs
    Write-UVOutput "🌐 Access URLs:" -Level "INFO"
    Write-UVOutput "  Vault API: http://localhost:$($ServiceConfig.VaultAPI.Port)" -Level "INFO"
    Write-UVOutput "  API Docs: http://localhost:$($ServiceConfig.VaultAPI.Port)/docs" -Level "INFO"
    Write-UVOutput "  Obsidian API: http://localhost:$($ServiceConfig.ObsidianAPI.Port)" -Level "INFO"
    
    if ($PerfConfig.Monitoring) {
        Write-UVOutput "  Prometheus: http://localhost:$($ServiceConfig.Monitoring.PrometheusPort)" -Level "INFO"
        Write-UVOutput "  Grafana: http://localhost:$($ServiceConfig.Monitoring.GrafanaPort)" -Level "INFO"
    }
}

function Cleanup-System {
    Write-UVOutput "🧹 Cleaning up system..." -Level "INFO"
    
    # Stop background jobs
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    
    # Clean UV cache if needed
    if ($PerfConfig.UltraFast) {
        Write-UVOutput "🧹 Cleaning UV cache..." -Level "DEBUG"
        uv cache clean
    }
    
    Write-UVOutput "✅ Cleanup completed" -Level "SUCCESS"
}

# Main execution
Write-UVBanner

# Check prerequisites
if (-not (Test-Prerequisites)) {
    Write-UVOutput "❌ Prerequisites check failed" -Level "ERROR"
    exit 1
}

# Initialize UV environment
if (-not (Initialize-UVEnvironment)) {
    Write-UVOutput "❌ UV environment initialization failed" -Level "ERROR"
    exit 1
}

try {
    # Start services or run tests
    if ($PerfConfig.Testing) {
        Start-TestingSuite
    } else {
        $services = Start-UVOptimizedServices
        Show-SystemStatus
        
        Write-UVOutput "🎉 UV-optimized system started successfully!" -Level "SUCCESS"
        Write-UVOutput "Press Ctrl+C to stop the system" -Level "INFO"
        
        # Keep running until interrupted
        try {
            while ($true) {
                Start-Sleep -Seconds 10
                
                # Check if services are still running
                $vaultAPIStatus = Get-Job -Name "VaultAPI" -ErrorAction SilentlyContinue
                if (-not $vaultAPIStatus -or $vaultAPIStatus.State -ne "Running") {
                    Write-UVOutput "⚠️ Vault API job stopped unexpectedly" -Level "WARNING"
                    break
                }
            }
        } catch {
            Write-UVOutput "🛑 System shutdown requested" -Level "INFO"
        }
    }
} catch {
    Write-UVOutput "❌ Critical error: $($_.Exception.Message)" -Level "ERROR"
    exit 1
} finally {
    Cleanup-System
}

Write-UVOutput "🎉 UV Ultra Production Launcher completed!" -Level "SUCCESS"

