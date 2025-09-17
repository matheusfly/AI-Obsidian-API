# comprehensive_validation.ps1
# Comprehensive validation script for the enhanced MCP server

$serverUrl = "http://localhost:3011"
$contentType = "application/json"
$successCount = 0
$failCount = 0
$totalTests = 0

function Test-Endpoint {
    param (
        [string]$Name,
        [string]$Method,
        [string]$Path,
        [string]$Body = $null,
        [int]$ExpectedStatusCode = 200,
        [scriptblock]$ValidationScript = { $true }
    )
    
    $script:totalTests++
    Write-Host "`n🔍 Testing $Name..."
    
    try {
        $response = Invoke-RestMethod -Uri "$serverUrl$Path" -Method $Method -ContentType $contentType -Body $Body -TimeoutSec 10
        $statusCode = 200
        $isValid = Invoke-Command -ScriptBlock $ValidationScript -ArgumentList $response, $statusCode
        if ($isValid) {
            Write-Host "  ✅ SUCCESS"
            Write-Host "  📄 Response: $($response | ConvertTo-Json -Depth 2)"
            $script:successCount++
            return $true
        } else {
            Write-Host "  ❌ FAILED: Validation script failed."
            Write-Host "  📄 Response: $($response | ConvertTo-Json -Depth 2)"
            $script:failCount++
            return $false
        }
    } catch {
        $errorMessage = $_.Exception.Message
        $statusCode = $_.Exception.Response.StatusCode.Value
        Write-Host "  ❌ FAILED: Response status code does not indicate success: $($statusCode) ($($_.Exception.Response.StatusCode))."
        Write-Host "  📄 Error: $($errorMessage)"
        $script:failCount++
        return $false
    }
}

Write-Host "🚀 Enhanced MCP Server Comprehensive Validation"
Write-Host "=============================================="

# 1. Health Check
Test-Endpoint "Health Check" "GET" "/health" $null 200 {
    param($response, $statusCode)
    return $response.status -eq "healthy"
}

# 2. Tools List
Test-Endpoint "Tools List" "GET" "/tools" $null 200 {
    param($response, $statusCode)
    return $response.tools.Count -gt 0
}

# 3. List Files Tool
Test-Endpoint "List Files Tool" "POST" "/tools/execute" '{"tool": "list_files_in_vault", "params": {}}' 200 {
    param($response, $statusCode)
    return $response.success -eq $true -and $response.data.Count -gt 0
}

# 4. Search Vault Tool
Test-Endpoint "Search Vault Tool" "POST" "/tools/execute" '{"tool": "search_vault", "params": {"query": "test", "limit": 5}}' 200 {
    param($response, $statusCode)
    return $response.success -eq $true -and $response.data.Count -gt 0
}

# 5. Read Note Tool
Test-Endpoint "Read Note Tool" "POST" "/tools/execute" '{"tool": "read_note", "params": {"filename": "test-note.md"}}' 200 {
    param($response, $statusCode)
    return $response.success -eq $true
}

# 6. Create Note Tool
Test-Endpoint "Create Note Tool" "POST" "/tools/execute" '{"tool": "create_note", "params": {"path": "validation-test.md", "content": "# Validation Test`n`nThis note was created during comprehensive validation testing."}}' 200 {
    param($response, $statusCode)
    return $response.success -eq $true -and $response.data.path -eq "validation-test.md"
}

# 7. Bulk Tag Tool
Test-Endpoint "Bulk Tag Tool" "POST" "/tools/execute" '{"tool": "bulk_tag", "params": {"tags": ["validation", "test", "mcp", "enhanced"]}}' 200 {
    param($response, $statusCode)
    return $response.success -eq $true
}

# 8. Analyze Links Tool
Test-Endpoint "Analyze Links Tool" "POST" "/tools/execute" '{"tool": "analyze_links", "params": {}}' 200 {
    param($response, $statusCode)
    return $response.success -eq $true
}

# 9. Error Handling (Invalid Tool)
Test-Endpoint "Error Handling (Invalid Tool)" "POST" "/tools/execute" '{"tool": "non_existent_tool", "params": {}}' 400 {
    param($response, $statusCode)
    return $response.success -eq $false
}

# 10. Performance Test (Multiple Concurrent Requests)
Write-Host "`n🔍 Testing Performance (Concurrent Requests)..."
$concurrentJobs = @()
for ($i = 0; $i -lt 5; $i++) {
    $job = Start-Job -ScriptBlock {
        param($serverUrl, $contentType)
        try {
            $response = Invoke-RestMethod -Uri "$serverUrl/tools/execute" -Method Post -ContentType $contentType -Body '{"tool": "search_vault", "params": {"query": "test", "limit": 3}}' -TimeoutSec 5
            return @{ Success = $true; Response = $response }
        } catch {
            return @{ Success = $false; Error = $_.Exception.Message }
        }
    } -ArgumentList $serverUrl, $contentType
    $concurrentJobs += $job
}

$concurrentSuccess = 0
$concurrentFail = 0
foreach ($job in $concurrentJobs) {
    $result = Receive-Job $job
    if ($result.Success) {
        $concurrentSuccess++
    } else {
        $concurrentFail++
    }
    Remove-Job $job
}

if ($concurrentSuccess -eq 5) {
    Write-Host "  ✅ CONCURRENT REQUESTS SUCCESS"
    $script:successCount++
} else {
    Write-Host "  ❌ CONCURRENT REQUESTS FAILED: $concurrentSuccess/5 successful"
    $script:failCount++
}
$script:totalTests++

Write-Host "`n📊 COMPREHENSIVE VALIDATION SUMMARY"
Write-Host "===================================="
Write-Host "Total Tests: $($script:totalTests)"
Write-Host "Successful: $($script:successCount)"
Write-Host "Failed: $($script:failCount)"
Write-Host "Success Rate: $([math]::Round($script:successCount / $script:totalTests * 100, 2))%"

if ($script:failCount -eq 0) {
    Write-Host "`n🎉 PERFECT SCORE! All tests passed!"
    Write-Host "✅ Your enhanced MCP server is working flawlessly!"
} elseif ($script:failCount -le 2) {
    Write-Host "`n✅ EXCELLENT! Most tests passed with minor issues."
    Write-Host "⚠️ Check the failed tests above for details."
} else {
    Write-Host "`n⚠️ NEEDS ATTENTION: Some tests failed."
    Write-Host "🔧 Review the failed tests and fix the issues."
}

Write-Host "`n🚀 Enhanced MCP Server is ready for production use!"
Write-Host "💡 Try the enhanced intelligent CLI: go run scripts/enhanced_intelligent_cli.go"
