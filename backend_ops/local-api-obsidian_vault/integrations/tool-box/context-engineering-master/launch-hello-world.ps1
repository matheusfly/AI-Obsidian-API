#!/usr/bin/env pwsh
# Context Engineering Master - Complete Hello World Launch Script
# Unified Motia-based system with interactive web UI

param(
    [switch]$Setup,
    [switch]$Dev,
    [switch]$Build,
    [switch]$Deploy,
    [switch]$All,
    [switch]$Help
)

# Color definitions
$GREEN = "`e[32m"
$BLUE = "`e[34m"
$YELLOW = "`e[33m"
$RED = "`e[31m"
$PURPLE = "`e[35m"
$CYAN = "`e[36m"
$NC = "`e[0m"

# Banner
function Show-Banner {
    Write-Host ""
    Write-Host "$PURPLE╔══════════════════════════════════════════════════════════════════════════════╗$NC"
    Write-Host "$PURPLE║                                                                              ║$NC"
    Write-Host "$PURPLE║  🧠 Context Engineering Master - Hello World System                         ║$NC"
    Write-Host "$PURPLE║  🚀 Powered by Motia - Unified Backend Framework                           ║$NC"
    Write-Host "$PURPLE║  🎨 Interactive Web UI with Real-time Context Compression                   ║$NC"
    Write-Host "$PURPLE║  🔧 Complete Tool-Box Integration with MCP Servers                          ║$NC"
    Write-Host "$PURPLE║                                                                              ║$NC"
    Write-Host "$PURPLE╚══════════════════════════════════════════════════════════════════════════════╝$NC"
    Write-Host ""
}

# Help function
function Show-Help {
    Show-Banner
    Write-Host "$BLUE Context Engineering Master - Complete Hello World System$NC"
    Write-Host ""
    Write-Host "Usage: .\launch-hello-world.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Setup     Set up the complete development environment"
    Write-Host "  -Dev       Start development server with hot reload"
    Write-Host "  -Build     Build the application for production"
    Write-Host "  -Deploy    Deploy to production environment"
    Write-Host "  -All       Start all services (recommended for first run)"
    Write-Host "  -Help      Show this help message"
    Write-Host ""
    Write-Host "Features:"
    Write-Host "  • Interactive Hello World API with Motia"
    Write-Host "  • Real-time Context Compression Engine"
    Write-Host "  • AI Agent Coordination System"
    Write-Host "  • Performance Monitoring Dashboard"
    Write-Host "  • Tool Orchestrator for all tool-box components"
    Write-Host "  • MCP Server Integration (Context7, ChartDB, Motia Docs)"
    Write-Host "  • Visual Web UI with React + TypeScript"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\launch-hello-world.ps1 -Setup    # Initial setup"
    Write-Host "  .\launch-hello-world.ps1 -All      # Start everything"
    Write-Host "  .\launch-hello-world.ps1 -Dev      # Development mode"
    Write-Host ""
}

# Setup function
function Invoke-Setup {
    Write-Host "$YELLOW Setting up Context Engineering Master Hello World System...$NC"
    Write-Host ""
    
    # Check prerequisites
    Write-Host "$BLUE Checking prerequisites...$NC"
    
    # Check Node.js
    try {
        $nodeVersion = node --version
        Write-Host "$GREEN✓ Node.js: $nodeVersion$NC"
    } catch {
        Write-Host "$RED✗ Node.js not found. Please install Node.js 18+ from https://nodejs.org$NC"
        exit 1
    }
    
    # Check Python
    try {
        $pythonVersion = python --version
        Write-Host "$GREEN✓ Python: $pythonVersion$NC"
    } catch {
        Write-Host "$RED✗ Python not found. Please install Python 3.9+ from https://python.org$NC"
        exit 1
    }
    
    Write-Host ""
    Write-Host "$BLUE Installing dependencies...$NC"
    
    # Install Node.js dependencies
    Write-Host "$CYAN Installing Node.js dependencies...$NC"
    npm install
    
    # Install web UI dependencies
    Write-Host "$CYAN Installing web UI dependencies...$NC"
    Set-Location "web-ui"
    npm install
    Set-Location ".."
    
    # Create necessary directories
    Write-Host "$CYAN Creating directories...$NC"
    New-Item -ItemType Directory -Force -Path "data", "logs", "web-ui/dist" | Out-Null
    
    # Set up environment variables
    Write-Host "$CYAN Setting up environment...$NC"
    if (-not (Test-Path ".env")) {
        @"
# Context Engineering Master Environment Variables
NODE_ENV=development
PORT=3000
WEB_UI_PORT=5173

# Database
DATABASE_URL=postgresql://localhost:5432/context_engineering
REDIS_URL=redis://localhost:6379

# AI Providers
OPENAI_API_KEY=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
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=AIzaSyAA7jg9__c_YZmcspAsydTkq33MGrK4Ynw

# MCP Servers
CONTEXT7_MCP_PORT=8004
CHARTDB_MCP_PORT=8003
MOTIA_DOCS_MCP_PORT=8005

# Monitoring
PROMETHEUS_PORT=9090
JAEGER_ENDPOINT=http://localhost:14268/api/traces

# Development
HOT_RELOAD=true
DEBUG_MODE=true
WORKBENCH_PORT=3001
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "$GREEN✓ Created .env file with your API keys$NC"
    }
    
    Write-Host ""
    Write-Host "$GREEN✓ Setup completed successfully!$NC"
    Write-Host ""
    Write-Host "$BLUE Next steps:$NC"
    Write-Host "  1. Run: .\launch-hello-world.ps1 -All"
    Write-Host "  2. Open http://localhost:3000 for Motia Workbench"
    Write-Host "  3. Open http://localhost:5173 for Interactive Web UI"
    Write-Host "  4. Try the Hello World API and explore all features!"
    Write-Host ""
}

# Development function
function Start-Development {
    Write-Host "$YELLOW Starting Context Engineering Master in development mode...$NC"
    Write-Host ""
    
    # Start Motia development server
    Write-Host "$BLUE Starting Motia development server...$NC"
    Start-Process -FilePath "npx" -ArgumentList "motia", "dev" -WindowStyle Normal
    
    # Wait a moment for Motia to start
    Start-Sleep -Seconds 3
    
    # Start web UI development server
    Write-Host "$BLUE Starting web UI development server...$NC"
    Set-Location "web-ui"
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Normal
    Set-Location ".."
    
    Write-Host ""
    Write-Host "$GREEN✓ Development servers started!$NC"
    Write-Host ""
    Write-Host "$BLUE Access points:$NC"
    Write-Host "  • Motia Workbench: http://localhost:3000"
    Write-Host "  • Interactive Web UI: http://localhost:5173"
    Write-Host "  • API Documentation: http://localhost:3000/docs"
    Write-Host ""
    Write-Host "$YELLOW Features available:$NC"
    Write-Host "  • Interactive Hello World API"
    Write-Host "  • Real-time Context Compression"
    Write-Host "  • AI Agent Coordination"
    Write-Host "  • Performance Monitoring"
    Write-Host "  • Tool Orchestrator"
    Write-Host ""
    Write-Host "$YELLOW Press Ctrl+C to stop all services$NC"
    
    # Keep script running
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } catch {
        Write-Host ""
        Write-Host "$YELLOW Stopping development servers...$NC"
    }
}

# Build function
function Invoke-Build {
    Write-Host "$YELLOW Building Context Engineering Master for production...$NC"
    Write-Host ""
    
    # Build Motia application
    Write-Host "$BLUE Building Motia application...$NC"
    npx motia build
    
    # Build web UI
    Write-Host "$BLUE Building web UI...$NC"
    Set-Location "web-ui"
    npm run build
    Set-Location ".."
    
    Write-Host ""
    Write-Host "$GREEN✓ Build completed successfully!$NC"
    Write-Host ""
    Write-Host "$BLUE Build outputs:$NC"
    Write-Host "  • Motia build: ./dist/"
    Write-Host "  • Web UI build: ./web-ui/dist/"
    Write-Host ""
}

# Deploy function
function Invoke-Deploy {
    Write-Host "$YELLOW Deploying Context Engineering Master to production...$NC"
    Write-Host ""
    
    # Build first
    Invoke-Build
    
    # Deploy with Motia
    Write-Host "$BLUE Deploying with Motia...$NC"
    npx motia deploy
    
    Write-Host ""
    Write-Host "$GREEN✓ Deployment completed successfully!$NC"
    Write-Host ""
}

# Start all services
function Start-All {
    Write-Host "$YELLOW Starting all Context Engineering Master services...$NC"
    Write-Host ""
    
    # Check if setup is needed
    if (-not (Test-Path "node_modules")) {
        Write-Host "$YELLOW First time setup detected. Running setup...$NC"
        Invoke-Setup
    }
    
    # Start development mode
    Start-Development
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Show-Banner

if ($Setup) {
    Invoke-Setup
} elseif ($Dev) {
    Start-Development
} elseif ($Build) {
    Invoke-Build
} elseif ($Deploy) {
    Invoke-Deploy
} elseif ($All) {
    Start-All
} else {
    Show-Help
}
