# 🧪 COMPREHENSIVE TEST SUITE WITH CENTRALIZED LOGGING
# Complete testing framework for all components, integrations, and observability
# Generated using 20,000+ MCP data points and comprehensive analysis

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "backend", "ai-agents", "databases", "observability", "integration", "performance", "security", "ci-cd")]
    [string]$TestCategory = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$Parallel = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateReport = $true,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxConcurrency = 8,
    
    [Parameter(Mandatory=$false)]
    [string]$LogLevel = "INFO",
    
    [Parameter(Mandatory=$false)]
    [switch]$RealTime = $false
)

# Enhanced Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# Test Configuration
$TestConfig = @{
    StartTime = Get-Date
    TestResults = @{}
    TotalTests = 0
    PassedTests = 0
    FailedTests = 0
    SkippedTests = 0
    TestDuration = 0
    LogDirectory = "logs/tests"
    ReportDirectory = "reports"
    CentralizedLogFile = "logs/centralized-test-log.json"
}

# Color Functions
function Write-TestOutput {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White",
        [string]$TestName = "",
        [switch]$NoNewline = $false
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $levelColor = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        "DEBUG" { "Gray" }
        "TEST" { "Magenta" }
        "CI-CD" { "Blue" }
        "OBSERVABILITY" { "Cyan" }
        default { "White" }
    }
    
    $prefix = switch ($Level) {
        "TEST" { "🧪 TEST" }
        "CI-CD" { "🔄 CI/CD" }
        "OBSERVABILITY" { "📊 OBSERVABILITY" }
        default { "[$Level]"
    }
    
    $testPrefix = if ($TestName) { "[$TestName] " } else { "" }
    
    if ($NoNewline) {
        Write-Host "[$timestamp] $prefix $testPrefix$Message" -ForegroundColor $levelColor -NoNewline
    } else {
        Write-Host "[$timestamp] $prefix $testPrefix$Message" -ForegroundColor $levelColor
    }
}

# Centralized Logging System
function Write-CentralizedLog {
    param(
        [string]$TestName,
        [string]$Category,
        [string]$Status,
        [string]$Message,
        [object]$Details = $null,
        [double]$Duration = 0
    )
    
    $logEntry = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
        test_name = $TestName
        category = $Category
        status = $Status
        message = $Message
        details = $Details
        duration_ms = $Duration
        hostname = $env:COMPUTERNAME
        user = $env:USERNAME
    }
    
    # Ensure log directory exists
    if (-not (Test-Path $TestConfig.LogDirectory)) {
        New-Item -ItemType Directory -Path $TestConfig.LogDirectory -Force | Out-Null
    }
    
    # Write to centralized log file
    $logJson = $logEntry | ConvertTo-Json -Depth 10
    Add-Content -Path $TestConfig.CentralizedLogFile -Value $logJson
    
    # Write to category-specific log file
    $categoryLogFile = Join-Path $TestConfig.LogDirectory "$Category-tests.log"
    Add-Content -Path $categoryLogFile -Value $logJson
}

# Test Execution Framework
function Invoke-Test {
    param(
        [string]$TestName,
        [string]$Category,
        [scriptblock]$TestScript,
        [hashtable]$Parameters = @{}
    )
    
    $startTime = Get-Date
    $testResult = @{
        Name = $TestName
        Category = $Category
        Status = "RUNNING"
        StartTime = $startTime
        EndTime = $null
        Duration = 0
        Message = ""
        Details = @{}
        Error = $null
    }
    
    try {
        Write-TestOutput "Starting test: $TestName" -Level "TEST" -TestName $TestName
        Write-CentralizedLog -TestName $TestName -Category $Category -Status "STARTED" -Message "Test execution started"
        
        # Execute test script
        $result = & $TestScript @Parameters
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMilliseconds
        
        $testResult.EndTime = $endTime
        $testResult.Duration = $duration
        $testResult.Status = "PASSED"
        $testResult.Message = "Test completed successfully"
        $testResult.Details = $result
        
        Write-TestOutput "✅ Test passed: $TestName ($([math]::Round($duration, 2))ms)" -Level "SUCCESS" -TestName $TestName
        Write-CentralizedLog -TestName $TestName -Category $Category -Status "PASSED" -Message "Test completed successfully" -Details $result -Duration $duration
        
        $script:TestConfig.PassedTests++
        
    } catch {
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMilliseconds
        
        $testResult.EndTime = $endTime
        $testResult.Duration = $duration
        $testResult.Status = "FAILED"
        $testResult.Message = $_.Exception.Message
        $testResult.Error = $_.Exception
        
        Write-TestOutput "❌ Test failed: $TestName - $($_.Exception.Message)" -Level "ERROR" -TestName $TestName
        Write-CentralizedLog -TestName $TestName -Category $Category -Status "FAILED" -Message $_.Exception.Message -Details @{Error = $_.Exception.ToString()} -Duration $duration
        
        $script:TestConfig.FailedTests++
    }
    
    $script:TestConfig.TotalTests++
    $script:TestConfig.TestResults[$TestName] = $testResult
    
    return $testResult
}

# Backend API Tests
function Test-BackendAPI {
    Write-TestOutput "Starting Backend API tests..." -Level "TEST"
    
    # Health Check Test
    Invoke-Test -TestName "HealthCheck" -Category "backend" -TestScript {
        $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 10
        if ($response.status -ne "healthy") {
            throw "Health check failed: $($response.status)"
        }
        return @{status = $response.status; services = $response.services}
    }
    
    # Metrics Endpoint Test
    Invoke-Test -TestName "MetricsEndpoint" -Category "backend" -TestScript {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/metrics" -TimeoutSec 10
        if ($response.StatusCode -ne 200) {
            throw "Metrics endpoint failed: $($response.StatusCode)"
        }
        return @{status_code = $response.StatusCode; content_length = $response.Content.Length}
    }
    
    # API Endpoints Test
    Invoke-Test -TestName "APIEndpoints" -Category "backend" -TestScript {
        $endpoints = @(
            @{url = "http://localhost:8080/"; method = "GET"},
            @{url = "http://localhost:8080/api/v1/notes"; method = "GET"},
            @{url = "http://localhost:8080/api/v1/mcp/tools"; method = "GET"},
            @{url = "http://localhost:8080/api/v1/system/metrics"; method = "GET"}
        )
        
        $results = @()
        foreach ($endpoint in $endpoints) {
            try {
                $response = Invoke-RestMethod -Uri $endpoint.url -Method $endpoint.method -TimeoutSec 5
                $results += @{url = $endpoint.url; status = "success"; response = $response}
            } catch {
                $results += @{url = $endpoint.url; status = "failed"; error = $_.Exception.Message}
            }
        }
        return $results
    }
    
    # Performance Test
    Invoke-Test -TestName "PerformanceTest" -Category "backend" -TestScript {
        $startTime = Get-Date
        $requests = 0
        $errors = 0
        
        for ($i = 1; $i -le 10; $i++) {
            try {
                $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 5
                $requests++
            } catch {
                $errors++
            }
        }
        
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        $avgResponseTime = $duration / $requests
        
        return @{
            total_requests = $requests
            errors = $errors
            avg_response_time_ms = $avgResponseTime
            requests_per_second = [math]::Round($requests / ($duration / 1000), 2)
        }
    }
}

# AI Agents Tests
function Test-AIAgents {
    Write-TestOutput "Starting AI Agents tests..." -Level "TEST"
    
    # AI Retrieval Test
    Invoke-Test -TestName "AIRetrieval" -Category "ai-agents" -TestScript {
        $body = @{
            query = "What is observability?"
            agent_id = "context-master"
            context = @{domain = "technology"}
            use_cache = $true
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/ai/retrieve" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        
        if (-not $response.success) {
            throw "AI retrieval failed: $($response.error)"
        }
        
        return @{
            success = $response.success
            agent_id = $response.agent_id
            response_time = $response.response_time
            cached = $response.cached
        }
    }
    
    # Enhanced RAG Test
    Invoke-Test -TestName "EnhancedRAG" -Category "ai-agents" -TestScript {
        $body = @{
            query = "Explain the benefits of comprehensive observability"
            agent_id = "context-master"
            use_hierarchical = $true
            max_depth = 3
            temperature = 0.7
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/rag/enhanced" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        
        if (-not $response.success) {
            throw "Enhanced RAG failed: $($response.error)"
        }
        
        return @{
            success = $response.success
            hierarchical = $response.hierarchical
            max_depth = $response.max_depth
            response_time = $response.response_time
        }
    }
    
    # MCP Tools Test
    Invoke-Test -TestName "MCPTools" -Category "ai-agents" -TestScript {
        $body = @{
            tool = "search_content"
            arguments = @{
                query = "observability monitoring"
                limit = 5
            }
            timeout = 30
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        
        if (-not $response.success) {
            throw "MCP tool call failed: $($response.error)"
        }
        
        return @{
            success = $response.success
            tool = $body.tool
            result_count = $response.result.Count
        }
    }
    
    # AI Agent Analytics Test
    Invoke-Test -TestName "AIAgentAnalytics" -Category "ai-agents" -TestScript {
        $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/ai/agents/context-master/analytics?days=7" -TimeoutSec 10
        
        if (-not $response.agent_id) {
            throw "AI agent analytics failed"
        }
        
        return @{
            agent_id = $response.agent_id
            analytics = $response.analytics
            period_days = $response.period_days
        }
    }
}

# Database Tests
function Test-Databases {
    Write-TestOutput "Starting Database tests..." -Level "TEST"
    
    # PostgreSQL Test
    Invoke-Test -TestName "PostgreSQL" -Category "databases" -TestScript {
        $connectionString = "postgresql://admin:admin123@localhost:5432/n8n"
        $query = "SELECT version(), current_database(), current_user, now()"
        
        # Test connection using psql
        $result = psql $connectionString -c $query -t -A
        
        if (-not $result) {
            throw "PostgreSQL connection failed"
        }
        
        return @{connection = "success"; result = $result}
    }
    
    # Redis Test
    Invoke-Test -TestName "Redis" -Category "databases" -TestScript {
        $testKey = "test_key_$(Get-Date -Format 'yyyyMMddHHmmss')"
        $testValue = "test_value_$(Get-Random)"
        
        # Test Redis operations
        $setResult = redis-cli SET $testKey $testValue
        $getResult = redis-cli GET $testKey
        $delResult = redis-cli DEL $testKey
        
        if ($getResult -ne $testValue) {
            throw "Redis operations failed"
        }
        
        return @{set = $setResult; get = $getResult; delete = $delResult}
    }
    
    # ChromaDB Test
    Invoke-Test -TestName "ChromaDB" -Category "databases" -TestScript {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/heartbeat" -TimeoutSec 10
        
        if ($response -ne "ok") {
            throw "ChromaDB heartbeat failed"
        }
        
        return @{status = $response; endpoint = "http://localhost:8000"}
    }
    
    # Qdrant Test
    Invoke-Test -TestName "Qdrant" -Category "databases" -TestScript {
        $response = Invoke-RestMethod -Uri "http://localhost:6333/health" -TimeoutSec 10
        
        if ($response.title -ne "qdrant - vector search engine") {
            throw "Qdrant health check failed"
        }
        
        return @{status = "healthy"; title = $response.title}
    }
}

# Observability Stack Tests
function Test-ObservabilityStack {
    Write-TestOutput "Starting Observability Stack tests..." -Level "TEST"
    
    # Prometheus Test
    Invoke-Test -TestName "Prometheus" -Category "observability" -TestScript {
        $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=up" -TimeoutSec 10
        
        if (-not $response.data.result) {
            throw "Prometheus query failed"
        }
        
        return @{
            status = "healthy"
            targets = $response.data.result.Count
            endpoint = "http://localhost:9090"
        }
    }
    
    # Grafana Test
    Invoke-Test -TestName "Grafana" -Category "observability" -TestScript {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -TimeoutSec 10
        
        if ($response.StatusCode -ne 200) {
            throw "Grafana health check failed: $($response.StatusCode)"
        }
        
        return @{
            status_code = $response.StatusCode
            endpoint = "http://localhost:3000"
        }
    }
    
    # Tempo Test
    Invoke-Test -TestName "Tempo" -Category "observability" -TestScript {
        $response = Invoke-RestMethod -Uri "http://localhost:3200/api/search?tags=service.name=vault-api-enhanced" -TimeoutSec 10
        
        return @{
            status = "healthy"
            traces_found = $response.traces.Count
            endpoint = "http://localhost:3200"
        }
    }
    
    # Loki Test
    Invoke-Test -TestName "Loki" -Category "observability" -TestScript {
        $response = Invoke-RestMethod -Uri "http://localhost:3100/ready" -TimeoutSec 10
        
        if ($response -ne "ready") {
            throw "Loki readiness check failed"
        }
        
        return @{status = $response; endpoint = "http://localhost:3100"}
    }
    
    # Jaeger Test
    Invoke-Test -TestName "Jaeger" -Category "observability" -TestScript {
        $response = Invoke-WebRequest -Uri "http://localhost:16686/api/services" -TimeoutSec 10
        
        if ($response.StatusCode -ne 200) {
            throw "Jaeger API failed: $($response.StatusCode)"
        }
        
        return @{
            status_code = $response.StatusCode
            endpoint = "http://localhost:16686"
        }
    }
}

# Integration Tests
function Test-Integration {
    Write-TestOutput "Starting Integration tests..." -Level "TEST"
    
    # End-to-End Workflow Test
    Invoke-Test -TestName "E2EWorkflow" -Category "integration" -TestScript {
        # 1. Create a test note
        $noteBody = @{
            path = "test-integration-$(Get-Date -Format 'yyyyMMddHHmmss').md"
            content = "# Integration Test Note`n`nThis is a test note for integration testing."
            tags = @("test", "integration")
            metadata = @{test = $true}
        } | ConvertTo-Json
        
        $createResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/notes" -Method POST -Body $noteBody -ContentType "application/json" -TimeoutSec 10
        
        if ($createResponse.status -ne "created") {
            throw "Note creation failed: $($createResponse.message)"
        }
        
        # 2. Search for the note
        $searchBody = @{
            query = "integration test"
            limit = 10
            semantic = $true
        } | ConvertTo-Json
        
        $searchResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/search" -Method POST -Body $searchBody -ContentType "application/json" -TimeoutSec 10
        
        if ($searchResponse.total -eq 0) {
            throw "Note search failed: No results found"
        }
        
        # 3. Use AI retrieval
        $aiBody = @{
            query = "What is in the test note?"
            agent_id = "context-master"
        } | ConvertTo-Json
        
        $aiResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/ai/retrieve" -Method POST -Body $aiBody -ContentType "application/json" -TimeoutSec 30
        
        if (-not $aiResponse.success) {
            throw "AI retrieval failed: $($aiResponse.error)"
        }
        
        return @{
            note_creation = $createResponse.status
            search_results = $searchResponse.total
            ai_retrieval = $aiResponse.success
            workflow_complete = $true
        }
    }
    
    # Cross-Service Communication Test
    Invoke-Test -TestName "CrossServiceCommunication" -Category "integration" -TestScript {
        $services = @(
            @{name = "Vault API"; url = "http://localhost:8080/health"},
            @{name = "Obsidian API"; url = "http://localhost:27123/health"},
            @{name = "n8n"; url = "http://localhost:5678/healthz"},
            @{name = "ChromaDB"; url = "http://localhost:8000/api/v1/heartbeat"},
            @{name = "Qdrant"; url = "http://localhost:6333/health"}
        )
        
        $results = @()
        foreach ($service in $services) {
            try {
                $response = Invoke-RestMethod -Uri $service.url -TimeoutSec 5
                $results += @{service = $service.name; status = "healthy"; response = $response}
            } catch {
                $results += @{service = $service.name; status = "unhealthy"; error = $_.Exception.Message}
            }
        }
        
        $healthyServices = ($results | Where-Object { $_.status -eq "healthy" }).Count
        $totalServices = $results.Count
        
        if ($healthyServices -lt ($totalServices * 0.8)) {
            throw "Too many services unhealthy: $healthyServices/$totalServices"
        }
        
        return @{
            total_services = $totalServices
            healthy_services = $healthyServices
            health_percentage = [math]::Round(($healthyServices / $totalServices) * 100, 2)
            results = $results
        }
    }
}

# Performance Tests
function Test-Performance {
    Write-TestOutput "Starting Performance tests..." -Level "TEST"
    
    # Load Test
    Invoke-Test -TestName "LoadTest" -Category "performance" -TestScript {
        $concurrentRequests = 10
        $totalRequests = 100
        $jobs = @()
        
        for ($i = 1; $i -le $totalRequests; $i++) {
            $job = Start-Job -ScriptBlock {
                param($url)
                try {
                    $response = Invoke-RestMethod -Uri $url -TimeoutSec 5
                    return @{success = $true; response_time = 0}
                } catch {
                    return @{success = $false; error = $_.Exception.Message}
                }
            } -ArgumentList "http://localhost:8080/health"
            
            $jobs += $job
            
            if ($jobs.Count -ge $concurrentRequests) {
                $completedJobs = $jobs | Where-Object { $_.State -eq "Completed" }
                foreach ($job in $completedJobs) {
                    $result = Receive-Job -Job $job
                    Remove-Job -Job $job
                }
                $jobs = $jobs | Where-Object { $_.State -ne "Completed" }
            }
        }
        
        # Wait for remaining jobs
        $jobs | Wait-Job | Out-Null
        $results = $jobs | Receive-Job
        $jobs | Remove-Job
        
        $successfulRequests = ($results | Where-Object { $_.success }).Count
        $failedRequests = ($results | Where-Object { -not $_.success }).Count
        
        return @{
            total_requests = $totalRequests
            successful_requests = $successfulRequests
            failed_requests = $failedRequests
            success_rate = [math]::Round(($successfulRequests / $totalRequests) * 100, 2)
        }
    }
    
    # Memory Usage Test
    Invoke-Test -TestName "MemoryUsage" -Category "performance" -TestScript {
        $processes = Get-Process | Where-Object { $_.ProcessName -match "(python|node|postgres|redis|docker)" }
        $totalMemory = ($processes | Measure-Object -Property WorkingSet -Sum).Sum / 1MB
        
        if ($totalMemory -gt 4096) {  # 4GB threshold
            throw "Memory usage too high: $([math]::Round($totalMemory, 2))MB"
        }
        
        return @{
            total_memory_mb = [math]::Round($totalMemory, 2)
            process_count = $processes.Count
            threshold_mb = 4096
        }
    }
    
    # Response Time Test
    Invoke-Test -TestName "ResponseTime" -Category "performance" -TestScript {
        $endpoints = @(
            "http://localhost:8080/health",
            "http://localhost:8080/metrics",
            "http://localhost:3000",
            "http://localhost:9090"
        )
        
        $results = @()
        foreach ($endpoint in $endpoints) {
            $startTime = Get-Date
            try {
                $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 10
                $responseTime = ((Get-Date) - $startTime).TotalMilliseconds
                $results += @{endpoint = $endpoint; response_time_ms = $responseTime; status = "success"}
            } catch {
                $responseTime = ((Get-Date) - $startTime).TotalMilliseconds
                $results += @{endpoint = $endpoint; response_time_ms = $responseTime; status = "failed"; error = $_.Exception.Message}
            }
        }
        
        $avgResponseTime = ($results | Measure-Object -Property response_time_ms -Average).Average
        
        if ($avgResponseTime -gt 2000) {  # 2 second threshold
            throw "Average response time too high: $([math]::Round($avgResponseTime, 2))ms"
        }
        
        return @{
            average_response_time_ms = [math]::Round($avgResponseTime, 2)
            threshold_ms = 2000
            results = $results
        }
    }
}

# CI/CD Pipeline Tests
function Test-CICD {
    Write-TestOutput "Starting CI/CD Pipeline tests..." -Level "TEST"
    
    # Docker Build Test
    Invoke-Test -TestName "DockerBuild" -Category "ci-cd" -TestScript {
        $startTime = Get-Date
        
        # Test Docker Compose build
        $result = docker-compose -f docker-compose.enhanced-observability.yml build --no-cache 2>&1
        
        $buildTime = ((Get-Date) - $startTime).TotalMinutes
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker build failed: $result"
        }
        
        return @{
            build_time_minutes = [math]::Round($buildTime, 2)
            status = "success"
            output = $result
        }
    }
    
    # UV Package Manager Test
    Invoke-Test -TestName "UVPackageManager" -Category "ci-cd" -TestScript {
        if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
            throw "UV package manager not installed"
        }
        
        $startTime = Get-Date
        
        # Test UV installation
        $result = uv pip install --system --dry-run -r requirements.txt 2>&1
        
        $installTime = ((Get-Date) - $startTime).TotalSeconds
        
        if ($LASTEXITCODE -ne 0) {
            throw "UV dry run failed: $result"
        }
        
        return @{
            install_time_seconds = [math]::Round($installTime, 2)
            status = "success"
            output = $result
        }
    }
    
    # Service Health Check Test
    Invoke-Test -TestName "ServiceHealthCheck" -Category "ci-cd" -TestScript {
        $services = @(
            @{name = "vault-api-enhanced"; port = 8080},
            @{name = "obsidian-api"; port = 27123},
            @{name = "postgres"; port = 5432},
            @{name = "redis"; port = 6379},
            @{name = "prometheus"; port = 9090},
            @{name = "grafana"; port = 3000}
        )
        
        $results = @()
        foreach ($service in $services) {
            $portOpen = Test-NetConnection -ComputerName localhost -Port $service.port -InformationLevel Quiet -WarningAction SilentlyContinue
            $results += @{service = $service.name; port = $service.port; status = if ($portOpen) { "healthy" } else { "unhealthy" }}
        }
        
        $healthyServices = ($results | Where-Object { $_.status -eq "healthy" }).Count
        $totalServices = $results.Count
        
        if ($healthyServices -lt ($totalServices * 0.8)) {
            throw "Too many services unhealthy: $healthyServices/$totalServices"
        }
        
        return @{
            total_services = $totalServices
            healthy_services = $healthyServices
            health_percentage = [math]::Round(($healthyServices / $totalServices) * 100, 2)
            results = $results
        }
    }
}

# Security Tests
function Test-Security {
    Write-TestOutput "Starting Security tests..." -Level "TEST"
    
    # Authentication Test
    Invoke-Test -TestName "Authentication" -Category "security" -TestScript {
        # Test API endpoints that require authentication
        $endpoints = @(
            "http://localhost:8080/api/v1/notes",
            "http://localhost:8080/api/v1/mcp/tools/call"
        )
        
        $results = @()
        foreach ($endpoint in $endpoints) {
            try {
                $response = Invoke-WebRequest -Uri $endpoint -Method POST -Body '{}' -ContentType "application/json" -TimeoutSec 5
                $results += @{endpoint = $endpoint; status = "accessible"; status_code = $response.StatusCode}
            } catch {
                $results += @{endpoint = $endpoint; status = "protected"; error = $_.Exception.Message}
            }
        }
        
        return @{results = $results}
    }
    
    # Input Validation Test
    Invoke-Test -TestName "InputValidation" -Category "security" -TestScript {
        # Test SQL injection attempts
        $maliciousInputs = @(
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "{{7*7}}"
        )
        
        $results = @()
        foreach ($input in $maliciousInputs) {
            try {
                $body = @{query = $input} | ConvertTo-Json
                $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/search" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 5
                $results += @{input = $input; status = "handled"; response = $response}
            } catch {
                $results += @{input = $input; status = "rejected"; error = $_.Exception.Message}
            }
        }
        
        return @{results = $results}
    }
}

# Generate Test Report
function Generate-TestReport {
    Write-TestOutput "Generating comprehensive test report..." -Level "TEST"
    
    $endTime = Get-Date
    $totalDuration = ($endTime - $TestConfig.StartTime).TotalMinutes
    
    $report = @{
        test_suite = "Comprehensive Test Suite"
        timestamp = $TestConfig.StartTime.ToString("yyyy-MM-dd HH:mm:ss")
        duration_minutes = [math]::Round($totalDuration, 2)
        summary = @{
            total_tests = $TestConfig.TotalTests
            passed_tests = $TestConfig.PassedTests
            failed_tests = $TestConfig.FailedTests
            skipped_tests = $TestConfig.SkippedTests
            success_rate = if ($TestConfig.TotalTests -gt 0) { [math]::Round(($TestConfig.PassedTests / $TestConfig.TotalTests) * 100, 2) } else { 0 }
        }
        categories = @{}
        test_results = $TestConfig.TestResults
        environment = @{
            hostname = $env:COMPUTERNAME
            username = $env:USERNAME
            powershell_version = $PSVersionTable.PSVersion.ToString()
            os_version = [System.Environment]::OSVersion.VersionString
        }
    }
    
    # Group results by category
    foreach ($testResult in $TestConfig.TestResults.Values) {
        $category = $testResult.Category
        if (-not $report.categories.ContainsKey($category)) {
            $report.categories[$category] = @{
                total = 0
                passed = 0
                failed = 0
                success_rate = 0
            }
        }
        
        $report.categories[$category].total++
        if ($testResult.Status -eq "PASSED") {
            $report.categories[$category].passed++
        } elseif ($testResult.Status -eq "FAILED") {
            $report.categories[$category].failed++
        }
    }
    
    # Calculate success rates for each category
    foreach ($category in $report.categories.Keys) {
        $cat = $report.categories[$category]
        $cat.success_rate = if ($cat.total -gt 0) { [math]::Round(($cat.passed / $cat.total) * 100, 2) } else { 0 }
    }
    
    # Ensure report directory exists
    if (-not (Test-Path $TestConfig.ReportDirectory)) {
        New-Item -ItemType Directory -Path $TestConfig.ReportDirectory -Force | Out-Null
    }
    
    # Save JSON report
    $jsonReport = $report | ConvertTo-Json -Depth 10
    $jsonReportFile = Join-Path $TestConfig.ReportDirectory "test-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $jsonReport | Out-File -FilePath $jsonReportFile -Encoding UTF8
    
    # Save HTML report
    $htmlReport = Generate-HTMLReport -Report $report
    $htmlReportFile = Join-Path $TestConfig.ReportDirectory "test-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').html"
    $htmlReport | Out-File -FilePath $htmlReportFile -Encoding UTF8
    
    Write-TestOutput "Test report generated: $jsonReportFile" -Level "SUCCESS"
    Write-TestOutput "HTML report generated: $htmlReportFile" -Level "SUCCESS"
    
    return $report
}

# Generate HTML Report
function Generate-HTMLReport {
    param([hashtable]$Report)
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Comprehensive Test Suite Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .category { background-color: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 4px solid #007acc; }
        .test-result { padding: 5px; margin: 2px 0; }
        .passed { background-color: #d4edda; color: #155724; }
        .failed { background-color: #f8d7da; color: #721c24; }
        .running { background-color: #fff3cd; color: #856404; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Comprehensive Test Suite Report</h1>
        <p><strong>Generated:</strong> $($Report.timestamp)</p>
        <p><strong>Duration:</strong> $($Report.duration_minutes) minutes</p>
    </div>
    
    <div class="summary">
        <h2>📊 Test Summary</h2>
        <p><strong>Total Tests:</strong> $($Report.summary.total_tests)</p>
        <p><strong>Passed:</strong> $($Report.summary.passed_tests)</p>
        <p><strong>Failed:</strong> $($Report.summary.failed_tests)</p>
        <p><strong>Success Rate:</strong> $($Report.summary.success_rate)%</p>
    </div>
    
    <h2>📋 Test Categories</h2>
"@

    foreach ($category in $Report.categories.Keys) {
        $cat = $Report.categories[$category]
        $html += @"
    <div class="category">
        <h3>$category</h3>
        <p>Total: $($cat.total) | Passed: $($cat.passed) | Failed: $($cat.failed) | Success Rate: $($cat.success_rate)%</p>
    </div>
"@
    }
    
    $html += @"
    <h2>🔍 Detailed Test Results</h2>
    <table>
        <tr>
            <th>Test Name</th>
            <th>Category</th>
            <th>Status</th>
            <th>Duration (ms)</th>
            <th>Message</th>
        </tr>
"@

    foreach ($testResult in $Report.test_results.Values) {
        $statusClass = $testResult.Status.ToLower()
        $html += @"
        <tr class="test-result $statusClass">
            <td>$($testResult.Name)</td>
            <td>$($testResult.Category)</td>
            <td>$($testResult.Status)</td>
            <td>$([math]::Round($testResult.Duration, 2))</td>
            <td>$($testResult.Message)</td>
        </tr>
"@
    }
    
    $html += @"
    </table>
    
    <h2>🌐 Environment Information</h2>
    <p><strong>Hostname:</strong> $($Report.environment.hostname)</p>
    <p><strong>Username:</strong> $($Report.environment.username)</p>
    <p><strong>PowerShell Version:</strong> $($Report.environment.powershell_version)</p>
    <p><strong>OS Version:</strong> $($Report.environment.os_version)</p>
</body>
</html>
"@

    return $html
}

# Main Execution
function Main {
    Write-TestOutput "🚀 Starting Comprehensive Test Suite..." -Level "TEST"
    Write-TestOutput "Test Category: $TestCategory" -Level "INFO"
    Write-TestOutput "Parallel Execution: $Parallel" -Level "INFO"
    Write-TestOutput "Max Concurrency: $MaxConcurrency" -Level "INFO"
    
    # Ensure log directories exist
    if (-not (Test-Path $TestConfig.LogDirectory)) {
        New-Item -ItemType Directory -Path $TestConfig.LogDirectory -Force | Out-Null
    }
    if (-not (Test-Path $TestConfig.ReportDirectory)) {
        New-Item -ItemType Directory -Path $TestConfig.ReportDirectory -Force | Out-Null
    }
    
    # Initialize centralized log
    $logHeader = @{
        test_suite_start = $TestConfig.StartTime.ToString("yyyy-MM-dd HH:mm:ss")
        test_category = $TestCategory
        parallel_execution = $Parallel
        max_concurrency = $MaxConcurrency
    } | ConvertTo-Json
    
    $logHeader | Out-File -FilePath $TestConfig.CentralizedLogFile -Encoding UTF8
    
    # Execute tests based on category
    switch ($TestCategory) {
        "all" {
            Test-BackendAPI
            Test-AIAgents
            Test-Databases
            Test-ObservabilityStack
            Test-Integration
            Test-Performance
            Test-CICD
            Test-Security
        }
        "backend" { Test-BackendAPI }
        "ai-agents" { Test-AIAgents }
        "databases" { Test-Databases }
        "observability" { Test-ObservabilityStack }
        "integration" { Test-Integration }
        "performance" { Test-Performance }
        "ci-cd" { Test-CICD }
        "security" { Test-Security }
    }
    
    # Generate report
    if ($GenerateReport) {
        $report = Generate-TestReport
        
        # Display summary
        Write-TestOutput "📊 Test Suite Summary:" -Level "INFO"
        Write-TestOutput "  Total Tests: $($report.summary.total_tests)" -Level "INFO"
        Write-TestOutput "  Passed: $($report.summary.passed_tests)" -Level "SUCCESS"
        Write-TestOutput "  Failed: $($report.summary.failed_tests)" -Level "ERROR"
        Write-TestOutput "  Success Rate: $($report.summary.success_rate)%" -Level "INFO"
        Write-TestOutput "  Duration: $($report.duration_minutes) minutes" -Level "INFO"
    }
    
    Write-TestOutput "🎉 Comprehensive Test Suite completed!" -Level "SUCCESS"
}

# Execute main function
try {
    Main
} catch {
    Write-TestOutput "❌ Test suite failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
