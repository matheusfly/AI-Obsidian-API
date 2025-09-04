# 🚀 SIMPLE FIX - Direct Service Startup
# Simple, direct approach to get all services running

Write-Host "🚀 SIMPLE FIX - Starting All Services" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Kill existing processes
Write-Host "🛑 Stopping existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force

# Start Flyde
Write-Host "🎨 Starting Flyde..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd flyde-project && npm run dev" -WindowStyle Hidden

# Start Motia
Write-Host "⚡ Starting Motia..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd motia-project && npm run dev" -WindowStyle Hidden

# Start Obsidian API
Write-Host "📝 Starting Obsidian API..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd obsidian-api && npx motia dev --port 27123" -WindowStyle Hidden

# Start Vault API
Write-Host "🏛️ Starting Vault API..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd vault-api && C:\Program Files\Python312\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload" -WindowStyle Hidden

# Wait
Write-Host ""
Write-Host "⏳ Waiting 30 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test services
Write-Host ""
Write-Host "🧪 Testing services..." -ForegroundColor Yellow

# Test Flyde
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Flyde: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Flyde: NOT RESPONDING" -ForegroundColor Red
}

# Test Motia
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Motia: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Motia: NOT RESPONDING" -ForegroundColor Red
}

# Test Obsidian API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:27123/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Obsidian API: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Obsidian API: NOT RESPONDING" -ForegroundColor Red
}

# Test Vault API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Vault API: HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "❌ Vault API: NOT RESPONDING" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 SIMPLE FIX COMPLETE!" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Access URLs:" -ForegroundColor White
Write-Host "  🎨 Flyde: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault: http://localhost:8080" -ForegroundColor Cyan
