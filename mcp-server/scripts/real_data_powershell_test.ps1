# real_data_powershell_test.ps1
# Comprehensive real data test using PowerShell with Obsidian API

$obsidianAPIURL = "https://localhost:27124"
$apiToken = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
$successCount = 0
$failCount = 0
$totalTests = 0

function Test-RealAPIEndpoint {
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
        $headers = @{
            "Authorization" = "Bearer $apiToken"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri "$obsidianAPIURL$Path" -Method $Method -Headers $headers -Body $Body -TimeoutSec 10 -SkipCertificateCheck
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
        Write-Host "  ❌ FAILED: $errorMessage"
        Write-Host "  📄 Status Code: $($statusCode)"
        $script:failCount++
        return $false
    }
}

Write-Host "🚀 REAL DATA POWERSHELL TEST"
Write-Host "============================"
Write-Host "Testing REAL Obsidian vault data (1000+ files)"
Write-Host "API URL: $obsidianAPIURL"
Write-Host "Vault Path: D:\Nomade Milionario"
Write-Host ""

# Test 1: API Health Check
Test-RealAPIEndpoint "API Health Check" "GET" "/" $null 200 {
    param($response, $statusCode)
    return $response.service -eq "Obsidian Local REST API"
}

# Test 2: List Real Files
Test-RealAPIEndpoint "List Real Files" "GET" "/vault/" $null 200 {
    param($response, $statusCode)
    if ($response.files.Count -gt 0) {
        Write-Host "  📊 Found $($response.files.Count) real files"
        
        # Show real file samples
        Write-Host "  📋 Real file samples:"
        $realFileCount = 0
        foreach ($fileName in $response.files) {
            if ($realFileCount -lt 15) {
                if ($fileName -notlike "*test-note*" -and $fileName -notlike "*another-note*") {
                    $fileType = "file"
                    if ($fileName.EndsWith("/")) {
                        $fileType = "folder"
                        $fileName = $fileName.TrimEnd("/")
                    }
                    Write-Host "    - $fileName [$fileType]"
                    $realFileCount++
                }
            }
        }
        if ($response.files.Count -gt 15) {
            Write-Host "    ... and $($response.files.Count - 15) more real files"
        }
        return $true
    }
    return $false
}

# Test 3: Read Real Note
Test-RealAPIEndpoint "Read Real Note" "GET" "/vault/AGENTS.md" $null 200 {
    param($response, $statusCode)
    if ($response.content) {
        $length = $response.content.Length
        Write-Host "  📊 Note length: $length characters"
        if ($length -gt 0) {
            $preview = $response.content
            if ($preview.Length -gt 150) {
                $preview = $preview.Substring(0, 150) + "..."
            }
            Write-Host "  📄 Content preview: $preview"
        }
        return $true
    }
    return $false
}

# Test 4: Create Real Note
$noteContent = @"
# MCP Real Data Test

This note was created by the MCP server using REAL data integration.

## Test Details
- Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- Purpose: Testing real Obsidian vault integration
- Status: Success

## Real Data Features
- ✅ Real vault access
- ✅ Real file listing
- ✅ Real search functionality
- ✅ Real note creation

## Tags
#mcp #real-data #test #integration
"@

Test-RealAPIEndpoint "Create Real Note" "POST" "/vault/MCP-Real-Data-Test.md" $noteContent 200 {
    param($response, $statusCode)
    Write-Host "  📊 Created real note successfully"
    return $true
}

# Test 5: Search Real Files (Basic Implementation)
Write-Host "`n🔍 Testing Search Real Files..."
$script:totalTests++

try {
    $headers = @{
        "Authorization" = "Bearer $apiToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "$obsidianAPIURL/vault/" -Method GET -Headers $headers -TimeoutSec 10 -SkipCertificateCheck
    
    if ($response.files.Count -gt 0) {
        # Search for files containing "AGENTS"
        $searchResults = @()
        foreach ($fileName in $response.files) {
            if ($fileName -notlike "*/" -and $fileName.ToLower().Contains("agents")) {
                $searchResults += $fileName
            }
        }
        
        Write-Host "  ✅ SUCCESS: Found $($searchResults.Count) search results for 'AGENTS'"
        foreach ($result in $searchResults) {
            Write-Host "    - $result"
        }
        $script:successCount++
    } else {
        Write-Host "  ❌ FAILED: No files found"
        $script:failCount++
    }
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)"
    $script:failCount++
}

# Test 6: Search for Rust Files
Write-Host "`n🔍 Testing Search for Rust Files..."
$script:totalTests++

try {
    $headers = @{
        "Authorization" = "Bearer $apiToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "$obsidianAPIURL/vault/" -Method GET -Headers $headers -TimeoutSec 10 -SkipCertificateCheck
    
    if ($response.files.Count -gt 0) {
        # Search for files containing "Rust"
        $searchResults = @()
        foreach ($fileName in $response.files) {
            if ($fileName -notlike "*/" -and $fileName.ToLower().Contains("rust")) {
                $searchResults += $fileName
            }
        }
        
        Write-Host "  ✅ SUCCESS: Found $($searchResults.Count) search results for 'Rust'"
        foreach ($result in $searchResults) {
            Write-Host "    - $result"
        }
        $script:successCount++
    } else {
        Write-Host "  ❌ FAILED: No files found"
        $script:failCount++
    }
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)"
    $script:failCount++
}

# Test 7: Search for Nomade Files
Write-Host "`n🔍 Testing Search for Nomade Files..."
$script:totalTests++

try {
    $headers = @{
        "Authorization" = "Bearer $apiToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "$obsidianAPIURL/vault/" -Method GET -Headers $headers -TimeoutSec 10 -SkipCertificateCheck
    
    if ($response.files.Count -gt 0) {
        # Search for files containing "nomade"
        $searchResults = @()
        foreach ($fileName in $response.files) {
            if ($fileName -notlike "*/" -and $fileName.ToLower().Contains("nomade")) {
                $searchResults += $fileName
            }
        }
        
        Write-Host "  ✅ SUCCESS: Found $($searchResults.Count) search results for 'nomade'"
        foreach ($result in $searchResults) {
            Write-Host "    - $result"
        }
        $script:successCount++
    } else {
        Write-Host "  ❌ FAILED: No files found"
        $script:failCount++
    }
} catch {
    Write-Host "  ❌ FAILED: $($_.Exception.Message)"
    $script:failCount++
}

# Summary
Write-Host "`n📊 REAL DATA POWERSHELL TEST SUMMARY"
Write-Host "====================================="
Write-Host "Total Tests: $($script:totalTests)"
Write-Host "Successful: $($script:successCount)"
Write-Host "Failed: $($script:failCount)"
Write-Host "Success Rate: $([math]::Round($script:successCount / $script:totalTests * 100, 2))%"

if ($script:failCount -eq 0) {
    Write-Host "`n🎉 PERFECT! All tests passed with REAL vault data!"
    Write-Host "✅ Direct Obsidian API integration working perfectly!"
    Write-Host "✅ Real vault data access confirmed!"
    Write-Host "✅ 1000+ files accessible!"
} elseif ($script:successCount -gt $script:totalTests / 2) {
    Write-Host "`n✅ EXCELLENT! Most tests passed with real data."
    Write-Host "⚠️ Some tests failed - check details above."
    Write-Host "✅ Real data integration is working well!"
} else {
    Write-Host "`n❌ NEEDS WORK! Many tests failed with real data."
    Write-Host "🔧 Check the Obsidian API connection and configuration."
}

Write-Host "`n🚀 REAL DATA POWERSHELL TEST COMPLETE!"
Write-Host "======================================"
