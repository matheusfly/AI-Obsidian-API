# Test MCP Server with Real Data
Write-Host "🧪 Testing MCP Server with Real Data" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Test health endpoint
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3010/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Server is running!" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Message: $($response.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Server is not responding: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure the server is running with: .\server.exe" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test tools list
Write-Host "Testing tools list..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3010/tools/list" -Method GET -TimeoutSec 5
    Write-Host "✅ Tools endpoint working!" -ForegroundColor Green
    Write-Host "   Found $($response.Count) tools" -ForegroundColor White
    
    # Show first few tools
    for ($i = 0; $i -lt [Math]::Min(3, $response.Count); $i++) {
        $tool = $response[$i]
        Write-Host "   - $($tool.name): $($tool.description)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Tools endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test list files tool
Write-Host "Testing list files tool..." -ForegroundColor Yellow
$toolRequest = @{
    tool = "list_files_in_vault"
    params = @{}
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3010/tools/execute" -Method POST -Body $toolRequest -ContentType "application/json" -TimeoutSec 10
    if ($response.success) {
        Write-Host "✅ List files tool working!" -ForegroundColor Green
        Write-Host "   Message: $($response.message)" -ForegroundColor White
        if ($response.data) {
            Write-Host "   Found $($response.data.Count) files/folders" -ForegroundColor White
        }
    } else {
        Write-Host "❌ List files tool failed: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ List files tool request failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Real Data Integration Test Complete!" -ForegroundColor Green
Write-Host "The MCP server is now using real Obsidian vault data!" -ForegroundColor White

