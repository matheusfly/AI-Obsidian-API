#!/usr/bin/env pwsh
# Enhanced RAG System Setup Script

Write-Host "🚀 Setting up Enhanced RAG System with LangGraph..." -ForegroundColor Cyan

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker not found" -ForegroundColor Red
    exit 1
}

# Install enhanced dependencies
Write-Host "📦 Installing enhanced dependencies..." -ForegroundColor Yellow
Set-Location servicesservices/vault-api"
pip install -r requirements.txt
Set-Location ".."

# Setup Qdrant collection
Write-Host "🔧 Configuring Qdrant vector database..." -ForegroundColor Yellow
$qdrantConfig = @{
    name = "obsidian_vault_enhanced"
    vectors = @{
        size = 384
        distance = "Cosine"
    }
    optimizers_config = @{
        indexing_threshold = 20000
        memmap_threshold = 10000
    }
    hnsw_config = @{
        m = 24
        ef_construct = 128
    }
} | ConvertTo-Json -Depth 3

# Start enhanced services
Write-Host "🐳 Starting enhanced RAG services..." -ForegroundColor Yellow
docker-compose -f docker-compose.enhanced-rag.yml up -d

# Wait for services
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test enhanced endpoints
Write-Host "🧪 Testing enhanced RAG endpoints..." -ForegroundColor Yellow

try {
    # Test performance metrics
    $metricsResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/performance/metrics" -Method GET
    Write-Host "✅ Performance metrics: OK" -ForegroundColor Green
    
    # Test enhanced RAG
    $ragRequest = @{
        query = scripts/ query for enhanced RAG"
        agent_id = scripts/_test"
        use_hierarchical = $true
        max_depth = 2
    } | ConvertTo-Json
    
    $ragResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/rag/enhanced" -Method POST -Body $ragRequest -ContentType "application/json"
    Write-Host "✅ Enhanced RAG: OK" -ForegroundColor Green
    
    Write-Host "🎉 Enhanced RAG system setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Available endpoints:" -ForegroundColor Cyan
    Write-Host "  - POST /api/v1/rag/enhanced - Hierarchical RAG with caching" -ForegroundColor White
    Write-Host "  - POST /api/v1/rag/batch - Batch query processing" -ForegroundColor White
    Write-Host "  - GET /api/v1/performance/metrics - System performance" -ForegroundColor White
    Write-Host "  - Grafana Dashboard: http://localhost:3000" -ForegroundColor White
    Write-Host "  - Prometheus Metrics: http://localhost:9090" -ForegroundColor White
    
} catch {
    Write-Host "❌ Setup validation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host scripts/ logs: docker-compose -f docker-compose.enhanced-rag.yml logs" -ForegroundColor Yellow
}