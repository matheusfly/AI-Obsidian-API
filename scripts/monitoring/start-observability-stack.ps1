# Data Vault Obsidian - Observability Stack Launcher
# PowerShell script to start the complete observability stack

Write-Host "🚀 Starting Data Vault Obsidian Observability Stack..." -ForegroundColor Cyan

# Check if Docker is running
Write-Host "🔍 Checking Docker status..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    if ($dockerVersion) {
        Write-Host "✅ Docker is available: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not available. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Docker is not available. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
Write-Host "🔍 Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    if ($composeVersion) {
        Write-Host "✅ Docker Compose is available: $composeVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker Compose is not available. Please install Docker Compose." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Docker Compose is not available. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Start the observability stack
Write-Host "🚀 Starting observability stack..." -ForegroundColor Green
docker-compose up -d

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "🔍 Checking service status..." -ForegroundColor Yellow
docker-compose ps

# Test service endpoints
Write-Host "🧪 Testing service endpoints..." -ForegroundColor Yellow

# Test Prometheus
try {
    $prometheusResponse = Invoke-RestMethod -Uri "http://localhost:9090/-/ready" -Method Get -TimeoutSec 10
    Write-Host "✅ Prometheus is running at http://localhost:9090" -ForegroundColor Green
} catch {
    Write-Host "❌ Prometheus is not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Grafana
try {
    $grafanaResponse = Invoke-RestMethod -Uri "http://localhost:3000/api/health" -Method Get -TimeoutSec 10
    Write-Host "✅ Grafana is running at http://localhost:3000" -ForegroundColor Green
    Write-Host "   Login: admin / admin123" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Grafana is not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Data Pipeline
try {
    $pipelineResponse = Invoke-RestMethod -Uri "http://localhost:8003/health" -Method Get -TimeoutSec 10
    Write-Host "✅ Data Pipeline is running at http://localhost:8003" -ForegroundColor Green
} catch {
    Write-Host "❌ Data Pipeline is not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test ChromaDB
try {
    $chromaResponse = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/heartbeat" -Method Get -TimeoutSec 10
    Write-Host "✅ ChromaDB is running at http://localhost:8001" -ForegroundColor Green
} catch {
    Write-Host "❌ ChromaDB is not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Redis
try {
    $redisResponse = Invoke-RestMethod -Uri "http://localhost:6379" -Method Get -TimeoutSec 10
    Write-Host "✅ Redis is running at http://localhost:6379" -ForegroundColor Green
} catch {
    Write-Host "❌ Redis is not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Observability Stack Status:" -ForegroundColor Cyan
Write-Host "📊 Grafana Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "📈 Prometheus Metrics: http://localhost:9090" -ForegroundColor White
Write-Host "🔧 Data Pipeline API: http://localhost:8003" -ForegroundColor White
Write-Host "🗄️ ChromaDB Vector DB: http://localhost:8001" -ForegroundColor White
Write-Host "💾 Redis Cache: http://localhost:6379" -ForegroundColor White

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open Grafana at http://localhost:3000" -ForegroundColor White
Write-Host "2. Login with admin / admin123" -ForegroundColor White
Write-Host "3. Check the 'Data Vault Obsidian - Comprehensive Observability' dashboard" -ForegroundColor White
Write-Host "4. Verify metrics are flowing from the data pipeline" -ForegroundColor White

Write-Host "`n🛑 To stop the stack, run: docker-compose down" -ForegroundColor Yellow
