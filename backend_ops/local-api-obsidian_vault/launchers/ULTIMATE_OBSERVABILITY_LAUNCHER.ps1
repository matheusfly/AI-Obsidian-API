# Ultimate Observability Launcher
# Comprehensive launcher for all observability tools and services

param(
    [string]$Mode = "full",  # full, performance, ai-focused, backend-focused, monitoring-only
    [switch]$SkipDocker = $false,
    [switch]$SkipTests = $false,
    [switch]$SkipAI = $false,
    [switch]$SkipBackend = $false,
    [switch]$RealTimeDashboard = $false,
    [switch]$PerformanceAnalysis = $false,
    [switch]$IntelligentAlerts = $false,
    [int]$Port = 8080,
    [string]$LogLevel = "INFO"
)

# Color definitions
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Blue = "Blue"
$Cyan = "Cyan"
$Magenta = "Magenta"
$White = "White"

# Global configuration
$Config = @{
    Mode = $Mode
    Port = $Port
    LogLevel = $LogLevel
    SkipDocker = $SkipDocker
    SkipTests = $SkipTests
    SkipAI = $SkipAI
    SkipBackend = $SkipBackend
    RealTimeDashboard = $RealTimeDashboard
    PerformanceAnalysis = $PerformanceAnalysis
    IntelligentAlerts = $IntelligentAlerts
    
    Services = @{
        Backend = @(
            "vault-api", "obsidian-api", "n8n", "postgres", "redis", "nginx"
        )
        AI = @(
            "ollama", "embedding-service", "advanced-indexer", "qdrant", 
            "motia-integration", "flyde-integration"
        )
        Monitoring = @(
            "prometheus", "grafana", "otel-collector"
        )
        Observability = @(
            "ai-agent-observability", "intelligent-alerting", "performance-analyzer"
        )
    }
    
    Scripts = @{
        PerformanceAnalyzer = "monitoring/ADVANCED_PERFORMANCE_ANALYZER.ps1"
        RealTimeDashboard = "monitoring/REAL_TIME_INTERACTIVE_DASHBOARD.ps1"
        ComprehensiveTests = "tests/COMPREHENSIVE_TEST_SUITE.ps1"
        CentralizedLogging = "monitoring/CENTRALIZED_LOGGING_DASHBOARD.ps1"
        CICDPipeline = "ci-cd/ENHANCED_CI_CD_PIPELINE.ps1"
        MaintenanceDashboard = "monitoring/CENTRALIZED_MAINTENANCE_DASHBOARD.ps1"
    }
    
    URLs = @{
        Grafana = "http://localhost:3000"
        Prometheus = "http://localhost:9090"
        VaultAPI = "http://localhost:8081"
        ObsidianAPI = "http://localhost:8082"
        N8N = "http://localhost:5678"
        RealTimeDashboard = "http://localhost:8080"
    }
}

function Write-UltimateLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor $Red }
        "WARNING" { Write-Host $LogMessage -ForegroundColor $Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor $Green }
        "INFO" { Write-Host $LogMessage -ForegroundColor $Blue }
        "DEBUG" { Write-Host $LogMessage -ForegroundColor $Cyan }
        "PERFORMANCE" { Write-Host $LogMessage -ForegroundColor $Magenta }
    }
}

function Show-Banner {
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Cyan
    Write-Host "║                        ULTIMATE OBSERVABILITY LAUNCHER                              ║" -ForegroundColor $Cyan
    Write-Host "╠══════════════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $Cyan
    Write-Host "║  🚀 Advanced Performance Monitoring  🤖 AI Agent Observability  📊 Real-time Dashboards ║" -ForegroundColor $White
    Write-Host "║  🔍 Intelligent Alerting  🧪 Comprehensive Testing  📈 CI/CD Observability           ║" -ForegroundColor $White
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Cyan
    Write-Host ""
}

function Show-Configuration {
    Write-Host "🔧 CONFIGURATION" -ForegroundColor $Magenta
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
    
    Write-Host "Mode:                 $($Config.Mode)" -ForegroundColor $White
    Write-Host "Port:                 $($Config.Port)" -ForegroundColor $White
    Write-Host "Log Level:            $($Config.LogLevel)" -ForegroundColor $White
    Write-Host "Skip Docker:          $($Config.SkipDocker)" -ForegroundColor $White
    Write-Host "Skip Tests:           $($Config.SkipTests)" -ForegroundColor $White
    Write-Host "Skip AI:              $($Config.SkipAI)" -ForegroundColor $White
    Write-Host "Skip Backend:         $($Config.SkipBackend)" -ForegroundColor $White
    Write-Host "Real-time Dashboard:  $($Config.RealTimeDashboard)" -ForegroundColor $White
    Write-Host "Performance Analysis: $($Config.PerformanceAnalysis)" -ForegroundColor $White
    Write-Host "Intelligent Alerts:   $($Config.IntelligentAlerts)" -ForegroundColor $White
    Write-Host ""
}

function Test-Prerequisites {
    Write-UltimateLog "Testing prerequisites..." "INFO"
    
    $Prerequisites = @{
        "Docker" = $false
        "Docker Compose" = $false
        "PowerShell" = $false
        "Python" = $false
        "Node.js" = $false
    }
    
    # Test Docker
    try {
        $DockerVersion = docker --version 2>$null
        if ($DockerVersion) {
            $Prerequisites["Docker"] = $true
            Write-UltimateLog "✓ Docker: $DockerVersion" "SUCCESS"
        }
    } catch {
        Write-UltimateLog "✗ Docker not found" "ERROR"
    }
    
    # Test Docker Compose
    try {
        $ComposeVersion = docker-compose --version 2>$null
        if ($ComposeVersion) {
            $Prerequisites["Docker Compose"] = $true
            Write-UltimateLog "✓ Docker Compose: $ComposeVersion" "SUCCESS"
        }
    } catch {
        Write-UltimateLog "✗ Docker Compose not found" "ERROR"
    }
    
    # Test PowerShell
    $Prerequisites["PowerShell"] = $true
    Write-UltimateLog "✓ PowerShell: $($PSVersionTable.PSVersion)" "SUCCESS"
    
    # Test Python
    try {
        $PythonVersion = python --version 2>$null
        if ($PythonVersion) {
            $Prerequisites["Python"] = $true
            Write-UltimateLog "✓ Python: $PythonVersion" "SUCCESS"
        }
    } catch {
        Write-UltimateLog "✗ Python not found" "ERROR"
    }
    
    # Test Node.js
    try {
        $NodeVersion = node --version 2>$null
        if ($NodeVersion) {
            $Prerequisites["Node.js"] = $true
            Write-UltimateLog "✓ Node.js: $NodeVersion" "SUCCESS"
        }
    } catch {
        Write-UltimateLog "✗ Node.js not found" "ERROR"
    }
    
    $MissingPrerequisites = $Prerequisites.GetEnumerator() | Where-Object { -not $_.Value }
    
    if ($MissingPrerequisites.Count -gt 0) {
        Write-UltimateLog "Missing prerequisites: $($MissingPrerequisites.Name -join ', ')" "WARNING"
        return $false
    }
    
    Write-UltimateLog "All prerequisites satisfied" "SUCCESS"
    return $true
}

function Start-DockerServices {
    if ($Config.SkipDocker) {
        Write-UltimateLog "Skipping Docker services as requested" "INFO"
        return
    }
    
    Write-UltimateLog "Starting Docker services..." "INFO"
    
    try {
        # Start the main observability stack
        Write-UltimateLog "Starting enhanced observability stack..." "INFO"
        docker-compose -f docker-compose.enhanced-observability.yml up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-UltimateLog "Enhanced observability stack started successfully" "SUCCESS"
        } else {
            Write-UltimateLog "Failed to start enhanced observability stack" "ERROR"
            return $false
        }
        
        # Wait for services to be ready
        Write-UltimateLog "Waiting for services to be ready..." "INFO"
        Start-Sleep -Seconds 10
        
        # Check service health
        $HealthyServices = 0
        $TotalServices = 0
        
        foreach ($ServiceType in $Config.Services.Keys) {
            foreach ($Service in $Config.Services[$ServiceType]) {
                $TotalServices++
                try {
                    $ContainerStatus = docker ps --filter "name=$Service" --format "{{.Status}}" 2>$null
                    if ($ContainerStatus -and $ContainerStatus -like "*Up*") {
                        $HealthyServices++
                        Write-UltimateLog "✓ $Service is running" "SUCCESS"
                    } else {
                        Write-UltimateLog "✗ $Service is not running" "ERROR"
                    }
                } catch {
                    Write-UltimateLog "✗ Failed to check $Service status" "ERROR"
                }
            }
        }
        
        Write-UltimateLog "Docker services health: $HealthyServices/$TotalServices healthy" "INFO"
        
        if ($HealthyServices -lt $TotalServices * 0.8) {
            Write-UltimateLog "Warning: Less than 80% of services are healthy" "WARNING"
        }
        
        return $true
        
    } catch {
        Write-UltimateLog "Failed to start Docker services: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-AIObservabilityServices {
    if ($Config.SkipAI) {
        Write-UltimateLog "Skipping AI observability services as requested" "INFO"
        return
    }
    
    Write-UltimateLog "Starting AI observability services..." "INFO"
    
    try {
        # Start AI Agent Observability service
        Write-UltimateLog "Starting AI Agent Observability service..." "INFO"
        $AIObservabilityScript = "services/observability/ai_agent_observability.py"
        if (Test-Path $AIObservabilityScript) {
            Start-Process python -ArgumentList $AIObservabilityScript -WindowStyle Hidden
            Write-UltimateLog "AI Agent Observability service started" "SUCCESS"
        } else {
            Write-UltimateLog "AI Agent Observability script not found" "WARNING"
        }
        
        # Start Intelligent Alerting System
        Write-UltimateLog "Starting Intelligent Alerting System..." "INFO"
        $AlertingScript = "services/observability/intelligent_alerting_system.py"
        if (Test-Path $AlertingScript) {
            Start-Process python -ArgumentList $AlertingScript -WindowStyle Hidden
            Write-UltimateLog "Intelligent Alerting System started" "SUCCESS"
        } else {
            Write-UltimateLog "Intelligent Alerting System script not found" "WARNING"
        }
        
        return $true
        
    } catch {
        Write-UltimateLog "Failed to start AI observability services: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-PerformanceAnalysis {
    if (-not $Config.PerformanceAnalysis) {
        Write-UltimateLog "Skipping performance analysis as requested" "INFO"
        return
    }
    
    Write-UltimateLog "Starting performance analysis..." "PERFORMANCE"
    
    try {
        $PerformanceScript = $Config.Scripts.PerformanceAnalyzer
        if (Test-Path $PerformanceScript) {
            Write-UltimateLog "Running advanced performance analyzer..." "PERFORMANCE"
            & $PerformanceScript -Mode $Config.Mode -OutputFormat "json"
            
            if ($LASTEXITCODE -eq 0) {
                Write-UltimateLog "Performance analysis completed successfully" "SUCCESS"
            } else {
                Write-UltimateLog "Performance analysis completed with warnings" "WARNING"
            }
        } else {
            Write-UltimateLog "Performance analyzer script not found" "WARNING"
        }
        
        return $true
        
    } catch {
        Write-UltimateLog "Failed to run performance analysis: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-ComprehensiveTests {
    if ($Config.SkipTests) {
        Write-UltimateLog "Skipping comprehensive tests as requested" "INFO"
        return
    }
    
    Write-UltimateLog "Starting comprehensive test suite..." "INFO"
    
    try {
        $TestScript = $Config.Scripts.ComprehensiveTests
        if (Test-Path $TestScript) {
            Write-UltimateLog "Running comprehensive test suite..." "INFO"
            & $TestScript -Mode $Config.Mode -LogLevel $Config.LogLevel
            
            if ($LASTEXITCODE -eq 0) {
                Write-UltimateLog "All tests passed successfully" "SUCCESS"
            } else {
                Write-UltimateLog "Some tests failed or completed with warnings" "WARNING"
            }
        } else {
            Write-UltimateLog "Comprehensive test script not found" "WARNING"
        }
        
        return $true
        
    } catch {
        Write-UltimateLog "Failed to run comprehensive tests: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-RealTimeDashboard {
    if (-not $Config.RealTimeDashboard) {
        Write-UltimateLog "Skipping real-time dashboard as requested" "INFO"
        return
    }
    
    Write-UltimateLog "Starting real-time interactive dashboard..." "INFO"
    
    try {
        $DashboardScript = $Config.Scripts.RealTimeDashboard
        if (Test-Path $DashboardScript) {
            Write-UltimateLog "Launching real-time dashboard..." "INFO"
            Start-Process powershell -ArgumentList "-File", $DashboardScript, "-Mode", $Config.Mode, "-AutoRefresh", "-Theme", "dark" -WindowStyle Normal
            Write-UltimateLog "Real-time dashboard launched" "SUCCESS"
        } else {
            Write-UltimateLog "Real-time dashboard script not found" "WARNING"
        }
        
        return $true
        
    } catch {
        Write-UltimateLog "Failed to start real-time dashboard: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-ServiceURLs {
    Write-Host "🌐 SERVICE URLs" -ForegroundColor $Magenta
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
    
    foreach ($Service in $Config.URLs.GetEnumerator()) {
        Write-Host "$($Service.Key.PadRight(20)) " -NoNewline -ForegroundColor $White
        Write-Host "$($Service.Value)" -ForegroundColor $Blue
    }
    
    Write-Host ""
    Write-Host "📊 OBSERVABILITY DASHBOARDS" -ForegroundColor $Magenta
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
    Write-Host "Grafana Dashboard:     http://localhost:3000" -ForegroundColor $Blue
    Write-Host "Prometheus Metrics:    http://localhost:9090" -ForegroundColor $Blue
    Write-Host "Real-time Dashboard:   http://localhost:8080" -ForegroundColor $Blue
    Write-Host "AI Observability:      http://localhost:8001" -ForegroundColor $Blue
    Write-Host "Intelligent Alerts:    http://localhost:8002" -ForegroundColor $Blue
    Write-Host ""
}

function Show-QuickCommands {
    Write-Host "⚡ QUICK COMMANDS" -ForegroundColor $Magenta
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
    
    Write-Host "Performance Analysis:" -ForegroundColor $White
    Write-Host "  .\monitoring\ADVANCED_PERFORMANCE_ANALYZER.ps1 -Mode full -RealTime" -ForegroundColor $Yellow
    Write-Host ""
    
    Write-Host "Real-time Dashboard:" -ForegroundColor $White
    Write-Host "  .\monitoring\REAL_TIME_INTERACTIVE_DASHBOARD.ps1 -Mode full -AutoRefresh" -ForegroundColor $Yellow
    Write-Host ""
    
    Write-Host "Comprehensive Tests:" -ForegroundColor $White
    Write-Host "  .\tests\COMPREHENSIVE_TEST_SUITE.ps1 -Mode full -LogLevel INFO" -ForegroundColor $Yellow
    Write-Host ""
    
    Write-Host "Centralized Logging:" -ForegroundColor $White
    Write-Host "  .\monitoring\CENTRALIZED_LOGGING_DASHBOARD.ps1" -ForegroundColor $Yellow
    Write-Host ""
    
    Write-Host "CI/CD Pipeline:" -ForegroundColor $White
    Write-Host "  .\ci-cd\ENHANCED_CI_CD_PIPELINE.ps1" -ForegroundColor $Yellow
    Write-Host ""
    
    Write-Host "Maintenance Dashboard:" -ForegroundColor $White
    Write-Host "  .\monitoring\CENTRALIZED_MAINTENANCE_DASHBOARD.ps1" -ForegroundColor $Yellow
    Write-Host ""
}

function Show-StatusSummary {
    Write-Host "📈 STATUS SUMMARY" -ForegroundColor $Magenta
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
    
    # Check Docker services
    $DockerServices = 0
    $DockerTotal = 0
    
    foreach ($ServiceType in $Config.Services.Keys) {
        foreach ($Service in $Config.Services[$ServiceType]) {
            $DockerTotal++
            try {
                $ContainerStatus = docker ps --filter "name=$Service" --format "{{.Status}}" 2>$null
                if ($ContainerStatus -and $ContainerStatus -like "*Up*") {
                    $DockerServices++
                }
            } catch {
                # Service not running
            }
        }
    }
    
    Write-Host "Docker Services:      $DockerServices/$DockerTotal running" -ForegroundColor $(if ($DockerServices -eq $DockerTotal) { $Green } else { $Yellow })
    
    # Check observability services
    $ObservabilityServices = 0
    $ObservabilityTotal = 3  # AI Observability, Intelligent Alerts, Performance Analyzer
    
    try {
        $AIObservability = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*ai_agent_observability*" }
        if ($AIObservability) { $ObservabilityServices++ }
    } catch { }
    
    try {
        $AlertingSystem = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*intelligent_alerting_system*" }
        if ($AlertingSystem) { $ObservabilityServices++ }
    } catch { }
    
    try {
        $PerformanceAnalyzer = Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*ADVANCED_PERFORMANCE_ANALYZER*" }
        if ($PerformanceAnalyzer) { $ObservabilityServices++ }
    } catch { }
    
    Write-Host "Observability Services: $ObservabilityServices/$ObservabilityTotal running" -ForegroundColor $(if ($ObservabilityServices -eq $ObservabilityTotal) { $Green } else { $Yellow })
    
    # Check dashboards
    $Dashboards = 0
    $DashboardTotal = 2  # Grafana, Real-time Dashboard
    
    try {
        $GrafanaResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($GrafanaResponse.StatusCode -eq 200) { $Dashboards++ }
    } catch { }
    
    try {
        $RealTimeResponse = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($RealTimeResponse.StatusCode -eq 200) { $Dashboards++ }
    } catch { }
    
    Write-Host "Dashboards:           $Dashboards/$DashboardTotal accessible" -ForegroundColor $(if ($Dashboards -eq $DashboardTotal) { $Green } else { $Yellow })
    
    Write-Host ""
}

function Start-UltimateObservability {
    Show-Banner
    Show-Configuration
    
    # Test prerequisites
    if (-not (Test-Prerequisites)) {
        Write-UltimateLog "Prerequisites test failed. Please install missing components." "ERROR"
        return
    }
    
    Write-UltimateLog "Starting Ultimate Observability System..." "INFO"
    
    # Start Docker services
    if (-not (Start-DockerServices)) {
        Write-UltimateLog "Failed to start Docker services" "ERROR"
        return
    }
    
    # Start AI observability services
    if (-not (Start-AIObservabilityServices)) {
        Write-UltimateLog "Failed to start AI observability services" "ERROR"
    }
    
    # Run performance analysis
    if (-not (Start-PerformanceAnalysis)) {
        Write-UltimateLog "Failed to run performance analysis" "ERROR"
    }
    
    # Run comprehensive tests
    if (-not (Start-ComprehensiveTests)) {
        Write-UltimateLog "Failed to run comprehensive tests" "ERROR"
    }
    
    # Start real-time dashboard
    if (-not (Start-RealTimeDashboard)) {
        Write-UltimateLog "Failed to start real-time dashboard" "ERROR"
    }
    
    # Show results
    Write-Host ""
    Show-ServiceURLs
    Show-QuickCommands
    Show-StatusSummary
    
    Write-UltimateLog "Ultimate Observability System startup completed!" "SUCCESS"
    Write-Host ""
    Write-Host "🎉 Your comprehensive observability system is now running!" -ForegroundColor $Green
    Write-Host "   Access the dashboards and monitoring tools using the URLs above." -ForegroundColor $White
    Write-Host "   Use the quick commands to run specific tools and analyses." -ForegroundColor $White
    Write-Host ""
}

# Main execution
Start-UltimateObservability
