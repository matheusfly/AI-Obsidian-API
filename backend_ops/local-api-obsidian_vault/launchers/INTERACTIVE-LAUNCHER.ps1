#!/usr/bin/env pwsh
# INTERACTIVE LAUNCHER WITH REAL-TIME DEBUGGING

$Host.UI.RawUI.WindowTitle = "🚀 Interactive System Launcher"
Clear-Host

Write-Host "🚀 INTERACTIVE SYSTEM LAUNCHER" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "Real-time debugging and output tracing active!" -ForegroundColor Green

$global:services = @{}
$global:logs = @{}

function Write-Status {
    param([string]$Service, [string]$Status, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Service`: $Status" -ForegroundColor $Color
    $global:logs[$Service] += "[$timestamp] $Status`n"
}

function Test-ServicePort {
    param([int]$Port, [string]$ServiceName)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($connection) {
        Write-Status $ServiceName "Port $Port is OPEN" "Green"
        return $true
    } else {
        Write-Status $ServiceName "Port $Port is CLOSED" "Red"
        return $false
    }
}

function Start-ServiceWithTrace {
    param([string]$Name, [string]$Path, [string]$Command, [int]$Port)
    
    Write-Status $Name "Starting service..." "Yellow"
    
    try {
        $job = Start-Job -Name $Name -ScriptBlock {
            param($WorkingDir, $Cmd)
            Set-Location $WorkingDir
            Invoke-Expression $Cmd
        } -ArgumentList $Path, $Command
        
        $global:services[$Name] = @{
            Job = $job
            Port = $Port
            Status = "Starting"
            StartTime = Get-Date
        }
        
        Write-Status $Name "Background job started (ID: $($job.Id))" "Green"
        
        # Wait and test port
        Start-Sleep -Seconds 3
        for ($i = 1; $i -le 10; $i++) {
            if (Test-ServicePort -Port $Port -ServiceName $Name) {
                $global:services[$Name].Status = "Running"
                Write-Status $Name "Service is RUNNING and responding!" "Green"
                return $true
            }
            Write-Status $Name "Waiting for port... attempt $i/10" "Yellow"
            Start-Sleep -Seconds 2
        }
        
        Write-Status $Name "Service started but port not responding" "Yellow"
        return $false
        
    } catch {
        Write-Status $Name "FAILED to start: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Show-LiveStatus {
    Clear-Host
    Write-Host "🚀 LIVE SERVICE STATUS" -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    foreach ($service in $global:services.GetEnumerator()) {
        $name = $service.Key
        $info = $service.Value
        $job = Get-Job -Id $info.Job.Id -ErrorAction SilentlyContinue
        
        if ($job) {
            $status = $job.State
            $color = switch ($status) {
                "Running" { "Green" }
                "Completed" { "Yellow" }
                "Failed" { "Red" }
                default { "Gray" }
            }
            
            $portStatus = if (Test-NetConnection -ComputerName localhost -Port $info.Port -InformationLevel Quiet -WarningAction SilentlyContinue) { "✅" } else { "❌" }
            
            Write-Host "$portStatus $name (Port $($info.Port)): $status" -ForegroundColor $color
            
            # Show recent job output
            $output = Receive-Job -Job $job -Keep | Select-Object -Last 2
            if ($output) {
                foreach ($line in $output) {
                    Write-Host "    └─ $line" -ForegroundColor Gray
                }
            }
        }
    }
    
    Write-Host ""
    Write-Host "🔗 Quick Access URLs:" -ForegroundColor Cyan
    Write-Host "  Vault API:    http://localhost:8080/docs" -ForegroundColor White
    Write-Host "  Obsidian API: http://localhost:27123" -ForegroundColor White
    Write-Host "  Motia:        http://localhost:3001" -ForegroundColor White
    Write-Host "  Flyde:        http://localhost:3002" -ForegroundColor White
    Write-Host ""
    Write-Host "Press 'q' to quit, 'r' to refresh, 's' to show logs" -ForegroundColor Yellow
}

# Initialize logs
$global:logs = @{
    "VaultAPI" = ""
    "ObsidianAPI" = ""
    "Motia" = ""
    "Flyde" = ""
}

# Start launching services
Write-Host "`n🔥 LAUNCHING SERVICES..." -ForegroundColor Yellow
Write-Host "========================" -ForegroundColor Yellow

# 1. Vault API
Write-Status "System" "Starting Vault API..." "Cyan"
Start-ServiceWithTrace -Name "VaultAPI" -Path "$PWDservices/vault-api" -Command "python main.py" -Port 8080

# 2. Obsidian API  
Write-Status "System" "Starting Obsidian API..." "Cyan"
Start-ServiceWithTrace -Name "ObsidianAPI" -Path "$PWDservices/obsidian-api" -Command "npm start" -Port 27123

# 3. Motia
Write-Status "System" "Starting Motia..." "Cyan"
Start-ServiceWithTrace -Name "Motia" -Path "$PWD/motia-project" -Command "npm start" -Port 3001

# 4. Flyde
Write-Status "System" "Starting Flyde..." "Cyan"
Start-ServiceWithTrace -Name "Flyde" -Path "$PWD/flyde-project" -Command "npm start" -Port 3002

Write-Status "System" "All services launched! Entering interactive mode..." "Green"

# Interactive monitoring loop
while ($true) {
    Show-LiveStatus
    
    $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    switch ($key.Character) {
        'q' { 
            Write-Host "`n🛑 Stopping all services..." -ForegroundColor Red
            Get-Job | Stop-Job -PassThru | Remove-Job -Force
            Write-Host "✅ All services stopped. Goodbye!" -ForegroundColor Green
            exit 
        }
        'r' { 
            # Refresh (do nothing, loop will refresh)
        }
        's' {
            Clear-Host
            Write-Host "📋 SERVICE LOGS" -ForegroundColor Cyan
            Write-Host "===============" -ForegroundColor Cyan
            foreach ($log in $global:logs.GetEnumerator()) {
                Write-Host "`n--- $($log.Key) ---" -ForegroundColor Yellow
                Write-Host $log.Value
            }
            Write-Host "`nPress any key to return..." -ForegroundColor Gray
            $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
        }
        't' {
            # Test all services
            Clear-Host
            Write-Host "🧪 TESTING ALL SERVICES" -ForegroundColor Cyan
            Write-Host "========================" -ForegroundColor Cyan
            
            @(
                @{ name = "Vault API"; url = "http://localhost:8080/health" },
                @{ name = "Obsidian API"; url = "http://localhost:27123/health" }
            ) | ForEach-Object {
                try {
                    $response = Invoke-RestMethod -Uri $_.url -TimeoutSec 3
                    Write-Host "✅ $($_.name): OK" -ForegroundColor Green
                } catch {
                    Write-Host "❌ $($_.name): Failed" -ForegroundColor Red
                }
            }
            
            Write-Host "`nPress any key to return..." -ForegroundColor Gray
            $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
        }
    }
    
    Start-Sleep -Seconds 1
}