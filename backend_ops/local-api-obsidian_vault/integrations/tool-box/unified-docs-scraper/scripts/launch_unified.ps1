# Unified Documentation Scraper Launcher
# Comprehensive PowerShell script for launching the unified scraping system

param(
    [Parameter(Position=0)]
    [ValidateSet("Setup", "All", "Motia", "Flyde", "ChartDB", "JSONCrack", "WebUI", "MCP", "Test", "Status", "Stop", "Restart")]
    [string]$Action = "All",
    
    [Parameter()]
    [switch]$Verbose,
    
    [Parameter()]
    [switch]$Force,
    
    [Parameter()]
    [string]$Config = "default"
)

# Color definitions
$Green = "`e[32m"
$Blue = "`e[34m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Cyan = "`e[36m"
$Magenta = "`e[35m"
$White = "`e[37m"
$Reset = "`e[0m"

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$LogDir = Join-Path $ProjectRoot "logs"
$DataDir = Join-Path $ProjectRoot "data"
$ConfigDir = Join-Path $ProjectRoot "config"

# Create directories if they don't exist
@($LogDir, $DataDir, $ConfigDir) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "${Green}Created directory: $_${Reset}"
    }
}

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host "${Red}$LogMessage${Reset}" }
        "WARN"  { Write-Host "${Yellow}$LogMessage${Reset}" }
        "INFO"  { Write-Host "${Blue}$LogMessage${Reset}" }
        "SUCCESS" { Write-Host "${Green}$LogMessage${Reset}" }
        default { Write-Host "$LogMessage" }
    }
    
    # Write to log file
    $LogFile = Join-Path $LogDir "unified_scraper_$(Get-Date -Format 'yyyyMMdd').log"
    Add-Content -Path $LogFile -Value $LogMessage
}

# Check prerequisites
function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    $Prerequisites = @{
        "Python" = $false
        "Node.js" = $false
        "PowerShell" = $false
        "Git" = $false
    }
    
    # Check Python
    try {
        $PythonVersion = python --version 2>&1
        if ($PythonVersion -match "Python 3\.(9|1[0-9])") {
            $Prerequisites["Python"] = $true
            Write-Log "Python found: $PythonVersion" "SUCCESS"
        } else {
            Write-Log "Python 3.9+ required. Found: $PythonVersion" "ERROR"
        }
    } catch {
        Write-Log "Python not found. Please install Python 3.9+" "ERROR"
    }
    
    # Check Node.js
    try {
        $NodeVersion = node --version 2>&1
        if ($NodeVersion -match "v(1[8-9]|[2-9][0-9])") {
            $Prerequisites["Node.js"] = $true
            Write-Log "Node.js found: $NodeVersion" "SUCCESS"
        } else {
            Write-Log "Node.js 18+ required. Found: $NodeVersion" "ERROR"
        }
    } catch {
        Write-Log "Node.js not found. Please install Node.js 18+" "ERROR"
    }
    
    # Check PowerShell
    if ($PSVersionTable.PSVersion.Major -ge 7) {
        $Prerequisites["PowerShell"] = $true
        Write-Log "PowerShell found: $($PSVersionTable.PSVersion)" "SUCCESS"
    } else {
        Write-Log "PowerShell 7+ required. Found: $($PSVersionTable.PSVersion)" "ERROR"
    }
    
    # Check Git
    try {
        $GitVersion = git --version 2>&1
        $Prerequisites["Git"] = $true
        Write-Log "Git found: $GitVersion" "SUCCESS"
    } catch {
        Write-Log "Git not found. Please install Git" "ERROR"
    }
    
    $AllPrerequisitesMet = $Prerequisites.Values -notcontains $false
    if (-not $AllPrerequisitesMet) {
        Write-Log "Not all prerequisites met. Please install missing requirements." "ERROR"
        return $false
    }
    
    Write-Log "All prerequisites met!" "SUCCESS"
    return $true
}

# Setup function
function Initialize-Setup {
    Write-Log "Starting unified scraper setup..."
    
    if (-not (Test-Prerequisites)) {
        Write-Log "Prerequisites check failed. Aborting setup." "ERROR"
        return $false
    }
    
    # Create virtual environment
    Write-Log "Creating Python virtual environment..."
    $VenvPath = Join-Path $ProjectRoot "venv"
    if (Test-Path $VenvPath) {
        if ($Force) {
            Remove-Item -Path $VenvPath -Recurse -Force
            Write-Log "Removed existing virtual environment" "WARN"
        } else {
            Write-Log "Virtual environment already exists. Use -Force to recreate." "WARN"
        }
    }
    
    if (-not (Test-Path $VenvPath)) {
        python -m venv $VenvPath
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Virtual environment created successfully" "SUCCESS"
        } else {
            Write-Log "Failed to create virtual environment" "ERROR"
            return $false
        }
    }
    
    # Activate virtual environment
    Write-Log "Activating virtual environment..."
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        & $ActivateScript
        Write-Log "Virtual environment activated" "SUCCESS"
    } else {
        Write-Log "Failed to activate virtual environment" "ERROR"
        return $false
    }
    
    # Install Python dependencies
    Write-Log "Installing Python dependencies..."
    $RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
    if (Test-Path $RequirementsFile) {
        pip install -r $RequirementsFile
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Python dependencies installed successfully" "SUCCESS"
        } else {
            Write-Log "Failed to install Python dependencies" "ERROR"
            return $false
        }
    } else {
        Write-Log "Requirements file not found. Creating basic requirements..." "WARN"
        $BasicRequirements = @"
# Unified Documentation Scraper Dependencies
requests>=2.31.0
aiohttp>=3.8.0
beautifulsoup4>=4.12.0
selenium>=4.15.0
playwright>=1.40.0
scrapfly-sdk>=1.3.0
scrapy>=2.11.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
redis>=5.0.0
pandas>=2.1.0
numpy>=1.24.0
structlog>=23.2.0
sentry-sdk>=1.38.0
"@
        Set-Content -Path $RequirementsFile -Value $BasicRequirements
        pip install -r $RequirementsFile
    }
    
    # Install Node.js dependencies
    Write-Log "Installing Node.js dependencies..."
    $PackageJson = Join-Path $ProjectRoot "package.json"
    if (Test-Path $PackageJson) {
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Node.js dependencies installed successfully" "SUCCESS"
        } else {
            Write-Log "Failed to install Node.js dependencies" "ERROR"
        }
    } else {
        Write-Log "Creating package.json..." "WARN"
        $PackageJsonContent = @"
{
  "name": "unified-docs-scraper",
  "version": "1.0.0",
  "description": "Unified documentation scraper for all tools",
  "main": "main.py",
  "scripts": {
    "start": "python main.py",
    "test": "python -m pytest tests/",
    "dev": "uvicorn web_ui.main:app --reload"
  },
  "dependencies": {
    "@flyde/core": "^0.106.1",
    "@flyde/loader": "^0.106.1",
    "@flyde/nodes": "^0.106.1"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  }
}
"@
        Set-Content -Path $PackageJson -Value $PackageJsonContent
        npm install
    }
    
    Write-Log "Setup completed successfully!" "SUCCESS"
    return $true
}

# Start all services
function Start-AllServices {
    Write-Log "Starting all unified scraper services..."
    
    # Start MCP servers
    Start-MCPServers
    
    # Start web UI
    Start-WebUI
    
    # Start scraping
    Start-Scraping
    
    Write-Log "All services started!" "SUCCESS"
}

# Start MCP servers
function Start-MCPServers {
    Write-Log "Starting MCP servers..."
    
    $MCPPorts = @(8001, 8002, 8003, 8004, 8005)
    $MCPTools = @("motia", "flyde", "chartdb", "jsoncrack", "context7")
    
    for ($i = 0; $i -lt $MCPPorts.Count; $i++) {
        $Port = $MCPPorts[$i]
        $Tool = $MCPTools[$i]
        
        Write-Log "Starting $Tool MCP server on port $Port..."
        
        Start-Process -FilePath "python" -ArgumentList "-m", "mcp_servers.${Tool}_mcp_server", "--port", $Port -WindowStyle Hidden
        
        Start-Sleep -Seconds 2
    }
    
    Write-Log "MCP servers started!" "SUCCESS"
}

# Start web UI
function Start-WebUI {
    Write-Log "Starting web UI..."
    
    Start-Process -FilePath "python" -ArgumentList "-m", "web_ui.main", "--port", "8000" -WindowStyle Hidden
    
    Start-Sleep -Seconds 3
    Write-Log "Web UI started on http://localhost:8000" "SUCCESS"
}

# Start scraping
function Start-Scraping {
    Write-Log "Starting unified scraping..."
    
    Start-Process -FilePath "python" -ArgumentList "main.py", "--unified", "--all-tools", "--ai-processing", "--semantic-search" -WindowStyle Hidden
    
    Write-Log "Unified scraping started!" "SUCCESS"
}

# Start specific tool
function Start-Tool {
    param([string]$Tool)
    
    Write-Log "Starting $Tool scraper..."
    
    $ToolCommands = @{
        "Motia" = "python main.py --tool motia --crawl-all"
        "Flyde" = "python main.py --tool flyde --extract-flows"
        "ChartDB" = "python main.py --tool chartdb --extract-diagrams"
        "JSONCrack" = "python main.py --tool jsoncrack --extract-visualizations"
    }
    
    if ($ToolCommands.ContainsKey($Tool)) {
        Start-Process -FilePath "python" -ArgumentList "main.py", "--tool", $Tool.ToLower(), "--crawl-all" -WindowStyle Hidden
        Write-Log "$Tool scraper started!" "SUCCESS"
    } else {
        Write-Log "Unknown tool: $Tool" "ERROR"
    }
}

# Test function
function Test-System {
    Write-Log "Running system tests..."
    
    # Test Python imports
    Write-Log "Testing Python imports..."
    python -c "import requests, aiohttp, beautifulsoup4, fastapi; print('All imports successful')"
    
    # Test Node.js imports
    Write-Log "Testing Node.js imports..."
    node -e "console.log('Node.js working')"
    
    Write-Log "System tests completed!" "SUCCESS"
}

# Status function
function Get-Status {
    Write-Log "Checking system status..."
    
    # Check processes
    $Processes = Get-Process | Where-Object { $_.ProcessName -eq "python" -or $_.ProcessName -eq "node" }
    Write-Log "Active processes: $($Processes.Count)"
    
    # Check ports
    $Ports = @(8000, 8001, 8002, 8003, 8004, 8005)
    foreach ($Port in $Ports) {
        $Connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($Connection) {
            Write-Log "Port $Port is active" "SUCCESS"
        } else {
            Write-Log "Port $Port is not active" "WARN"
        }
    }
    
    # Check data directory
    $DataFiles = Get-ChildItem -Path $DataDir -Recurse | Measure-Object
    Write-Log "Data files: $($DataFiles.Count)"
    
    # Check logs
    $LogFiles = Get-ChildItem -Path $LogDir | Measure-Object
    Write-Log "Log files: $($LogFiles.Count)"
}

# Stop function
function Stop-AllServices {
    Write-Log "Stopping all services..."
    
    # Stop Python processes
    Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force
    
    # Stop Node.js processes
    Get-Process | Where-Object { $_.ProcessName -eq "node" } | Stop-Process -Force
    
    Write-Log "All services stopped!" "SUCCESS"
}

# Restart function
function Restart-AllServices {
    Write-Log "Restarting all services..."
    Stop-AllServices
    Start-Sleep -Seconds 3
    Start-AllServices
}

# Main execution
Write-Log "Unified Documentation Scraper Launcher" "INFO"
Write-Log "Action: $Action" "INFO"
Write-Log "Project Root: $ProjectRoot" "INFO"

switch ($Action) {
    "Setup" {
        Initialize-Setup
    }
    "All" {
        Start-AllServices
    }
    "Motia" {
        Start-Tool "Motia"
    }
    "Flyde" {
        Start-Tool "Flyde"
    }
    "ChartDB" {
        Start-Tool "ChartDB"
    }
    "JSONCrack" {
        Start-Tool "JSONCrack"
    }
    "WebUI" {
        Start-WebUI
    }
    "MCP" {
        Start-MCPServers
    }
    "Test" {
        Test-System
    }
    "Status" {
        Get-Status
    }
    "Stop" {
        Stop-AllServices
    }
    "Restart" {
        Restart-AllServices
    }
    default {
        Write-Log "Unknown action: $Action" "ERROR"
        Write-Log "Available actions: Setup, All, Motia, Flyde, ChartDB, JSONCrack, WebUI, MCP, Test, Status, Stop, Restart" "INFO"
    }
}

Write-Log "Script execution completed!" "SUCCESS"