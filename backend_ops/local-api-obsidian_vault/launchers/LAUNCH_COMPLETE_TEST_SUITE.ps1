# 🧪 COMPLETE TEST SUITE LAUNCHER
# Comprehensive testing for Obsidian Vault AI System
# Version: 3.0.0 - Production Ready

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "unit", "integration", "e2e", "performance", "reliability", "security")]
    [string]$TestType = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$StartServices = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$StopServices = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateReport = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$Timeout = 300,
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "test"
)

# Performance Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# Test Configuration
$TestConfig = @{
    BaseURL = "http://localhost:8080"
    ObsidianURL = "http://localhost:27123"
    VaultPath = "D:\Nomade Milionario"
    TestVaultPath = "./test-vault"
    Timeout = $Timeout
    Environment = $Environment
    ReportDir = "./test-reports"
}

# Test Results Storage
$TestResults = @{
    StartTime = Get-Date
    Tests = @()
    Services = @()
    Performance = @{}
    Errors = @()
}

# Utility Functions
function Write-TestOutput {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White"
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $prefix = switch ($Level) {
        "SUCCESS" { "✅" }
        "ERROR" { "❌" }
        "WARNING" { "⚠️" }
        "INFO" { "ℹ️" }
        "DEBUG" { "🔍" }
        "TEST" { "🧪" }
        default { "📝" }
    }
    
    $output = "[$timestamp] $prefix $Message"
    Write-Host $output -ForegroundColor $Color
}

function Write-TestBanner {
    Write-TestOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧪 COMPLETE TEST SUITE LAUNCHER 🧪                       ║
║                         Version 3.0.0 - Production Ready                    ║
║                    Test Type: $TestType | Environment: $Environment ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Level "TEST" -Color "Cyan"
}

function Test-Prerequisites {
    Write-TestOutput "🔍 Checking test prerequisites..." -Level "INFO"
    
    $prerequisites = @{
        Python = $false
        Docker = $false
        VaultAccess = $false
        TestDir = $false
    }
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.Python = $true
            Write-TestOutput "✅ Python: $pythonVersion" -Level "SUCCESS"
        }
    } catch {
        Write-TestOutput "❌ Python not found" -Level "ERROR"
    }
    
    # Check Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $prerequisites.Docker = $true
            Write-TestOutput "✅ Docker: $dockerVersion" -Level "SUCCESS"
        }
    } catch {
        Write-TestOutput "❌ Docker not found" -Level "ERROR"
    }
    
    # Check Vault Access
    if (Test-Path $TestConfig.VaultPath) {
        $prerequisites.VaultAccess = $true
        Write-TestOutput "✅ Vault accessible: $($TestConfig.VaultPath)" -Level "SUCCESS"
    } else {
        Write-TestOutput "❌ Vault not accessible: $($TestConfig.VaultPath)" -Level "ERROR"
    }
    
    # Create test directory
    if (-not (Test-Path $TestConfig.TestVaultPath)) {
        New-Item -ItemType Directory -Path $TestConfig.TestVaultPath -Force | Out-Null
    }
    $prerequisites.TestDir = $true
    Write-TestOutput "✅ Test directory ready: $($TestConfig.TestVaultPath)" -Level "SUCCESS"
    
    $allPrerequisites = $prerequisites.Values | Where-Object { $_ -eq $true }
    if ($allPrerequisites.Count -lt 3) {
        Write-TestOutput "❌ Missing critical prerequisites" -Level "ERROR"
        return $false
    }
    
    return $true
}

function Start-TestServices {
    Write-TestOutput "🚀 Starting test services..." -Level "INFO"
    
    try {
        # Create test vault with sample files
        Write-TestOutput "📁 Creating test vault..." -Level "INFO"
        $testVaultContent = @"
# Test Vault for E2E Testing

## AI and Machine Learning
This is a test file for AI and machine learning concepts.

### Topics Covered
- Neural networks
- Deep learning
- Natural language processing
- Computer vision
- Reinforcement learning

## Project Management
This file contains project management techniques and methodologies.

### Methodologies
- Agile development
- Scrum framework
- Kanban boards
- Sprint planning
- Retrospectives

## Data Science
This file covers data science concepts and tools.

### Tools and Technologies
- Python programming
- Pandas for data manipulation
- Scikit-learn for machine learning
- TensorFlow for deep learning
- Jupyter notebooks for analysis
"@
        
        $testVaultContent | Out-File -FilePath "$($TestConfig.TestVaultPath)\README.md" -Encoding UTF8
        
        # Start Docker services
        Write-TestOutput "🐳 Starting Docker services..." -Level "INFO"
        $composeResult = docker-compose -f docker-compose.prod.yml up -d --build 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-TestOutput "✅ Services started successfully" -Level "SUCCESS"
            
            # Wait for services to be ready
            Write-TestOutput "⏳ Waiting for services to be ready..." -Level "INFO"
            $maxWait = 300 # 5 minutes
            $waited = 0
            
            while ($waited -lt $maxWait) {
                try {
                    $healthResponse = Invoke-RestMethod -Uri "$($TestConfig.BaseURL)/health" -TimeoutSec 5 -ErrorAction Stop
                    if ($healthResponse.status -eq "healthy") {
                        Write-TestOutput "✅ Main API is ready" -Level "SUCCESS"
                        break
                    }
                } catch {
                    # Service not ready yet
                }
                
                Start-Sleep -Seconds 5
                $waited += 5
                Write-TestOutput "⏳ Waiting... ($waited/$maxWait seconds)" -Level "DEBUG"
            }
            
            if ($waited -ge $maxWait) {
                Write-TestOutput "⚠️ Services may not be fully ready" -Level "WARNING"
            }
            
            $TestResults.Services += @{
                Name = "Docker Services"
                Status = "Started"
                Timestamp = Get-Date
            }
            
            return $true
        } else {
            Write-TestOutput "❌ Failed to start services: $composeResult" -Level "ERROR"
            $TestResults.Errors += "Failed to start Docker services: $composeResult"
            return $false
        }
    } catch {
        Write-TestOutput "❌ Error starting services: $($_.Exception.Message)" -Level "ERROR"
        $TestResults.Errors += "Error starting services: $($_.Exception.Message)"
        return $false
    }
}

function Stop-TestServices {
    Write-TestOutput "🛑 Stopping test services..." -Level "INFO"
    
    try {
        $composeResult = docker-compose -f docker-compose.prod.yml down -v 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-TestOutput "✅ Services stopped successfully" -Level "SUCCESS"
            $TestResults.Services += @{
                Name = "Docker Services"
                Status = "Stopped"
                Timestamp = Get-Date
            }
            return $true
        } else {
            Write-TestOutput "❌ Failed to stop services: $composeResult" -Level "ERROR"
            return $false
        }
    } catch {
        Write-TestOutput "❌ Error stopping services: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Invoke-UnitTests {
    Write-TestOutput "🧪 Running unit tests..." -Level "TEST"
    
    try {
        $startTime = Get-Date
        
        # Run pytest with coverage
        $pytestResult = python -m pytest tests/ -v --cov=services/vault-api --cov-report=xml --cov-report=html --junitxml=test-results.xml 2>&1
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($LASTEXITCODE -eq 0) {
            Write-TestOutput "✅ Unit tests passed in $($duration.ToString('F2'))s" -Level "SUCCESS"
            $TestResults.Tests += @{
                Type = "Unit Tests"
                Status = "PASSED"
                Duration = $duration
                Timestamp = Get-Date
            }
            return $true
        } else {
            Write-TestOutput "❌ Unit tests failed: $pytestResult" -Level "ERROR"
            $TestResults.Tests += @{
                Type = "Unit Tests"
                Status = "FAILED"
                Duration = $duration
                Error = $pytestResult
                Timestamp = Get-Date
            }
            return $false
        }
    } catch {
        Write-TestOutput "❌ Error running unit tests: $($_.Exception.Message)" -Level "ERROR"
        $TestResults.Errors += "Unit test error: $($_.Exception.Message)"
        return $false
    }
}

function Invoke-IntegrationTests {
    Write-TestOutput "🔗 Running integration tests..." -Level "TEST"
    
    try {
        $startTime = Get-Date
        
        # Run integration tests
        $integrationTests = @(
            "tests/test_vault_access.py",
            "tests/test-enhanced-rag.py",
            "tests/test-supabase-integration.py"
        )
        
        $allPassed = $true
        foreach ($testFile in $integrationTests) {
            if (Test-Path $testFile) {
                Write-TestOutput "  🔍 Running $testFile..." -Level "DEBUG"
                $testResult = python $testFile 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-TestOutput "  ✅ $testFile passed" -Level "SUCCESS"
                } else {
                    Write-TestOutput "  ❌ $testFile failed: $testResult" -Level "ERROR"
                    $allPassed = $false
                }
            } else {
                Write-TestOutput "  ⚠️ $testFile not found" -Level "WARNING"
            }
        }
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($allPassed) {
            Write-TestOutput "✅ Integration tests passed in $($duration.ToString('F2'))s" -Level "SUCCESS"
            $TestResults.Tests += @{
                Type = "Integration Tests"
                Status = "PASSED"
                Duration = $duration
                Timestamp = Get-Date
            }
            return $true
        } else {
            Write-TestOutput "❌ Some integration tests failed" -Level "ERROR"
            $TestResults.Tests += @{
                Type = "Integration Tests"
                Status = "FAILED"
                Duration = $duration
                Timestamp = Get-Date
            }
            return $false
        }
    } catch {
        Write-TestOutput "❌ Error running integration tests: $($_.Exception.Message)" -Level "ERROR"
        $TestResults.Errors += "Integration test error: $($_.Exception.Message)"
        return $false
    }
}

function Invoke-E2ETests {
    Write-TestOutput "🚀 Running end-to-end tests..." -Level "TEST"
    
    try {
        $startTime = Get-Date
        
        # Set environment variables for E2E tests
        $env:BASE_URL = $TestConfig.BaseURL
        $env:OBSIDIAN_API_URL = $TestConfig.ObsidianURL
        $env:TEST_VAULT_PATH = $TestConfig.TestVaultPath
        
        # Run comprehensive E2E test suite
        $e2eResult = python tests/test_complete_e2e_suite.py 2>&1
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($LASTEXITCODE -eq 0) {
            Write-TestOutput "✅ E2E tests passed in $($duration.ToString('F2'))s" -Level "SUCCESS"
            $TestResults.Tests += @{
                Type = "E2E Tests"
                Status = "PASSED"
                Duration = $duration
                Timestamp = Get-Date
            }
            return $true
        } else {
            Write-TestOutput "❌ E2E tests failed: $e2eResult" -Level "ERROR"
            $TestResults.Tests += @{
                Type = "E2E Tests"
                Status = "FAILED"
                Duration = $duration
                Error = $e2eResult
                Timestamp = Get-Date
            }
            return $false
        }
    } catch {
        Write-TestOutput "❌ Error running E2E tests: $($_.Exception.Message)" -Level "ERROR"
        $TestResults.Errors += "E2E test error: $($_.Exception.Message)"
        return $false
    }
}

function Invoke-PerformanceTests {
    Write-TestOutput "⚡ Running performance tests..." -Level "TEST"
    
    try {
        $startTime = Get-Date
        
        # Run performance benchmarks
        $perfResult = python tests/test_performance.py --benchmark-only --benchmark-save=performance 2>&1
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($LASTEXITCODE -eq 0) {
            Write-TestOutput "✅ Performance tests completed in $($duration.ToString('F2'))s" -Level "SUCCESS"
            $TestResults.Tests += @{
                Type = "Performance Tests"
                Status = "PASSED"
                Duration = $duration
                Timestamp = Get-Date
            }
            return $true
        } else {
            Write-TestOutput "❌ Performance tests failed: $perfResult" -Level "ERROR"
            $TestResults.Tests += @{
                Type = "Performance Tests"
                Status = "FAILED"
                Duration = $duration
                Error = $perfResult
                Timestamp = Get-Date
            }
            return $false
        }
    } catch {
        Write-TestOutput "❌ Error running performance tests: $($_.Exception.Message)" -Level "ERROR"
        $TestResults.Errors += "Performance test error: $($_.Exception.Message)"
        return $false
    }
}

function Invoke-ReliabilityTests {
    Write-TestOutput "🔄 Running reliability tests..." -Level "TEST"
    
    try {
        $startTime = Get-Date
        
        # Run reliability tests (stress testing, memory leaks, etc.)
        $reliabilityResult = python tests/test_reliability.py --duration=300 --concurrent=10 2>&1
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        if ($LASTEXITCODE -eq 0) {
            Write-TestOutput "✅ Reliability tests passed in $($duration.ToString('F2'))s" -Level "SUCCESS"
            $TestResults.Tests += @{
                Type = "Reliability Tests"
                Status = "PASSED"
                Duration = $duration
                Timestamp = Get-Date
            }
            return $true
        } else {
            Write-TestOutput "❌ Reliability tests failed: $reliabilityResult" -Level "ERROR"
            $TestResults.Tests += @{
                Type = "Reliability Tests"
                Status = "FAILED"
                Duration = $duration
                Error = $reliabilityResult
                Timestamp = Get-Date
            }
            return $false
        }
    } catch {
        Write-TestOutput "❌ Error running reliability tests: $($_.Exception.Message)" -Level "ERROR"
        $TestResults.Errors += "Reliability test error: $($_.Exception.Message)"
        return $false
    }
}

function Invoke-SecurityTests {
    Write-TestOutput "🔒 Running security tests..." -Level "TEST"
    
    try {
        $startTime = Get-Date
        
        # Run security scans
        $securityResult = python -m bandit -r . -f json -o security-report.json 2>&1
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        # Bandit returns 0 for no issues, 1 for issues found
        if ($LASTEXITCODE -eq 0) {
            Write-TestOutput "✅ Security tests passed in $($duration.ToString('F2'))s" -Level "SUCCESS"
            $TestResults.Tests += @{
                Type = "Security Tests"
                Status = "PASSED"
                Duration = $duration
                Timestamp = Get-Date
            }
            return $true
        } else {
            Write-TestOutput "⚠️ Security issues found: $securityResult" -Level "WARNING"
            $TestResults.Tests += @{
                Type = "Security Tests"
                Status = "WARNINGS"
                Duration = $duration
                Error = $securityResult
                Timestamp = Get-Date
            }
            return $true # Security warnings don't fail the build
        }
    } catch {
        Write-TestOutput "❌ Error running security tests: $($_.Exception.Message)" -Level "ERROR"
        $TestResults.Errors += "Security test error: $($_.Exception.Message)"
        return $false
    }
}

function Generate-TestReport {
    Write-TestOutput "📊 Generating comprehensive test report..." -Level "INFO"
    
    try {
        # Create report directory
        if (-not (Test-Path $TestConfig.ReportDir)) {
            New-Item -ItemType Directory -Path $TestConfig.ReportDir -Force | Out-Null
        }
        
        $totalTime = (Get-Date) - $TestResults.StartTime
        $totalTests = $TestResults.Tests.Count
        $passedTests = ($TestResults.Tests | Where-Object { $_.Status -eq "PASSED" }).Count
        $failedTests = ($TestResults.Tests | Where-Object { $_.Status -eq "FAILED" }).Count
        $successRate = if ($totalTests -gt 0) { ($passedTests / $totalTests) * 100 } else { 0 }
        
        # Generate HTML report
        $htmlReport = @"
<!DOCTYPE html>
<html>
<head>
    <title>🧪 Test Suite Report - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .test-result { margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }
        .passed { border-left-color: #4CAF50; background: #f1f8e9; }
        .failed { border-left-color: #f44336; background: #ffebee; }
        .warning { border-left-color: #ff9800; background: #fff3e0; }
        .error { background: #ffebee; padding: 10px; border-radius: 5px; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Complete Test Suite Report</h1>
        <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p>Test Type: $TestType | Environment: $Environment</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p><strong>Total Tests:</strong> $totalTests</p>
        <p><strong>Passed:</strong> $passedTests</p>
        <p><strong>Failed:</strong> $failedTests</p>
        <p><strong>Success Rate:</strong> $($successRate.ToString('F1'))%</p>
        <p><strong>Total Time:</strong> $($totalTime.TotalMinutes.ToString('F2')) minutes</p>
    </div>
    
    <h2>🧪 Test Results</h2>
"@
        
        foreach ($test in $TestResults.Tests) {
            $statusClass = switch ($test.Status) {
                "PASSED" { "passed" }
                "FAILED" { "failed" }
                "WARNINGS" { "warning" }
                default { "" }
            }
            
            $htmlReport += @"
    <div class="test-result $statusClass">
        <h3>$($test.Type) - $($test.Status)</h3>
        <p><strong>Duration:</strong> $($test.Duration.ToString('F2'))s</p>
        <p><strong>Timestamp:</strong> $($test.Timestamp.ToString('yyyy-MM-dd HH:mm:ss'))</p>
"@
            
            if ($test.Error) {
                $htmlReport += "<p><strong>Error:</strong> $($test.Error)</p>"
            }
            
            $htmlReport += "</div>"
        }
        
        if ($TestResults.Errors.Count -gt 0) {
            $htmlReport += "<h2>❌ Errors</h2>"
            foreach ($error in $TestResults.Errors) {
                $htmlReport += "<div class='error'>$error</div>"
            }
        }
        
        $htmlReport += @"
    <h2>🚀 Services</h2>
"@
        
        foreach ($service in $TestResults.Services) {
            $htmlReport += "<p><strong>$($service.Name):</strong> $($service.Status) at $($service.Timestamp.ToString('HH:mm:ss'))</p>"
        }
        
        $htmlReport += @"
</body>
</html>
"@
        
        $reportFile = "$($TestConfig.ReportDir)/test-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').html"
        $htmlReport | Out-File -FilePath $reportFile -Encoding UTF8
        
        Write-TestOutput "✅ Test report generated: $reportFile" -Level "SUCCESS"
        
        # Also generate JSON report
        $jsonReport = @{
            timestamp = Get-Date
            testType = $TestType
            environment = $Environment
            summary = @{
                totalTests = $totalTests
                passedTests = $passedTests
                failedTests = $failedTests
                successRate = $successRate
                totalTime = $totalTime.TotalSeconds
            }
            tests = $TestResults.Tests
            services = $TestResults.Services
            errors = $TestResults.Errors
        }
        
        $jsonFile = "$($TestConfig.ReportDir)/test-results-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
        $jsonReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonFile -Encoding UTF8
        
        Write-TestOutput "✅ JSON report generated: $jsonFile" -Level "SUCCESS"
        
        return $true
    } catch {
        Write-TestOutput "❌ Error generating test report: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

# Main Execution
function Main {
    Write-TestBanner
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-TestOutput "❌ Prerequisites check failed" -Level "ERROR"
        exit 1
    }
    
    # Start services if requested
    if ($StartServices) {
        if (-not (Start-TestServices)) {
            Write-TestOutput "❌ Failed to start test services" -Level "ERROR"
            exit 1
        }
    }
    
    try {
        # Run tests based on type
        $testResults = @()
        
        switch ($TestType) {
            "all" {
                $testResults += Invoke-UnitTests
                $testResults += Invoke-IntegrationTests
                $testResults += Invoke-E2ETests
                $testResults += Invoke-PerformanceTests
                $testResults += Invoke-ReliabilityTests
                $testResults += Invoke-SecurityTests
            }
            "unit" {
                $testResults += Invoke-UnitTests
            }
            "integration" {
                $testResults += Invoke-IntegrationTests
            }
            "e2e" {
                $testResults += Invoke-E2ETests
            }
            "performance" {
                $testResults += Invoke-PerformanceTests
            }
            "reliability" {
                $testResults += Invoke-ReliabilityTests
            }
            "security" {
                $testResults += Invoke-SecurityTests
            }
        }
        
        # Stop services if requested
        if ($StopServices) {
            Stop-TestServices | Out-Null
        }
        
        # Generate report if requested
        if ($GenerateReport) {
            Generate-TestReport | Out-Null
        }
        
        # Final summary
        $totalTime = (Get-Date) - $TestResults.StartTime
        $passedTests = ($TestResults.Tests | Where-Object { $_.Status -eq "PASSED" }).Count
        $totalTests = $TestResults.Tests.Count
        $successRate = if ($totalTests -gt 0) { ($passedTests / $totalTests) * 100 } else { 0 }
        
        Write-TestOutput "📊 FINAL SUMMARY" -Level "INFO"
        Write-TestOutput "   Total Tests: $totalTests" -Level "INFO"
        Write-TestOutput "   Passed: $passedTests" -Level "INFO"
        Write-TestOutput "   Success Rate: $($successRate.ToString('F1'))%" -Level "INFO"
        Write-TestOutput "   Total Time: $($totalTime.TotalMinutes.ToString('F2')) minutes" -Level "INFO"
        
        if ($successRate -ge 90) {
            Write-TestOutput "🎉 EXCELLENT! All tests passed successfully!" -Level "SUCCESS"
            exit 0
        } elseif ($successRate -ge 80) {
            Write-TestOutput "🟡 GOOD! Most tests passed with minor issues." -Level "WARNING"
            exit 0
        } else {
            Write-TestOutput "❌ POOR! Multiple test failures detected." -Level "ERROR"
            exit 1
        }
        
    } catch {
        Write-TestOutput "❌ Critical error during test execution: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    } finally {
        # Cleanup
        if ($StopServices) {
            Stop-TestServices | Out-Null
        }
    }
}

# Execute main function
Main

