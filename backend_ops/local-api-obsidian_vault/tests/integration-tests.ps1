# Integration Tests for Complete System Functionality
param(
    [switch]$StartServices = $false,
    [switch]$StopServices = $false,
    [int]$TimeoutSeconds = 300
)

$script:Results = @{Passed = 0; Failed = 0; Tests = @()}

function Test-Integration {
    param([string]$Name, [scriptblock]$Test)
    
    Write-Host "🔄 Testing: $Name" -ForegroundColor Cyan
    try {
        $result = & $Test
        if ($result) {
            $script:Results.Passed++
            Write-Host "✅ PASS: $Name" -ForegroundColor Green
        } else {
            $script:Results.Failed++
            Write-Host "❌ FAIL: $Name" -ForegroundColor Red
        }
    } catch {
        $script:Results.Failed++
        Write-Host "❌ ERROR: $Name - $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-SystemStartup {
    Write-Host "=== SYSTEM STARTUP TESTS ===" -ForegroundColor Yellow
    
    if ($StartServices) {
        Write-Host "🚀 Starting services..." -ForegroundColor Blue
        & ".\scripts\launch.ps1" -Action start -SkipHealthCheck
        Start-Sleep -Seconds 30
    }
    
    Test-Integration "Service Health Checks" {
        $services = @(
            @{Name="Vault API"; URL="http://localhost:8080/health"},
            @{Name="Obsidian API"; URL="http://localhost:27123/health"},
            @{Name="n8n"; URL="http://localhost:5678/health"}
        )
        
        $healthy = 0
        foreach ($service in $services) {
            try {
                $response = Invoke-RestMethod -Uri $service.URL -TimeoutSec 10
                if ($response) { $healthy++ }
            } catch {
                Write-Host "⚠️ $($service.Name) not responding" -ForegroundColor Yellow
            }
        }
        return $healthy -ge 2  # At least 2 services should be healthy
    }
    
    Test-Integration "Container Status" {
        $containers = docker-compose ps --services
        $running = docker-compose ps --services --filter "status=running"
        return $running.Count -ge ($containers.Count * 0.7)  # 70% containers running
    }
}

function Test-APIFunctionality {
    Write-Host "=== API FUNCTIONALITY TESTS ===" -ForegroundColor Yellow
    
    Test-Integration "Vault API Root Endpoint" {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8080/" -TimeoutSec 10
            return $response.message -match "Obsidian Vault AI API"
        } catch {
            return $false
        }
    }
    
    Test-Integration "MCP Tools List" {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools" -TimeoutSec 10
            return $response.tools.Count -gt 10
        } catch {
            return $false
        }
    }
    
    Test-Integration "MCP Tool Execution" {
        try {
            $body = @{
                tool = "list_files"
                arguments = @{path = "brain_dump"; pattern = "*.md"}
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
            return $response.success -eq $true
        } catch {
            return $false
        }
    }
    
    Test-Integration "Search Functionality" {
        try {
            $body = @{
                query = "test"
                limit = 5
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/search" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
            return $response.results -ne $null
        } catch {
            return $false
        }
    }
}

function Test-VaultOperations {
    Write-Host "=== VAULT OPERATIONS TESTS ===" -ForegroundColor Yellow
    
    Test-Integration "Vault Path Access" {
        $vaultPath = "D:\Nomade Milionario"
        if (Test-Path $vaultPath) {
            $files = Get-ChildItem -Path $vaultPath -Filter "*.md" -Recurse | Select-Object -First 5
            return $files.Count -gt 0
        }
        return $false
    }
    
    Test-Integration "Read Existing Note" {
        try {
            $body = @{
                tool = "read_file"
                arguments = @{path = "AGENTS.md"}
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
            return $response.success -eq $true -and $response.result.Length -gt 0
        } catch {
            return $false
        }
    }
    
    Test-Integration "Create Test Note" {
        try {
            $testContent = "# Test Note`n`nCreated at $(Get-Date)"
            $body = @{
                tool = "write_file"
                arguments = @{
                    path = "test-integration-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
                    content = $testContent
                }
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
            return $response.success -eq $true
        } catch {
            return $false
        }
    }
}

function Test-CLIFunctionality {
    Write-Host "=== CLI FUNCTIONALITY TESTS ===" -ForegroundColor Yellow
    
    Test-Integration "Launch Script Health Check" {
        try {
            $output = & ".\scripts\launch.ps1" -Action health 2>&1
            return $output -match "healthy"
        } catch {
            return $false
        }
    }
    
    Test-Integration "Vault CLI Health" {
        try {
            $output = & ".\scripts\vault-cli.ps1" -Command health -BaseUrl "http://localhost:8080" 2>&1
            return $output -match "Vault Status"
        } catch {
            return $false
        }
    }
    
    Test-Integration "Vault CLI Tools List" {
        try {
            $output = & ".\scripts\vault-cli.ps1" -Command tools -BaseUrl "http://localhost:8080" 2>&1
            return $output -match "Available MCP Tools"
        } catch {
            return $false
        }
    }
}

function Test-Performance {
    Write-Host "=== PERFORMANCE TESTS ===" -ForegroundColor Yellow
    
    Test-Integration "API Response Time" {
        $times = @()
        for ($i = 0; $i -lt 5; $i++) {
            try {
                $start = Get-Date
                Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 5 | Out-Null
                $end = Get-Date
                $times += ($end - $start).TotalMilliseconds
            } catch {
                return $false
            }
        }
        $avgTime = ($times | Measure-Object -Average).Average
        Write-Host "Average response time: $([math]::Round($avgTime, 2))ms" -ForegroundColor Blue
        return $avgTime -lt 1000  # Less than 1 second
    }
    
    Test-Integration "Concurrent Requests" {
        $jobs = @()
        for ($i = 0; $i -lt 5; $i++) {
            $jobs += Start-Job -ScriptBlock {
                try {
                    Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools" -TimeoutSec 10
                    return $true
                } catch {
                    return $false
                }
            }
        }
        
        $results = $jobs | Wait-Job | Receive-Job
        $jobs | Remove-Job
        
        $successful = ($results | Where-Object { $_ -eq $true }).Count
        return $successful -ge 4  # At least 4 out of 5 should succeed
    }
}

function Test-ErrorHandling {
    Write-Host "=== ERROR HANDLING TESTS ===" -ForegroundColor Yellow
    
    Test-Integration "Invalid API Endpoint" {
        try {
            Invoke-RestMethod -Uri "http://localhost:8080/invalid-endpoint" -TimeoutSec 5 -ErrorAction Stop
            return $false  # Should have failed
        } catch {
            return $true  # Expected to fail
        }
    }
    
    Test-Integration "Invalid MCP Tool" {
        try {
            $body = @{
                tool = "nonexistent_tool"
                arguments = @{}
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
            return $response.error -ne $null
        } catch {
            return $true  # Expected to fail
        }
    }
    
    Test-Integration "Malformed Request" {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body "invalid json" -ContentType "application/json" -TimeoutSec 10
            return $false  # Should have failed
        } catch {
            return $true  # Expected to fail
        }
    }
}

# Main execution
Write-Host "🧪 Starting Integration Tests" -ForegroundColor Cyan
Write-Host "Timeout: $TimeoutSeconds seconds" -ForegroundColor Blue

try {
    Test-SystemStartup
    Test-APIFunctionality
    Test-VaultOperations
    Test-CLIFunctionality
    Test-Performance
    Test-ErrorHandling
    
    if ($StopServices) {
        Write-Host "🛑 Stopping services..." -ForegroundColor Blue
        & ".\scripts\launch.ps1" -Action stop
    }
    
    $total = $script:Results.Passed + $script:Results.Failed
    $successRate = if ($total -gt 0) { [math]::Round(($script:Results.Passed / $total) * 100, 2) } else { 0 }
    
    Write-Host "`n=== INTEGRATION TEST SUMMARY ===" -ForegroundColor Yellow
    Write-Host "Total Tests: $total" -ForegroundColor Blue
    Write-Host "Passed: $($script:Results.Passed)" -ForegroundColor Green
    Write-Host "Failed: $($script:Results.Failed)" -ForegroundColor Red
    Write-Host "Success Rate: $successRate%" -ForegroundColor Blue
    
    if ($script:Results.Failed -eq 0) {
        Write-Host "🎉 All integration tests passed!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Some integration tests failed" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "💥 Integration test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}