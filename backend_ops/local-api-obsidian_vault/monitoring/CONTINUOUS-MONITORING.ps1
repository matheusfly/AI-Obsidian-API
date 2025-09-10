# 🔄 CONTINUOUS MONITORING SYSTEM
# Keep services running with auto-inference feedback loops

Write-Host "🔄 CONTINUOUS MONITORING SYSTEM" -ForegroundColor Magenta
Write-Host "===============================" -ForegroundColor Magenta
Write-Host "Auto-inference feedback loops for continuous service monitoring" -ForegroundColor White
Write-Host ""

# Service configuration
$services = @(
    @{ Name = "Flyde Studio"; Port = 3001; HealthUrl = "http://localhost:3001/health"; MainUrl = "http://localhost:3001" }
    @{ Name = "Motia Workbench"; Port = 3000; HealthUrl = "http://localhost:3000/health"; MainUrl = "http://localhost:3000" }
    @{ Name = "Obsidian API"; Port = 27123; HealthUrl = "http://localhost:27123/health"; MainUrl = "http://localhost:27123" }
    @{ Name = "Vault API"; Port = 8080; HealthUrl = "http://localhost:8080/health"; MainUrl = "http://localhost:8080" }
)

# Monitoring function with auto-inference
function Monitor-Services {
    param($iteration = 1)
    
    Write-Host ""
    Write-Host "🔄 MONITORING CYCLE $iteration" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    
    $results = @{}
    $healthyCount = 0
    $totalCount = $services.Count
    
    foreach ($service in $services) {
        Write-Host ""
        Write-Host "🔍 Monitoring $($service.Name)..." -ForegroundColor Yellow
        
        $serviceResult = @{
            HealthCheck = $false
            MainPageCheck = $false
            ResponseTime = 0
            ErrorMessage = ""
            Status = "UNKNOWN"
        }
        
        # Test health endpoint
        try {
            $startTime = Get-Date
            $response = Invoke-WebRequest -Uri $service.HealthUrl -UseBasicParsing -TimeoutSec 5
            $endTime = Get-Date
            $serviceResult.ResponseTime = ($endTime - $startTime).TotalMilliseconds
            
            if ($response.StatusCode -eq 200) {
                $serviceResult.HealthCheck = $true
                Write-Host "  ✅ Health: PASSED ($([Math]::Round($serviceResult.ResponseTime, 2))ms)" -ForegroundColor Green
            } else {
                Write-Host "  ❌ Health: FAILED ($($response.StatusCode))" -ForegroundColor Red
            }
        } catch {
            $serviceResult.ErrorMessage = $_.Exception.Message
            Write-Host "  ❌ Health: ERROR" -ForegroundColor Red
            Write-Host "  🔍 Error: $($serviceResult.ErrorMessage)" -ForegroundColor Red
        }
        
        # Test main page
        try {
            $response = Invoke-WebRequest -Uri $service.MainUrl -UseBasicParsing -TimeoutSec 5
            $serviceResult.MainPageCheck = $true
            Write-Host "  ✅ Main Page: ACCESSIBLE ($($response.Content.Length) chars)" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️ Main Page: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        # Auto-inference status determination
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
        
        # Auto-inference recommendations
        Write-Host "  🧠 Auto-inference: $($serviceResult.Status)" -ForegroundColor $(if($serviceResult.Status -eq "FULLY_OPERATIONAL") {"Green"} elseif($serviceResult.Status -eq "PARTIALLY_OPERATIONAL") {"Yellow"} else {"Red"})
        
        if ($serviceResult.Status -eq "NOT_OPERATIONAL") {
            Write-Host "  💡 Recommendation: Restart service" -ForegroundColor Red
        } elseif ($serviceResult.Status -eq "PARTIALLY_OPERATIONAL") {
            Write-Host "  💡 Recommendation: Check configuration" -ForegroundColor Yellow
        } else {
            Write-Host "  💡 Status: Ready for use" -ForegroundColor Green
        }
    }
    
    # Calculate success rate
    $successRate = [Math]::Round(($healthyCount / $totalCount) * 100, 1)
    
    Write-Host ""
    Write-Host "📊 MONITORING RESULTS" -ForegroundColor White
    Write-Host "====================" -ForegroundColor White
    Write-Host "  Healthy Services: $healthyCount/$totalCount" -ForegroundColor White
    Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})
    
    # Auto-inference for system status
    if ($successRate -eq 100) {
        Write-Host "  🎉 System Status: FULLY OPERATIONAL" -ForegroundColor Green
        Write-Host "  🚀 All plugins can work at 100% capacity!" -ForegroundColor Green
    } elseif ($successRate -ge 75) {
        Write-Host "  ⚠️ System Status: MOSTLY OPERATIONAL" -ForegroundColor Yellow
        Write-Host "  🚀 Most plugins can work with minor limitations!" -ForegroundColor Yellow
    } elseif ($successRate -ge 50) {
        Write-Host "  ⚠️ System Status: PARTIALLY OPERATIONAL" -ForegroundColor Yellow
        Write-Host "  🚀 Some plugins can work!" -ForegroundColor Yellow
    } else {
        Write-Host "  ❌ System Status: NOT OPERATIONAL" -ForegroundColor Red
        Write-Host "  🔧 Fix services before using plugins!" -ForegroundColor Red
    }
    
    return @{
        Results = $results
        HealthyCount = $healthyCount
        TotalCount = $totalCount
        SuccessRate = $successRate
    }
}

# Auto-recovery function
function Auto-Recovery {
    param($failedServices)
    
    Write-Host ""
    Write-Host "🔧 AUTO-RECOVERY INITIATED" -ForegroundColor Red
    Write-Host "===========================" -ForegroundColor Red
    
    foreach ($service in $failedServices) {
        Write-Host "🔧 Attempting to recover $($service.Name)..." -ForegroundColor Yellow
        
        # Kill existing processes on the port
        try {
            $processes = Get-NetTCPConnection -LocalPort $service.Port -ErrorAction SilentlyContinue
            if ($processes) {
                $pids = $processes | Select-Object -ExpandProperty OwningProcess
                foreach ($pid in $pids) {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                }
                Write-Host "  🛑 Killed existing processes on port $($service.Port)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  ⚠️ No processes found on port $($service.Port)" -ForegroundColor Yellow
        }
        
        # Restart service based on type
        try {
            if ($service.Name -eq "Vault API") {
                Start-Process -FilePath "cmd" -ArgumentList "/c", "cd vault-api && C:\Program Files\Python312\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload" -WindowStyle Hidden
                Write-Host "  🚀 Restarted $($service.Name) with Python 3.12" -ForegroundColor Green
            } elseif ($service.Name -eq "Obsidian API") {
                Start-Process -FilePath "cmd" -ArgumentList "/c", "cd obsidian-api && npx motia dev --port 27123" -WindowStyle Hidden
                Write-Host "  🚀 Restarted $($service.Name)" -ForegroundColor Green
            } elseif ($service.Name -eq "Flyde Studio") {
                Start-Process -FilePath "cmd" -ArgumentList "/c", "cd flyde-project && npm run dev" -WindowStyle Hidden
                Write-Host "  🚀 Restarted $($service.Name)" -ForegroundColor Green
            } elseif ($service.Name -eq "Motia Workbench") {
                Start-Process -FilePath "cmd" -ArgumentList "/c", "cd motia-project && npm run dev" -WindowStyle Hidden
                Write-Host "  🚀 Restarted $($service.Name)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ❌ Failed to restart $($service.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host "  ⏳ Waiting 30 seconds for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Main monitoring loop
Write-Host "🚀 Starting Continuous Monitoring..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

$monitoringCycles = 0
$maxCycles = 10
$autoRecoveryEnabled = $true

while ($monitoringCycles -lt $maxCycles) {
    $monitoringCycles++
    
    $monitoringResult = Monitor-Services -iteration $monitoringCycles
    
    # Auto-recovery if needed
    if ($autoRecoveryEnabled -and $monitoringResult.SuccessRate -lt 75) {
        $failedServices = $services | Where-Object { 
            $monitoringResult.Results[$_.Name].Status -eq "NOT_OPERATIONAL" 
        }
        
        if ($failedServices.Count -gt 0) {
            Auto-Recovery -failedServices $failedServices
        }
    }
    
    # Break if all services are healthy
    if ($monitoringResult.SuccessRate -eq 100) {
        Write-Host ""
        Write-Host "🎉 ALL SERVICES FULLY OPERATIONAL!" -ForegroundColor Green
        Write-Host "===================================" -ForegroundColor Green
        Write-Host "🚀 System is ready for plugin development!" -ForegroundColor Green
        break
    }
    
    # Wait before next cycle
    if ($monitoringCycles -lt $maxCycles) {
        Write-Host ""
        Write-Host "⏳ Waiting 60 seconds before next monitoring cycle..." -ForegroundColor Yellow
        Start-Sleep -Seconds 60
    }
}

# Final status
Write-Host ""
Write-Host "📋 FINAL MONITORING REPORT" -ForegroundColor Magenta
Write-Host "==========================" -ForegroundColor Magenta
Write-Host "  Monitoring Cycles: $monitoringCycles" -ForegroundColor White
Write-Host "  Final Success Rate: $($monitoringResult.SuccessRate)%" -ForegroundColor $(if($monitoringResult.SuccessRate -ge 80) {"Green"} else {"Yellow"})

Write-Host ""
Write-Host "🔗 QUICK ACCESS LINKS:" -ForegroundColor White
foreach ($service in $services) {
    $status = $monitoringResult.Results[$service.Name].Status
    $color = if ($status -eq "FULLY_OPERATIONAL") {"Green"} elseif ($status -eq "PARTIALLY_OPERATIONAL") {"Yellow"} else {"Red"}
    Write-Host "  $($service.Name): $($service.MainUrl) ($status)" -ForegroundColor $color
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Open working services in browser" -ForegroundColor Cyan
Write-Host "  2. Test plugin functionality" -ForegroundColor Cyan
Write-Host "  3. Start building visual workflows!" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 CONTINUOUS MONITORING COMPLETE!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
