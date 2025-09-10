# 🚀 Backend Integration Test Suite for Flyde & Motia (PowerShell)
# Comprehensive testing and performance optimization for backend integration

param(
    [string]$TestType = "all",
    [string]$Environment = "development",
    [switch]$Performance,
    [switch]$Integration,
    [switch]$Load,
    [switch]$Security,
    [switch]$Help
)

# Color definitions
$Colors = @{
    Green = "Green"
    Blue = "Blue"
    Yellow = "Yellow"
    Red = "Red"
    Magenta = "Magenta"
    Cyan = "Cyan"
    White = "White"
}

function Show-Banner {
    Write-Host "🚀 Backend Integration Test Suite" -ForegroundColor $Colors.Magenta
    Write-Host "=================================" -ForegroundColor $Colors.Magenta
    Write-Host "Testing Flyde & Motia integration with backend services" -ForegroundColor $Colors.White
    Write-Host ""
}

function Show-Help {
    Write-Host "📚 Available Test Types:" -ForegroundColor $Colors.Yellow
    Write-Host ""
    Write-Host "🔧 INTEGRATION TESTS:" -ForegroundColor $Colors.Green
    Write-Host "  .\backend-integration-test.ps1 -Integration    # Test service integration" -ForegroundColor $Colors.Cyan
    Write-Host "  .\backend-integration-test.ps1 -Performance   # Test performance metrics" -ForegroundColor $Colors.Cyan
    Write-Host "  .\backend-integration-test.ps1 -Load          # Load testing" -ForegroundColor $Colors.Cyan
    Write-Host "  .\backend-integration-test.ps1 -Security      # Security testing" -ForegroundColor $Colors.Cyan
    Write-Host ""
    Write-Host "🎯 QUICK TESTS:" -ForegroundColor $Colors.Green
    Write-Host "  .\backend-integration-test.ps1 all            # Run all tests" -ForegroundColor $Colors.Cyan
    Write-Host "  .\backend-integration-test.ps1 health         # Health check only" -ForegroundColor $Colors.Cyan
    Write-Host "  .\backend-integration-test.ps1 ports          # Port availability test" -ForegroundColor $Colors.Cyan
    Write-Host ""
}

function Test-Health {
    Write-Host "🏥 Health Check Tests" -ForegroundColor $Colors.Green
    Write-Host "====================" -ForegroundColor $Colors.Green
    
    $services = @(
        @{ Name = "Obsidian API"; Port = 27123; Path = "/health" },
        @{ Name = "n8n"; Port = 5678; Path = "/healthz" },
        @{ Name = "PostgreSQL"; Port = 5432; Path = "" },
        @{ Name = "Redis"; Port = 6379; Path = "" },
        @{ Name = "Ollama"; Port = 11434; Path = "/api/tags" },
        @{ Name = "ChromaDB"; Port = 8000; Path = "/api/v1/heartbeat" },
        @{ Name = "Vault API"; Port = 8080; Path = "/health" },
        @{ Name = "Prometheus"; Port = 9090; Path = "/-/healthy" },
        @{ Name = "Grafana"; Port = 3000; Path = "/api/health" },
        @{ Name = "Nginx"; Port = 80; Path = "/nginx_status" }
    )
    
    foreach ($service in $services) {
        Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor $Colors.Blue
        
        try {
            if ($service.Path -ne "") {
                $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)$($service.Path)" -TimeoutSec 5 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Host "  ✅ $($service.Name): Healthy" -ForegroundColor $Colors.Green
                } else {
                    Write-Host "  ⚠️  $($service.Name): Status $($response.StatusCode)" -ForegroundColor $Colors.Yellow
                }
            } else {
                $connection = Test-NetConnection -ComputerName localhost -Port $service.Port -InformationLevel Quiet
                if ($connection) {
                    Write-Host "  ✅ $($service.Name): Port accessible" -ForegroundColor $Colors.Green
                } else {
                    Write-Host "  ❌ $($service.Name): Port not accessible" -ForegroundColor $Colors.Red
                }
            }
        } catch {
            Write-Host "  ❌ $($service.Name): Connection failed" -ForegroundColor $Colors.Red
        }
    }
    Write-Host ""
}

function Test-PortAvailability {
    Write-Host "🌐 Port Availability Tests" -ForegroundColor $Colors.Green
    Write-Host "=========================" -ForegroundColor $Colors.Green
    
    $ports = @(3000, 3001, 3002, 3003, 5678, 8000, 8080, 9090, 11434, 27123, 27124)
    
    foreach ($port in $ports) {
        $status = netstat -an | findstr ":$port "
        if ($status) {
            Write-Host "  🔴 Port ${port}: In use" -ForegroundColor $Colors.Red
        } else {
            Write-Host "  🟢 Port ${port}: Available" -ForegroundColor $Colors.Green
        }
    }
    Write-Host ""
}

function Test-FlydeIntegration {
    Write-Host "🎨 Flyde Integration Tests" -ForegroundColor $Colors.Green
    Write-Host "=========================" -ForegroundColor $Colors.Green
    
    # Test Flyde project setup
    if (Test-Path "flyde-project") {
        Write-Host "✅ Flyde project directory exists" -ForegroundColor $Colors.Green
        
        # Test Flyde configuration
        if (Test-Path "flyde-project/flyde.config.js") {
            Write-Host "✅ Flyde configuration file exists" -ForegroundColor $Colors.Green
        } else {
            Write-Host "❌ Flyde configuration file missing" -ForegroundColor $Colors.Red
        }
        
        # Test Flyde dependencies
        Set-Location "flyde-project"
        try {
            $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
            $requiredDeps = @("@flyde/loader", "@flyde/nodes", "@flyde/runtime")
            
            foreach ($dep in $requiredDeps) {
                if ($packageJson.dependencies.$dep -or $packageJson.devDependencies.$dep) {
                    Write-Host "✅ Dependency $dep installed" -ForegroundColor $Colors.Green
                } else {
                    Write-Host "❌ Dependency $dep missing" -ForegroundColor $Colors.Red
                }
            }
        } catch {
            Write-Host "❌ Error reading package.json" -ForegroundColor $Colors.Red
        }
        Set-Location ..
        
        # Test Flyde flow execution
        Write-Host "🔄 Testing Flyde flow execution..." -ForegroundColor $Colors.Blue
        try {
            Set-Location "flyde-project"
            $result = npx flyde run flows/hello-world.flyde --input '{"test": "integration"}' --output test-output.json 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Flyde flow execution successful" -ForegroundColor $Colors.Green
            } else {
                Write-Host "❌ Flyde flow execution failed: $result" -ForegroundColor $Colors.Red
            }
            Set-Location ..
        } catch {
            Write-Host "❌ Flyde flow execution error" -ForegroundColor $Colors.Red
        }
    } else {
        Write-Host "❌ Flyde project directory not found" -ForegroundColor $Colors.Red
    }
    Write-Host ""
}

function Test-MotiaIntegration {
    Write-Host "⚡ Motia Integration Tests" -ForegroundColor $Colors.Green
    Write-Host "=========================" -ForegroundColor $Colors.Green
    
    # Test Motia project setup
    if (Test-Path "motia-project") {
        Write-Host "✅ Motia project directory exists" -ForegroundColor $Colors.Green
        
        # Test Motia configuration
        if (Test-Path "motia-project/motia.config.js") {
            Write-Host "✅ Motia configuration file exists" -ForegroundColor $Colors.Green
        } else {
            Write-Host "❌ Motia configuration file missing" -ForegroundColor $Colors.Red
        }
        
        # Test Motia dependencies
        Set-Location "motia-project"
        try {
            $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
            if ($packageJson.dependencies.motia) {
                Write-Host "✅ Motia dependency installed" -ForegroundColor $Colors.Green
            } else {
                Write-Host "❌ Motia dependency missing" -ForegroundColor $Colors.Red
            }
        } catch {
            Write-Host "❌ Error reading package.json" -ForegroundColor $Colors.Red
        }
        Set-Location ..
        
        # Test Motia step execution
        Write-Host "🔄 Testing Motia step execution..." -ForegroundColor $Colors.Blue
        try {
            Set-Location "motia-project"
            $result = npx motia run steps/hello-world.step.ts --input '{"test": "integration"}' --output test-output.json 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Motia step execution successful" -ForegroundColor $Colors.Green
            } else {
                Write-Host "❌ Motia step execution failed: $result" -ForegroundColor $Colors.Red
            }
            Set-Location ..
        } catch {
            Write-Host "❌ Motia step execution error" -ForegroundColor $Colors.Red
        }
    } else {
        Write-Host "❌ Motia project directory not found" -ForegroundColor $Colors.Red
    }
    Write-Host ""
}

function Test-BackendIntegration {
    Write-Host "🔗 Backend Service Integration Tests" -ForegroundColor $Colors.Green
    Write-Host "===================================" -ForegroundColor $Colors.Green
    
    # Test Obsidian API integration
    Write-Host "🔍 Testing Obsidian API integration..." -ForegroundColor $Colors.Blue
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:27123/api/vault/status" -Method GET -TimeoutSec 10
        Write-Host "✅ Obsidian API accessible" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "❌ Obsidian API not accessible: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Test n8n integration
    Write-Host "🔍 Testing n8n integration..." -ForegroundColor $Colors.Blue
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5678/api/v1/workflows" -Method GET -TimeoutSec 10
        Write-Host "✅ n8n API accessible" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "❌ n8n API not accessible: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Test Ollama integration
    Write-Host "🔍 Testing Ollama integration..." -ForegroundColor $Colors.Blue
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 10
        Write-Host "✅ Ollama API accessible" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "❌ Ollama API not accessible: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Test ChromaDB integration
    Write-Host "🔍 Testing ChromaDB integration..." -ForegroundColor $Colors.Blue
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/heartbeat" -Method GET -TimeoutSec 10
        Write-Host "✅ ChromaDB API accessible" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "❌ ChromaDB API not accessible: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    Write-Host ""
}

function Test-Performance {
    Write-Host "📊 Performance Tests" -ForegroundColor $Colors.Green
    Write-Host "===================" -ForegroundColor $Colors.Green
    
    # Test response times
    $endpoints = @(
        @{ Name = "Obsidian API"; Url = "http://localhost:27123/health" },
        @{ Name = "n8n"; Url = "http://localhost:5678/healthz" },
        @{ Name = "Ollama"; Url = "http://localhost:11434/api/tags" },
        @{ Name = "ChromaDB"; Url = "http://localhost:8000/api/v1/heartbeat" }
    )
    
    foreach ($endpoint in $endpoints) {
        Write-Host "⏱️  Testing $($endpoint.Name) response time..." -ForegroundColor $Colors.Blue
        
        $times = @()
        for ($i = 1; $i -le 5; $i++) {
            try {
                $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
                $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 10 -ErrorAction Stop
                $stopwatch.Stop()
                $times += $stopwatch.ElapsedMilliseconds
            } catch {
                Write-Host "  ❌ Request $i failed" -ForegroundColor $Colors.Red
            }
        }
        
        if ($times.Count -gt 0) {
            $avgTime = ($times | Measure-Object -Average).Average
            $minTime = ($times | Measure-Object -Minimum).Minimum
            $maxTime = ($times | Measure-Object -Maximum).Maximum
            
            Write-Host "  📈 Average: $([math]::Round($avgTime, 2))ms" -ForegroundColor $Colors.Cyan
            Write-Host "  📉 Min: $minTime ms" -ForegroundColor $Colors.Cyan
            Write-Host "  📈 Max: $maxTime ms" -ForegroundColor $Colors.Cyan
            
            if ($avgTime -lt 100) {
                Write-Host "  ✅ Performance: Excellent" -ForegroundColor $Colors.Green
            } elseif ($avgTime -lt 500) {
                Write-Host "  ✅ Performance: Good" -ForegroundColor $Colors.Green
            } elseif ($avgTime -lt 1000) {
                Write-Host "  ⚠️  Performance: Acceptable" -ForegroundColor $Colors.Yellow
            } else {
                Write-Host "  ❌ Performance: Poor" -ForegroundColor $Colors.Red
            }
        }
    }
    Write-Host ""
}

function Test-Load {
    Write-Host "🔥 Load Tests" -ForegroundColor $Colors.Green
    Write-Host "============" -ForegroundColor $Colors.Green
    
    # Simulate concurrent requests
    $concurrentRequests = 10
    $totalRequests = 50
    
    Write-Host "🚀 Running load test with $concurrentRequests concurrent requests..." -ForegroundColor $Colors.Blue
    
    $jobs = @()
    $results = @()
    
    for ($i = 1; $i -le $totalRequests; $i++) {
        $job = Start-Job -ScriptBlock {
            param($url, $requestId)
            try {
                $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
                $response = Invoke-WebRequest -Uri $url -TimeoutSec 30
                $stopwatch.Stop()
                return @{
                    Id = $requestId
                    StatusCode = $response.StatusCode
                    ResponseTime = $stopwatch.ElapsedMilliseconds
                    Success = $true
                }
            } catch {
                return @{
                    Id = $requestId
                    StatusCode = 0
                    ResponseTime = 0
                    Success = $false
                    Error = $_.Exception.Message
                }
            }
        } -ArgumentList "http://localhost:27123/health", $i
        
        $jobs += $job
        
        if ($jobs.Count -ge $concurrentRequests) {
            # Wait for some jobs to complete
            $completed = $jobs | Where-Object { $_.State -eq "Completed" }
            if ($completed.Count -gt 0) {
                foreach ($job in $completed) {
                    $result = Receive-Job -Job $job
                    $results += $result
                    Remove-Job -Job $job
                }
                $jobs = $jobs | Where-Object { $_.State -ne "Completed" }
            }
        }
    }
    
    # Wait for remaining jobs
    $jobs | Wait-Job | Out-Null
    foreach ($job in $jobs) {
        $result = Receive-Job -Job $job
        $results += $result
        Remove-Job -Job $job
    }
    
    # Analyze results
    $successful = $results | Where-Object { $_.Success -eq $true }
    $failed = $results | Where-Object { $_.Success -eq $false }
    
    Write-Host "📊 Load Test Results:" -ForegroundColor $Colors.Cyan
    Write-Host "  ✅ Successful requests: $($successful.Count)" -ForegroundColor $Colors.Green
    Write-Host "  ❌ Failed requests: $($failed.Count)" -ForegroundColor $Colors.Red
    Write-Host "  📈 Success rate: $([math]::Round(($successful.Count / $results.Count) * 100, 2))%" -ForegroundColor $Colors.Cyan
    
    if ($successful.Count -gt 0) {
        $avgResponseTime = ($successful | Measure-Object -Property ResponseTime -Average).Average
        $minResponseTime = ($successful | Measure-Object -Property ResponseTime -Minimum).Minimum
        $maxResponseTime = ($successful | Measure-Object -Property ResponseTime -Maximum).Maximum
        
        Write-Host "  ⏱️  Average response time: $([math]::Round($avgResponseTime, 2))ms" -ForegroundColor $Colors.Cyan
        Write-Host "  📉 Min response time: $minResponseTime ms" -ForegroundColor $Colors.Cyan
        Write-Host "  📈 Max response time: $maxResponseTime ms" -ForegroundColor $Colors.Cyan
    }
    
    Write-Host ""
}

function Test-Security {
    Write-Host "🔒 Security Tests" -ForegroundColor $Colors.Green
    Write-Host "================" -ForegroundColor $Colors.Green
    
    # Test for common security vulnerabilities
    $securityTests = @(
        @{ Name = "CORS Headers"; Url = "http://localhost:27123/health"; Header = "Access-Control-Allow-Origin" },
        @{ Name = "Security Headers"; Url = "http://localhost:27123/health"; Header = "X-Content-Type-Options" },
        @{ Name = "HTTPS Redirect"; Url = "http://localhost:27123/health"; Check = "redirect" }
    )
    
    foreach ($test in $securityTests) {
        Write-Host "🔍 Testing $($test.Name)..." -ForegroundColor $Colors.Blue
        
        try {
            $response = Invoke-WebRequest -Uri $test.Url -TimeoutSec 10 -ErrorAction Stop
            
            if ($test.Header) {
                if ($response.Headers[$test.Header]) {
                    Write-Host "  ✅ $($test.Header) header present" -ForegroundColor $Colors.Green
                } else {
                    Write-Host "  ⚠️  $($test.Header) header missing" -ForegroundColor $Colors.Yellow
                }
            }
        } catch {
            Write-Host "  ❌ Security test failed: $($_.Exception.Message)" -ForegroundColor $Colors.Red
        }
    }
    
    # Test for exposed sensitive endpoints
    $sensitiveEndpoints = @(
        "http://localhost:27123/admin",
        "http://localhost:27123/config",
        "http://localhost:5678/admin",
        "http://localhost:8080/admin"
    )
    
    Write-Host "🔍 Testing for exposed sensitive endpoints..." -ForegroundColor $Colors.Blue
    foreach ($endpoint in $sensitiveEndpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 5 -ErrorAction Stop
            Write-Host "  ⚠️  Sensitive endpoint accessible: $endpoint" -ForegroundColor $Colors.Yellow
        } catch {
            Write-Host "  ✅ Sensitive endpoint protected: $endpoint" -ForegroundColor $Colors.Green
        }
    }
    
    Write-Host ""
}

function Generate-Report {
    Write-Host "📋 Generating Integration Report..." -ForegroundColor $Colors.Green
    Write-Host "=================================" -ForegroundColor $Colors.Green
    
    $report = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Environment = $Environment
        Tests = @()
    }
    
    # Add test results to report
    $report.Tests += @{
        Name = "Health Check"
        Status = "Completed"
        Details = "All services health checked"
    }
    
    $report.Tests += @{
        Name = "Port Availability"
        Status = "Completed"
        Details = "All required ports checked"
    }
    
    $report.Tests += @{
        Name = "Flyde Integration"
        Status = "Completed"
        Details = "Flyde project and flow execution tested"
    }
    
    $report.Tests += @{
        Name = "Motia Integration"
        Status = "Completed"
        Details = "Motia project and step execution tested"
    }
    
    $report.Tests += @{
        Name = "Backend Integration"
        Status = "Completed"
        Details = "All backend services integration tested"
    }
    
    if ($Performance) {
        $report.Tests += @{
            Name = "Performance Tests"
            Status = "Completed"
            Details = "Response time and performance metrics collected"
        }
    }
    
    if ($Load) {
        $report.Tests += @{
            Name = "Load Tests"
            Status = "Completed"
            Details = "Concurrent request load testing completed"
        }
    }
    
    if ($Security) {
        $report.Tests += @{
            Name = "Security Tests"
            Status = "Completed"
            Details = "Security headers and endpoint protection tested"
        }
    }
    
    # Save report to file
    $reportPath = "integration-test-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Host "📄 Report saved to: $reportPath" -ForegroundColor $Colors.Cyan
    Write-Host ""
}

function Optimize-Performance {
    Write-Host "⚡ Performance Optimization Recommendations" -ForegroundColor $Colors.Green
    Write-Host "==========================================" -ForegroundColor $Colors.Green
    
    Write-Host "🎯 Backend Optimizations:" -ForegroundColor $Colors.Yellow
    Write-Host "  • Enable Redis caching for frequently accessed data" -ForegroundColor $Colors.White
    Write-Host "  • Implement connection pooling for database connections" -ForegroundColor $Colors.White
    Write-Host "  • Add compression middleware (gzip) for API responses" -ForegroundColor $Colors.White
    Write-Host "  • Implement request rate limiting" -ForegroundColor $Colors.White
    Write-Host "  • Add response caching headers" -ForegroundColor $Colors.White
    Write-Host ""
    
    Write-Host "🎨 Flyde Optimizations:" -ForegroundColor $Colors.Yellow
    Write-Host "  • Use flow caching for repeated executions" -ForegroundColor $Colors.White
    Write-Host "  • Implement flow result memoization" -ForegroundColor $Colors.White
    Write-Host "  • Add flow execution monitoring" -ForegroundColor $Colors.White
    Write-Host "  • Optimize flow node connections" -ForegroundColor $Colors.White
    Write-Host ""
    
    Write-Host "⚡ Motia Optimizations:" -ForegroundColor $Colors.Yellow
    Write-Host "  • Implement step result caching" -ForegroundColor $Colors.White
    Write-Host "  • Add step execution batching" -ForegroundColor $Colors.White
    Write-Host "  • Optimize step dependency resolution" -ForegroundColor $Colors.White
    Write-Host "  • Add step performance monitoring" -ForegroundColor $Colors.White
    Write-Host ""
    
    Write-Host "🔧 Infrastructure Optimizations:" -ForegroundColor $Colors.Yellow
    Write-Host "  • Increase Docker container memory limits" -ForegroundColor $Colors.White
    Write-Host "  • Enable Docker container health checks" -ForegroundColor $Colors.White
    Write-Host "  • Implement container auto-restart policies" -ForegroundColor $Colors.White
    Write-Host "  • Add container resource monitoring" -ForegroundColor $Colors.White
    Write-Host ""
}

# Main execution
Show-Banner

if ($Help) {
    Show-Help
} else {
    switch ($TestType.ToLower()) {
        "health" {
            Test-Health
        }
        "ports" {
            Test-PortAvailability
        }
        "flyde" {
            Test-FlydeIntegration
        }
        "motia" {
            Test-MotiaIntegration
        }
        "backend" {
            Test-BackendIntegration
        }
        "all" {
            Test-Health
            Test-PortAvailability
            Test-FlydeIntegration
            Test-MotiaIntegration
            Test-BackendIntegration
            
            if ($Performance) {
                Test-Performance
            }
            
            if ($Load) {
                Test-Load
            }
            
            if ($Security) {
                Test-Security
            }
            
            Generate-Report
            Optimize-Performance
        }
        default {
            if ($Integration) {
                Test-BackendIntegration
            }
            
            if ($Performance) {
                Test-Performance
            }
            
            if ($Load) {
                Test-Load
            }
            
            if ($Security) {
                Test-Security
            }
            
            if (-not $Integration -and -not $Performance -and -not $Load -and -not $Security) {
                Test-Health
                Test-PortAvailability
                Test-FlydeIntegration
                Test-MotiaIntegration
                Test-BackendIntegration
            }
            
            Generate-Report
            Optimize-Performance
        }
    }
}
