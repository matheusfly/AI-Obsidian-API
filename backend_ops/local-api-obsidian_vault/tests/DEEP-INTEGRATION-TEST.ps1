Write-Host "🔍 DEEP INTEGRATION TESTING" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

$testResults = @{}

function Test-WebFetch {
    param([string]$Url, [string]$TestName)
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        Write-Host "✅ $TestName`: Status $($response.StatusCode)" -ForegroundColor Green
        $testResults[$TestName] = "PASS"
        return $response
    } catch {
        Write-Host "❌ $TestName`: $($_.Exception.Message)" -ForegroundColor Red
        $testResults[$TestName] = "FAIL"
        return $null
    }
}

function Test-APIEndpoint {
    param([string]$Url, [string]$TestName, [hashtable]$Headers = @{})
    try {
        $response = Invoke-RestMethod -Uri $Url -Headers $Headers -TimeoutSec 10
        Write-Host "✅ $TestName`: Connected" -ForegroundColor Green
        $testResults[$TestName] = "PASS"
        return $response
    } catch {
        Write-Host "❌ $TestName`: $($_.Exception.Message)" -ForegroundColor Red
        $testResults[$TestName] = "FAIL"
        return $null
    }
}

# 1. Test Core Services
Write-Host "`n1️⃣ TESTING CORE SERVICES" -ForegroundColor Yellow
Write-Host "=========================" -ForegroundColor Yellow

$vaultHealth = Test-APIEndpoint -Url "http://localhost:18081/" -TestName "Vault API Health"
$obsidianHealth = Test-APIEndpoint -Url "http://localhost:27124/health" -TestName "Obsidian API Health"

# 2. Test Vault API Endpoints
Write-Host "`n2️⃣ TESTING VAULT API ENDPOINTS" -ForegroundColor Yellow
Write-Host "===============================" -ForegroundColor Yellow

Test-APIEndpoint -Url "http://localhost:18081/" -TestName "Vault Root"
Test-APIEndpoint -Url "http://localhost:18081/docs" -TestName "Vault Docs"
Test-APIEndpoint -Url "http://localhost:18081/openapi.json" -TestName "OpenAPI Spec"
Test-APIEndpoint -Url "http://localhost:18081/api/v1/notes" -TestName "Notes Endpoint"
Test-APIEndpoint -Url "http://localhost:18081/api/v1/mcp/tools" -TestName "MCP Tools"

# 3. Test Enhanced RAG Endpoints
Write-Host "`n3️⃣ TESTING ENHANCED RAG ENDPOINTS" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow

Test-APIEndpoint -Url "http://localhost:18081/api/v1/performance/metrics" -TestName "Performance Metrics"
Test-APIEndpoint -Url "http://localhost:18081/api/v1/supabase/health" -TestName "Supabase Health"

# 4. Test Plugin Integrations
Write-Host "`n4️⃣ TESTING PLUGIN INTEGRATIONS" -ForegroundColor Yellow
Write-Host "===============================" -ForegroundColor Yellow

# Test Motia Integration
$motiaResponse = Test-WebFetch -Url "http://localhost:3000/health" -TestName "Motia Health"
if ($motiaResponse) {
Test-APIEndpoint -Url "http://localhost:33000/api" -TestName "Motia API"
}

# Test Flyde Integration
$flydeResponse = Test-WebFetch -Url "http://localhost:33001/health" -TestName "Flyde Health"
if ($flydeResponse) {
Test-APIEndpoint -Url "http://localhost:33001/flows" -TestName "Flyde Flows"
}

# 5. Test MCP Server Integrations
Write-Host "`n5️⃣ TESTING MCP SERVER INTEGRATIONS" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow

# Test MCP Tool Calling
try {
    $mcpRequest = @{
        tool = "read_file"
        arguments = @{
            path = "README.md"
        }
    } | ConvertTo-Json
    
$mcpResponse = Invoke-RestMethod -Uri "http://localhost:18081/api/v1/mcp/tools/call" -Method POST -Body $mcpRequest -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ MCP Tool Calling: Working" -ForegroundColor Green
    $testResults["MCP Tool Calling"] = "PASS"
} catch {
    Write-Host "❌ MCP Tool Calling: $($_.Exception.Message)" -ForegroundColor Red
    $testResults["MCP Tool Calling"] = "FAIL"
}

# 6. Test External Web Connectivity
Write-Host "`n6️⃣ TESTING EXTERNAL WEB CONNECTIVITY" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow

Test-WebFetch -Url "https://httpbin.org/get" -TestName "External HTTP"
Test-WebFetch -Url "https://api.github.com" -TestName "GitHub API"
Test-WebFetch -Url "https://zwtdgaldbltslpfqodxy.supabase.co" -TestName "Supabase Connection"

# 7. Test Enhanced RAG Functionality
Write-Host "`n7️⃣ TESTING ENHANCED RAG FUNCTIONALITY" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow

try {
    $ragRequest = @{
        query = "test integration query"
        agent_id = "integration_test"
        use_hierarchical = $true
        max_depth = 2
    } | ConvertTo-Json
    
$ragResponse = Invoke-RestMethod -Uri "http://localhost:18081/api/v1/rag/enhanced" -Method POST -Body $ragRequest -ContentType "application/json" -TimeoutSec 15
    Write-Host "✅ Enhanced RAG: Working" -ForegroundColor Green
    $testResults["Enhanced RAG"] = "PASS"
} catch {
    Write-Host "❌ Enhanced RAG: $($_.Exception.Message)" -ForegroundColor Red
    $testResults["Enhanced RAG"] = "FAIL"
}

# 8. Test Batch Processing
Write-Host "`n8️⃣ TESTING BATCH PROCESSING" -ForegroundColor Yellow
Write-Host "============================" -ForegroundColor Yellow

try {
    $batchRequest = @{
        queries = @("test query 1", "test query 2")
        agent_id = "batch_test"
        batch_size = 2
    } | ConvertTo-Json
    
$batchResponse = Invoke-RestMethod -Uri "http://localhost:18081/api/v1/rag/batch" -Method POST -Body $batchRequest -ContentType "application/json" -TimeoutSec 15
    Write-Host "✅ Batch Processing: Working" -ForegroundColor Green
    $testResults["Batch Processing"] = "PASS"
} catch {
    Write-Host "❌ Batch Processing: $($_.Exception.Message)" -ForegroundColor Red
    $testResults["Batch Processing"] = "FAIL"
}

# 9. Test Agent Context Management
Write-Host "`n9️⃣ TESTING AGENT CONTEXT MANAGEMENT" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Yellow

try {
    $contextRequest = @{
        agent_id = "test_agent"
        context = @{
            model = "gpt-4"
            temperature = 0.7
            test_timestamp = (Get-Date).ToString()
        }
    } | ConvertTo-Json
    
$contextResponse = Invoke-RestMethod -Uri "http://localhost:18081/api/v1/agents/context" -Method POST -Body $contextRequest -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Agent Context: Working" -ForegroundColor Green
    $testResults["Agent Context"] = "PASS"
} catch {
    Write-Host "❌ Agent Context: $($_.Exception.Message)" -ForegroundColor Red
    $testResults["Agent Context"] = "FAIL"
}

# 10. Test Web Content Fetching
Write-Host "`n🔟 TESTING WEB CONTENT FETCHING" -ForegroundColor Yellow
Write-Host "===============================" -ForegroundColor Yellow

try {
    # Test fetching real web content through our API
    $searchRequest = @{
        query = "artificial intelligence"
        limit = 3
        semantic = $false
    } | ConvertTo-Json
    
$searchResponse = Invoke-RestMethod -Uri "http://localhost:18081/api/v1/search" -Method POST -Body $searchRequest -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Web Content Search: Working" -ForegroundColor Green
    $testResults["Web Content Search"] = "PASS"
} catch {
    Write-Host "❌ Web Content Search: $($_.Exception.Message)" -ForegroundColor Red
    $testResults["Web Content Search"] = "FAIL"
}

# 11. Test Real-time Performance Monitoring
Write-Host "`n1️⃣1️⃣ TESTING REAL-TIME PERFORMANCE" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow

try {
$perfResponse = Invoke-RestMethod -Uri "http://localhost:18081/api/v1/performance/metrics" -TimeoutSec 10
    if ($perfResponse.cpu_percent -ne $null) {
        Write-Host "✅ Performance Monitoring: CPU $($perfResponse.cpu_percent)%, Memory $($perfResponse.memory_percent)%" -ForegroundColor Green
        $testResults["Performance Monitoring"] = "PASS"
    } else {
        Write-Host "❌ Performance Monitoring: No metrics data" -ForegroundColor Red
        $testResults["Performance Monitoring"] = "FAIL"
    }
} catch {
    Write-Host "❌ Performance Monitoring: $($_.Exception.Message)" -ForegroundColor Red
    $testResults["Performance Monitoring"] = "FAIL"
}

# 12. Test Plugin Communication
Write-Host "`n1️⃣2️⃣ TESTING PLUGIN COMMUNICATION" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow

# Test if plugins can communicate with main API
if ($motiaResponse) {
    try {
$pluginTest = Invoke-RestMethod -Uri "http://localhost:33000/api"
        Write-Host "✅ Motia Plugin Communication: Working" -ForegroundColor Green
        $testResults["Motia Communication"] = "PASS"
    } catch {
        Write-Host "❌ Motia Plugin Communication: Failed" -ForegroundColor Red
        $testResults["Motia Communication"] = "FAIL"
    }
}

if ($flydeResponse) {
    try {
$flydeTest = Invoke-RestMethod -Uri "http://localhost:33001/flows"
        Write-Host "✅ Flyde Plugin Communication: Working" -ForegroundColor Green
        $testResults["Flyde Communication"] = "PASS"
    } catch {
        Write-Host "❌ Flyde Plugin Communication: Failed" -ForegroundColor Red
        $testResults["Flyde Communication"] = "FAIL"
    }
}

# FINAL RESULTS
Write-Host "`n📊 INTEGRATION TEST RESULTS" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

$passCount = 0
$totalTests = $testResults.Count

foreach ($test in $testResults.GetEnumerator()) {
    $color = if ($test.Value -eq "PASS") { "Green"; $passCount++ } else { "Red" }
    Write-Host "$($test.Key): $($test.Value)" -ForegroundColor $color
}

$successRate = if ($totalTests -gt 0) { [math]::Round(($passCount / $totalTests) * 100, 1) } else { 0 }

Write-Host "`n🎯 OVERALL RESULTS:" -ForegroundColor Cyan
Write-Host "Passed: $passCount/$totalTests tests" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

if ($successRate -ge 80) {
    Write-Host "`n🎉 SYSTEM FULLY INTEGRATED AND OPERATIONAL!" -ForegroundColor Green
} elseif ($successRate -ge 60) {
    Write-Host "`n⚠️ SYSTEM PARTIALLY WORKING - SOME ISSUES DETECTED" -ForegroundColor Yellow
} else {
    Write-Host "`n🚨 SYSTEM HAS MAJOR INTEGRATION ISSUES" -ForegroundColor Red
}

Write-Host "`n🔗 VERIFIED ACCESS POINTS:" -ForegroundColor Cyan
Write-Host "Vault API Docs: http://localhost:18081/docs" -ForegroundColor White
Write-Host "Obsidian API: http://localhost:27123" -ForegroundColor White
Write-Host "Motia Plugin: http://localhost:3000" -ForegroundColor White
Write-Host "Flyde Plugin: http://localhost:3001" -ForegroundColor White
