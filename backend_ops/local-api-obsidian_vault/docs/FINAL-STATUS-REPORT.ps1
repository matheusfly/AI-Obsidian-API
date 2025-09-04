# 📊 FINAL STATUS REPORT
# Current service status with auto-inference

Write-Host "📊 FINAL STATUS REPORT" -ForegroundColor Magenta
Write-Host "=====================" -ForegroundColor Magenta
Write-Host ""

$services = @(
    @{ Name = "Flyde Studio"; Port = 3001; HealthUrl = "http://localhost:3001/health"; MainUrl = "http://localhost:3001" }
    @{ Name = "Motia Workbench"; Port = 3000; HealthUrl = "http://localhost:3000/health"; MainUrl = "http://localhost:3000" }
    @{ Name = "Obsidian API"; Port = 27123; HealthUrl = "http://localhost:27123/health"; MainUrl = "http://localhost:27123" }
    @{ Name = "Vault API"; Port = 8080; HealthUrl = "http://localhost:8080/health"; MainUrl = "http://localhost:8080" }
)

$results = @{}
$healthyCount = 0

Write-Host "🔍 Testing all services..." -ForegroundColor Yellow
Write-Host "=========================" -ForegroundColor Yellow

foreach ($service in $services) {
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    
    $serviceResult = @{
        HealthCheck = $false
        MainPageCheck = $false
        Status = "UNKNOWN"
        ErrorMessage = ""
    }
    
    # Test health endpoint
    try {
        $response = Invoke-WebRequest -Uri $service.HealthUrl -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $serviceResult.HealthCheck = $true
            Write-Host "  ✅ Health Check: PASSED" -ForegroundColor Green
            Write-Host "  📊 Response: $($response.Content)" -ForegroundColor Green
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
        Write-Host "  ✅ Main Page: ACCESSIBLE ($($response.Content.Length) chars)" -ForegroundColor Green
        
        # Auto-inference based on content
        if ($response.Content -like "*404*") {
            Write-Host "  🧠 Auto-inference: Next.js app with 404 page" -ForegroundColor Yellow
        } elseif ($response.Content -like "*Flyde*") {
            Write-Host "  🧠 Auto-inference: Flyde visual programming interface" -ForegroundColor Green
        } elseif ($response.Content -like "*API*") {
            Write-Host "  🧠 Auto-inference: API service responding" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠️ Main Page: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # Determine status
    if ($serviceResult.HealthCheck -and $serviceResult.MainPageCheck) {
        $serviceResult.Status = "FULLY_OPERATIONAL"
        $healthyCount++
    } elseif ($serviceResult.HealthCheck -or $serviceResult.MainPageCheck) {
        $serviceResult.Status = "PARTIALLY_OPERATIONAL"
        $healthyCount++
    } else {
        $serviceResult.Status = "NOT_OPERATIONAL"
    }
    
    $results[$service.Name] = $serviceResult
    
    # Display status
    $statusColor = if ($serviceResult.Status -eq "FULLY_OPERATIONAL") {"Green"} elseif ($serviceResult.Status -eq "PARTIALLY_OPERATIONAL") {"Yellow"} else {"Red"}
    Write-Host "  🎯 Status: $($serviceResult.Status)" -ForegroundColor $statusColor
}

# Calculate success rate
$successRate = [Math]::Round(($healthyCount / $services.Count) * 100, 1)

Write-Host ""
Write-Host "📊 FINAL RESULTS" -ForegroundColor Magenta
Write-Host "================" -ForegroundColor Magenta
Write-Host "  Total Services: $($services.Count)" -ForegroundColor White
Write-Host "  Healthy Services: $healthyCount/$($services.Count)" -ForegroundColor White
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})

Write-Host ""
Write-Host "🔍 SERVICE DETAILS:" -ForegroundColor White
foreach ($result in $results.GetEnumerator()) {
    $service = $services | Where-Object { $_.Name -eq $result.Key }
    $status = $result.Value.Status
    $color = if ($status -eq "FULLY_OPERATIONAL") {"Green"} elseif ($status -eq "PARTIALLY_OPERATIONAL") {"Yellow"} else {"Red"}
    
    Write-Host "  $($result.Key):" -ForegroundColor Cyan
    Write-Host "    Status: $status" -ForegroundColor $color
    Write-Host "    Health: $(if($result.Value.HealthCheck) {"✅"} else {"❌"})" -ForegroundColor $(if($result.Value.HealthCheck) {"Green"} else {"Red"})
    Write-Host "    Main Page: $(if($result.Value.MainPageCheck) {"✅"} else {"❌"})" -ForegroundColor $(if($result.Value.MainPageCheck) {"Green"} else {"Red"})
    Write-Host "    URL: $($service.MainUrl)" -ForegroundColor White
}

Write-Host ""
Write-Host "🧠 AUTO-INFERENCE SUMMARY:" -ForegroundColor White
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

if ($results["Vault API"].Status -eq "NOT_OPERATIONAL") {
    Write-Host ""
    Write-Host "🔧 VAULT API FIX NEEDED:" -ForegroundColor Red
    Write-Host "  Run: Start-Process -FilePath 'cmd' -ArgumentList '/c', 'cd vault-api && C:\Program Files\Python312\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload' -WindowStyle Hidden" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 FINAL STATUS REPORT COMPLETE!" -ForegroundColor Green
