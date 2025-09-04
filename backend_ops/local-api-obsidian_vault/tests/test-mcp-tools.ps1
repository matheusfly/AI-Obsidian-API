# Test MCP Tools
Write-Host "Testing MCP Tools..." -ForegroundColor Green

# Test Graphiti server
Write-Host "Testing Graphiti server..." -ForegroundColor Yellow
try {
    node graphiti-server/index.js --test
    Write-Host "✅ Graphiti server test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Graphiti server test failed" -ForegroundColor Red
}

# Test ACI server
Write-Host "Testing ACI server..." -ForegroundColor Yellow
try {
    node aci-server/index.js --test
    Write-Host "✅ ACI server test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ ACI server test failed" -ForegroundColor Red
}

# Test Obsidian Vault server
Write-Host "Testing Obsidian Vault server..." -ForegroundColor Yellow
try {
    node obsidian-mcp-server/index.js --test
    Write-Host "✅ Obsidian Vault server test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Obsidian Vault server test failed" -ForegroundColor Red
}

Write-Host "MCP Tools testing completed!" -ForegroundColor Green
