#!/usr/bin/env pwsh
# LIVE LAUNCHER WITH REAL-TIME TRACING

Clear-Host
Write-Host "🚀 LIVE SYSTEM LAUNCHER" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

$services = @()

function Write-Trace {
    param([string]$Message, [string]$Color = "White")
    $time = Get-Date -Format "HH:mm:ss"
    Write-Host "[$time] $Message" -ForegroundColor $Color
}

function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

Write-Trace "🔥 Starting service launch sequence..." "Yellow"

# Launch Vault API
Write-Trace "Starting Vault API on port 8080..." "Cyan"
$vaultJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWDservices/vault-api"
    python main.py
}
$services += @{ Name = "VaultAPI"; Job = $vaultJob; Port = 8080 }
Write-Trace "✅ Vault API job started (ID: $($vaultJob.Id))" "Green"

Start-Sleep -Seconds 2

# Launch Obsidian API
Write-Trace "Starting Obsidian API on port 27123..." "Cyan"
$obsidianJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWDservices/obsidian-api"
    npm start
}
$services += @{ Name = "ObsidianAPI"; Job = $obsidianJob; Port = 27123 }
Write-Trace "✅ Obsidian API job started (ID: $($obsidianJob.Id))" "Green"

Start-Sleep -Seconds 2

# Launch Motia
Write-Trace "Starting Motia on port 3001..." "Cyan"
$motiaJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD/motia-project"
    npm start
}
$services += @{ Name = "Motia"; Job = $motiaJob; Port = 3001 }
Write-Trace "✅ Motia job started (ID: $($motiaJob.Id))" "Green"

Start-Sleep -Seconds 2

# Launch Flyde
Write-Trace "Starting Flyde on port 3002..." "Cyan"
$flydeJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD/flyde-project"
    npm start
}
$services += @{ Name = "Flyde"; Job = $flydeJob; Port = 3002 }
Write-Trace "✅ Flyde job started (ID: $flydeJob.Id)" "Green"

Write-Trace "⏳ Waiting 15 seconds for services to initialize..." "Yellow"
Start-Sleep -Seconds 15

# Real-time monitoring loop
Write-Trace "🔍 Starting real-time monitoring..." "Green"

for ($i = 1; $i -le 60; $i++) {
    Clear-Host
    Write-Host "🚀 LIVE SERVICE STATUS - Cycle $i" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    $runningCount = 0
    
    foreach ($service in $services) {
        $job = Get-Job -Id $service.Job.Id -ErrorAction SilentlyContinue
        $portOpen = Test-Port -Port $service.Port
        
        if ($job) {
            $status = $job.State
            $statusColor = switch ($status) {
                "Running" { "Green"; $runningCount++ }
                "Completed" { "Yellow" }
                "Failed" { "Red" }
                default { "Gray" }
            }
            
            $portStatus = if ($portOpen) { "✅ OPEN" } else { "❌ CLOSED" }
            $portColor = if ($portOpen) { "Green" } else { "Red" }
            
            Write-Host "$($service.Name) (Port $($service.Port)):" -ForegroundColor White
            Write-Host "  Job State: $status" -ForegroundColor $statusColor
            Write-Host "  Port Status: $portStatus" -ForegroundColor $portColor
            
            # Show recent output
            $output = Receive-Job -Job $job -Keep | Select-Object -Last 1
            if ($output) {
                Write-Host "  Latest: $output" -ForegroundColor Gray
            }
            Write-Host ""
        }
    }
    
    Write-Host "📊 SUMMARY: $runningCount/4 services active" -ForegroundColor $(if ($runningCount -ge 3) { "Green" } else { "Yellow" })
    Write-Host ""
    
    # Test API endpoints
    Write-Host "🌐 API HEALTH CHECKS:" -ForegroundColor Cyan
    
    try {
        $vaultHealth = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 2
        Write-Host "  ✅ Vault API: Healthy" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Vault API: Not responding" -ForegroundColor Red
    }
    
    try {
        $obsidianHealth = Invoke-RestMethod -Uri "http://localhost:27123/health" -TimeoutSec 2
        Write-Host "  ✅ Obsidian API: Healthy" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Obsidian API: Not responding" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "🔗 ACCESS URLS:" -ForegroundColor Cyan
    Write-Host "  Vault API:    http://localhost:8080/docs" -ForegroundColor White
    Write-Host "  Obsidian API: http://localhost:27123" -ForegroundColor White
    Write-Host "  Motia:        http://localhost:3001" -ForegroundColor White
    Write-Host "  Flyde:        http://localhost:3002" -ForegroundColor White
    Write-Host ""
    Write-Host monitoring/... (Ctrl+C to stop)" -ForegroundColor Gray
    
    Start-Sleep -Seconds 5
}

Write-Host "🏁 Monitoring complete. Services are running in background." -ForegroundColor Green
Write-Host "Use 'Get-Job' to check status and 'Get-Job | Stop-Job' to stop all." -ForegroundColor Yellow