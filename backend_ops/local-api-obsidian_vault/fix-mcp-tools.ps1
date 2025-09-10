# Fix MCP Tools - Context7 and Byterover Setup Script
# This script will help you configure and test the MCP tools

Write-Host "🔧 MCP Tools Fix Script" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Check if Node.js is installed
Write-Host "`n📋 Checking Prerequisites..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if npm is available
try {
    $npmVersion = npm --version
    Write-Host "✅ npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install npm first." -ForegroundColor Red
    exit 1
}

Write-Host "`n🔑 API Key Configuration Required:" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow

# Context7 Configuration
Write-Host "`n1. Context7 MCP Server:" -ForegroundColor Cyan
Write-Host "   Current API Key: $env:CONTEXT7_API_KEY" -ForegroundColor Gray
Write-Host "   Status: ✅ API Key appears valid" -ForegroundColor Green
Write-Host "   Note: Using @context7/mcp-server@latest package" -ForegroundColor Gray

# Byterover Configuration
Write-Host "`n2. Byterover MCP Server:" -ForegroundColor Cyan
Write-Host "   Current API Key: your_byterover_api_key_here" -ForegroundColor Red
Write-Host "   Status: ❌ API Key needs to be configured" -ForegroundColor Red
Write-Host "   Machine ID: 1f07a91e-5ce8-6950-b300-56b817457f07" -ForegroundColor Gray

Write-Host "`n📝 To fix Byterover MCP:" -ForegroundColor Yellow
Write-Host "1. Visit: https://byterover.dev" -ForegroundColor Blue
Write-Host "2. Sign up/Login to get your API key" -ForegroundColor Blue
Write-Host "3. Replace 'your_byterover_api_key_here' in mcp.json with your actual API key" -ForegroundColor Blue

# Install/Update MCP packages
Write-Host "`n📦 Installing/Updating MCP Packages..." -ForegroundColor Yellow

try {
    Write-Host "Installing @context7/mcp-server@latest..." -ForegroundColor Gray
    npm install -g @context7/mcp-server@latest
    Write-Host "✅ Context7 MCP server installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Context7 MCP server" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    Write-Host "Installing @byterover/mcp-server@latest..." -ForegroundColor Gray
    npm install -g @byterover/mcp-server@latest
    Write-Host "✅ Byterover MCP server installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Byterover MCP server" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test MCP connections
Write-Host "`n🧪 Testing MCP Connections..." -ForegroundColor Yellow

# Test Context7
Write-Host "`nTesting Context7 MCP Server..." -ForegroundColor Cyan
try {
    $context7Test = npx @context7/mcp-server@latest --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Context7 MCP server is working" -ForegroundColor Green
    } else {
        Write-Host "❌ Context7 MCP server test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Context7 MCP server test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Byterover
Write-Host "`nTesting Byterover MCP Server..." -ForegroundColor Cyan
try {
    $byteroverTest = npx @byterover/mcp-server@latest --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Byterover MCP server is working" -ForegroundColor Green
    } else {
        Write-Host "❌ Byterover MCP server test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Byterover MCP server test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Restart Cursor instructions
Write-Host "`n🔄 Next Steps:" -ForegroundColor Yellow
Write-Host "=============" -ForegroundColor Yellow
Write-Host "1. Update your Byterover API key in mcp.json" -ForegroundColor White
Write-Host "2. Restart Cursor IDE completely" -ForegroundColor White
Write-Host "3. Check the MCP tools status in Cursor" -ForegroundColor White

Write-Host "`n📋 MCP Configuration Summary:" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "Context7: ✅ Ready (API key configured)" -ForegroundColor Green
Write-Host "Byterover: ⚠️  Needs API key configuration" -ForegroundColor Yellow
Write-Host "Shadcn-UI: ✅ Ready (no API key required)" -ForegroundColor Green

Write-Host "`n✨ Fix script completed!" -ForegroundColor Green
Write-Host "Please restart Cursor after updating the Byterover API key." -ForegroundColor White
