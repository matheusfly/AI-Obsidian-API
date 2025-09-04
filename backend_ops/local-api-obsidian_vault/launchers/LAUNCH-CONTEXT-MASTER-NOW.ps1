# Context Engineering Master - Ultimate Launch Script
# One-click launch for the complete unified knowledge compression and visual programming system

# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Clear screen and show banner
Clear-Host

# Color functions
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    if ($Color -eq "*") { $Color = "White" }
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host "`n" -NoNewline
    Write-ColorOutput "=" * 80 "Cyan"
    Write-ColorOutput " $Title" "Cyan"
    Write-ColorOutput "=" * 80 "Cyan"
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" "Yellow"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Magenta"
}

# Main banner
Write-Header "CONTEXT ENGINEERING MASTER"
Write-ColorOutput "🧠 Unified Knowledge Compression & Interactive Visual Programming" "White"
Write-ColorOutput "🚀 Powered by Motia, Flyde, MCP, and Context Engineering" "White"
Write-ColorOutput "📱 Interactive Web UI with Real-time Flow Execution" "White"
Write-ColorOutput "🎯 Compressing ALL your tools into ONE powerful system!" "White"
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path servicesservices/context-engineering-master")) {
    Write-Error "Context Engineering Master directory not found!"
    Write-Info "Please run this script from the correct location."
    Write-Info "Expected directory structure:"
    Write-Info "  local-api-obsidian_vault/"
    Write-Info "  ├── context-engineering-master/"
    Write-Info "  └── LAUNCH-CONTEXT-MASTER-NOW.ps1"
    Write-Host ""
    Write-Info "Current directory: $(Get-Location)"
    Write-Info "Available directories:"
    Get-ChildItem -Directory | ForEach-Object { Write-Info "  - $($_.Name)" }
    exit 1
}

# Change to context engineering directory
Set-Location servicesservices/context-engineering-master"

Write-Header "INITIALIZING CONTEXT ENGINEERING MASTER"

# Check prerequisites
Write-Info scripts/ing prerequisites..."

$prerequisites = @{
    "Node.js" = @{ Command = "node --version"; Required = $true }
    "npm" = @{ Command = "npm --version"; Required = $true }
}

$allGood = $true
foreach ($prereq in $prerequisites.GetEnumerator()) {
    try {
        $version = Invoke-Expression $prereq.Value.Command 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$($prereq.Key): $($version.Split("`n")[0])"
        } else {
            if ($prereq.Value.Required) {
                Write-Error "$($prereq.Key) is required but not found"
                $allGood = $false
            }
        }
    } catch {
        if ($prereq.Value.Required) {
            Write-Error "$($prereq.Key) is required but not found"
            $allGood = $false
        }
    }
}

if (-not $allGood) {
    Write-Error "Missing required prerequisites. Please install them and try again."
    Write-Info "Required: Node.js 18+ and npm"
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Info scripts/ing dependencies..."
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependencies installed successfully"
    } else {
        Write-Error "Failed to install dependencies"
        exit 1
    }
} else {
    Write-Success "Dependencies already installed"
}

Write-Header "STARTING CONTEXT ENGINEERING MASTER"

Write-Info "🚀 Starting the unified knowledge compression system..."
Write-Info "📱 Web UI will be available at: http://localhost:3000"
Write-Info "🔌 WebSocket: ws://localhost:3000"
Write-Info "📊 API: http://localhost:3000/api"
Write-Info "🕸️ Knowledge Graph: http://localhost:3000/api/graph/d3"
Write-Host ""

Write-ColorOutput "🎯 What you can do:" "Cyan"
Write-ColorOutput "  1. Open http://localhost:3000 in your browser" "White"
Write-ColorOutput "  2. Try the Hello World example flow" "White"
Write-ColorOutput "  3. Explore all your integrated tools" "White"
Write-ColorOutput "  4. Build custom visual workflows" "White"
Write-ColorOutput "  5. View the knowledge graph visualization" "White"
Write-ColorOutput "  6. Monitor MCP server integrations" "White"
Write-Host ""

Write-ColorOutput "🧠 Context Compression Features:" "Cyan"
Write-ColorOutput "  • Unified knowledge from ALL your tools" "White"
Write-ColorOutput "  • Real-time context compression" "White"
Write-ColorOutput "  • Visual relationship mapping" "White"
Write-ColorOutput "  • Intelligent tool recommendations" "White"
Write-ColorOutput "  • Interactive visual programming" "White"
Write-Host ""

Write-ColorOutput "🛠️ Integrated Tools:" "Cyan"
Write-ColorOutput "  • Motia Docs Scraper" "White"
Write-ColorOutput "  • ChartDB Visualizer" "White"
Write-ColorOutput "  • Flyde Visual Flows" "White"
Write-ColorOutput "  • Context7 Memory" "White"
Write-ColorOutput "  • Byterover MCP" "White"
Write-ColorOutput "  • Sentry Monitoring" "White"
Write-ColorOutput "  • Task Master AI" "White"
Write-ColorOutput "  • Obsidian Vault" "White"
Write-ColorOutput "  • PostgreSQL & Redis" "White"
Write-ColorOutput "  • GitHub Integration" "White"
Write-ColorOutput "  • And many more..." "White"
Write-Host ""

Write-ColorOutput "Press Ctrl+C to stop the server" "Magenta"
Write-Host ""

# Start the system
try {
    node src/index.js
} catch {
    Write-Error "Failed to start Context Engineering Master"
    Write-Info "Please check the logs and try again"
    exit 1
}

Write-Header "CONTEXT ENGINEERING MASTER STOPPED"
Write-Success "Thank you for using Context Engineering Master!"
Write-Info "Your knowledge has been compressed and your tools unified! 🧠✨"
