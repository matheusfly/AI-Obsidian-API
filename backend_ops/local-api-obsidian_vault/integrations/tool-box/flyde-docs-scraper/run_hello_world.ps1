# PowerShell script to run the Hello World example

Write-Host "🚀 Running Flyde Docs Scraper Hello World Example..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+ and try again." -ForegroundColor Red
    exit 1
}

# Navigate to the scraper directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install Playwright browsers
Write-Host "🌐 Installing Playwright browsers..." -ForegroundColor Yellow
playwright install

# Create data directories
Write-Host "📁 Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data"
New-Item -ItemType Directory -Force -Path "data/cache"
New-Item -ItemType Directory -Force -Path "logs"

# Run the hello world example
Write-Host "🎯 Running Hello World example..." -ForegroundColor Green
Write-Host "Target URL: https://flyde.dev/playground/blog-generator" -ForegroundColor Cyan
Write-Host ""

python main.py

Write-Host ""
Write-Host "✅ Hello World example completed!" -ForegroundColor Green
Write-Host "📁 Check the 'data' folder for results" -ForegroundColor Cyan