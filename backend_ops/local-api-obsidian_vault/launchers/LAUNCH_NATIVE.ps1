# 🚀 NATIVE LAUNCH - NO DOCKER REQUIRED!
# This launches the system without Docker

Write-Host "🚀 LAUNCHING NATIVE SYSTEM (NO DOCKER)..." -ForegroundColor Green
Write-Host "📊 Starting services natively..." -ForegroundColor Cyan

# Check if Python is available
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✅ Python found, starting Vault API..." -ForegroundColor Green
    
    # Start the Vault API directly
    Set-Location vault-api
    Start-Process python -ArgumentList "main_visual.py" -WindowStyle Minimized
    Set-Location ..
    
    Write-Host "🌐 Vault API starting at: http://localhost:8081" -ForegroundColor Yellow
    Write-Host "📊 System Overview: http://localhost:8081/system/overview" -ForegroundColor Yellow
    
    # Wait a moment then open browser
    Start-Sleep 5
    Start-Process "http://localhost:8081/system/overview"
    
} else {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
}

Write-Host "🎉 NATIVE SYSTEM LAUNCHED!" -ForegroundColor Green
