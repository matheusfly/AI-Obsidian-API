# 🚀 QUICK TEST - Test All Documentation Scrapers
# Simple test script to verify all scrapers are working

Write-Host "🚀 QUICK TEST - Documentation Scrapers" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Test Motia
Write-Host "`n🔧 Testing Motia scraper..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://www.motia.dev/" -TimeoutSec 10
    Write-Host "✅ Motia site accessible: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Motia site error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Flyde
Write-Host "`n🔧 Testing Flyde scraper..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://flyde.dev/" -TimeoutSec 10
    Write-Host "✅ Flyde site accessible: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Flyde site error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test ChartDB
Write-Host "`n🔧 Testing ChartDB scraper..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://chartdb.io/" -TimeoutSec 10
    Write-Host "✅ ChartDB site accessible: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ ChartDB site error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test JSON Crack
Write-Host "`n🔧 Testing JSON Crack scraper..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://jsoncrack.com/" -TimeoutSec 10
    Write-Host "✅ JSON Crack site accessible: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ JSON Crack site error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Python
Write-Host "`n🔧 Testing Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
}

# Test Node.js
Write-Host "`n🔧 Testing Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
}

Write-Host "`n🎉 Quick test completed!" -ForegroundColor Cyan
Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Run: .\LAUNCH_ALL_TOOLS.ps1 Setup" -ForegroundColor White
Write-Host "   2. Run: .\LAUNCH_ALL_TOOLS.ps1 All" -ForegroundColor White
Write-Host "   3. Access: http://localhost:8000" -ForegroundColor White