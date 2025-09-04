# 🚀 LAUNCH ALL TOOLS - Unified Documentation Scraper
# Quick launcher for all documentation scrapers

param(
    [Parameter(Position=0)]
    [ValidateSet("Setup", "All", "Motia", "Flyde", "ChartDB", "JSONCrack", "WebUI", "Test", "Status", "Stop")]
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
$Magenta = "`e[35m"
$White = "`e[37m"
$Reset = "`e[0m"

# Get current directory
$CurrentDir = Get-Location
$ToolBoxDir = "D:\codex\master_code\backend_ops\local-api-obsidian_vault\tool-box"

Write-Host "${Cyan}🚀 UNIFIED DOCUMENTATION SCRAPER LAUNCHER${Reset}"
Write-Host "${Blue}Action: $Action${Reset}"
Write-Host "${Blue}Tool Box Directory: $ToolBoxDir${Reset}"

# Function to run command in tool-box directory
function Invoke-ToolBoxCommand {
    param([string]$Command, [string]$WorkingDir = $ToolBoxDir)
    
    Write-Host "${Yellow}Executing: $Command${Reset}"
    Set-Location $WorkingDir
    Invoke-Expression $Command
    Set-Location $CurrentDir
}

# Setup function
function Initialize-Setup {
    Write-Host "${Green}🔧 Setting up unified scraper system...${Reset}"
    
    # Setup unified scraper
    Invoke-ToolBoxCommand ".\unified-docs-scraper\scripts\launch_unified.ps1 -Action Setup -Force"
    
    # Setup individual scrapers
    Invoke-ToolBoxCommand ".\motia-docs-scraper\scripts\launch_motia.ps1 -Action Setup -Force"
    Invoke-ToolBoxCommand ".\flyde-docs-scraper\scripts\launch_flyde.ps1 -Action Setup -Force"
    Invoke-ToolBoxCommand ".\chartdb-docs-scraper\scripts\launch_chartdb.ps1 -Action Setup -Force"
    Invoke-ToolBoxCommand ".\jsoncrack-docs-scraper\scripts\launch_jsoncrack.ps1 -Action Setup -Force"
    
    Write-Host "${Green}✅ Setup completed!${Reset}"
}

# Start all services
function Start-AllServices {
    Write-Host "${Green}🚀 Starting all documentation scrapers...${Reset}"
    
    # Start unified scraper
    Invoke-ToolBoxCommand ".\unified-docs-scraper\scripts\launch_unified.ps1 -Action All"
    
    Write-Host "${Green}✅ All services started!${Reset}"
    Write-Host "${Cyan}🌐 Web UI: http://localhost:8000${Reset}"
    Write-Host "${Cyan}📊 MCP Servers: 8001-8005${Reset}"
}

# Start specific tool
function Start-Tool {
    param([string]$Tool)
    
    Write-Host "${Green}🚀 Starting $Tool scraper...${Reset}"
    
    switch ($Tool) {
        "Motia" {
            Invoke-ToolBoxCommand ".\motia-docs-scraper\scripts\launch_motia.ps1 -Action All"
        }
        "Flyde" {
            Invoke-ToolBoxCommand ".\flyde-docs-scraper\scripts\launch_flyde.ps1 -Action All"
        }
        "ChartDB" {
            Invoke-ToolBoxCommand ".\chartdb-docs-scraper\scripts\launch_chartdb.ps1 -Action All"
        }
        "JSONCrack" {
            Invoke-ToolBoxCommand ".\jsoncrack-docs-scraper\scripts\launch_jsoncrack.ps1 -Action All"
        }
    }
    
    Write-Host "${Green}✅ $Tool scraper started!${Reset}"
}

# Start web UI
function Start-WebUI {
    Write-Host "${Green}🌐 Starting web UI...${Reset}"
    Invoke-ToolBoxCommand ".\unified-docs-scraper\scripts\launch_unified.ps1 -Action WebUI"
    Write-Host "${Green}✅ Web UI started at http://localhost:8000${Reset}"
}

# Test system
function Test-System {
    Write-Host "${Green}🧪 Testing system...${Reset}"
    Invoke-ToolBoxCommand ".\unified-docs-scraper\scripts\launch_unified.ps1 -Action Test"
    Write-Host "${Green}✅ System test completed!${Reset}"
}

# Get status
function Get-Status {
    Write-Host "${Green}📊 Checking system status...${Reset}"
    Invoke-ToolBoxCommand ".\unified-docs-scraper\scripts\launch_unified.ps1 -Action Status"
}

# Stop all services
function Stop-AllServices {
    Write-Host "${Red}🛑 Stopping all services...${Reset}"
    Invoke-ToolBoxCommand ".\unified-docs-scraper\scripts\launch_unified.ps1 -Action Stop"
    Write-Host "${Red}✅ All services stopped!${Reset}"
}

# Main execution
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
    "Test" {
        Test-System
    }
    "Status" {
        Get-Status
    }
    "Stop" {
        Stop-AllServices
    }
    default {
        Write-Host "${Red}❌ Unknown action: $Action${Reset}"
        Write-Host "${Yellow}Available actions: Setup, All, Motia, Flyde, ChartDB, JSONCrack, WebUI, Test, Status, Stop${Reset}"
    }
}

Write-Host "${Cyan}🎉 Script execution completed!${Reset}"