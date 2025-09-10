# MCP Tools Complete Setup Script
# This script sets up all MCP tools for Cursor and Warp

Write-Host "🚀 Starting MCP Tools Complete Setup..." -ForegroundColor Green

# Check if Node.js is installed
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if npm is available
try {
    $npmVersion = npm --version
    Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install npm first." -ForegroundColor Red
    exit 1
}

# Install global MCP packages
Write-Host "📦 Installing MCP packages..." -ForegroundColor Yellow

$mcpPackages = @(
    "@modelcontextprotocol/server-filesystem",
    "@modelcontextprotocol/server-github",
    "mcp-server-sqlite",
    "mcp-server-postgres",
    "mcp-server-brave-search",
    "mcp-server-playwright",
    "mcp-server-context7",
    "mcp-server-shadcn-ui",
    "mcp-server-byterover",
    "mcp-server-sequential-thinking",
    "mcp-server-web-search",
    "mcp-server-memory"
)

foreach ($package in $mcpPackages) {
    Write-Host scripts/ing $package..." -ForegroundColor Cyan
    try {
        npm install -g $package
        Write-Host "✅ $package installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Failed to install $package, continuing..." -ForegroundColor Yellow
    }
}

# Install dependencies for custom MCP servers
Write-Host "📦 Installing custom MCP server dependencies..." -ForegroundColor Yellow

$customServers = @("graphiti-server", servicesservices/aci-server", servicesservices/obsidian-mcp-server")

foreach ($server in $customServers) {
    $serverPath = Join-Path $PSScriptRoot $server
    if (Test-Path $serverPath) {
        Write-Host scripts/ing dependencies for $server..." -ForegroundColor Cyan
        Set-Location $serverPath
        try {
            npm install
            Write-Host "✅ $server dependencies installed" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Failed to install dependencies for $server" -ForegroundColor Yellow
        }
        Set-Location $PSScriptRoot
    }
}

# Create environment file
Write-Host "🔧 Creating environment configuration..." -ForegroundColor Yellow

$envContent = @"
# MCP Tools Environment Configuration
# Copy this to your .env file or set these as system environment variables

# OpenAI API Key
OPENAI_API_KEY=$env:OPENAI_API_KEY

# ACI Key
ACI_KEY=$env:ACI_KEY

# GitHub Personal Access Token (replace with your token)
GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_TOKEN_HERE

# Brave Search API Key (get from https://brave.com/search/api/)
BRAVE_API_KEY=YOUR_BRAVE_API_KEY_HERE

# Context7 API Key (get from https://context7.ai/)
CONTEXT7_API_KEY=YOUR_CONTEXT7_API_KEY_HERE

# Byterover API Key (get from https://byterover.com/)
BYTEROVER_API_KEY=YOUR_BYTEROVER_API_KEY_HERE

# SERP API Key (get from https://serpapi.com/)
SERP_API_KEY=YOUR_SERP_API_KEY_HERE

# Vault Path
VAULT_PATH=D:\Nomade Milionario

# Database Paths
MEMORY_DB_PATH=D:\codex\master_code\backend_ops\local-api-obsidian_vault\memory.db
"@

$envContent | Out-File -FilePath "mcp-env-template.txt" -Encoding UTF8
Write-Host "✅ Environment template created: mcp-env-template.txt" -ForegroundColor Green

# Create directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow

$directories = @(
    data/",
    logs/",
    datadata/memory"
)

foreach ($dir in $directories) {
    $dirPath = Join-Path $PSScriptRoot $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# Create test script
Write-Host "🧪 Creating test script..." -ForegroundColor Yellow

$testScriptContent = @"
# Test MCP Tools
Write-Host scripts/ing MCP Tools..." -ForegroundColor Green

# Test Graphiti server
Write-Host scripts/ing Graphiti server..." -ForegroundColor Yellow
try {
    node graphiti-server/index.js --test
    Write-Host "✅ Graphiti server test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Graphiti server test failed" -ForegroundColor Red
}

# Test ACI server
Write-Host scripts/ing ACI server..." -ForegroundColor Yellow
try {
    node aci-server/index.js --test
    Write-Host "✅ ACI server test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ ACI server test failed" -ForegroundColor Red
}

# Test Obsidian Vault server
Write-Host scripts/ing Obsidian Vault server..." -ForegroundColor Yellow
try {
    node obsidian-mcp-server/index.js --test
    Write-Host "✅ Obsidian Vault server test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Obsidian Vault server test failed" -ForegroundColor Red
}

Write-Host "MCP Tools testing completed!" -ForegroundColor Green
"@

$testScriptContent | Out-File -FilePath scripts/-mcp-tools.ps1" -Encoding UTF8
Write-Host "✅ Test script created: test-mcp-tools.ps1" -ForegroundColor Green

Write-Host "🎉 MCP Tools setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update API keys in mcp-env-template.txt" -ForegroundColor White
Write-Host "2. Copy cursor-mcp-config.json to Cursor settings" -ForegroundColor White
Write-Host "3. Copy WARP_MCP_CONFIG_PASTE_READY.json to Warp settings" -ForegroundColor White
Write-Host "4. Run test-mcp-tools.ps1 to verify installation" -ForegroundColor White
Write-Host "5. Read MCP_COMPLETE_SETUP_README.md for detailed usage instructions" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding with MCP tools! 🚀" -ForegroundColor Green
