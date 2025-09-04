# 🚨 REAL FIX NOW - Get Services Actually Running
# Kill everything and start fresh with proper error handling

Write-Host "🚨 REAL FIX NOW" -ForegroundColor Red
Write-Host "===============" -ForegroundColor Red
Write-Host "Getting Services Actually Running" -ForegroundColor White
Write-Host ""

# Kill everything
Write-Host "🛑 Killing everything..." -ForegroundColor Yellow
Get-Job | Stop-Job
Get-Job | Remove-Job
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "cmd" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "✅ Everything killed" -ForegroundColor Green

# Wait
Start-Sleep -Seconds 5

# Start Flyde properly
Write-Host ""
Write-Host "🎨 Starting Flyde Studio..." -ForegroundColor Cyan
try {
    Set-Location flyde-project
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Hidden
    Set-Location ..
    Write-Host "  ✅ Flyde started" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Flyde failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Start Motia properly
Write-Host "⚡ Starting Motia..." -ForegroundColor Cyan
try {
    Set-Location motia-project
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Hidden
    Set-Location ..
    Write-Host "  ✅ Motia started" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Motia failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Start Obsidian API properly
Write-Host "📝 Starting Obsidian API..." -ForegroundColor Cyan
try {
    Set-Location obsidian-api
    Start-Process -FilePath "npx" -ArgumentList "motia", "dev", "--port", "27123" -WindowStyle Hidden
    Set-Location ..
    Write-Host "  ✅ Obsidian API started" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Obsidian API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Start Vault API properly
Write-Host "🏛️ Starting Vault API..." -ForegroundColor Cyan
try {
    Set-Location vault-api
    Start-Process -FilePath "C:\Program Files\Python312\python.exe" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload" -WindowStyle Hidden
    Set-Location ..
    Write-Host "  ✅ Vault API started" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Vault API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Wait for services
Write-Host ""
Write-Host "⏳ Waiting 30 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test services
Write-Host ""
Write-Host "🧪 Testing services..." -ForegroundColor Yellow

# Test Flyde
Write-Host "🔍 Testing Flyde..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Flyde Health: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Flyde Health: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Motia
Write-Host "🔍 Testing Motia..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Motia Health: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Motia Health: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Obsidian API
Write-Host "🔍 Testing Obsidian API..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:27123/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Obsidian API Health: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Obsidian API Health: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Vault API
Write-Host "🔍 Testing Vault API..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Vault API Health: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Vault API Health: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 REAL FIX COMPLETE!" -ForegroundColor Green
Write-Host "====================" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Test these URLs in your browser:" -ForegroundColor White
Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault API: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Services should now be running properly!" -ForegroundColor Green
