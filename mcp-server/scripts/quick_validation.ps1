# Quick MCP Server Validation Script for Windows PowerShell
# Usage: .\quick_validation.ps1

Write-Host "🚀 MCP Server Quick Validation" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green

$serverURL = "http://localhost:3011"
$successCount = 0
$totalTests = 0

function Test-Endpoint {
    param($name, $url, $method = "GET", $body = $null)
    
    $totalTests++
    Write-Host "`n🔍 Testing $name..." -ForegroundColor Yellow
    
    try {
        if ($method -eq "POST" -and $body) {
            $response = Invoke-RestMethod -Uri $url -Method POST -Body $body -ContentType "application/json"
        } else {
            $response = Invoke-RestMethod -Uri $url -Method $method
        }
        
        Write-Host "  ✅ SUCCESS" -ForegroundColor Green
        if ($response -is [string]) {
            Write-Host "  📄 Response: $response" -ForegroundColor White
        } else {
            Write-Host "  📄 Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor White
        }
        $script:successCount++
        return $true
    } catch {
        Write-Host "  ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test 1: Health Check
Test-Endpoint "Health Check" "$serverURL/health"

# Test 2: Tools List
Test-Endpoint "Tools List" "$serverURL/tools"

# Test 3: List Files Tool
$listFilesPayload = @{
    tool = "list_files_in_vault"
    params = @{}
} | ConvertTo-Json
Test-Endpoint "List Files Tool" "$serverURL/tools/execute" "POST" $listFilesPayload

# Test 4: Search Vault Tool
$searchPayload = @{
    tool = "search_vault"
    params = @{
        query = "test"
        limit = 5
    }
} | ConvertTo-Json
Test-Endpoint "Search Vault Tool" "$serverURL/tools/execute" "POST" $searchPayload

# Test 5: Read Note Tool
$readNotePayload = @{
    tool = "read_note"
    params = @{
        filename = "test-note.md"
    }
} | ConvertTo-Json
Test-Endpoint "Read Note Tool" "$serverURL/tools/execute" "POST" $readNotePayload

# Test 6: Semantic Search Tool
$semanticPayload = @{
    tool = "semantic_search"
    params = @{
        query = "artificial intelligence"
        top_k = 3
    }
} | ConvertTo-Json
Test-Endpoint "Semantic Search Tool" "$serverURL/tools/execute" "POST" $semanticPayload

# Test 7: Create Note Tool
$createNotePayload = @{
    tool = "create_note"
    params = @{
        path = "validation-test.md"
        content = "# Validation Test`n`nThis note was created during validation testing."
    }
} | ConvertTo-Json
Test-Endpoint "Create Note Tool" "$serverURL/tools/execute" "POST" $createNotePayload

# Test 8: Bulk Tag Tool
$bulkTagPayload = @{
    tool = "bulk_tag"
    params = @{
        tags = @("validation", "test", "mcp")
    }
} | ConvertTo-Json
Test-Endpoint "Bulk Tag Tool" "$serverURL/tools/execute" "POST" $bulkTagPayload

# Test 9: Analyze Links Tool
$analyzeLinksPayload = @{
    tool = "analyze_links"
    params = @{}
} | ConvertTo-Json
Test-Endpoint "Analyze Links Tool" "$serverURL/tools/execute" "POST" $analyzeLinksPayload

# Test 10: Error Handling (Invalid Tool)
$invalidToolPayload = @{
    tool = "nonexistent_tool"
    params = @{}
} | ConvertTo-Json
Write-Host "`n🔍 Testing Error Handling (Invalid Tool)..." -ForegroundColor Yellow
$totalTests++
try {
    $response = Invoke-RestMethod -Uri "$serverURL/tools/execute" -Method POST -Body $invalidToolPayload -ContentType "application/json"
    if ($response.success -eq $false) {
        Write-Host "  ✅ SUCCESS (Error handled correctly)" -ForegroundColor Green
        Write-Host "  📄 Error: $($response.error)" -ForegroundColor White
        $successCount++
    } else {
        Write-Host "  ❌ FAILED (Should have returned error)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✅ SUCCESS (Error handled correctly)" -ForegroundColor Green
    Write-Host "  📄 Exception: $($_.Exception.Message)" -ForegroundColor White
    $successCount++
}

# Summary
Write-Host "`n📊 VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $($totalTests - $successCount)" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($successCount/$totalTests)*100, 1))%" -ForegroundColor Yellow

if ($successCount -eq $totalTests) {
    Write-Host "`n🎉 ALL TESTS PASSED! MCP Server is fully functional." -ForegroundColor Green
} elseif ($successCount -ge ($totalTests * 0.8)) {
    Write-Host "`n⚠️ MOSTLY FUNCTIONAL: $([math]::Round(($successCount/$totalTests)*100, 1))% success rate" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ NEEDS ATTENTION: $([math]::Round(($successCount/$totalTests)*100, 1))% success rate" -ForegroundColor Red
}

Write-Host "`n🚀 Ready to start interactive chat!" -ForegroundColor Green
Write-Host "Run: go run scripts/interactive_cli.go" -ForegroundColor White
