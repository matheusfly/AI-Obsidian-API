# 🎨 ENHANCED LAUNCH - BEAUTIFUL VISUALIZATIONS & CUSTOM STYLING!
# This launches the complete enhanced system with beautiful styling

Write-Host "🎨 LAUNCHING ENHANCED VISUALIZATION SYSTEM..." -ForegroundColor Magenta
Write-Host "✨ Starting services with beautiful custom styling..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker ps | Out-Null
    $dockerRunning = $true
} catch {
    $dockerRunning = $false
    Write-Host "⚠️ Docker not running, launching native mode..." -ForegroundColor Yellow
}

if ($dockerRunning) {
    Write-Host "🐳 Docker detected, starting enhanced services..." -ForegroundColor Green
    
    # Start enhanced services
    docker-compose -f docker-compose.jsoncrack-fixed.yml up -d
    
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep 10
    
    # Check service status
    Write-Host "🔍 Checking enhanced service status..." -ForegroundColor Cyan
    
    $services = @(
        @{Name="Vault API"; URL="http://localhost:8081/health"},
        @{Name="JSON Viewer"; URL="http://localhost:3003"},
        @{Name="Enhanced Dashboard"; URL="http://localhost:8081/enhanced/dashboard"}
    )
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✅ $($service.Name) is running" -ForegroundColor Green
            } else {
                Write-Host "  ⚠️ $($service.Name) responded with status $($response.StatusCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  ❌ $($service.Name) is not responding" -ForegroundColor Red
        }
    }
    
} else {
    Write-Host "🚀 Launching native enhanced mode..." -ForegroundColor Green
    
    # Check if Python is available
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "✅ Python found, starting Enhanced Vault API..." -ForegroundColor Green
        
        # Start the Enhanced Vault API directly
        Set-Location vault-api
        Start-Process python -ArgumentList "main_visual.py" -WindowStyle Minimized
        Set-Location ..
        
        Write-Host "⏳ Waiting for API to start..." -ForegroundColor Yellow
        Start-Sleep 8
    } else {
        Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎨 ENHANCED VISUALIZATION ACCESS POINTS:" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta
Write-Host "🎨 Enhanced Dashboard:     http://localhost:8081/enhanced/dashboard" -ForegroundColor Yellow
Write-Host "📊 System Overview:        http://localhost:8081/system/overview" -ForegroundColor Yellow
Write-Host "🎨 Enhanced JSON Viewer:   http://localhost:3003/enhanced-viewer.html" -ForegroundColor Yellow
Write-Host "🔗 Vault API:              http://localhost:8081" -ForegroundColor Yellow
Write-Host "📚 API Documentation:      http://localhost:8081/docs" -ForegroundColor Yellow

Write-Host ""
Write-Host "🎨 ENHANCED FEATURES:" -ForegroundColor Magenta
Write-Host "====================" -ForegroundColor Magenta
Write-Host "✨ Beautiful custom themes (Dark, Light, Neon, Ocean)" -ForegroundColor Cyan
Write-Host "🎨 Interactive JSON visualizations" -ForegroundColor Cyan
Write-Host "📊 Real-time system statistics" -ForegroundColor Cyan
Write-Host "🔧 Advanced customization options" -ForegroundColor Cyan
Write-Host "📱 Responsive design for all devices" -ForegroundColor Cyan
Write-Host "🎯 Multiple layout options" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎨 ENHANCED API ENDPOINTS:" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta
Write-Host "📊 /enhanced/stats          - Enhanced system statistics" -ForegroundColor Green
Write-Host "🔗 /enhanced/endpoints      - Beautiful endpoint listing" -ForegroundColor Green
Write-Host "🛠️ /enhanced/mcp-tools     - Enhanced MCP tools display" -ForegroundColor Green
Write-Host "🎨 /enhanced/jsoncrack-data - Enhanced JSON Crack data" -ForegroundColor Green
Write-Host "📊 /enhanced/custom-visualization - Custom visualization data" -ForegroundColor Green

Write-Host ""
Write-Host "🎨 QUICK ACTIONS:" -ForegroundColor Magenta
Write-Host "================" -ForegroundColor Magenta
Write-Host "🎨 Open Enhanced Dashboard..." -ForegroundColor Yellow
Start-Sleep 2
Start-Process "http://localhost:8081/enhanced/dashboard"

Write-Host "🎨 Open Enhanced JSON Viewer..." -ForegroundColor Yellow
Start-Sleep 1
Start-Process "http://localhost:3003/enhanced-viewer.html"

Write-Host ""
Write-Host "🎉 ENHANCED SYSTEM LAUNCHED!" -ForegroundColor Green
Write-Host "✨ Your beautiful, interactive visualization system is ready!" -ForegroundColor Green
Write-Host "🎨 Enjoy the enhanced styling and custom layouts!" -ForegroundColor Magenta

