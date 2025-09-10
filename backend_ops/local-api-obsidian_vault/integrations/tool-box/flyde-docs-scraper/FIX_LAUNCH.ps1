# Fixed launch script for Flyde Docs Scraper

Write-Host "🔧 Fixing Flyde Docs Scraper Setup..." -ForegroundColor Green

# Navigate to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "📍 Current directory: $(Get-Location)" -ForegroundColor Cyan

# Check Python
if (-not (Test-Command "python")) {
    Write-Host "❌ Python not found. Please install Python 3.9+ and try again." -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

# Remove existing venv if it's corrupted
if (Test-Path "venv") {
    Write-Host "🗑️ Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
}

# Create fresh virtual environment
Write-Host "📦 Creating new virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Check if venv was created successfully
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green

# Activate virtual environment using proper PowerShell syntax
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verify activation
$env:VIRTUAL_ENV = ".\venv"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

# Create directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data"
New-Item -ItemType Directory -Force -Path "data/cache"
New-Item -ItemType Directory -Force -Path "logs"

# Create .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚙️ Creating .env file..." -ForegroundColor Yellow
    @"
# Flyde Docs Scraper Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./data/flyde_docs.db
REDIS_URL=redis://localhost:6379

# Scraping Configuration
MAX_CONCURRENT_REQUESTS=10
REQUEST_DELAY=1.0
TIMEOUT=30
MAX_RETRIES=3
REQUESTS_PER_MINUTE=60
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

Write-Host ""
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Now you can run:" -ForegroundColor Cyan
Write-Host "   .\LAUNCH_ALL.ps1 web" -ForegroundColor White
Write-Host "   .\LAUNCH_ALL.ps1 hello-world" -ForegroundColor White
Write-Host "   .\LAUNCH_ALL.ps1 test" -ForegroundColor White