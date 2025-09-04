# Comprehensive launch script for Flyde Docs Scraper

param(
    [string]$Mode = "web",  # web, hello-world, test, all
    [switch]$Install,
    [switch]$Test
)

Write-Host "🚀 Flyde Docs Scraper - Comprehensive Launch Script" -ForegroundColor Green
Write-Host "Mode: $Mode" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to check Python installation
function Test-Python {
    if (Test-Command "python") {
        $version = python --version 2>&1
        Write-Host "✅ Python found: $version" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Python not found. Please install Python 3.9+ and try again." -ForegroundColor Red
        return $false
    }
}

# Function to setup environment
function Setup-Environment {
    Write-Host "🔧 Setting up environment..." -ForegroundColor Yellow
    
    # Navigate to script directory
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $scriptDir
    
    # Create virtual environment if it doesn't exist
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
    
    # Create directories
    Write-Host "📁 Creating directories..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path "data"
    New-Item -ItemType Directory -Force -Path "data/cache"
    New-Item -ItemType Directory -Force -Path "logs"
    
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
    
    Write-Host "✅ Environment setup completed!" -ForegroundColor Green
}

# Function to run tests
function Run-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Install test dependencies
    pip install pytest pytest-asyncio
    
    # Run tests
    python -m pytest tests/ -v
    
    Write-Host "✅ Tests completed!" -ForegroundColor Green
}

# Function to run hello world example
function Run-HelloWorld {
    Write-Host "🎯 Running Hello World example..." -ForegroundColor Yellow
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Run the example
    python main.py
    
    Write-Host "✅ Hello World example completed!" -ForegroundColor Green
}

# Function to launch web UI
function Launch-WebUI {
    Write-Host "🌐 Launching web UI..." -ForegroundColor Yellow
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    Write-Host "📍 Web UI will be available at:" -ForegroundColor Cyan
    Write-Host "   Main UI: http://localhost:8000" -ForegroundColor White
    Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor White
    Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    
    # Start the FastAPI server
    python web_ui/main.py
}

# Function to show status
function Show-Status {
    Write-Host "📊 System Status:" -ForegroundColor Cyan
    
    # Check if virtual environment exists
    if (Test-Path "venv") {
        Write-Host "✅ Virtual environment: Ready" -ForegroundColor Green
    } else {
        Write-Host "❌ Virtual environment: Not found" -ForegroundColor Red
    }
    
    # Check if requirements are installed
    if (Test-Path "venv\Scripts\python.exe") {
        Write-Host "✅ Python environment: Ready" -ForegroundColor Green
    } else {
        Write-Host "❌ Python environment: Not ready" -ForegroundColor Red
    }
    
    # Check if data directory exists
    if (Test-Path "data") {
        $fileCount = (Get-ChildItem "data" -Recurse -File).Count
        Write-Host "✅ Data directory: Ready ($fileCount files)" -ForegroundColor Green
    } else {
        Write-Host "❌ Data directory: Not found" -ForegroundColor Red
    }
    
    # Check if .env exists
    if (Test-Path ".env") {
        Write-Host "✅ Configuration: Ready" -ForegroundColor Green
    } else {
        Write-Host "❌ Configuration: Not found" -ForegroundColor Red
    }
}

# Function to show help
function Show-Help {
    Write-Host "📖 Usage:" -ForegroundColor Cyan
    Write-Host "  .\LAUNCH_ALL.ps1 [Mode] [Options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Modes:" -ForegroundColor Cyan
    Write-Host "  web         - Launch web UI (default)" -ForegroundColor White
    Write-Host "  hello-world - Run hello world example" -ForegroundColor White
    Write-Host "  test        - Run tests" -ForegroundColor White
    Write-Host "  all         - Run everything" -ForegroundColor White
    Write-Host "  status      - Show system status" -ForegroundColor White
    Write-Host "  help        - Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  -Install    - Install dependencies" -ForegroundColor White
    Write-Host "  -Test       - Run tests after setup" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\LAUNCH_ALL.ps1 web" -ForegroundColor White
    Write-Host "  .\LAUNCH_ALL.ps1 hello-world" -ForegroundColor White
    Write-Host "  .\LAUNCH_ALL.ps1 -Install" -ForegroundColor White
    Write-Host "  .\LAUNCH_ALL.ps1 all -Test" -ForegroundColor White
}

# Main execution
if (-not (Test-Python)) {
    exit 1
}

# Navigate to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Handle different modes
switch ($Mode.ToLower()) {
    "web" {
        if ($Install) {
            Setup-Environment
        }
        Launch-WebUI
    }
    "hello-world" {
        if ($Install) {
            Setup-Environment
        }
        Run-HelloWorld
    }
    "test" {
        if ($Install) {
            Setup-Environment
        }
        Run-Tests
    }
    "all" {
        Setup-Environment
        if ($Test) {
            Run-Tests
        }
        Run-HelloWorld
        Launch-WebUI
    }
    "status" {
        Show-Status
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "❌ Unknown mode: $Mode" -ForegroundColor Red
        Show-Help
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Flyde Docs Scraper launch completed!" -ForegroundColor Green