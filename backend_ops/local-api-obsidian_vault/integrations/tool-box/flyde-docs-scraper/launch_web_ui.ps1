# PowerShell script to launch the Flyde Docs Scraper Web UI

Write-Host "🚀 Launching Flyde Docs Scraper Web UI..." -ForegroundColor Green

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

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "⚙️ Creating .env file..." -ForegroundColor Yellow
    @"
# Flyde Docs Scraper Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Scrapfly Configuration (optional)
# SCRAPFLY_API_KEY=your_scrapfly_api_key
# SCRAPFLY_ACCOUNT=your_scrapfly_account

# Sentry Configuration (optional)
# SENTRY_DSN=your_sentry_dsn
# SENTRY_ENVIRONMENT=development

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

# Create data directories
Write-Host "📁 Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data"
New-Item -ItemType Directory -Force -Path "data/cache"
New-Item -ItemType Directory -Force -Path "logs"

# Launch the web UI
Write-Host "🌐 Starting web UI..." -ForegroundColor Green
Write-Host "📍 Web UI will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🔍 Health check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "📊 API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

# Start the FastAPI server
python web_ui/main.py