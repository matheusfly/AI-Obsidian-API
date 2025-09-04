# 🧪 TEST ALL NOW - Final Comprehensive Test
# Test all services and provide final status

Write-Host "🧪 TEST ALL NOW" -ForegroundColor Magenta
Write-Host "===============" -ForegroundColor Magenta
Write-Host ""

$services = @(
    @{ Name = "Flyde Studio"; Port = 3001; Url = "http://localhost:3001/health" }
    @{ Name = "Motia Workbench"; Port = 3000; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian API"; Port = 27123; Url = "http://localhost:27123/health" }
    @{ Name = "Vault API"; Port = 8080; Url = "http://localhost:8080/health" }
)

$running = 0
$total = $services.Count

Write-Host "🔍 Testing all services..." -ForegroundColor Yellow
Write-Host "=========================" -ForegroundColor Yellow

foreach ($service in $services) {
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    Write-Host "  Port: $($service.Port)" -ForegroundColor White
    
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Status: HEALTHY" -ForegroundColor Green
            Write-Host "  📊 Response: $($response.StatusCode)" -ForegroundColor Green
            $running++
        } else {
            Write-Host "  ❌ Status: ERROR $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ Status: NOT RESPONDING" -ForegroundColor Red
        Write-Host "  🔍 Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Final results
Write-Host ""
Write-Host "📊 FINAL RESULTS" -ForegroundColor Magenta
Write-Host "===============" -ForegroundColor Magenta
Write-Host ""

$successRate = [Math]::Round(($running / $total) * 100, 1)

Write-Host "🎯 Overall Status:" -ForegroundColor White
Write-Host "  Total Services: $total" -ForegroundColor White
Write-Host "  Running: $running/$total" -ForegroundColor White
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})

Write-Host ""
Write-Host "🔗 Quick Access Links:" -ForegroundColor White
Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault API: http://localhost:8080" -ForegroundColor Cyan

if ($running -eq $total) {
    Write-Host ""
    Write-Host "🎉 ALL SERVERS RUNNING!" -ForegroundColor Green
    Write-Host "======================" -ForegroundColor Green
    Write-Host "🚀 Plugins can now work properly!" -ForegroundColor Green
    Write-Host "🎨 Start building visual workflows!" -ForegroundColor Green
} elseif ($running -ge 2) {
    Write-Host ""
    Write-Host "⚠️ PARTIAL SUCCESS!" -ForegroundColor Yellow
    Write-Host "==================" -ForegroundColor Yellow
    Write-Host "🚀 Some plugins can work!" -ForegroundColor Yellow
    Write-Host "🔧 Fix remaining services for full functionality!" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ SERVERS NOT RUNNING!" -ForegroundColor Red
    Write-Host "=======================" -ForegroundColor Red
    Write-Host "🔧 Plugins cannot work!" -ForegroundColor Red
    Write-Host "🔄 Run .\QUICK-FIX-ALL.ps1 to fix!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Open working services in browser" -ForegroundColor Cyan
Write-Host "  2. Test plugin functionality" -ForegroundColor Cyan
Write-Host "  3. Fix remaining services if needed" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 TEST ALL NOW COMPLETE!" -ForegroundColor Green
