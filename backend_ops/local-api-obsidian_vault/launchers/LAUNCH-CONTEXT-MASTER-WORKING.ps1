# Launch Context Engineering Master - WORKING VERSION
# Fixed version that actually works!

Write-Host "🧠 LAUNCHING CONTEXT ENGINEERING MASTER - WORKING VERSION" -ForegroundColor Cyan
Write-Host "📱 Web UI: http://localhost:3001" -ForegroundColor Yellow
Write-Host "🔌 WebSocket: ws://localhost:3001" -ForegroundColor Yellow
Write-Host "📊 API: http://localhost:3001/api" -ForegroundColor Yellow
Write-Host ""

# Check if context-engineering-master directory exists
if (-not (Test-Path servicesservices/context-engineering-master")) {
    Write-Host "❌ Context Engineering Master directory not found!" -ForegroundColor Red
    Write-Host "Please run the setup first." -ForegroundColor Yellow
    exit 1
}

# Change to the directory
Set-Location servicesservices/context-engineering-master"

# Check if working-server.js exists
if (-not (Test-Path "src\working-server.js")) {
    Write-Host "❌ Working server not found!" -ForegroundColor Red
    Write-Host "Please run the fix script first." -ForegroundColor Yellow
    Set-Location ".."
    exit 1
}

# Check if package.json exists
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Package.json not found!" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the server
Write-Host "🚀 Starting Context Engineering Master..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

node src/working-server.js
