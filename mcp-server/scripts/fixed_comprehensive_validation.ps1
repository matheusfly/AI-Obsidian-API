# fixed_comprehensive_validation.ps1
# Fixed PowerShell script for comprehensive validation with proper job management

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

function Test-ConcurrentRequests {
    param (
        [int]$ConcurrentCount = 5
    )
    
    Write-Host "`n🔄 Testing Concurrent Requests ($ConcurrentCount requests)..."
    
    $jobs = @()
    $successfulRequests = 0
    
    # Start concurrent requests
    for ($i = 1; $i -le $ConcurrentCount; $i++) {
        $job = Start-Job -ScriptBlock {
            param($url, $contentType)
            try {
                $response = Invoke-RestMethod -Uri "$url/health" -Method GET -ContentType $contentType -TimeoutSec 5
                return @{ Success = $true; Response = $response }
            } catch {
                return @{ Success = $false; Error = $_.Exception.Message }
            }
        } -ArgumentList $serverUrl, $contentType
        
        $jobs += $job
    }
    
    # Wait for all jobs to complete with timeout
    $timeout = 30
    $startTime = Get-Date
    
    while ($jobs | Where-Object { $_.State -eq "Running" }) {
        if ((Get-Date) - $startTime -gt [TimeSpan]::FromSeconds($timeout)) {
            Write-Host "  ⚠️ Timeout reached, stopping remaining jobs..."
            $jobs | Where-Object { $_.State -eq "Running" } | Stop-Job -Force
            break
        }
        Start-Sleep -Milliseconds 100
    }
    
    # Collect results
    foreach ($job in $jobs) {
        $result = Receive-Job -Job $job
        if ($result.Success) {
            $successfulRequests++
        }
        Remove-Job -Job $job -Force
    }
    
    Write-Host "  📊 Concurrent Results: $successfulRequests/$ConcurrentCount successful"
    
    if ($successfulRequests -eq $ConcurrentCount) {
        Write-Host "  ✅ CONCURRENT REQUESTS SUCCESS"
        $script:successCount++
    } else {
        Write-Host "  ❌ CONCURRENT REQUESTS FAILED: $successfulRequests/$ConcurrentCount successful"
        $script:failCount++
    }
    
    $script:totalTests++
}

Write-Host "🚀 Fixed Comprehensive MCP Server Validation"
Write-Host "==========================================="
Write-Host "Testing MCP Server with real Obsidian vault data"
Write-Host ""

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

# 3. List Files Tool (Should show real vault files)
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

# 4. Search Vault Tool (Should find real files)
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

# 5. Search for "Rust" (Should find Rust.md)
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

# 6. Read Note Tool (Try to read a real file)
Test-Endpoint "Read Note Tool (Real File)" "POST" "/tools/execute" '{"tool": "read_note", "params": {"filename": "AGENTS.md"}}' 200 {
    param($response, $statusCode)
    return $response.success -eq $true
}

# 7. Error Handling (Invalid Tool)
Test-Endpoint "Error Handling (Invalid Tool)" "POST" "/tools/execute" '{"tool": "non_existent_tool", "params": {}}' 400 {
    param($response, $statusCode)
    return $response.success -eq $false -and $statusCode -eq 400
}

# 8. Concurrent Requests Test
Test-ConcurrentRequests -ConcurrentCount 5

Write-Host "`n📊 COMPREHENSIVE VALIDATION SUMMARY"
Write-Host "===================================="
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

Write-Host "`n🚀 Fixed Comprehensive Validation Complete!"
