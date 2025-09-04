# 🎯 FINAL STATUS CHECK - Comprehensive Service Verification
# Check all services and provide final status report

Write-Host "🎯 FINAL STATUS CHECK" -ForegroundColor Magenta
Write-Host "====================" -ForegroundColor Magenta
Write-Host "Comprehensive Service Verification" -ForegroundColor White
Write-Host ""

$services = @(
    @{ Name = "Flyde Studio"; Port = 3001; Url = "http://localhost:3001/health" }
    @{ Name = "Motia Integration"; Port = 3000; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian API"; Port = 27123; Url = "http://localhost:27123/health" }
    @{ Name = "Vault API"; Port = 8080; Url = "http://localhost:8080/health" }
)

$results = @{}
$successCount = 0

foreach ($service in $services) {
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Status: HEALTHY" -ForegroundColor Green
            Write-Host "  📊 Response: $($response.StatusCode)" -ForegroundColor Green
            $results[$service.Name] = $true
            $successCount++
        } else {
            Write-Host "  ⚠️ Status: UNEXPECTED RESPONSE" -ForegroundColor Yellow
            Write-Host "  📊 Response: $($response.StatusCode)" -ForegroundColor Yellow
            $results[$service.Name] = $false
        }
    } catch {
        Write-Host "  ❌ Status: NOT RESPONDING" -ForegroundColor Red
        Write-Host "  🔍 Error: $($_.Exception.Message)" -ForegroundColor Red
        $results[$service.Name] = $false
    }
}

# Calculate success rate
$totalServices = $services.Count
$successRate = [Math]::Round(($successCount / $totalServices) * 100, 1)

# Final status report
Write-Host ""
Write-Host "📊 FINAL STATUS REPORT" -ForegroundColor Magenta
Write-Host "=====================" -ForegroundColor Magenta
Write-Host ""

Write-Host "🎯 Overall Status:" -ForegroundColor White
Write-Host "  Total Services: $totalServices" -ForegroundColor White
Write-Host "  Running: $successCount/$totalServices" -ForegroundColor White
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})

Write-Host ""
Write-Host "🔍 Service Details:" -ForegroundColor White
foreach ($result in $results.GetEnumerator()) {
    $status = if ($result.Value) { "✅ RUNNING" } else { "❌ NOT RUNNING" }
    $color = if ($result.Value) { "Green" } else { "Red" }
    Write-Host "  $($result.Key): $status" -ForegroundColor $color
}

Write-Host ""
Write-Host "🔗 Quick Access Links:" -ForegroundColor White
Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault API: http://localhost:8080" -ForegroundColor Cyan

if ($successRate -ge 80) {
    Write-Host ""
    Write-Host "🎉 SUCCESS! SERVICES ARE RUNNING!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "🚀 All visual development tools are operational!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ SOME SERVICES NEED ATTENTION" -ForegroundColor Yellow
    Write-Host "===============================" -ForegroundColor Yellow
    Write-Host "🔧 Run .\SIMPLE-FIX.ps1 to restart services" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Open Flyde Studio at http://localhost:3001" -ForegroundColor Cyan
Write-Host "  2. Open Motia Workbench at http://localhost:3000" -ForegroundColor Cyan
Write-Host "  3. Start building visual workflows!" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 FINAL STATUS CHECK COMPLETE!" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
