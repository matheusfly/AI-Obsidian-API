#!/usr/bin/env pwsh
# Complete Test Suite for All Integrations

param(
    [switch]$Performance,
    [switch]$Integration,
    [switch]$Stress,
    [switch]$All,
    [int]$Timeout = 300
)

if ($All) {
    $Performance = $true
    $Integration = $true
    $Stress = $true
}

Write-Host "🧪 Complete Integration Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$testResults = @{}
$startTime = Get-Date

function Write-TestHeader {
    param([string]$TestName)
    Write-Host "`n🔬 $TestName" -ForegroundColor Yellow
    Write-Host ("-" * ($TestName.Length + 3)) -ForegroundColor Yellow
}

function Test-Prerequisites {
    Write-TestHeader "Prerequisites Check"
    
    $checks = @{
        "Docker" = { docker --version }
        "Node.js" = { node --version }
        "Python" = { python --version }
        "PowerShell" = { $PSVersionTable.PSVersion }
    }
    
    $allPassed = $true
    foreach ($check in $checks.GetEnumerator()) {
        try {
            $result = & $check.Value
            Write-Host "✅ $($check.Key): $result" -ForegroundColor Green
        } catch {
            Write-Host "❌ $($check.Key): Not available" -ForegroundColor Red
            $allPassed = $false
        }
    }
    
    return $allPassed
}

function Test-ServiceHealth {
    Write-TestHeader "Service Health Check"
    
    $services = @(
        @{ name = "Vault API"; url = "http://localhost:8080/health"; port = 8080 },
        @{ name = "Obsidian API"; url = "http://localhost:27123/health"; port = 27123 },
        @{ name = "Qdrant"; url = "http://localhost:6333/collections"; port = 6333 },
        @{ name = "Embedding Server"; url = "http://localhost:3000/health"; port = 3000 }
    )
    
    $healthyServices = 0
    foreach ($service in $services) {
        # Check if port is listening
        $portOpen = Test-NetConnection -ComputerName localhost -Port $service.port -InformationLevel Quiet -WarningAction SilentlyContinue
        
        if ($portOpen) {
            try {
                $response = Invoke-RestMethod -Uri $service.url -Method GET -TimeoutSec 5
                Write-Host "✅ $($service.name): Healthy" -ForegroundColor Green
                $healthyServices++
            } catch {
                Write-Host "⚠️ $($service.name): Port open but service unhealthy" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ $($service.name): Port $($service.port) not accessible" -ForegroundColor Red
        }
    }
    
    $testResults["ServiceHealth"] = @{
        "Total" = $services.Count
        "Healthy" = $healthyServices
        "Success" = ($healthyServices -eq $services.Count)
    }
    
    return ($healthyServices -eq $services.Count)
}

function Test-MotiaFlyde {
    Write-TestHeader "Motia & Flyde Integration Test"
    
    $integrationResults = @{}
    
    # Test Motia
    try {
        Set-Location "motia-project"
        $motiaTest = Start-Process -FilePath "npm" -ArgumentList "run", scripts/" -PassThru -NoNewWindow -Wait -TimeoutSec 30
        $integrationResults["Motia"] = ($motiaTest.ExitCode -eq 0)
        
        if ($motiaTest.ExitCode -eq 0) {
            Write-Host "✅ Motia: Integration test passed" -ForegroundColor Green
        } else {
            Write-Host "❌ Motia: Integration test failed" -ForegroundColor Red
        }
        Set-Location ..
    } catch {
        Write-Host "❌ Motia: Test execution failed - $($_.Exception.Message)" -ForegroundColor Red
        $integrationResults["Motia"] = $false
        Set-Location ..
    }
    
    # Test Flyde
    try {
        Set-Location "flyde-project"
        $flydeTest = Start-Process -FilePath "npm" -ArgumentList "run", scripts/" -PassThru -NoNewWindow -Wait -TimeoutSec 30
        $integrationResults["Flyde"] = ($flydeTest.ExitCode -eq 0)
        
        if ($flydeTest.ExitCode -eq 0) {
            Write-Host "✅ Flyde: Integration test passed" -ForegroundColor Green
        } else {
            Write-Host "❌ Flyde: Integration test failed" -ForegroundColor Red
        }
        Set-Location ..
    } catch {
        Write-Host "❌ Flyde: Test execution failed - $($_.Exception.Message)" -ForegroundColor Red
        $integrationResults["Flyde"] = $false
        Set-Location ..
    }
    
    $testResults["MotiaFlyde"] = $integrationResults
    return ($integrationResults["Motia"] -and $integrationResults["Flyde"])
}

function Test-EnhancedRAG {
    Write-TestHeader "Enhanced RAG System Test"
    
    try {
        $ragTest = Start-Process -FilePath "python" -ArgumentList scripts/-enhanced-rag.py" -PassThru -NoNewWindow -Wait -TimeoutSec 120
        
        if ($ragTest.ExitCode -eq 0) {
            Write-Host "✅ Enhanced RAG: All tests passed" -ForegroundColor Green
            $testResults["EnhancedRAG"] = $true
            return $true
        } else {
            Write-Host "❌ Enhanced RAG: Tests failed" -ForegroundColor Red
            $testResults["EnhancedRAG"] = $false
            return $false
        }
    } catch {
        Write-Host "❌ Enhanced RAG: Test execution failed - $($_.Exception.Message)" -ForegroundColor Red
        $testResults["EnhancedRAG"] = $false
        return $false
    }
}

function Test-SupabaseIntegration {
    Write-TestHeader "Supabase Integration Test"
    
    try {
        $supabaseTest = Start-Process -FilePath "python" -ArgumentList scripts/-supabase-integration.py" -PassThru -NoNewWindow -Wait -TimeoutSec 60
        
        if ($supabaseTest.ExitCode -eq 0) {
            Write-Host "✅ Supabase: Integration test passed" -ForegroundColor Green
            $testResults["Supabase"] = $true
            return $true
        } else {
            Write-Host "❌ Supabase: Integration test failed" -ForegroundColor Red
            $testResults["Supabase"] = $false
            return $false
        }
    } catch {
        Write-Host "❌ Supabase: Test execution failed - $($_.Exception.Message)" -ForegroundColor Red
        $testResults["Supabase"] = $false
        return $false
    }
}

function Test-PerformanceBenchmark {
    Write-TestHeader "Performance Benchmark"
    
    if (-not $Performance) {
        Write-Host "⏭️ Performance tests skipped (use -Performance flag)" -ForegroundColor Yellow
        return $true
    }
    
    $performanceMetrics = @{}
    
    # API Response Time Test
    try {
        $apiTests = @(
            @{ name = "Health Check"; url = "http://localhost:8080/health" },
            @{ name = "Performance Metrics"; url = "http://localhost:8080/api/v1/performance/metrics" }
        )
        
        foreach ($test in $apiTests) {
            $times = @()
            for ($i = 0; $i -lt 5; $i++) {
                $start = Get-Date
                Invoke-RestMethod -Uri $test.url -Method GET -TimeoutSec 10 | Out-Null
                $end = Get-Date
                $times += ($end - $start).TotalMilliseconds
            }
            
            $avgTime = ($times | Measure-Object -Average).Average
            $performanceMetrics[$test.name] = $avgTime
            
            if ($avgTime -lt 500) {
                Write-Host "✅ $($test.name): ${avgTime:F2}ms (Excellent)" -ForegroundColor Green
            } elseif ($avgTime -lt 1000) {
                Write-Host "⚠️ $($test.name): ${avgTime:F2}ms (Good)" -ForegroundColor Yellow
            } else {
                Write-Host "❌ $($test.name): ${avgTime:F2}ms (Slow)" -ForegroundColor Red
            }
        }
        
        $testResults["Performance"] = $performanceMetrics
        return $true
        
    } catch {
        Write-Host "❌ Performance test failed: $($_.Exception.Message)" -ForegroundColor Red
        $testResults["Performance"] = $false
        return $false
    }
}

function Test-StressLoad {
    Write-TestHeader "Stress & Load Test"
    
    if (-not $Stress) {
        Write-Host "⏭️ Stress tests skipped (use -Stress flag)" -ForegroundColor Yellow
        return $true
    }
    
    try {
        # Concurrent API calls
        $jobs = @()
        $concurrentRequests = 10
        
        Write-Host "🔥 Running $concurrentRequests concurrent requests..." -ForegroundColor Yellow
        
        for ($i = 0; $i -lt $concurrentRequests; $i++) {
            $job = Start-Job -ScriptBlock {
                try {
                    Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET -TimeoutSec 30
                    return $true
                } catch {
                    return $false
                }
            }
            $jobs += $job
        }
        
        # Wait for all jobs to complete
        $results = $jobs | Wait-Job -Timeout 60 | Receive-Job
        $jobs | Remove-Job -Force
        
        $successCount = ($results | Where-Object { $_ -eq $true }).Count
        $successRate = ($successCount / $concurrentRequests) * 100
        
        Write-Host "📊 Stress Test Results:" -ForegroundColor Cyan
        Write-Host "  Concurrent Requests: $concurrentRequests" -ForegroundColor White
        Write-Host "  Successful: $successCount" -ForegroundColor White
        Write-Host "  Success Rate: ${successRate:F1}%" -ForegroundColor White
        
        if ($successRate -ge 90) {
            Write-Host "✅ Stress Test: Excellent performance" -ForegroundColor Green
            $testResults["StressTest"] = "Excellent"
            return $true
        } elseif ($successRate -ge 70) {
            Write-Host "⚠️ Stress Test: Good performance" -ForegroundColor Yellow
            $testResults["StressTest"] = "Good"
            return $true
        } else {
            Write-Host "❌ Stress Test: Poor performance" -ForegroundColor Red
            $testResults["StressTest"] = "Poor"
            return $false
        }
        
    } catch {
        Write-Host "❌ Stress test failed: $($_.Exception.Message)" -ForegroundColor Red
        $testResults["StressTest"] = $false
        return $false
    }
}

function Show-TestSummary {
    $endTime = Get-Date
    $totalTime = ($endTime - $startTime).TotalSeconds
    
    Write-Host "`n📊 TEST SUMMARY" -ForegroundColor Cyan
    Write-Host "===============" -ForegroundColor Cyan
    Write-Host "Total Execution Time: ${totalTime:F2} seconds" -ForegroundColor White
    Write-Host ""
    
    $passedTests = 0
    $totalTests = 0
    
    foreach ($result in $testResults.GetEnumerator()) {
        $totalTests++
        if ($result.Value -eq $true -or ($result.Value -is [hashtable] -and $result.Value.Success)) {
            Write-Host "✅ $($result.Key): PASSED" -ForegroundColor Green
            $passedTests++
        } elseif ($result.Value -eq "Excellent" -or $result.Value -eq "Good") {
            Write-Host "✅ $($result.Key): $($result.Value)" -ForegroundColor Green
            $passedTests++
        } else {
            Write-Host "❌ $($result.Key): FAILED" -ForegroundColor Red
        }
    }
    
    $successRate = if ($totalTests -gt 0) { ($passedTests / $totalTests) * 100 } else { 0 }
    
    Write-Host ""
    Write-Host "Overall Success Rate: ${successRate:F1}% ($passedTests/$totalTests)" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })
    
    if ($successRate -ge 80) {
        Write-Host "🎉 System is ready for production!" -ForegroundColor Green
    } elseif ($successRate -ge 60) {
        Write-Host "⚠️ System needs some attention before production" -ForegroundColor Yellow
    } else {
        Write-Host "🚨 System requires significant fixes" -ForegroundColor Red
    }
}

# Execute test suite
Write-Host "Starting comprehensive test suite..." -ForegroundColor Cyan
Write-Host "Timeout: $Timeout seconds" -ForegroundColor Gray

# Run tests
Test-Prerequisites
Test-ServiceHealth

if ($Integration -or $All) {
    Test-MotiaFlyde
    Test-EnhancedRAG
    Test-SupabaseIntegration
}

if ($Performance -or $All) {
    Test-PerformanceBenchmark
}

if ($Stress -or $All) {
    Test-StressLoad
}

Show-TestSummary

Write-Host "`n🚀 Quick Fix Commands:" -ForegroundColor Cyan
Write-Host "  .\scripts\debug-integrations.ps1 -Fix    # Auto-fix common issues" -ForegroundColor White
Write-Host "  .\scripts\quick-start.ps1                # Restart all services" -ForegroundColor White
Write-Host "  docker-compose restart                   # Restart Docker services" -ForegroundColor White