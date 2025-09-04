Write-Host "📊 LIVE SYSTEM MONITOR" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

while ($true) {
    Clear-Host
    Write-Host "📊 LIVE SYSTEM MONITOR - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
    Write-Host "=================================================" -ForegroundColor Cyan
    
    # Job Status
    Write-Host "`n🔧 BACKGROUND JOBS:" -ForegroundColor Yellow
    $jobs = Get-Job
    if ($jobs) {
        $jobs | Format-Table -Property Id, Name, State
    } else {
        Write-Host "No background jobs running" -ForegroundColor Red
    }
    
    # Port Status
    Write-Host "`n🌐 PORT STATUS:" -ForegroundColor Yellow
    $ports = @(
@{Port=8081; Name="Vault API"; Url="http://localhost:8081/health"},
        @{Port=27124; Name="Obsidian API"; Url="http://localhost:27124/health"},
        @{Port=33000; Name="Motia"; Url="http://localhost:33000/health"},
        @{Port=33001; Name="Flyde"; Url="http://localhost:33001/health"}
    )
    
    foreach ($service in $ports) {
        $portOpen = Test-NetConnection -ComputerName localhost -Port $service.Port -InformationLevel Quiet -WarningAction SilentlyContinue
        $portStatus = if ($portOpen) { "✅ OPEN" } else { "❌ CLOSED" }
        
        # Test HTTP response
        $httpStatus = "❌ NO RESPONSE"
        try {
            $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 2
            $httpStatus = "✅ HTTP $($response.StatusCode)"
        } catch {
            # Try without /health
            try {
                $baseUrl = $service.Url -replace "/health", ""
                $response = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -TimeoutSec 2
                $httpStatus = "⚠️ HTTP $($response.StatusCode) (no /health)"
            } catch {
                $httpStatus = "❌ NO RESPONSE"
            }
        }
        
        Write-Host "$($service.Name) (Port $($service.Port)): $portStatus | $httpStatus" -ForegroundColor $(if ($portOpen) { "Green" } else { "Red" })
    }
    
    # System Resources
    Write-Host "`n💻 SYSTEM RESOURCES:" -ForegroundColor Yellow
    $cpu = Get-WmiObject -Class Win32_Processor | Measure-Object -Property LoadPercentage -Average
    $memory = Get-WmiObject -Class Win32_OperatingSystem
    $memoryUsed = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 1)
    
    Write-Host "CPU Usage: $([math]::Round($cpu.Average, 1))%" -ForegroundColor $(if ($cpu.Average -lt 80) { "Green" } else { "Red" })
    Write-Host datadata/memory Usage: $memoryUsed%" -ForegroundColor $(if ($memoryUsed -lt 80) { "Green" } else { "Red" })
    
    # Process Check
    Write-Host "`n🔍 PROCESS CHECK:" -ForegroundColor Yellow
    $pythonProcs = Get-Process -Name python -ErrorAction SilentlyContinue
    $nodeProcs = Get-Process -Name node -ErrorAction SilentlyContinue
    
    Write-Host "Python Processes: $($pythonProcs.Count)" -ForegroundColor $(if ($pythonProcs.Count -gt 0) { "Green" } else { "Red" })
    Write-Host "Node.js Processes: $($nodeProcs.Count)" -ForegroundColor $(if ($nodeProcs.Count -gt 0) { "Green" } else { "Red" })
    
    # Quick API Test
    Write-Host "`n🧪 QUICK API TESTS:" -ForegroundColor Yellow
    try {
$vaultTest = Invoke-RestMethod -Uri "http://localhost:18081/" -TimeoutSec 3
        Write-Host "✅ Vault API: Responding" -ForegroundColor Green
    } catch {
        Write-Host "❌ Vault API: Failed" -ForegroundColor Red
    }
    
    try {
        $obsidianTest = Invoke-WebRequest -Uri "http://localhost:27123" -UseBasicParsing -TimeoutSec 3
        Write-Host "✅ Obsidian API: Responding" -ForegroundColor Green
    } catch {
        Write-Host "❌ Obsidian API: Failed" -ForegroundColor Red
    }
    
    # Web Connectivity Test
    Write-Host "`n🌍 WEB CONNECTIVITY:" -ForegroundColor Yellow
    try {
        $webTest = Invoke-WebRequest -Uri "https://httpbin.org/get" -UseBasicParsing -TimeoutSec 5
        Write-Host "✅ Internet: Connected" -ForegroundColor Green
    } catch {
        Write-Host "❌ Internet: Failed" -ForegroundColor Red
    }
    
    Write-Host "`n🔗 QUICK ACCESS:" -ForegroundColor Cyan
Write-Host "http://localhost:18081/docs - Vault API Documentation" -ForegroundColor White
    Write-Host "http://localhost:27123 - Obsidian API" -ForegroundColor White
Write-Host "http://localhost:3000 - Motia Plugin" -ForegroundColor White
Write-Host "http://localhost:3001 - Flyde Plugin" -ForegroundColor White
    
    Write-Host "`n⏱️ Auto-refresh in 10 seconds... (Ctrl+C to stop)" -ForegroundColor Gray
    Start-Sleep -Seconds 10
}