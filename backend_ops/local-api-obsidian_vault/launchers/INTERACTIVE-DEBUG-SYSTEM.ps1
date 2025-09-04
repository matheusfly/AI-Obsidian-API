# 🔄 INTERACTIVE DEBUG SYSTEM
# Auto-inference feedback loops for service debugging

Write-Host "🔄 INTERACTIVE DEBUG SYSTEM" -ForegroundColor Magenta
Write-Host "===========================" -ForegroundColor Magenta
Write-Host "Auto-inference feedback loops for service debugging" -ForegroundColor White
Write-Host ""

# Service configuration
$services = @(
    @{ 
        Name = "Flyde Studio"; 
        Port = 3001; 
        Url = "http://localhost:3001"; 
        HealthUrl = "http://localhost:3001/health";
        Critical = $true;
        ExpectedContent = "Flyde";
        Category = "Visual Development"
    }
    @{ 
        Name = "Motia Workbench"; 
        Port = 3000; 
        Url = "http://localhost:3000"; 
        HealthUrl = "http://localhost:3000/health";
        Critical = $true;
        ExpectedContent = "Motia";
        Category = "Workflow Automation"
    }
    @{ 
        Name = "Obsidian API"; 
        Port = 27123; 
        Url = "http://localhost:27123"; 
        HealthUrl = "http://localhost:27123/health";
        Critical = $true;
        ExpectedContent = "API";
        Category = "Backend Service"
    }
    @{ 
        Name = "Vault API"; 
        Port = 8080; 
        Url = "http://localhost:8080"; 
        HealthUrl = "http://localhost:8080/health";
        Critical = $true;
        ExpectedContent = "vault";
        Category = data/ Management"
    }
)

# Auto-inference feedback loop function
function Test-ServiceWithInference {
    param($service, $iteration = 1)
    
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name) (Iteration $iteration)..." -ForegroundColor Cyan
    Write-Host "  Category: $($service.Category)" -ForegroundColor White
    Write-Host "  Port: $($service.Port)" -ForegroundColor White
    Write-Host "  Critical: $($service.Critical)" -ForegroundColor $(if($service.Critical) {"Red"} else {"Yellow"})
    
    $results = @{
        HealthCheck = $false
        ContentCheck = $false
        ResponseTime = 0
        ErrorMessage = ""
        StatusCode = 0
        Content = ""
    }
    
    # Test health endpoint
    try {
        $startTime = Get-Date
        $response = Invoke-WebRequest -Uri $service.HealthUrl -UseBasicParsing -TimeoutSec 10
        $endTime = Get-Date
        $results.ResponseTime = ($endTime - $startTime).TotalMilliseconds
        $results.StatusCode = $response.StatusCode
        
        if ($response.StatusCode -eq 200) {
            $results.HealthCheck = $true
            $results.Content = $response.Content
            Write-Host "  ✅ Health Check: PASSED" -ForegroundColor Green
            Write-Host "  📊 Response Time: $([Math]::Round($results.ResponseTime, 2))ms" -ForegroundColor Green
            Write-Host "  📄 Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..." -ForegroundColor Green
        } else {
            Write-Host "  ❌ Health Check: FAILED ($($response.StatusCode))" -ForegroundColor Red
        }
    } catch {
        $results.ErrorMessage = $_.Exception.Message
        Write-Host "  ❌ Health Check: ERROR" -ForegroundColor Red
        Write-Host "  🔍 Error: $($results.ErrorMessage)" -ForegroundColor Red
    }
    
    # Test main page content
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 10
        if ($response.Content -like "*$($service.ExpectedContent)*") {
            $results.ContentCheck = $true
            Write-Host "  ✅ Content Check: PASSED" -ForegroundColor Green
            Write-Host "  📄 Content contains: $($service.ExpectedContent)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ Content Check: PARTIAL" -ForegroundColor Yellow
            Write-Host "  📄 Content preview: $($response.Content.Substring(0, [Math]::Min(200, $response.Content.Length)))..." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ Content Check: FAILED" -ForegroundColor Red
        Write-Host "  🔍 Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    return $results
}

# Auto-inference analysis function
function Analyze-ServiceResults {
    param($service, $results, $iteration)
    
    Write-Host ""
    Write-Host "🧠 AUTO-INFERENCE ANALYSIS" -ForegroundColor Magenta
    Write-Host "===========================" -ForegroundColor Magenta
    
    $inferences = @()
    $recommendations = @()
    
    # Analyze health check
    if ($results.HealthCheck) {
        $inferences += "✅ Service is responding to health checks"
        if ($results.ResponseTime -lt 1000) {
            $inferences += "✅ Service response time is excellent (< 1s)"
        } elseif ($results.ResponseTime -lt 3000) {
            $inferences += "⚠️ Service response time is acceptable (< 3s)"
        } else {
            $inferences += "❌ Service response time is slow (> 3s)"
            $recommendations += "🔧 Consider optimizing service performance"
        }
    } else {
        $inferences += "❌ Service is not responding to health checks"
        $recommendations += "🔧 Check if service is actually running"
        $recommendations += "🔧 Verify port $($service.Port) is not blocked"
        $recommendations += "🔧 Check service logs for errors"
    }
    
    # Analyze content check
    if ($results.ContentCheck) {
        $inferences += "✅ Service is serving expected content"
    } else {
        $inferences += "⚠️ Service content may not be as expected"
        $recommendations += "🔧 Verify service is serving correct content"
    }
    
    # Analyze error patterns
    if ($results.ErrorMessage -like "*timeout*") {
        $inferences += "❌ Service is timing out"
        $recommendations += "🔧 Increase timeout or check service performance"
    } elseif ($results.ErrorMessage -like "*connection refused*") {
        $inferences += "❌ Service is not listening on port $($service.Port)"
        $recommendations += "🔧 Start the service or check port configuration"
    } elseif ($results.ErrorMessage -like "*404*") {
        $inferences += "❌ Service is running but health endpoint not found"
        $recommendations += "🔧 Check if health endpoint is implemented"
    }
    
    # Display inferences
    Write-Host "🔍 Inferences:" -ForegroundColor White
    foreach ($inference in $inferences) {
        Write-Host "  $inference" -ForegroundColor $(if($inference.StartsWith("✅")) {"Green"} elseif($inference.StartsWith("⚠️")) {"Yellow"} else {"Red"})
    }
    
    # Display recommendations
    if ($recommendations.Count -gt 0) {
        Write-Host ""
        Write-Host "💡 Recommendations:" -ForegroundColor White
        foreach ($recommendation in $recommendations) {
            Write-Host "  $recommendation" -ForegroundColor Cyan
        }
    }
    
    return @{
        Inferences = $inferences
        Recommendations = $recommendations
        OverallHealth = $results.HealthCheck -and $results.ContentCheck
    }
}

# Main debugging loop with auto-inference
Write-Host "🚀 Starting Interactive Debug Session..." -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow

$allResults = @{}
$maxIterations = 3
$iteration = 1

while ($iteration -le $maxIterations) {
    Write-Host ""
    Write-Host "🔄 ITERATION $iteration/$maxIterations" -ForegroundColor Magenta
    Write-Host "===============================" -ForegroundColor Magenta
    
    $iterationResults = @{}
    $healthyServices = 0
    $totalServices = $services.Count
    
    foreach ($service in $services) {
        $results = Test-ServiceWithInference -service $service -iteration $iteration
        $analysis = Analyze-ServiceResults -service $service -results $results -iteration $iteration
        
        $iterationResults[$service.Name] = @{
            Service = $service
            Results = $results
            Analysis = $analysis
        }
        
        if ($analysis.OverallHealth) {
            $healthyServices++
        }
    }
    
    $allResults["Iteration$iteration"] = $iterationResults
    
    # Calculate success rate
    $successRate = [Math]::Round(($healthyServices / $totalServices) * 100, 1)
    
    Write-Host ""
    Write-Host "📊 ITERATION $iteration SUMMARY" -ForegroundColor White
    Write-Host "===============================" -ForegroundColor White
    Write-Host "  Healthy Services: $healthyServices/$totalServices" -ForegroundColor White
    Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})
    
    # Auto-inference for next iteration
    if ($successRate -eq 100) {
        Write-Host ""
        Write-Host "🎉 ALL SERVICES HEALTHY!" -ForegroundColor Green
        Write-Host "=======================" -ForegroundColor Green
        Write-Host "🚀 System is ready for plugin development!" -ForegroundColor Green
        break
    } elseif ($iteration -lt $maxIterations) {
        Write-Host ""
        Write-Host "🔄 Auto-inference: Continuing to next iteration..." -ForegroundColor Yellow
        Write-Host "  Some services need more time to start" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    } else {
        Write-Host ""
        Write-Host "⚠️ MAX ITERATIONS REACHED" -ForegroundColor Red
        Write-Host "========================" -ForegroundColor Red
        Write-Host "🔧 Some services may need manual intervention" -ForegroundColor Red
    }
    
    $iteration++
}

# Final comprehensive report
Write-Host ""
Write-Host "📋 FINAL COMPREHENSIVE REPORT" -ForegroundColor Magenta
Write-Host "=============================" -ForegroundColor Magenta

$finalHealthy = 0
$finalTotal = $services.Count

foreach ($service in $services) {
    $lastResults = $allResults["Iteration$($allResults.Keys.Count)"][$service.Name]
    $status = if ($lastResults.Analysis.OverallHealth) { "✅ HEALTHY" } else { "❌ UNHEALTHY" }
    $color = if ($lastResults.Analysis.OverallHealth) { "Green" } else { "Red" }
    
    Write-Host ""
    Write-Host "🔍 $($service.Name) ($($service.Category))" -ForegroundColor White
    Write-Host "  Status: $status" -ForegroundColor $color
    Write-Host "  Port: $($service.Port)" -ForegroundColor White
    Write-Host "  URL: $($service.Url)" -ForegroundColor Cyan
    
    if ($lastResults.Analysis.OverallHealth) {
        $finalHealthy++
    } else {
        Write-Host "  Issues:" -ForegroundColor Red
        foreach ($recommendation in $lastResults.Analysis.Recommendations) {
            Write-Host "    $recommendation" -ForegroundColor Red
        }
    }
}

$finalSuccessRate = [Math]::Round(($finalHealthy / $finalTotal) * 100, 1)

Write-Host ""
Write-Host "🎯 FINAL SYSTEM STATUS" -ForegroundColor White
Write-Host "=====================" -ForegroundColor White
Write-Host "  Total Services: $finalTotal" -ForegroundColor White
Write-Host "  Healthy Services: $finalHealthy/$finalTotal" -ForegroundColor White
Write-Host "  Success Rate: $finalSuccessRate%" -ForegroundColor $(if($finalSuccessRate -ge 80) {"Green"} else {"Yellow"})

if ($finalSuccessRate -eq 100) {
    Write-Host ""
    Write-Host "🎉 SYSTEM FULLY OPERATIONAL!" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green
    Write-Host "🚀 All plugins can now work properly!" -ForegroundColor Green
    Write-Host "🎨 Start building visual workflows!" -ForegroundColor Green
} elseif ($finalSuccessRate -ge 50) {
    Write-Host ""
    Write-Host "⚠️ PARTIAL SYSTEM OPERATIONAL" -ForegroundColor Yellow
    Write-Host "=============================" -ForegroundColor Yellow
    Write-Host "🚀 Some plugins can work!" -ForegroundColor Yellow
    Write-Host "🔧 Fix remaining services for full functionality!" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ SYSTEM NOT OPERATIONAL" -ForegroundColor Red
    Write-Host "=========================" -ForegroundColor Red
    Write-Host "🔧 Fix services before using plugins!" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔗 Quick Access Links:" -ForegroundColor White
foreach ($service in $services) {
    Write-Host "  $($service.Name): $($service.Url)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎉 INTERACTIVE DEBUG SYSTEM COMPLETE!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
