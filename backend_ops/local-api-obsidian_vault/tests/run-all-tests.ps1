# Master Test Runner - Execute All Test Suites
param(
    [switch]$Quick = $false,
    [switch]$Integration = $false,
    [switch]$StartServices = $false,
    [switch]$GenerateReport = $false,
    [string]$OutputDir = "test-results"
)

$ErrorActionPreference = "Continue"

# Test configuration
$script:TestConfig = @{
    StartTime = Get-Date
    TotalTests = 0
    TotalPassed = 0
    TotalFailed = 0
    TotalSkipped = 0
    Suites = @()
}

function Write-TestHeader {
    param([string]$Title)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host " $Title " -ForegroundColor Yellow -NoNewline
    Write-Host "=" * (78 - $Title.Length) -ForegroundColor Cyan
}

function Write-TestFooter {
    Write-Host "=" * 80 -ForegroundColor Cyan
}

function Invoke-TestSuite {
    param(
        [string]$Name,
        [string]$Script,
        [hashtable]$Parameters = @{}
    )
    
    Write-TestHeader "RUNNING: $Name"
    
    $suiteResult = @{
        Name = $Name
        StartTime = Get-Date
        EndTime = $null
        ExitCode = 0
        Output = ""
        Passed = 0
        Failed = 0
        Skipped = 0
    }
    
    try {
        $paramString = ""
        foreach ($key in $Parameters.Keys) {
            $value = $Parameters[$key]
            if ($value -is [switch] -and $value) {
                $paramString += " -$key"
            } elseif ($value -isnot [switch]) {
                $paramString += " -$key `"$value`""
            }
        }
        
        Write-Host "Executing: $Script $paramString" -ForegroundColor Blue
        
        $output = & $Script @Parameters 2>&1
        $suiteResult.ExitCode = $LASTEXITCODE
        $suiteResult.Output = $output -join "`n"
        
        # Parse output for test counts
        if ($output -match "Passed:\s*(\d+)") { $suiteResult.Passed = [int]$matches[1] }
        if ($output -match "Failed:\s*(\d+)") { $suiteResult.Failed = [int]$matches[1] }
        if ($output -match "Skipped:\s*(\d+)") { $suiteResult.Skipped = [int]$matches[1] }
        
        $script:TestConfig.TotalPassed += $suiteResult.Passed
        $script:TestConfig.TotalFailed += $suiteResult.Failed
        $script:TestConfig.TotalSkipped += $suiteResult.Skipped
        
        if ($suiteResult.ExitCode -eq 0) {
            Write-Host "✅ $Name completed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ $Name failed with exit code $($suiteResult.ExitCode)" -ForegroundColor Red
        }
        
    } catch {
        $suiteResult.ExitCode = 1
        $suiteResult.Output = $_.Exception.Message
        $script:TestConfig.TotalFailed++
        Write-Host "💥 $Name crashed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    $suiteResult.EndTime = Get-Date
    $script:TestConfig.Suites += $suiteResult
    
    Write-TestFooter
    return $suiteResult
}

function Test-Prerequisites {
    Write-TestHeader "PREREQUISITES CHECK"
    
    $checks = @(
        @{Name="PowerShell Version"; Test={$PSVersionTable.PSVersion.Major -ge 5}},
        @{Name="Docker Available"; Test={docker --version 2>$null}},
        @{Name="Docker Running"; Test={docker info 2>$null}},
        @{Name="Project Structure"; Test={Test-Path "scripts\launch.ps1" -and Test-Path "docker-compose.yml"}},
        @{Name="Vault Path"; Test={Test-Path "D:\Nomade Milionario"}}
    )
    
    $passed = 0
    foreach ($check in $checks) {
        try {
            $result = & $check.Test
            if ($result) {
                Write-Host "✅ $($check.Name)" -ForegroundColor Green
                $passed++
            } else {
                Write-Host "❌ $($check.Name)" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ $($check.Name) - Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host "`nPrerequisites: $passed/$($checks.Count) passed" -ForegroundColor $(if($passed -eq $checks.Count){"Green"}else{"Yellow"})
    Write-TestFooter
    
    return $passed -eq $checks.Count
}

function Start-TestExecution {
    Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧪 OBSIDIAN VAULT AI TEST SUITE 🧪                       ║
║                         Complete System Validation                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

    Write-Host "Test Mode: $(if($Quick){'Quick'}elseif($Integration){'Integration'}else{'Full'})" -ForegroundColor Blue
    Write-Host "Start Services: $StartServices" -ForegroundColor Blue
    Write-Host "Generate Report: $GenerateReport" -ForegroundColor Blue
    Write-Host "Output Directory: $OutputDir" -ForegroundColor Blue
    Write-Host ""
}

function Write-FinalReport {
    $endTime = Get-Date
    $duration = $endTime - $script:TestConfig.StartTime
    $totalTests = $script:TestConfig.TotalPassed + $script:TestConfig.TotalFailed + $script:TestConfig.TotalSkipped
    
    Write-TestHeader "FINAL TEST REPORT"
    
    Write-Host "📊 Test Execution Summary:" -ForegroundColor Yellow
    Write-Host "  Duration: $([math]::Round($duration.TotalMinutes, 2)) minutes" -ForegroundColor Blue
    Write-Host "  Total Tests: $totalTests" -ForegroundColor Blue
    Write-Host "  Passed: $($script:TestConfig.TotalPassed)" -ForegroundColor Green
    Write-Host "  Failed: $($script:TestConfig.TotalFailed)" -ForegroundColor Red
    Write-Host "  Skipped: $($script:TestConfig.TotalSkipped)" -ForegroundColor Yellow
    
    if ($totalTests -gt 0) {
        $successRate = [math]::Round(($script:TestConfig.TotalPassed / $totalTests) * 100, 2)
        Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 90){"Green"}elseif($successRate -ge 70){"Yellow"}else{"Red"})
    }
    
    Write-Host "`n📋 Suite Results:" -ForegroundColor Yellow
    foreach ($suite in $script:TestConfig.Suites) {
        $status = if ($suite.ExitCode -eq 0) { "✅ PASS" } else { "❌ FAIL" }
        $color = if ($suite.ExitCode -eq 0) { "Green" } else { "Red" }
        $suiteDuration = if ($suite.EndTime) { [math]::Round(($suite.EndTime - $suite.StartTime).TotalSeconds, 1) } else { "N/A" }
        Write-Host "  $status $($suite.Name) ($suiteDuration s)" -ForegroundColor $color
    }
    
    if ($GenerateReport) {
        Write-TestReport
    }
    
    Write-TestFooter
    
    # Return overall success
    return $script:TestConfig.TotalFailed -eq 0
}

function Write-TestReport {
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    
    # Generate JSON report
    $jsonReport = @{
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
        duration_minutes = [math]::Round(((Get-Date) - $script:TestConfig.StartTime).TotalMinutes, 2)
        summary = @{
            total = $script:TestConfig.TotalPassed + $script:TestConfig.TotalFailed + $script:TestConfig.TotalSkipped
            passed = $script:TestConfig.TotalPassed
            failed = $script:TestConfig.TotalFailed
            skipped = $script:TestConfig.TotalSkipped
        }
        suites = $script:TestConfig.Suites
    } | ConvertTo-Json -Depth 10
    
    $jsonPath = Join-Path $OutputDir "test-results.json"
    $jsonReport | Out-File -FilePath $jsonPath -Encoding UTF8
    
    # Generate HTML report
    $htmlReport = @"
<!DOCTYPE html>
<html>
<head>
    <title>Obsidian Vault AI Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .metric { background: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }
        .pass { color: green; } .fail { color: red; } .skip { color: orange; }
        .suite { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .suite.pass { border-left: 5px solid green; }
        .suite.fail { border-left: 5px solid red; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Obsidian Vault AI Test Results</h1>
        <p>Generated: $(Get-Date)</p>
        <p>Duration: $([math]::Round(((Get-Date) - $script:TestConfig.StartTime).TotalMinutes, 2)) minutes</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>Total Tests</h3>
            <div>$($script:TestConfig.TotalPassed + $script:TestConfig.TotalFailed + $script:TestConfig.TotalSkipped)</div>
        </div>
        <div class="metric pass">
            <h3>Passed</h3>
            <div>$($script:TestConfig.TotalPassed)</div>
        </div>
        <div class="metric fail">
            <h3>Failed</h3>
            <div>$($script:TestConfig.TotalFailed)</div>
        </div>
        <div class="metric skip">
            <h3>Skipped</h3>
            <div>$($script:TestConfig.TotalSkipped)</div>
        </div>
    </div>
    
    <h2>Test Suites</h2>
"@
    
    foreach ($suite in $script:TestConfig.Suites) {
        $suiteClass = if ($suite.ExitCode -eq 0) { "pass" } else { "fail" }
        $htmlReport += @"
    <div class="suite $suiteClass">
        <h3>$($suite.Name)</h3>
        <p>Status: $(if($suite.ExitCode -eq 0){"✅ PASS"}else{"❌ FAIL"})</p>
        <p>Duration: $([math]::Round(($suite.EndTime - $suite.StartTime).TotalSeconds, 1)) seconds</p>
        <details>
            <summary>Output</summary>
            <pre>$($suite.Output)</pre>
        </details>
    </div>
"@
    }
    
    $htmlReport += "</body></html>"
    
    $htmlPath = Join-Path $OutputDir "test-results.html"
    $htmlReport | Out-File -FilePath $htmlPath -Encoding UTF8
    
    Write-Host "📄 Reports generated:" -ForegroundColor Green
    Write-Host "  JSON: $jsonPath" -ForegroundColor Blue
    Write-Host "  HTML: $htmlPath" -ForegroundColor Blue
}

# Main execution
try {
    Start-TestExecution
    
    # Prerequisites check
    if (-not (Test-Prerequisites)) {
        Write-Host "❌ Prerequisites check failed. Please fix the issues above." -ForegroundColor Red
        exit 1
    }
    
    # Run test suites based on mode
    if ($Quick) {
        # Quick tests - basic functionality only
        Invoke-TestSuite "Launch Script Tests" ".\tests\launch-tests.ps1" @{TestSuite="launch"; ContinueOnError=$true}
        Invoke-TestSuite "CLI Tests" ".\tests\launch-tests.ps1" @{TestSuite="cli"; ContinueOnError=$true}
        Invoke-TestSuite "Docker Config Tests" ".\tests\launch-tests.ps1" @{TestSuite="docker"; ContinueOnError=$true}
        
    } elseif ($Integration) {
        # Integration tests - requires running services
        Invoke-TestSuite "Prerequisites" ".\tests\launch-tests.ps1" @{TestSuite="prerequisites"}
        Invoke-TestSuite "Integration Tests" ".\tests\integration-tests.ps1" @{StartServices=$StartServices; StopServices=$StartServices}
        
    } else {
        # Full test suite
        Invoke-TestSuite "Prerequisites" ".\tests\launch-tests.ps1" @{TestSuite="prerequisites"}
        Invoke-TestSuite "Launch Scripts" ".\tests\launch-tests.ps1" @{TestSuite="launch"}
        Invoke-TestSuite "Vault CLI" ".\tests\launch-tests.ps1" @{TestSuite="cli"}
        Invoke-TestSuite "Docker Configuration" ".\tests\launch-tests.ps1" @{TestSuite="docker"}
        Invoke-TestSuite "Port Availability" ".\tests\launch-tests.ps1" @{TestSuite="ports"}
        
        if ($Integration -or $StartServices) {
            Invoke-TestSuite "Integration Tests" ".\tests\integration-tests.ps1" @{StartServices=$StartServices; StopServices=$StartServices}
        } else {
            Invoke-TestSuite "API Tests (if running)" ".\tests\launch-tests.ps1" @{TestSuite="api"}
        }
    }
    
    # Generate final report
    $success = Write-FinalReport
    
    if ($success) {
        Write-Host "🎉 All test suites completed successfully!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Some test suites failed. Check the output above for details." -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "💥 Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}