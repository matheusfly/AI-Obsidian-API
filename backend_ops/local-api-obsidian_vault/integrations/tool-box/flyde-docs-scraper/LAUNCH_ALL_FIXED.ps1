# Fixed comprehensive launch script for Flyde Docs Scraper

param(
    [string]$Mode = "web",  # web, hello-world, test, all, setup
    [switch]$Install,
    [switch]$Test
)

Write-Host "🚀 Flyde Docs Scraper - Fixed Launch Script" -ForegroundColor Green
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
    
    # Remove existing venv if it's corrupted
    if (Test-Path "venv") {
        Write-Host "🗑️ Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force "venv"
    }
    
    # Create virtual environment
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    
    # Check if venv was created successfully
    if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    
    # Activate virtual environment
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    
    # Set environment variables
    $env:VIRTUAL_ENV = ".\venv"
    $env:PATH = ".\venv\Scripts;$env:PATH"
    
    # Install dependencies
    Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
    & ".\venv\Scripts\python.exe" -m pip install --upgrade pip
    & ".\venv\Scripts\python.exe" -m pip install -r requirements.txt
    
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

# Function to activate environment
function Activate-Environment {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $scriptDir
    
    if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
        Write-Host "❌ Virtual environment not found. Run setup first." -ForegroundColor Red
        exit 1
    }
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Set environment variables
    $env:VIRTUAL_ENV = ".\venv"
    $env:PATH = ".\venv\Scripts;$env:PATH"
    
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
}

# Function to run tests
function Run-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    
    Activate-Environment
    
    # Install test dependencies
    & ".\venv\Scripts\python.exe" -m pip install pytest pytest-asyncio
    
    # Run tests
    & ".\venv\Scripts\python.exe" -m pytest tests/ -v
    
    Write-Host "✅ Tests completed!" -ForegroundColor Green
}

# Function to run hello world example
function Run-HelloWorld {
    Write-Host "🎯 Running Hello World example..." -ForegroundColor Yellow
    
    Activate-Environment
    
    # Run the example
    & ".\venv\Scripts\python.exe" main.py
    
    Write-Host "✅ Hello World example completed!" -ForegroundColor Green
}

# Function to launch web UI
function Launch-WebUI {
    Write-Host "🌐 Launching web UI..." -ForegroundColor Yellow
    
    Activate-Environment
    
    Write-Host "📍 Web UI will be available at:" -ForegroundColor Cyan
    Write-Host "   Main UI: http://localhost:8000" -ForegroundColor White
    Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor White
    Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    
    # Start the FastAPI server
    & ".\venv\Scripts\python.exe" web_ui/main.py
}

# Function to show status
function Show-Status {
    Write-Host "📊 System Status:" -ForegroundColor Cyan
    
    # Check if virtual environment exists
    if (Test-Path "venv\Scripts\Activate.ps1") {
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
    Write-Host "  .\LAUNCH_ALL_FIXED.ps1 [Mode] [Options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Modes:" -ForegroundColor Cyan
    Write-Host "  setup        - Setup environment (run this first)" -ForegroundColor White
    Write-Host "  web          - Launch web UI" -ForegroundColor White
    Write-Host "  hello-world  - Run hello world example" -ForegroundColor White
    Write-Host "  test         - Run tests" -ForegroundColor White
    Write-Host "  all          - Run everything" -ForegroundColor White
    Write-Host "  status       - Show system status" -ForegroundColor White
    Write-Host "  help         - Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\LAUNCH_ALL_FIXED.ps1 setup" -ForegroundColor White
    Write-Host "  .\LAUNCH_ALL_FIXED.ps1 web" -ForegroundColor White
    Write-Host "  .\LAUNCH_ALL_FIXED.ps1 hello-world" -ForegroundColor White
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
    "setup" {
        Setup-Environment
    }
    "web" {
        Launch-WebUI
    }
    "hello-world" {
        Run-HelloWorld
    }
    "test" {
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