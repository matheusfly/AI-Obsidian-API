# PowerShell script to launch the Flyde visual flow

Write-Host "🚀 Launching Flyde Hello World Visual Flow..." -ForegroundColor Green
Write-Host "Target: https://flyde.dev/playground/blog-generator" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 16+ and try again." -ForegroundColor Red
    exit 1
}

# Navigate to the scraper directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
}

# Check if Python environment is set up
if (-not (Test-Path "venv")) {
    Write-Host "🐍 Setting up Python environment..." -ForegroundColor Yellow
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
}

# Create data directories
Write-Host "📁 Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data"
New-Item -ItemType Directory -Force -Path "data/cache"
New-Item -ItemType Directory -Force -Path "logs"

Write-Host ""
Write-Host "🎯 Running Flyde Visual Flow..." -ForegroundColor Green
Write-Host "This will execute the hello-world.flyde flow file" -ForegroundColor Cyan
Write-Host ""

# Run the Flyde flow
node run_flyde_flow.js

Write-Host ""
Write-Host "✅ Flyde flow execution completed!" -ForegroundColor Green
Write-Host "📁 Check the 'data' folder for results" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 To view the flow visually:" -ForegroundColor Yellow
Write-Host "   1. Install the Flyde VS Code extension" -ForegroundColor White
Write-Host "   2. Open flows/hello-world.flyde" -ForegroundColor White
Write-Host "   3. Use 'Flyde: Test Flow' to run it visually" -ForegroundColor White