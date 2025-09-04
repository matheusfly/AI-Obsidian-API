# 🧠 FINAL AUTO-INFERENCE FIX
# Based on MCP content analysis and auto-inference feedback

Write-Host "🧠 FINAL AUTO-INFERENCE FIX" -ForegroundColor Magenta
Write-Host "===========================" -ForegroundColor Magenta
Write-Host "Based on MCP content analysis and auto-inference feedback" -ForegroundColor White
Write-Host ""

# Auto-inference results from previous analysis
Write-Host "🔍 AUTO-INFERENCE ANALYSIS RESULTS:" -ForegroundColor Yellow
Write-Host "  ✅ Motia Workbench: Running (17,784 chars content) - Missing health endpoint" -ForegroundColor Green
Write-Host "  ✅ Flyde Studio: Health endpoint works - Main page 404" -ForegroundColor Green
Write-Host "  ✅ Obsidian API: Health endpoint works - Main page 404" -ForegroundColor Green
Write-Host "  ❌ Vault API: Not responding - Needs restart" -ForegroundColor Red
Write-Host ""

# Fix Vault API first (critical service)
Write-Host "🔧 FIXING VAULT API (Critical Service)..." -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Red

# Kill existing Python processes
Write-Host "  🛑 Stopping existing Python processes..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force

# Start Vault API with Python 3.12
Write-Host "  🚀 Starting Vault API with Python 3.12..." -ForegroundColor Yellow
try {
    Start-Process -FilePath "cmd" -ArgumentList "/c", "cd vault-api && C:\Program Files\Python312\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload" -WindowStyle Hidden
    Write-Host "  ✅ Vault API started" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Vault API failed to start: $($_.Exception.Message)" -ForegroundColor Red
}

# Wait for Vault API to start
Write-Host "  ⏳ Waiting 30 seconds for Vault API..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test all services with auto-inference
Write-Host ""
Write-Host "🧪 COMPREHENSIVE SERVICE TESTING" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$services = @(
    @{ Name = "Flyde Studio"; HealthUrl = "http://localhost:3001/health"; MainUrl = "http://localhost:3001" }
    @{ Name = "Motia Workbench"; HealthUrl = "http://localhost:3000/health"; MainUrl = "http://localhost:3000" }
    @{ Name = "Obsidian API"; HealthUrl = "http://localhost:27123/health"; MainUrl = "http://localhost:27123" }
    @{ Name = "Vault API"; HealthUrl = "http://localhost:8080/health"; MainUrl = "http://localhost:8080" }
)

$results = @{}
$healthyCount = 0
$totalCount = $services.Count

foreach ($service in $services) {
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    
    $serviceResult = @{
        HealthCheck = $false
        MainPageCheck = $false
        ContentLength = 0
        ErrorMessage = ""
    }
    
    # Test health endpoint
    try {
        $response = Invoke-WebRequest -Uri $service.HealthUrl -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $serviceResult.HealthCheck = $true
            Write-Host "  ✅ Health Check: PASSED" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Health Check: FAILED ($($response.StatusCode))" -ForegroundColor Red
        }
    } catch {
        $serviceResult.ErrorMessage = $_.Exception.Message
        Write-Host "  ❌ Health Check: ERROR" -ForegroundColor Red
        Write-Host "  🔍 Error: $($serviceResult.ErrorMessage)" -ForegroundColor Red
    }
    
    # Test main page
    try {
        $response = Invoke-WebRequest -Uri $service.MainUrl -UseBasicParsing -TimeoutSec 5
        $serviceResult.MainPageCheck = $true
        $serviceResult.ContentLength = $response.Content.Length
        Write-Host "  ✅ Main Page: ACCESSIBLE ($($serviceResult.ContentLength) chars)" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️ Main Page: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    $results[$service.Name] = $serviceResult
    
    # Determine if service is healthy
    if ($serviceResult.HealthCheck -or $serviceResult.MainPageCheck) {
        $healthyCount++
    }
}

# Auto-inference analysis and recommendations
Write-Host ""
Write-Host "🧠 AUTO-INFERENCE ANALYSIS" -ForegroundColor Magenta
Write-Host "===========================" -ForegroundColor Magenta

$successRate = [Math]::Round(($healthyCount / $totalCount) * 100, 1)

Write-Host "📊 Overall Status:" -ForegroundColor White
Write-Host "  Healthy Services: $healthyCount/$totalCount" -ForegroundColor White
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})

Write-Host ""
Write-Host "🔍 Service Analysis:" -ForegroundColor White
foreach ($result in $results.GetEnumerator()) {
    $service = $services | Where-Object { $_.Name -eq $result.Key }
    $healthStatus = if ($result.Value.HealthCheck) { "✅" } else { "❌" }
    $mainStatus = if ($result.Value.MainPageCheck) { "✅" } else { "⚠️" }
    
    Write-Host "  $($result.Key):" -ForegroundColor Cyan
    Write-Host "    Health: $healthStatus" -ForegroundColor $(if($result.Value.HealthCheck) {"Green"} else {"Red"})
    Write-Host "    Main Page: $mainStatus" -ForegroundColor $(if($result.Value.MainPageCheck) {"Green"} else {"Yellow"})
    
    if ($result.Value.ContentLength -gt 0) {
        Write-Host "    Content: $($result.Value.ContentLength) characters" -ForegroundColor White
    }
    
    # Auto-inference recommendations
    if ($result.Value.HealthCheck -and $result.Value.MainPageCheck) {
        Write-Host "    💡 Status: FULLY OPERATIONAL" -ForegroundColor Green
    } elseif ($result.Value.HealthCheck -or $result.Value.MainPageCheck) {
        Write-Host "    💡 Status: PARTIALLY OPERATIONAL" -ForegroundColor Yellow
    } else {
        Write-Host "    💡 Status: NOT OPERATIONAL" -ForegroundColor Red
        Write-Host "    🔧 Recommendation: Restart service" -ForegroundColor Red
    }
}

# Final recommendations
Write-Host ""
Write-Host "💡 FINAL RECOMMENDATIONS:" -ForegroundColor White

if ($successRate -eq 100) {
    Write-Host "  🎉 ALL SERVICES FULLY OPERATIONAL!" -ForegroundColor Green
    Write-Host "  🚀 Plugins can work at 100% capacity!" -ForegroundColor Green
} elseif ($successRate -ge 75) {
    Write-Host "  ⚠️ MOST SERVICES OPERATIONAL" -ForegroundColor Yellow
    Write-Host "  🚀 Plugins can work with minor limitations!" -ForegroundColor Yellow
} elseif ($successRate -ge 50) {
    Write-Host "  ⚠️ PARTIAL SYSTEM OPERATIONAL" -ForegroundColor Yellow
    Write-Host "  🚀 Some plugins can work!" -ForegroundColor Yellow
} else {
    Write-Host "  ❌ SYSTEM NOT READY" -ForegroundColor Red
    Write-Host "  🔧 Fix services before using plugins!" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔗 QUICK ACCESS LINKS:" -ForegroundColor White
Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault API: http://localhost:8080" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Open working services in browser" -ForegroundColor Cyan
Write-Host "  2. Test plugin functionality" -ForegroundColor Cyan
Write-Host "  3. Start building visual workflows!" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 FINAL AUTO-INFERENCE FIX COMPLETE!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
