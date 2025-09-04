#!/usr/bin/env pwsh
# ChartDB Hello World - Quick Launch Script
# Interactive UI Nodes with Real-time Updates

param(
    [switch]$Install,
    [switch]$Start,
    [switch]$Dev,
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
    Write-Host "$PURPLE║  📊 ChartDB Hello World - Interactive UI Nodes                              ║$NC"
    Write-Host "$PURPLE║  🎨 Real-time Visualizations with WebSocket Updates                         ║$NC"
    Write-Host "$PURPLE║  🔗 Interactive Network Graphs and Data Charts                              ║$NC"
    Write-Host "$PURPLE║  ⚡ Quick Start for Visual Database Exploration                             ║$NC"
    Write-Host "$PURPLE║                                                                              ║$NC"
    Write-Host "$PURPLE╚══════════════════════════════════════════════════════════════════════════════╝$NC"
    Write-Host ""
}

# Help function
function Show-Help {
    Show-Banner
    Write-Host "$BLUE ChartDB Hello World - Interactive UI Nodes$NC"
    Write-Host ""
    Write-Host "Usage: .\launch-chartdb.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Install    Install dependencies"
    Write-Host "  -Start      Start the server"
    Write-Host "  -Dev        Start in development mode with auto-reload"
    Write-Host "  -All        Install and start everything (recommended)"
    Write-Host "  -Help       Show this help message"
    Write-Host ""
    Write-Host "Features:"
    Write-Host "  • Interactive Network Visualization"
    Write-Host "  • Real-time WebSocket Updates"
    Write-Host "  • Clickable UI Nodes"
    Write-Host "  • Live Data Charts"
    Write-Host "  • Responsive Design"
    Write-Host "  • Node Statistics"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\launch-chartdb.ps1 -All      # Quick start"
    Write-Host "  .\launch-chartdb.ps1 -Dev      # Development mode"
    Write-Host ""
}

# Install function
function Invoke-Install {
    Write-Host "$YELLOW Installing ChartDB Hello World dependencies...$NC"
    Write-Host ""
    
    # Check Node.js
    try {
        $nodeVersion = node --version
        Write-Host "$GREEN✓ Node.js: $nodeVersion$NC"
    } catch {
        Write-Host "$RED✗ Node.js not found. Please install Node.js 18+ from https://nodejs.org$NC"
        exit 1
    }
    
    # Install dependencies
    Write-Host "$CYAN Installing npm packages...$NC"
    npm install
    
    Write-Host ""
    Write-Host "$GREEN✓ Installation completed successfully!$NC"
    Write-Host ""
}

# Start function
function Start-Server {
    Write-Host "$YELLOW Starting ChartDB Hello World server...$NC"
    Write-Host ""
    
    # Start server
    Write-Host "$BLUE Starting server on http://localhost:3001$NC"
    Write-Host "$BLUE Interactive UI available at http://localhost:3001$NC"
    Write-Host ""
    Write-Host "$YELLOW Features available:$NC"
    Write-Host "  • Interactive Network Visualization"
    Write-Host "  • Clickable UI Nodes with real-time updates"
    Write-Host "  • Live Data Charts and Statistics"
    Write-Host "  • WebSocket real-time communication"
    Write-Host ""
    Write-Host "$YELLOW Press Ctrl+C to stop the server$NC"
    Write-Host ""
    
    node server.js
}

# Development function
function Start-Development {
    Write-Host "$YELLOW Starting ChartDB Hello World in development mode...$NC"
    Write-Host ""
    
    # Check if nodemon is installed
    try {
        nodemon --version | Out-Null
    } catch {
        Write-Host "$YELLOW Installing nodemon for development...$NC"
        npm install -g nodemon
    }
    
    Write-Host "$BLUE Starting development server with auto-reload...$NC"
    Write-Host "$BLUE Server: http://localhost:3001$NC"
    Write-Host "$BLUE Interactive UI: http://localhost:3001$NC"
    Write-Host ""
    Write-Host "$YELLOW Development features:$NC"
    Write-Host "  • Auto-reload on file changes"
    Write-Host "  • Interactive debugging"
    Write-Host "  • Real-time WebSocket updates"
    Write-Host "  • Live node interactions"
    Write-Host ""
    Write-Host "$YELLOW Press Ctrl+C to stop the development server$NC"
    Write-Host ""
    
    npm run dev
}

# Start all
function Start-All {
    Write-Host "$YELLOW Starting ChartDB Hello World - Complete Setup$NC"
    Write-Host ""
    
    # Check if setup is needed
    if (-not (Test-Path "node_modules")) {
        Write-Host "$YELLOW First time setup detected. Installing dependencies...$NC"
        Invoke-Install
    }
    
    # Start server
    Start-Server
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Show-Banner

if ($Install) {
    Invoke-Install
} elseif ($Start) {
    Start-Server
} elseif ($Dev) {
    Start-Development
} elseif ($All) {
    Start-All
} else {
    Show-Help
}
