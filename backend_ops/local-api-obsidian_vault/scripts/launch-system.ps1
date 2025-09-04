# Simple System Launch Script
Write-Host "🚀 LAUNCHING OBSIDIAN VAULT AI SYSTEM" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Blue

# Stop existing services
Write-Host "🛑 Stopping existing services..." -ForegroundColor Yellow
docker-compose down

# Start services
Write-Host "🔨 Starting services..." -ForegroundColor Blue
docker-compose up -d --build

# Wait for startup
Write-Host "⏳ Waiting 30 seconds for services..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test services
Write-Host "🔍 Testing services..." -ForegroundColor Blue

# Test Vault API
try {
    $vaultHealth = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 5
    Write-Host "✅ Vault API: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Vault API: FAILED" -ForegroundColor Red
}

# Test Obsidian API
try {
    $obsidianHealth = Invoke-RestMethod -Uri "http://localhost:27123/health" -TimeoutSec 5
    Write-Host "✅ Obsidian API: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Obsidian API: FAILED" -ForegroundColor Red
}

# Test OpenAPI endpoint
try {
    $openapi = Invoke-RestMethod -Uri "http://localhost:8080/openapi.json" -TimeoutSec 5
    Write-Host "✅ OpenAPI Spec: AVAILABLE" -ForegroundColor Green
} catch {
    Write-Host "❌ OpenAPI Spec: FAILED" -ForegroundColor Red
}

# Test MCP Tools
try {
    $tools = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools" -TimeoutSec 5
    Write-Host "✅ MCP Tools: $($tools.total) available" -ForegroundColor Green
} catch {
    Write-Host "❌ MCP Tools: FAILED" -ForegroundColor Red
}

# Test vault access
try {
    $vaultInfo = Invoke-RestMethod -Uri "http://localhost:27123/vault/info" -TimeoutSec 5
    Write-Host "✅ Vault Access: $($vaultInfo.markdownFiles) files" -ForegroundColor Green
} catch {
    Write-Host "❌ Vault Access: FAILED" -ForegroundColor Red
}

Write-Host "`n🌐 ACCESS POINTS:" -ForegroundColor Cyan
Write-Host "   Vault API: http://localhost:8080" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8080/docs" -ForegroundColor White
Write-Host "   Obsidian API: http://localhost:27123" -ForegroundColor White
Write-Host "   OpenAPI Spec: http://localhost:8080/openapi.json" -ForegroundColor White

Write-Host "`n🧪 QUICK TESTS:" -ForegroundColor Yellow
Write-Host "# Test health" -ForegroundColor Gray
Write-Host "Invoke-RestMethod 'http://localhost:8080/health'" -ForegroundColor Gray
Write-Host "`n# List MCP tools" -ForegroundColor Gray  
Write-Host "Invoke-RestMethod 'http://localhost:8080/api/v1/mcp/tools'" -ForegroundColor Gray
Write-Host "`n# Get vault info" -ForegroundColor Gray
Write-Host "Invoke-RestMethod 'http://localhost:27123/vault/info'" -ForegroundColor Gray

Write-Host "`n🎉 SYSTEM LAUNCHED!" -ForegroundColor Green