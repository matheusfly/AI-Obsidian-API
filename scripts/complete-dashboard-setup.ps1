#!/usr/bin/env pwsh
<#
.SYNOPSIS
Complete Dashboard Setup and Observability Stack
.DESCRIPTION
This script will restart all services, generate test metrics, and verify dashboard functionality
#>

Write-Host "🚀 COMPLETE DASHBOARD SETUP & OBSERVABILITY STACK" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Step 1: Stop all services
Write-Host "`n📋 Step 1: Stopping all services..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml down
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to stop services" -ForegroundColor Red
    exit 1
}

# Step 2: Start all services
Write-Host "`n📋 Step 2: Starting all services..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}

# Step 3: Wait for services to start
Write-Host "`n📋 Step 3: Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep 30

# Step 4: Check service status
Write-Host "`n📋 Step 4: Checking service status..." -ForegroundColor Yellow
docker-compose -f docker-compose.production.yml ps

# Step 5: Wait for data pipeline to be ready
Write-Host "`n📋 Step 5: Waiting for data pipeline to be ready..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
do {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8003/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Data pipeline is ready!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "⏳ Waiting for data pipeline... (attempt $($retryCount + 1)/$maxRetries)" -ForegroundColor Yellow
        Start-Sleep 2
        $retryCount++
    }
} while ($retryCount -lt $maxRetries)

if ($retryCount -eq $maxRetries) {
    Write-Host "❌ Data pipeline failed to start" -ForegroundColor Red
    exit 1
}

# Step 6: Generate test metrics
Write-Host "`n📋 Step 6: Generating test metrics..." -ForegroundColor Yellow

# Health checks (generates http_requests_total)
Write-Host "  📊 Making health check requests..." -ForegroundColor Cyan
for ($i = 1; $i -le 15; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8003/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "    Health check $i`: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "    Health check $i failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep 0.5
}

# Stats endpoint
Write-Host "  📊 Making stats requests..." -ForegroundColor Cyan
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8003/stats" -UseBasicParsing -TimeoutSec 5
        Write-Host "    Stats request $i`: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "    Stats request $i failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep 0.5
}

# Search requests
Write-Host "  📊 Making search requests..." -ForegroundColor Cyan
$searchBody = @{query="test search query"} | ConvertTo-Json
for ($i = 1; $i -le 5; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8003/search" -Method POST -Body $searchBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
        Write-Host "    Search request $i`: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "    Search request $i failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep 1
}

# Query requests
Write-Host "  📊 Making query requests..." -ForegroundColor Cyan
$queryBody = @{query="test query with Gemini"} | ConvertTo-Json
for ($i = 1; $i -le 3; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8003/query" -Method POST -Body $queryBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 15
        Write-Host "    Query request $i`: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "    Query request $i failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    Start-Sleep 2
}

# Step 7: Check metrics generation
Write-Host "`n📋 Step 7: Checking metrics generation..." -ForegroundColor Yellow
try {
    $metricsResponse = Invoke-WebRequest -Uri "http://localhost:8003/metrics" -UseBasicParsing -TimeoutSec 10
    $metricsContent = $metricsResponse.Content
    
    # Check for key metrics
    $httpRequests = ($metricsContent | Select-String -Pattern "http_requests_total").Count
    $processCpu = ($metricsContent | Select-String -Pattern "process_cpu_seconds_total").Count
    $processMemory = ($metricsContent | Select-String -Pattern "process_resident_memory_bytes").Count
    
    Write-Host "  📈 HTTP requests metrics: $httpRequests found" -ForegroundColor Green
    Write-Host "  📈 Process CPU metrics: $processCpu found" -ForegroundColor Green
    Write-Host "  📈 Process memory metrics: $processMemory found" -ForegroundColor Green
    
    if ($httpRequests -gt 0) {
        Write-Host "✅ Metrics are being generated!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No HTTP metrics found - dashboards may show 'No data'" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to check metrics: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Check Prometheus collection
Write-Host "`n📋 Step 8: Checking Prometheus collection..." -ForegroundColor Yellow
try {
    $prometheusResponse = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/query?query=up{job=`"data-pipeline`"}" -UseBasicParsing -TimeoutSec 10
    $prometheusData = $prometheusResponse.Content | ConvertFrom-Json
    
    if ($prometheusData.data.result.Count -gt 0) {
        Write-Host "✅ Prometheus is collecting metrics from data pipeline!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Prometheus not collecting data pipeline metrics" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to check Prometheus: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 9: Open Grafana
Write-Host "`n📋 Step 9: Opening Grafana..." -ForegroundColor Yellow
try {
    Start-Process "http://localhost:3000"
    Write-Host "✅ Grafana opened in browser" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to open Grafana: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 10: Final status
Write-Host "`n🎉 COMPLETE DASHBOARD SETUP FINISHED!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "`n📊 Dashboard URLs:" -ForegroundColor Cyan
Write-Host "  • Grafana: http://localhost:3000 (admin/admin123)" -ForegroundColor White
Write-Host "  • Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "  • Data Pipeline API: http://localhost:8003/docs" -ForegroundColor White

Write-Host "`n📈 Available Dashboards:" -ForegroundColor Cyan
Write-Host "  • Data Pipeline Overview" -ForegroundColor White
Write-Host "  • Enhanced Observability Dashboard" -ForegroundColor White
Write-Host "  • Vector Database Monitoring" -ForegroundColor White
Write-Host "  • LangSmith Trace Integration" -ForegroundColor White
Write-Host "  • Production Operations Dashboard" -ForegroundColor White

Write-Host "`n🔧 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Login to Grafana with admin/admin123" -ForegroundColor White
Write-Host "  2. Go to 'Data Pipeline Overview' dashboard" -ForegroundColor White
Write-Host "  3. Change time range to 'Last 5 minutes'" -ForegroundColor White
Write-Host "  4. Click refresh button (🔄)" -ForegroundColor White
Write-Host "  5. You should now see data in all panels!" -ForegroundColor White

Write-Host "`n✅ OBSERVABILITY STACK COMPLETE!" -ForegroundColor Green
