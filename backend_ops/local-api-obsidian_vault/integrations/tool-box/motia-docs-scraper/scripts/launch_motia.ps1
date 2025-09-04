# Motia Documentation Scraper Launcher
# PowerShell script for launching Motia scraper

param(
    [Parameter(Position=0)]
    [ValidateSet("Setup", "All", "Scrape", "WebUI", "MCP", "Test", "Status", "Stop")]
    [string]$Action = "All",
    
    [Parameter()]
    [switch]$Force
)

# Color definitions
$Green = "`e[32m"
$Blue = "`e[34m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Cyan = "`e[36m"
$Reset = "`e[0m"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "${Cyan}🚀 Motia Documentation Scraper${Reset}"
Write-Host "${Blue}Action: $Action${Reset}"

# Setup function
function Initialize-Setup {
    Write-Host "${Green}🔧 Setting up Motia scraper...${Reset}"
    
    # Create virtual environment
    $VenvPath = Join-Path $ProjectRoot "venv"
    if (Test-Path $VenvPath -and $Force) {
        Remove-Item -Path $VenvPath -Recurse -Force
    }
    
    if (-not (Test-Path $VenvPath)) {
        python -m venv $VenvPath
        Write-Host "${Green}✅ Virtual environment created${Reset}"
    }
    
    # Activate virtual environment
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        & $ActivateScript
        Write-Host "${Green}✅ Virtual environment activated${Reset}"
    }
    
    # Install dependencies
    $RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
    if (Test-Path $RequirementsFile) {
        pip install -r $RequirementsFile
        Write-Host "${Green}✅ Dependencies installed${Reset}"
    }
    
    Write-Host "${Green}✅ Motia scraper setup completed!${Reset}"
}

# Start all services
function Start-AllServices {
    Write-Host "${Green}🚀 Starting Motia scraper...${Reset}"
    
    # Start MCP server
    Start-Process -FilePath "python" -ArgumentList "-m", "mcp_servers.motia_mcp_server", "--port", "8001" -WindowStyle Hidden
    
    # Start web UI
    Start-Process -FilePath "python" -ArgumentList "-m", "web_ui.main", "--port", "8001" -WindowStyle Hidden
    
    # Start scraping
    Start-Process -FilePath "python" -ArgumentList "main.py", "--crawl-all" -WindowStyle Hidden
    
    Write-Host "${Green}✅ Motia scraper started!${Reset}"
    Write-Host "${Cyan}🌐 Web UI: http://localhost:8001${Reset}"
}

# Test function
function Test-System {
    Write-Host "${Green}🧪 Testing Motia scraper...${Reset}"
    
    # Test Python imports
    python -c "import requests, aiohttp, beautifulsoup4; print('All imports successful')"
    
    # Test basic scraping
    python -c "
import requests
try:
    response = requests.get('https://www.motia.dev/', timeout=10)
    print(f'Motia site accessible: {response.status_code}')
except Exception as e:
    print(f'Error: {e}')
"
    
    Write-Host "${Green}✅ Motia scraper test completed!${Reset}"
}

# Main execution
switch ($Action) {
    "Setup" {
        Initialize-Setup
    }
    "All" {
        Start-AllServices
    }
    "Test" {
        Test-System
    }
    default {
        Write-Host "${Red}❌ Unknown action: $Action${Reset}"
    }
}

Write-Host "${Cyan}🎉 Motia scraper execution completed!${Reset}"