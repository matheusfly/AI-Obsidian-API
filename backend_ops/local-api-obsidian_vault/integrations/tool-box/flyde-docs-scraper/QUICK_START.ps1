# Quick Start Script for Flyde Docs Scraper

Write-Host "🚀 Flyde Docs Scraper - Quick Start" -ForegroundColor Green
Write-Host ""

# Navigate to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "📍 Current directory: $(Get-Location)" -ForegroundColor Cyan

# Check Python
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.9+ and try again." -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

# Create data directory
Write-Host "📁 Creating data directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data"

# Install basic requirements
Write-Host "📥 Installing basic requirements..." -ForegroundColor Yellow
pip install requests

# Run simple test
Write-Host ""
Write-Host "🎯 Running simple test..." -ForegroundColor Green
python simple_test.py

Write-Host ""
Write-Host "✅ Quick start completed!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Check the 'data' folder for results" -ForegroundColor White
Write-Host "   2. Run '.\FIX_LAUNCH.ps1' for full setup" -ForegroundColor White
Write-Host "   3. Use '.\LAUNCH_ALL_FIXED.ps1 setup' for complete environment" -ForegroundColor White