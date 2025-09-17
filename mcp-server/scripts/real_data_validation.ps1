# real_data_validation.ps1
# Comprehensive validation with real Obsidian vault data

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

Write-Host "🚀 Real Obsidian Vault Data Validation"
Write-Host "======================================"
Write-Host "Testing MCP Server with real vault data from: D:\Nomade Milionario"
Write-Host "Expected: Real file names like 'AGENTS.md', 'Rust.md', etc."
Write-Host ""

# 1. Health Check
Test-Endpoint "Health Check" "GET" "/health" $null 200 {
    param($response, $statusCode)
    return $response.status -eq "healthy"
}

# 2. List Files Tool (Should show real vault files)
Test-Endpoint "List Files Tool (Real Data)" "POST" "/tools/execute" '{"tool": "list_files_in_vault", "params": {}}' 200 {
    param($response, $statusCode)
    if ($response.success -eq $true -and $response.data.Count -gt 0) {
        # Check if we're getting real data (not mock data)
        $hasRealFiles = $false
        foreach ($file in $response.data) {
            if ($file.name -like "*AGENTS*" -or $file.name -like "*Rust*" -or $file.name -like "*nomade*") {
                $hasRealFiles = $true
                break
            }
        }
        return $hasRealFiles
    }
    return $false
}

# 3. Search Vault Tool (Should find real files)
Test-Endpoint "Search Vault Tool (Real Data)" "POST" "/tools/execute" '{"tool": "search_vault", "params": {"query": "AGENTS", "limit": 5}}' 200 {
    param($response, $statusCode)
    if ($response.success -eq $true) {
        # Check if we found real files
        $hasRealResults = $false
        foreach ($result in $response.data) {
            if ($result.path -like "*AGENTS*") {
                $hasRealResults = $true
                break
            }
        }
        return $hasRealResults
    }
    return $false
}

# 4. Search for "Rust" (Should find Rust.md)
Test-Endpoint "Search for Rust" "POST" "/tools/execute" '{"tool": "search_vault", "params": {"query": "Rust", "limit": 5}}' 200 {
    param($response, $statusCode)
    if ($response.success -eq $true) {
        $hasRustResults = $false
        foreach ($result in $response.data) {
            if ($result.path -like "*Rust*") {
                $hasRustResults = $true
                break
            }
        }
        return $hasRustResults
    }
    return $false
}

# 5. Search for "nomade" (Should find files with "nomade" in name)
Test-Endpoint "Search for nomade" "POST" "/tools/execute" '{"tool": "search_vault", "params": {"query": "nomade", "limit": 5}}' 200 {
    param($response, $statusCode)
    if ($response.success -eq $true) {
        $hasNomadeResults = $false
        foreach ($result in $response.data) {
            if ($result.path -like "*nomade*" -or $result.path -like "*Nomade*") {
                $hasNomadeResults = $true
                break
            }
        }
        return $hasNomadeResults
    }
    return $false
}

# 6. Read Note Tool (Try to read a real file)
Test-Endpoint "Read Note Tool (Real File)" "POST" "/tools/execute" '{"tool": "read_note", "params": {"filename": "AGENTS.md"}}' 200 {
    param($response, $statusCode)
    return $response.success -eq $true
}

Write-Host "`n📊 REAL DATA VALIDATION SUMMARY"
Write-Host "================================"
Write-Host "Total Tests: $($script:totalTests)"
Write-Host "Successful: $($script:successCount)"
Write-Host "Failed: $($script:failCount)"
Write-Host "Success Rate: $([math]::Round($script:successCount / $script:totalTests * 100, 2))%"

if ($script:failCount -eq 0) {
    Write-Host "`n🎉 PERFECT! All tests passed with real vault data!"
    Write-Host "✅ MCP Server is successfully consuming real Obsidian vault data!"
} elseif ($script:successCount -gt 0) {
    Write-Host "`n✅ PARTIAL SUCCESS! Some tests passed with real data."
    Write-Host "⚠️ Check the failed tests above for details."
} else {
    Write-Host "`n❌ FAILED! Server is still using mock data."
    Write-Host "🔧 Server needs to be restarted in real mode."
}

Write-Host "`n🚀 Real Obsidian Vault Integration Test Complete!"
