# PowerShell Concurrent Testing Script for MCP Server
# Usage: .\concurrent_test.ps1

Write-Host "🚀 Starting Concurrent MCP Server Testing" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

$serverURL = "http://localhost:3011"
$testPayload = @{
    tool = "search_vault"
    params = @{
        query = "test"
        limit = 5
    }
} | ConvertTo-Json

Write-Host "📊 Testing 10 concurrent requests..." -ForegroundColor Yellow

# Test 1: Sequential requests (baseline)
Write-Host "`n1️⃣ Sequential Requests (Baseline):" -ForegroundColor Cyan
$sequentialTimes = @()
for ($i = 1; $i -le 5; $i++) {
    $startTime = Get-Date
    try {
        $response = Invoke-RestMethod -Uri "$serverURL/tools/execute" -Method POST -Body $testPayload -ContentType "application/json"
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMilliseconds
        $sequentialTimes += $duration
        Write-Host "  Request $i`: $([math]::Round($duration, 2))ms" -ForegroundColor White
    } catch {
        Write-Host "  Request $i`: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    }
}

$avgSequential = ($sequentialTimes | Measure-Object -Average).Average
Write-Host "  Average Sequential: $([math]::Round($avgSequential, 2))ms" -ForegroundColor Green

# Test 2: Concurrent requests using jobs
Write-Host "`n2️⃣ Concurrent Requests (Jobs):" -ForegroundColor Cyan
$jobs = @()
$startTime = Get-Date

# Start 10 concurrent jobs
for ($i = 1; $i -le 10; $i++) {
    $job = Start-Job -ScriptBlock {
        param($url, $payload)
        try {
            $response = Invoke-RestMethod -Uri "$url/tools/execute" -Method POST -Body $payload -ContentType "application/json"
            return @{ Success = $true; Response = $response }
        } catch {
            return @{ Success = $false; Error = $_.Exception.Message }
        }
    } -ArgumentList $serverURL, $testPayload
    $jobs += $job
}

# Wait for all jobs to complete
$results = $jobs | Wait-Job | Receive-Job
$jobs | Remove-Job

$endTime = Get-Date
$totalDuration = ($endTime - $startTime).TotalMilliseconds
$successCount = ($results | Where-Object { $_.Success }).Count

Write-Host "  Total Duration: $([math]::Round($totalDuration, 2))ms" -ForegroundColor White
Write-Host "  Success Rate: $successCount/10 ($([math]::Round(($successCount/10)*100, 1))%)" -ForegroundColor White
Write-Host "  Average per Request: $([math]::Round($totalDuration/10, 2))ms" -ForegroundColor Green

# Test 3: Load testing with multiple iterations
Write-Host "`n3️⃣ Load Testing (50 requests):" -ForegroundColor Cyan
$loadTestJobs = @()
$loadStartTime = Get-Date

for ($i = 1; $i -le 50; $i++) {
    $job = Start-Job -ScriptBlock {
        param($url, $payload)
        try {
            $response = Invoke-RestMethod -Uri "$url/tools/execute" -Method POST -Body $payload -ContentType "application/json"
            return @{ Success = $true; Duration = (Get-Date) }
        } catch {
            return @{ Success = $false; Error = $_.Exception.Message }
        }
    } -ArgumentList $serverURL, $testPayload
    $loadTestJobs += $job
}

$loadResults = $loadTestJobs | Wait-Job | Receive-Job
$loadTestJobs | Remove-Job

$loadEndTime = Get-Date
$loadTotalDuration = ($loadEndTime - $loadStartTime).TotalMilliseconds
$loadSuccessCount = ($loadResults | Where-Object { $_.Success }).Count

Write-Host "  Total Duration: $([math]::Round($loadTotalDuration, 2))ms" -ForegroundColor White
Write-Host "  Success Rate: $loadSuccessCount/50 ($([math]::Round(($loadSuccessCount/50)*100, 1))%)" -ForegroundColor White
Write-Host "  Throughput: $([math]::Round(50/($loadTotalDuration/1000), 2)) req/s" -ForegroundColor Green

# Test 4: Different tools concurrently
Write-Host "`n4️⃣ Mixed Tool Testing:" -ForegroundColor Cyan
$mixedJobs = @()

# List files
$listJob = Start-Job -ScriptBlock {
    param($url)
    try {
        $payload = @{ tool = "list_files_in_vault"; params = @{} } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$url/tools/execute" -Method POST -Body $payload -ContentType "application/json"
        return @{ Tool = "list_files"; Success = $true; Response = $response }
    } catch {
        return @{ Tool = "list_files"; Success = $false; Error = $_.Exception.Message }
    }
} -ArgumentList $serverURL

# Search vault
$searchJob = Start-Job -ScriptBlock {
    param($url)
    try {
        $payload = @{ tool = "search_vault"; params = @{ query = "test"; limit = 5 } } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$url/tools/execute" -Method POST -Body $payload -ContentType "application/json"
        return @{ Tool = "search_vault"; Success = $true; Response = $response }
    } catch {
        return @{ Tool = "search_vault"; Success = $false; Error = $_.Exception.Message }
    }
} -ArgumentList $serverURL

# Read note
$readJob = Start-Job -ScriptBlock {
    param($url)
    try {
        $payload = @{ tool = "read_note"; params = @{ filename = "test.md" } } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$url/tools/execute" -Method POST -Body $payload -ContentType "application/json"
        return @{ Tool = "read_note"; Success = $true; Response = $response }
    } catch {
        return @{ Tool = "read_note"; Success = $false; Error = $_.Exception.Message }
    }
} -ArgumentList $serverURL

$mixedJobs = @($listJob, $searchJob, $readJob)
$mixedResults = $mixedJobs | Wait-Job | Receive-Job
$mixedJobs | Remove-Job

foreach ($result in $mixedResults) {
    if ($result.Success) {
        Write-Host "  ✅ $($result.Tool): SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($result.Tool): FAILED - $($result.Error)" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Concurrent Testing Complete!" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  - Sequential Average: $([math]::Round($avgSequential, 2))ms" -ForegroundColor White
Write-Host "  - Concurrent (10): $([math]::Round($totalDuration/10, 2))ms per request" -ForegroundColor White
Write-Host "  - Load Test (50): $([math]::Round($loadTotalDuration/50, 2))ms per request" -ForegroundColor White
Write-Host "  - Throughput: $([math]::Round(50/($loadTotalDuration/1000), 2)) req/s" -ForegroundColor White
