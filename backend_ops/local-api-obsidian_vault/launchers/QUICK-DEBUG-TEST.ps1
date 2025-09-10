# 🚀 QUICK DEBUG TEST
# Fast service testing with auto-inference

Write-Host "🚀 QUICK DEBUG TEST" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""

$services = @(
    @{ Name = "Flyde Studio"; Url = "http://localhost:3001/health" }
    @{ Name = "Motia Workbench"; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian API"; Url = "http://localhost:27123/health" }
    @{ Name = "Vault API"; Url = "http://localhost:8080/health" }
)

$running = 0
$total = $services.Count

Write-Host "🔍 Testing services with auto-inference..." -ForegroundColor Yellow

foreach ($service in $services) {
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Status: HEALTHY" -ForegroundColor Green
            Write-Host "  📊 Response: $($response.Content)" -ForegroundColor Green
            $running++
        } else {
            Write-Host "  ❌ Status: ERROR $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ Status: NOT RESPONDING" -ForegroundColor Red
        Write-Host "  🔍 Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Auto-inference for common errors
        if ($_.Exception.Message -like "*timeout*") {
            Write-Host "  💡 Inference: Service may be starting up" -ForegroundColor Yellow
        } elseif ($_.Exception.Message -like "*connection refused*") {
            Write-Host "  💡 Inference: Service not running on port" -ForegroundColor Yellow
        } elseif ($_.Exception.Message -like "*404*") {
            Write-Host "  💡 Inference: Service running but health endpoint missing" -ForegroundColor Yellow
        }
    }
}

# Results with auto-inference
Write-Host ""
Write-Host "📊 RESULTS WITH AUTO-INFERENCE" -ForegroundColor Magenta
Write-Host "===============================" -ForegroundColor Magenta

$successRate = [Math]::Round(($running / $total) * 100, 1)

Write-Host "🎯 Overall Status:" -ForegroundColor White
Write-Host "  Running: $running/$total" -ForegroundColor White
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})

# Auto-inference recommendations
Write-Host ""
Write-Host "🧠 AUTO-INFERENCE RECOMMENDATIONS:" -ForegroundColor White

if ($successRate -eq 100) {
    Write-Host "  🎉 All services healthy - system ready!" -ForegroundColor Green
    Write-Host "  🚀 Plugins can work properly!" -ForegroundColor Green
} elseif ($successRate -ge 50) {
    Write-Host "  ⚠️ Partial system - some plugins can work" -ForegroundColor Yellow
    Write-Host "  🔧 Fix remaining services for full functionality" -ForegroundColor Yellow
} else {
    Write-Host "  ❌ System not ready - fix services first" -ForegroundColor Red
    Write-Host "  🔧 Run .\QUICK-FIX-ALL.ps1 to restart services" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔗 Test URLs:" -ForegroundColor White
Write-Host "  🎨 Flyde: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault: http://localhost:8080" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 QUICK DEBUG TEST COMPLETE!" -ForegroundColor Green
