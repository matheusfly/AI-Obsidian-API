# Production Health Check Script for Data Vault Obsidian
# This script performs comprehensive health checks on all production services

param(
    [switch]$Detailed,
    [switch]$Json,
    [string]$OutputFile = ""
)

$ErrorActionPreference = "SilentlyContinue"

# Health check results
$healthResults = @{
    timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    overall_status = "unknown"
    services = @{}
    checks = @()
}

function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [string]$Url,
        [string]$ExpectedStatus = 200,
        [string]$Auth = ""
    )
    
    try {
        $headers = @{}
        if ($Auth) {
            $headers["Authorization"] = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($Auth)))"
        }
        
        $response = Invoke-WebRequest -Uri $Url -Headers $headers -TimeoutSec 10
        $isHealthy = $response.StatusCode -eq $ExpectedStatus
        
        return @{
            name = $ServiceName
            url = $Url
            status = if ($isHealthy) { "healthy" } else { "unhealthy" }
            status_code = $response.StatusCode
            response_time = $response.Headers["X-Response-Time"]
            error = $null
        }
    } catch {
        return @{
            name = $ServiceName
            url = $Url
            status = "unhealthy"
            status_code = $null
            response_time = $null
            error = $_.Exception.Message
        }
    }
}

function Test-DockerService {
    param(
        [string]$ContainerName
    )
    
    try {
        $container = docker inspect $ContainerName --format='{{.State.Health.Status}}' 2>$null
        $isRunning = docker ps --filter "name=$ContainerName" --filter "status=running" --format "{{.Names}}" | Select-String $ContainerName
        
        return @{
            name = $ContainerName
            status = if ($container -eq "healthy" -and $isRunning) { "healthy" } else { "unhealthy" }
            health_status = $container
            is_running = [bool]$isRunning
            error = $null
        }
    } catch {
        return @{
            name = $ContainerName
            status = "unhealthy"
            health_status = "unknown"
            is_running = $false
            error = $_.Exception.Message
        }
    }
}

Write-Host "🔍 Starting Production Health Check..." -ForegroundColor Green

# Test Docker services
Write-Host "`n📦 Testing Docker Services..." -ForegroundColor Blue

$dockerServices = @(
    "obsidian-chroma-prod",
    "obsidian-redis-prod", 
    "obsidian-data-pipeline-prod",
    "obsidian-otel-collector-prod",
    "obsidian-prometheus-prod",
    "obsidian-grafana-prod",
    "obsidian-nginx-prod"
)

foreach ($service in $dockerServices) {
    $result = Test-DockerService -ContainerName $service
    $healthResults.services[$service] = $result
    $healthResults.checks += $result
    
    $statusColor = if ($result.status -eq "healthy") { "Green" } else { "Red" }
    Write-Host "  $($service): " -NoNewline
    Write-Host $result.status -ForegroundColor $statusColor
    
    if ($Detailed -and $result.error) {
        Write-Host "    Error: $($result.error)" -ForegroundColor Red
    }
}

# Test HTTP endpoints
Write-Host "`n🌐 Testing HTTP Endpoints..." -ForegroundColor Blue

$httpServices = @(
    @{ Name = "Grafana"; Url = "http://localhost:3000/api/health"; Auth = "" },
    @{ Name = "Prometheus"; Url = "http://localhost:9090/-/healthy"; Auth = "admin:$($env:PROMETHEUS_PASSWORD)" },
    @{ Name = "Data Pipeline"; Url = "http://localhost:8003/health"; Auth = "" },
    @{ Name = "Nginx Proxy"; Url = "http://localhost/health"; Auth = "" }
)

foreach ($service in $httpServices) {
    $result = Test-ServiceHealth -ServiceName $service.Name -Url $service.Url -Auth $service.Auth
    $healthResults.services[$service.Name] = $result
    $healthResults.checks += $result
    
    $statusColor = if ($result.status -eq "healthy") { "Green" } else { "Red" }
    Write-Host "  $($service.Name): " -NoNewline
    Write-Host $result.status -ForegroundColor $statusColor
    
    if ($Detailed -and $result.error) {
        Write-Host "    Error: $($result.error)" -ForegroundColor Red
    }
    if ($Detailed -and $result.response_time) {
        Write-Host "    Response Time: $($result.response_time)" -ForegroundColor Gray
    }
}

# Test specific functionality
Write-Host "`n🔧 Testing Specific Functionality..." -ForegroundColor Blue

# Test ChromaDB API
try {
    $chromaResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v2/heartbeat" -TimeoutSec 10
    $chromaHealthy = $chromaResponse.StatusCode -eq 200
    Write-Host "  ChromaDB API: " -NoNewline
    Write-Host $(if ($chromaHealthy) { "healthy" } else { "unhealthy" }) -ForegroundColor $(if ($chromaHealthy) { "Green" } else { "Red" })
} catch {
    Write-Host "  ChromaDB API: unhealthy" -ForegroundColor Red
    if ($Detailed) {
        Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test Redis
try {
    $redisResponse = Invoke-WebRequest -Uri "http://localhost:6379" -TimeoutSec 5
    $redisHealthy = $true
    Write-Host "  Redis: " -NoNewline
    Write-Host "healthy" -ForegroundColor Green
} catch {
    # Redis doesn't respond to HTTP, so we'll check if the port is open
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    try {
        $tcpClient.Connect("localhost", 6379)
        $redisHealthy = $true
        Write-Host "  Redis: " -NoNewline
        Write-Host "healthy" -ForegroundColor Green
    } catch {
        Write-Host "  Redis: unhealthy" -ForegroundColor Red
        if ($Detailed) {
            Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } finally {
        $tcpClient.Close()
    }
}

# Test Metrics Endpoint
try {
    $metricsResponse = Invoke-WebRequest -Uri "http://localhost:8003/metrics" -TimeoutSec 10
    $metricsHealthy = $metricsResponse.StatusCode -eq 200
    Write-Host "  Metrics Endpoint: " -NoNewline
    Write-Host $(if ($metricsHealthy) { "healthy" } else { "unhealthy" }) -ForegroundColor $(if ($metricsHealthy) { "Green" } else { "Red" })
} catch {
    Write-Host "  Metrics Endpoint: unhealthy" -ForegroundColor Red
    if ($Detailed) {
        Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Calculate overall status
$unhealthyServices = $healthResults.checks | Where-Object { $_.status -ne "healthy" }
$healthResults.overall_status = if ($unhealthyServices.Count -eq 0) { "healthy" } else { "unhealthy" }

# Display summary
Write-Host "`n📊 Health Check Summary:" -ForegroundColor Green
Write-Host "  Overall Status: " -NoNewline
$overallColor = if ($healthResults.overall_status -eq "healthy") { "Green" } else { "Red" }
Write-Host $healthResults.overall_status -ForegroundColor $overallColor

$healthyCount = ($healthResults.checks | Where-Object { $_.status -eq "healthy" }).Count
$totalCount = $healthResults.checks.Count
Write-Host "  Healthy Services: $healthyCount/$totalCount" -ForegroundColor Gray

if ($unhealthyServices.Count -gt 0) {
    Write-Host "`n❌ Unhealthy Services:" -ForegroundColor Red
    foreach ($service in $unhealthyServices) {
        Write-Host "  - $($service.name): $($service.error)" -ForegroundColor Red
    }
}

# Output JSON if requested
if ($Json -or $OutputFile) {
    $jsonOutput = $healthResults | ConvertTo-Json -Depth 3
    
    if ($OutputFile) {
        $jsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8
        Write-Host "`n📄 Health check results saved to: $OutputFile" -ForegroundColor Green
    } else {
        Write-Host "`n📄 JSON Output:" -ForegroundColor Blue
        Write-Host $jsonOutput
    }
}

# Exit with appropriate code
if ($healthResults.overall_status -eq "healthy") {
    exit 0
} else {
    exit 1
}

