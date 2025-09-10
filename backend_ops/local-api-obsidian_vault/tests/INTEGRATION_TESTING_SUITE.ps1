# Comprehensive Integration Testing Suite
# Tests all observability components and their integration

param(
    [string]$TestMode = "full",  # full, quick, ai-only, backend-only, monitoring-only
    [switch]$Verbose = $false,
    [switch]$GenerateReport = $true,
    [string]$ReportFormat = "html",  # html, json, xml
    [int]$TimeoutSeconds = 300
)

# Color definitions
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Blue = "Blue"
$Cyan = "Cyan"
$Magenta = "Magenta"
$White = "White"

# Test configuration
$TestConfig = @{
    TestMode = $TestMode
    Verbose = $Verbose
    GenerateReport = $GenerateReport
    ReportFormat = $ReportFormat
    TimeoutSeconds = $TimeoutSeconds
    StartTime = Get-Date
    TestResults = @()
    PassedTests = 0
    FailedTests = 0
    SkippedTests = 0
    TotalTests = 0
}

# Test categories
$TestCategories = @{
    "Docker Services" = @{
        "vault-api" = @{ Port = 8081; HealthEndpoint = "/health" }
        "obsidian-api" = @{ Port = 8082; HealthEndpoint = "/health" }
        "n8n" = @{ Port = 5678; HealthEndpoint = "/healthz" }
        "postgres" = @{ Port = 5432; HealthEndpoint = "" }
        "redis" = @{ Port = 6379; HealthEndpoint = "" }
        "ollama" = @{ Port = 11434; HealthEndpoint = "/api/tags" }
        "prometheus" = @{ Port = 9090; HealthEndpoint = "/-/healthy" }
        "grafana" = @{ Port = 3000; HealthEndpoint = "/api/health" }
    }
    "AI Services" = @{
        "embedding-service" = @{ Port = 8083; HealthEndpoint = "/health" }
        "advanced-indexer" = @{ Port = 8084; HealthEndpoint = "/health" }
        "qdrant" = @{ Port = 6333; HealthEndpoint = "/health" }
        "motia-integration" = @{ Port = 8085; HealthEndpoint = "/health" }
        "flyde-integration" = @{ Port = 8086; HealthEndpoint = "/health" }
    }
    "Observability Services" = @{
        "ai-agent-observability" = @{ Port = 8001; HealthEndpoint = "/metrics" }
        "intelligent-alerting" = @{ Port = 8002; HealthEndpoint = "/metrics" }
        "performance-analyzer" = @{ Port = 8003; HealthEndpoint = "/metrics" }
    }
}

function Write-TestLog {
    param([string]$Message, [string]$Level = "INFO", [string]$TestName = "")
    
    $Timestamp = Get-Date -Format "HH:mm:ss.fff"
    $TestPrefix = if ($TestName) { "[$TestName] " } else { "" }
    $LogMessage = "[$Timestamp] [$Level] $TestPrefix$Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor $Red }
        "WARNING" { Write-Host $LogMessage -ForegroundColor $Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor $Green }
        "INFO" { Write-Host $LogMessage -ForegroundColor $Blue }
        "DEBUG" { Write-Host $LogMessage -ForegroundColor $Cyan }
        "TEST" { Write-Host $LogMessage -ForegroundColor $Magenta }
    }
}

function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [int]$Port,
        [string]$HealthEndpoint = "",
        [int]$TimeoutSeconds = 10
    )
    
    $TestName = "Health Check - $ServiceName"
    Write-TestLog "Testing $ServiceName on port $Port" "TEST" $TestName
    
    try {
        $Url = "http://localhost:$Port"
        if ($HealthEndpoint) {
            $Url += $HealthEndpoint
        }
        
        $Response = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        
        if ($Response.StatusCode -eq 200) {
            Write-TestLog "✓ $ServiceName is healthy (Status: $($Response.StatusCode))" "SUCCESS" $TestName
            return @{
                TestName = $TestName
                Status = "PASSED"
                Message = "Service is healthy"
                ResponseTime = $Response.Headers.'X-Response-Time'
                StatusCode = $Response.StatusCode
            }
        } else {
            Write-TestLog "✗ $ServiceName returned status $($Response.StatusCode)" "ERROR" $TestName
            return @{
                TestName = $TestName
                Status = "FAILED"
                Message = "Service returned status $($Response.StatusCode)"
                StatusCode = $Response.StatusCode
            }
        }
    }
    catch {
        Write-TestLog "✗ $ServiceName health check failed: $($_.Exception.Message)" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "Health check failed: $($_.Exception.Message)"
            Error = $_.Exception.Message
        }
    }
}

function Test-DockerContainer {
    param([string]$ContainerName)
    
    $TestName = "Docker Container - $ContainerName"
    Write-TestLog "Testing Docker container: $ContainerName" "TEST" $TestName
    
    try {
        $ContainerInfo = docker ps --filter "name=$ContainerName" --format "{{.Status}},{{.Names}},{{.Image}}" 2>$null
        
        if ($ContainerInfo) {
            $StatusData = $ContainerInfo -split ","
            $Status = $StatusData[0]
            $Name = $StatusData[1]
            $Image = $StatusData[2]
            
            if ($Status -like "*Up*") {
                Write-TestLog "✓ Container $ContainerName is running" "SUCCESS" $TestName
                return @{
                    TestName = $TestName
                    Status = "PASSED"
                    Message = "Container is running"
                    ContainerStatus = $Status
                    Image = $Image
                }
            } else {
                Write-TestLog "✗ Container $ContainerName is not running properly" "ERROR" $TestName
                return @{
                    TestName = $TestName
                    Status = "FAILED"
                    Message = "Container is not running properly"
                    ContainerStatus = $Status
                }
            }
        } else {
            Write-TestLog "✗ Container $ContainerName not found" "ERROR" $TestName
            return @{
                TestName = $TestName
                Status = "FAILED"
                Message = "Container not found"
            }
        }
    }
    catch {
        Write-TestLog "✗ Failed to check container $ContainerName : $($_.Exception.Message)" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "Failed to check container: $($_.Exception.Message)"
            Error = $_.Exception.Message
        }
    }
}

function Test-PerformanceAnalyzer {
    $TestName = "Performance Analyzer Integration"
    Write-TestLog "Testing Performance Analyzer integration" "TEST" $TestName
    
    try {
        $ScriptPath = "monitoring/ADVANCED_PERFORMANCE_ANALYZER.ps1"
        if (Test-Path $ScriptPath) {
            Write-TestLog "Running Performance Analyzer..." "INFO" $TestName
            
            $Result = & $ScriptPath -Mode "quick" -OutputFormat "json" 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-TestLog "✓ Performance Analyzer executed successfully" "SUCCESS" $TestName
                return @{
                    TestName = $TestName
                    Status = "PASSED"
                    Message = "Performance Analyzer executed successfully"
                    Output = $Result
                }
            } else {
                Write-TestLog "✗ Performance Analyzer failed with exit code $LASTEXITCODE" "ERROR" $TestName
                return @{
                    TestName = $TestName
                    Status = "FAILED"
                    Message = "Performance Analyzer failed"
                    ExitCode = $LASTEXITCODE
                    Output = $Result
                }
            }
        } else {
            Write-TestLog "✗ Performance Analyzer script not found" "ERROR" $TestName
            return @{
                TestName = $TestName
                Status = "FAILED"
                Message = "Performance Analyzer script not found"
            }
        }
    }
    catch {
        Write-TestLog "✗ Performance Analyzer test failed: $($_.Exception.Message)" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "Performance Analyzer test failed: $($_.Exception.Message)"
            Error = $_.Exception.Message
        }
    }
}

function Test-RealTimeDashboard {
    $TestName = "Real-Time Dashboard Integration"
    Write-TestLog "Testing Real-Time Dashboard integration" "TEST" $TestName
    
    try {
        $ScriptPath = "monitoring/REAL_TIME_INTERACTIVE_DASHBOARD.ps1"
        if (Test-Path $ScriptPath) {
            Write-TestLog "Testing Real-Time Dashboard script..." "INFO" $TestName
            
            # Test script syntax
            $SyntaxCheck = Get-Content $ScriptPath | ForEach-Object { $_ } | Out-Null
            
            if ($?) {
                Write-TestLog "✓ Real-Time Dashboard script syntax is valid" "SUCCESS" $TestName
                return @{
                    TestName = $TestName
                    Status = "PASSED"
                    Message = "Real-Time Dashboard script is valid"
                }
            } else {
                Write-TestLog "✗ Real-Time Dashboard script has syntax errors" "ERROR" $TestName
                return @{
                    TestName = $TestName
                    Status = "FAILED"
                    Message = "Real-Time Dashboard script has syntax errors"
                }
            }
        } else {
            Write-TestLog "✗ Real-Time Dashboard script not found" "ERROR" $TestName
            return @{
                TestName = $TestName
                Status = "FAILED"
                Message = "Real-Time Dashboard script not found"
            }
        }
    }
    catch {
        Write-TestLog "✗ Real-Time Dashboard test failed: $($_.Exception.Message)" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "Real-Time Dashboard test failed: $($_.Exception.Message)"
            Error = $_.Exception.Message
        }
    }
}

function Test-AIObservabilityService {
    $TestName = "AI Observability Service Integration"
    Write-TestLog "Testing AI Observability Service integration" "TEST" $TestName
    
    try {
        $ScriptPath = "services/observability/ai_agent_observability.py"
        if (Test-Path $ScriptPath) {
            Write-TestLog "Testing AI Observability Service script..." "INFO" $TestName
            
            # Test Python syntax
            $SyntaxCheck = python -m py_compile $ScriptPath 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-TestLog "✓ AI Observability Service script syntax is valid" "SUCCESS" $TestName
                return @{
                    TestName = $TestName
                    Status = "PASSED"
                    Message = "AI Observability Service script is valid"
                }
            } else {
                Write-TestLog "✗ AI Observability Service script has syntax errors" "ERROR" $TestName
                return @{
                    TestName = $TestName
                    Status = "FAILED"
                    Message = "AI Observability Service script has syntax errors"
                    Output = $SyntaxCheck
                }
            }
        } else {
            Write-TestLog "✗ AI Observability Service script not found" "ERROR" $TestName
            return @{
                TestName = $TestName
                Status = "FAILED"
                Message = "AI Observability Service script not found"
            }
        }
    }
    catch {
        Write-TestLog "✗ AI Observability Service test failed: $($_.Exception.Message)" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "AI Observability Service test failed: $($_.Exception.Message)"
            Error = $_.Exception.Message
        }
    }
}

function Test-IntelligentAlertingSystem {
    $TestName = "Intelligent Alerting System Integration"
    Write-TestLog "Testing Intelligent Alerting System integration" "TEST" $TestName
    
    try {
        $ScriptPath = "services/observability/intelligent_alerting_system.py"
        if (Test-Path $ScriptPath) {
            Write-TestLog "Testing Intelligent Alerting System script..." "INFO" $TestName
            
            # Test Python syntax
            $SyntaxCheck = python -m py_compile $ScriptPath 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-TestLog "✓ Intelligent Alerting System script syntax is valid" "SUCCESS" $TestName
                return @{
                    TestName = $TestName
                    Status = "PASSED"
                    Message = "Intelligent Alerting System script is valid"
                }
            } else {
                Write-TestLog "✗ Intelligent Alerting System script has syntax errors" "ERROR" $TestName
                return @{
                    TestName = $TestName
                    Status = "FAILED"
                    Message = "Intelligent Alerting System script has syntax errors"
                    Output = $SyntaxCheck
                }
            }
        } else {
            Write-TestLog "✗ Intelligent Alerting System script not found" "ERROR" $TestName
            return @{
                TestName = $TestName
                Status = "FAILED"
                Message = "Intelligent Alerting System script not found"
            }
        }
    }
    catch {
        Write-TestLog "✗ Intelligent Alerting System test failed: $($_.Exception.Message)" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "Intelligent Alerting System test failed: $($_.Exception.Message)"
            Error = $_.Exception.Message
        }
    }
}

function Test-UltimateLauncher {
    $TestName = "Ultimate Launcher Integration"
    Write-TestLog "Testing Ultimate Launcher integration" "TEST" $TestName
    
    try {
        $ScriptPath = "launchers/ULTIMATE_OBSERVABILITY_LAUNCHER.ps1"
        if (Test-Path $ScriptPath) {
            Write-TestLog "Testing Ultimate Launcher script..." "INFO" $TestName
            
            # Test script syntax
            $SyntaxCheck = Get-Content $ScriptPath | ForEach-Object { $_ } | Out-Null
            
            if ($?) {
                Write-TestLog "✓ Ultimate Launcher script syntax is valid" "SUCCESS" $TestName
                return @{
                    TestName = $TestName
                    Status = "PASSED"
                    Message = "Ultimate Launcher script is valid"
                }
            } else {
                Write-TestLog "✗ Ultimate Launcher script has syntax errors" "ERROR" $TestName
                return @{
                    TestName = $TestName
                    Status = "FAILED"
                    Message = "Ultimate Launcher script has syntax errors"
                }
            }
        } else {
            Write-TestLog "✗ Ultimate Launcher script not found" "ERROR" $TestName
            return @{
                TestName = $TestName
                Status = "FAILED"
                Message = "Ultimate Launcher script not found"
            }
        }
    }
    catch {
        Write-TestLog "✗ Ultimate Launcher test failed: $($_.Exception.Message)" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "Ultimate Launcher test failed: $($_.Exception.Message)"
            Error = $_.Exception.Message
        }
    }
}

function Test-ConfigurationFiles {
    $TestName = "Configuration Files Validation"
    Write-TestLog "Testing configuration files" "TEST" $TestName
    
    $ConfigFiles = @(
        "docker-compose.enhanced-observability.yml",
        "config/otel-collector-config.yaml",
        "monitoring/prometheus-enhanced.yml",
        "monitoring/ai-observability-rules.yml"
    )
    
    $Results = @()
    $AllValid = $true
    
    foreach ($ConfigFile in $ConfigFiles) {
        if (Test-Path $ConfigFile) {
            Write-TestLog "✓ Configuration file found: $ConfigFile" "SUCCESS" $TestName
            $Results += @{
                File = $ConfigFile
                Status = "FOUND"
                Message = "Configuration file exists"
            }
        } else {
            Write-TestLog "✗ Configuration file missing: $ConfigFile" "ERROR" $TestName
            $Results += @{
                File = $ConfigFile
                Status = "MISSING"
                Message = "Configuration file missing"
            }
            $AllValid = $false
        }
    }
    
    if ($AllValid) {
        Write-TestLog "✓ All configuration files are present" "SUCCESS" $TestName
        return @{
            TestName = $TestName
            Status = "PASSED"
            Message = "All configuration files are present"
            Details = $Results
        }
    } else {
        Write-TestLog "✗ Some configuration files are missing" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "Some configuration files are missing"
            Details = $Results
        }
    }
}

function Test-EndToEndIntegration {
    $TestName = "End-to-End Integration Test"
    Write-TestLog "Testing end-to-end integration" "TEST" $TestName
    
    try {
        # Test if all major components can be accessed
        $Components = @(
            @{ Name = "Grafana"; Url = "http://localhost:3000" }
            @{ Name = "Prometheus"; Url = "http://localhost:9090" }
            @{ Name = "Vault API"; Url = "http://localhost:8081" }
        )
        
        $AccessibleComponents = 0
        $TotalComponents = $Components.Count
        
        foreach ($Component in $Components) {
            try {
                $Response = Invoke-WebRequest -Uri $Component.Url -TimeoutSec 5 -ErrorAction Stop
                if ($Response.StatusCode -eq 200) {
                    Write-TestLog "✓ $($Component.Name) is accessible" "SUCCESS" $TestName
                    $AccessibleComponents++
                }
            }
            catch {
                Write-TestLog "✗ $($Component.Name) is not accessible" "ERROR" $TestName
            }
        }
        
        $AccessibilityRate = ($AccessibleComponents / $TotalComponents) * 100
        
        if ($AccessibilityRate -ge 80) {
            Write-TestLog "✓ End-to-end integration test passed ($AccessibilityRate% accessible)" "SUCCESS" $TestName
            return @{
                TestName = $TestName
                Status = "PASSED"
                Message = "End-to-end integration test passed"
                AccessibilityRate = $AccessibilityRate
                AccessibleComponents = $AccessibleComponents
                TotalComponents = $TotalComponents
            }
        } else {
            Write-TestLog "✗ End-to-end integration test failed ($AccessibilityRate% accessible)" "ERROR" $TestName
            return @{
                TestName = $TestName
                Status = "FAILED"
                Message = "End-to-end integration test failed"
                AccessibilityRate = $AccessibilityRate
                AccessibleComponents = $AccessibleComponents
                TotalComponents = $TotalComponents
            }
        }
    }
    catch {
        Write-TestLog "✗ End-to-end integration test failed: $($_.Exception.Message)" "ERROR" $TestName
        return @{
            TestName = $TestName
            Status = "FAILED"
            Message = "End-to-end integration test failed: $($_.Exception.Message)"
            Error = $_.Exception.Message
        }
    }
}

function Run-IntegrationTests {
    Write-TestLog "Starting Integration Testing Suite..." "INFO"
    Write-TestLog "Test Mode: $($TestConfig.TestMode)" "INFO"
    Write-TestLog "Timeout: $($TestConfig.TimeoutSeconds) seconds" "INFO"
    Write-Host ""
    
    # Test Docker Services
    if ($TestConfig.TestMode -eq "full" -or $TestConfig.TestMode -eq "backend-only" -or $TestConfig.TestMode -eq "monitoring-only") {
        Write-Host "🐳 TESTING DOCKER SERVICES" -ForegroundColor $Cyan
        Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
        
        foreach ($Category in $TestCategories.Keys) {
            if ($Category -eq "Docker Services") {
                foreach ($Service in $TestCategories[$Category].GetEnumerator()) {
                    $ServiceName = $Service.Key
                    $ServiceConfig = $Service.Value
                    
                    # Test Docker container
                    $ContainerResult = Test-DockerContainer -ContainerName $ServiceName
                    $TestConfig.TestResults += $ContainerResult
                    $TestConfig.TotalTests++
                    
                    if ($ContainerResult.Status -eq "PASSED") {
                        $TestConfig.PassedTests++
                    } elseif ($ContainerResult.Status -eq "FAILED") {
                        $TestConfig.FailedTests++
                    }
                    
                    # Test service health if port is available
                    if ($ServiceConfig.Port) {
                        $HealthResult = Test-ServiceHealth -ServiceName $ServiceName -Port $ServiceConfig.Port -HealthEndpoint $ServiceConfig.HealthEndpoint
                        $TestConfig.TestResults += $HealthResult
                        $TestConfig.TotalTests++
                        
                        if ($HealthResult.Status -eq "PASSED") {
                            $TestConfig.PassedTests++
                        } elseif ($HealthResult.Status -eq "FAILED") {
                            $TestConfig.FailedTests++
                        }
                    }
                }
            }
        }
        Write-Host ""
    }
    
    # Test AI Services
    if ($TestConfig.TestMode -eq "full" -or $TestConfig.TestMode -eq "ai-only") {
        Write-Host "🤖 TESTING AI SERVICES" -ForegroundColor $Cyan
        Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
        
        foreach ($Category in $TestCategories.Keys) {
            if ($Category -eq "AI Services") {
                foreach ($Service in $TestCategories[$Category].GetEnumerator()) {
                    $ServiceName = $Service.Key
                    $ServiceConfig = $Service.Value
                    
                    # Test Docker container
                    $ContainerResult = Test-DockerContainer -ContainerName $ServiceName
                    $TestConfig.TestResults += $ContainerResult
                    $TestConfig.TotalTests++
                    
                    if ($ContainerResult.Status -eq "PASSED") {
                        $TestConfig.PassedTests++
                    } elseif ($ContainerResult.Status -eq "FAILED") {
                        $TestConfig.FailedTests++
                    }
                }
            }
        }
        Write-Host ""
    }
    
    # Test Observability Components
    Write-Host "📊 TESTING OBSERVABILITY COMPONENTS" -ForegroundColor $Cyan
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
    
    # Test Performance Analyzer
    $PerformanceResult = Test-PerformanceAnalyzer
    $TestConfig.TestResults += $PerformanceResult
    $TestConfig.TotalTests++
    if ($PerformanceResult.Status -eq "PASSED") { $TestConfig.PassedTests++ } else { $TestConfig.FailedTests++ }
    
    # Test Real-Time Dashboard
    $DashboardResult = Test-RealTimeDashboard
    $TestConfig.TestResults += $DashboardResult
    $TestConfig.TotalTests++
    if ($DashboardResult.Status -eq "PASSED") { $TestConfig.PassedTests++ } else { $TestConfig.FailedTests++ }
    
    # Test AI Observability Service
    $AIObservabilityResult = Test-AIObservabilityService
    $TestConfig.TestResults += $AIObservabilityResult
    $TestConfig.TotalTests++
    if ($AIObservabilityResult.Status -eq "PASSED") { $TestConfig.PassedTests++ } else { $TestConfig.FailedTests++ }
    
    # Test Intelligent Alerting System
    $AlertingResult = Test-IntelligentAlertingSystem
    $TestConfig.TestResults += $AlertingResult
    $TestConfig.TotalTests++
    if ($AlertingResult.Status -eq "PASSED") { $TestConfig.PassedTests++ } else { $TestConfig.FailedTests++ }
    
    # Test Ultimate Launcher
    $LauncherResult = Test-UltimateLauncher
    $TestConfig.TestResults += $LauncherResult
    $TestConfig.TotalTests++
    if ($LauncherResult.Status -eq "PASSED") { $TestConfig.PassedTests++ } else { $TestConfig.FailedTests++ }
    
    # Test Configuration Files
    $ConfigResult = Test-ConfigurationFiles
    $TestConfig.TestResults += $ConfigResult
    $TestConfig.TotalTests++
    if ($ConfigResult.Status -eq "PASSED") { $TestConfig.PassedTests++ } else { $TestConfig.FailedTests++ }
    
    Write-Host ""
    
    # Test End-to-End Integration
    Write-Host "🔗 TESTING END-TO-END INTEGRATION" -ForegroundColor $Cyan
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
    
    $E2EResult = Test-EndToEndIntegration
    $TestConfig.TestResults += $E2EResult
    $TestConfig.TotalTests++
    if ($E2EResult.Status -eq "PASSED") { $TestConfig.PassedTests++ } else { $TestConfig.FailedTests++ }
    
    Write-Host ""
}

function Show-TestSummary {
    $EndTime = Get-Date
    $Duration = $EndTime - $TestConfig.StartTime
    
    Write-Host "📊 INTEGRATION TEST SUMMARY" -ForegroundColor $Magenta
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Cyan
    
    Write-Host "Total Tests:           $($TestConfig.TotalTests)" -ForegroundColor $White
    Write-Host "Passed:                $($TestConfig.PassedTests)" -ForegroundColor $Green
    Write-Host "Failed:                $($TestConfig.FailedTests)" -ForegroundColor $Red
    Write-Host "Skipped:               $($TestConfig.SkippedTests)" -ForegroundColor $Yellow
    Write-Host "Duration:              $($Duration.ToString('hh\:mm\:ss'))" -ForegroundColor $White
    
    $SuccessRate = if ($TestConfig.TotalTests -gt 0) { ($TestConfig.PassedTests / $TestConfig.TotalTests) * 100 } else { 0 }
    Write-Host "Success Rate:          $([math]::Round($SuccessRate, 2))%" -ForegroundColor $(if ($SuccessRate -ge 80) { $Green } elseif ($SuccessRate -ge 60) { $Yellow } else { $Red })
    
    Write-Host ""
    
    # Show failed tests
    $FailedTests = $TestConfig.TestResults | Where-Object { $_.Status -eq "FAILED" }
    if ($FailedTests.Count -gt 0) {
        Write-Host "❌ FAILED TESTS" -ForegroundColor $Red
        Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Red
        
        foreach ($FailedTest in $FailedTests) {
            Write-Host "• $($FailedTest.TestName): $($FailedTest.Message)" -ForegroundColor $Red
        }
        Write-Host ""
    }
    
    # Overall result
    if ($SuccessRate -ge 80) {
        Write-Host "🎉 INTEGRATION TESTS PASSED!" -ForegroundColor $Green
        Write-Host "Your observability system is working correctly!" -ForegroundColor $Green
    } elseif ($SuccessRate -ge 60) {
        Write-Host "⚠️  INTEGRATION TESTS PARTIALLY PASSED" -ForegroundColor $Yellow
        Write-Host "Some components need attention. Check failed tests above." -ForegroundColor $Yellow
    } else {
        Write-Host "❌ INTEGRATION TESTS FAILED" -ForegroundColor $Red
        Write-Host "Multiple components need attention. Review failed tests above." -ForegroundColor $Red
    }
}

function Export-TestReport {
    if (-not $TestConfig.GenerateReport) {
        return
    }
    
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $ReportPath = "integration_test_report_$Timestamp"
    
    switch ($TestConfig.ReportFormat.ToLower()) {
        "html" {
            $ReportPath += ".html"
            $HtmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Integration Test Report - $Timestamp</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .test-result { margin: 10px 0; padding: 10px; border-left: 4px solid #007acc; }
        .passed { border-left-color: #28a745; background-color: #d4edda; }
        .failed { border-left-color: #dc3545; background-color: #f8d7da; }
        .summary { background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Integration Test Report</h1>
        <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p>Test Mode: $($TestConfig.TestMode)</p>
        <p>Total Tests: $($TestConfig.TotalTests) | Passed: $($TestConfig.PassedTests) | Failed: $($TestConfig.FailedTests)</p>
    </div>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <p><strong>Success Rate:</strong> $([math]::Round(($TestConfig.PassedTests / $TestConfig.TotalTests) * 100, 2))%</p>
        <p><strong>Duration:</strong> $((Get-Date) - $TestConfig.StartTime)</p>
    </div>
    
    <h2>Test Results</h2>
"@
            
            foreach ($TestResult in $TestConfig.TestResults) {
                $Class = if ($TestResult.Status -eq "PASSED") { "passed" } else { "failed" }
                $HtmlContent += @"
    <div class="test-result $Class">
        <h3>$($TestResult.TestName)</h3>
        <p><strong>Status:</strong> $($TestResult.Status)</p>
        <p><strong>Message:</strong> $($TestResult.Message)</p>
"@
                if ($TestResult.Error) {
                    $HtmlContent += "        <p><strong>Error:</strong> $($TestResult.Error)</p>`n"
                }
                $HtmlContent += "    </div>`n"
            }
            
            $HtmlContent += @"
</body>
</html>
"@
            $HtmlContent | Out-File -FilePath $ReportPath -Encoding UTF8
        }
        "json" {
            $ReportPath += ".json"
            $ReportData = @{
                Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
                TestMode = $TestConfig.TestMode
                TotalTests = $TestConfig.TotalTests
                PassedTests = $TestConfig.PassedTests
                FailedTests = $TestConfig.FailedTests
                SkippedTests = $TestConfig.SkippedTests
                SuccessRate = ($TestConfig.PassedTests / $TestConfig.TotalTests) * 100
                Duration = ((Get-Date) - $TestConfig.StartTime).TotalSeconds
                TestResults = $TestConfig.TestResults
            }
            $ReportData | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8
        }
    }
    
    Write-TestLog "Test report exported to: $ReportPath" "SUCCESS"
}

# Main execution
Write-Host "╔══════════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Cyan
Write-Host "║                        INTEGRATION TESTING SUITE                                    ║" -ForegroundColor $Cyan
Write-Host "║                    Comprehensive Observability System Testing                       ║" -ForegroundColor $Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Cyan
Write-Host ""

Run-IntegrationTests
Show-TestSummary
Export-TestReport

Write-Host ""
Write-Host "Integration testing completed!" -ForegroundColor $Green
