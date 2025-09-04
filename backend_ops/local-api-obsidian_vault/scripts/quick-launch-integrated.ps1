#!/usr/bin/env pwsh
# Quick Launch Integrated System with All Components

param(
    [switch]$SkipTests,
    [switch]$Verbose,
    [switch]$Background
)

Write-Host "🚀 Quick Launch - Integrated Obsidian Vault System" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

$services = @()
$errors = @()

function Start-ServiceWithCheck {
    param(
        [string]$Name,
        [scriptblock]$StartCommand,
        [string]$HealthUrl = $null,
        [int]$Port = $null,
        [int]$WaitSeconds = 10
    )
    
    Write-Host "`n🔧 Starting $Name..." -ForegroundColor Yellow
    
    try {
        # Execute start command
        $result = & $StartCommand
        
        if ($result -and $result.ExitCode -ne 0) {
            throw "Start command failed with exit code $($result.ExitCode)"
        }
        
        # Wait for service to be ready
        if ($Port) {
            Write-Host "⏳ Waiting for port $Port..." -ForegroundColor Gray
            $timeout = $WaitSeconds
            while ($timeout -gt 0) {
                $portOpen = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
                if ($portOpen) {
                    break
                }
                Start-Sleep -Seconds 1
                $timeout--
            }
            
            if ($timeout -le 0) {
                throw "Port $Port not accessible after $WaitSeconds seconds"
            }
        }
        
        # Health check
        if ($HealthUrl) {
            Write-Host "🏥 Health check: $HealthUrl" -ForegroundColor Gray
            $healthTimeout = 5
            while ($healthTimeout -gt 0) {
                try {
                    Invoke-RestMethod -Uri $HealthUrl -Method GET -TimeoutSec 3 | Out-Null
                    break
                } catch {
                    Start-Sleep -Seconds 1
                    $healthTimeout--
                }
            }
            
            if ($healthTimeout -le 0) {
                Write-Host "⚠️ Health check failed, but service may still be starting..." -ForegroundColor Yellow
            }
        }
        
        Write-Host "✅ ${Name}: Started successfully" -ForegroundColor Green
        $services += @{ Name = $Name; Status = "Running"; Port = $Port }
        return $true
        
    } catch {
        Write-Host "❌ ${Name}: Failed to start - $($_.Exception.Message)" -ForegroundColor Red
        $errors += "$Name: $($_.Exception.Message)"
        $services += @{ Name = $Name; Status = "Failed"; Error = $_.Exception.Message }
        return $false
    }
}

# 1. Start Docker Services
$dockerSuccess = Start-ServiceWithCheck -Name "Docker Services" -StartCommand {
    Write-Host "  Starting Docker Compose..." -ForegroundColor Gray
    docker-compose up -d
    return @{ ExitCode = $LASTEXITCODE }
} -WaitSeconds 15

# 2. Start Qdrant Vector Database
if ($dockerSuccess) {
    Start-ServiceWithCheck -Name "Qdrant Vector DB" -Port 6333 -HealthUrl "http://localhost:6333/collections" -WaitSeconds 20
}

# 3. Start Embedding Server
if ($dockerSuccess) {
    Start-ServiceWithCheck -Name "Embedding Server" -Port 3000 -HealthUrl "http://localhost:3000/health" -WaitSeconds 25
}

# 4. Start Vault API
Start-ServiceWithCheck -Name "Vault API" -StartCommand {
    Write-Host "  Starting Vault API server..." -ForegroundColor Gray
    if ($Background) {
        Start-Process -FilePath "python" -ArgumentList servicesservices/vault-api/main.py" -WindowStyle Hidden
    } else {
        Start-Job -ScriptBlock { 
            Set-Location $using:PWD
            python vault-api/main.py 
        } | Out-Null
    }
    return @{ ExitCode = 0 }
} -Port 8080 -HealthUrl "http://localhost:8080/health" -WaitSeconds 15

# 5. Start Obsidian API (if not running)
$obsidianRunning = Test-NetConnection -ComputerName localhost -Port 27123 -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $obsidianRunning) {
    Start-ServiceWithCheck -Name "Obsidian API" -StartCommand {
        Write-Host "  Starting Obsidian API server..." -ForegroundColor Gray
        Set-Location servicesservices/obsidian-api"
        if ($Background) {
            Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Hidden
        } else {
            Start-Job -ScriptBlock { 
                Set-Location "$using:PWDservices/obsidian-api"
                npm start 
            } | Out-Null
        }
        Set-Location ".."
        return @{ ExitCode = 0 }
    } -Port 27123 -HealthUrl "http://localhost:27123/health" -WaitSeconds 20
} else {
    Write-Host "✅ Obsidian API: Already running" -ForegroundColor Green
    $services += @{ Name = "Obsidian API"; Status = "Already Running"; Port = 27123 }
}

# 6. Start Motia Integration
Start-ServiceWithCheck -Name "Motia Integration" -StartCommand {
    Write-Host "  Starting Motia server..." -ForegroundColor Gray
    Set-Location "motia-project"
    if ($Background) {
        Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Hidden
    } else {
        Start-Job -ScriptBlock { 
            Set-Location "$using:PWD/motia-project"
            npm start 
        } | Out-Null
    }
    Set-Location ".."
    return @{ ExitCode = 0 }
} -Port 3001 -WaitSeconds 10

# 7. Start Flyde Integration
Start-ServiceWithCheck -Name "Flyde Integration" -StartCommand {
    Write-Host "  Starting Flyde server..." -ForegroundColor Gray
    Set-Location "flyde-project"
    if ($Background) {
        Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Hidden
    } else {
        Start-Job -ScriptBlock { 
            Set-Location "$using:PWD/flyde-project"
            npm start 
        } | Out-Null
    }
    Set-Location ".."
    return @{ ExitCode = 0 }
} -Port 3002 -WaitSeconds 10

# Wait for all services to stabilize
Write-Host "`n⏳ Allowing services to stabilize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run integration tests if not skipped
if (-not $SkipTests) {
    Write-Host "`n🧪 Running integration tests..." -ForegroundColor Cyan
    try {
        .\scripts\test-complete-suite.ps1 -Integration
    } catch {
        Write-Host "⚠️ Integration tests failed, but services may still be functional" -ForegroundColor Yellow
    }
}

# Display service status
Write-Host "`n📊 SERVICE STATUS DASHBOARD" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

foreach ($service in $services) {
    $statusColor = switch ($service.Status) {
        "Running" { "Green" }
        "Already Running" { "Green" }
        "Failed" { "Red" }
        default { "Yellow" }
    }
    
    $portInfo = if ($service.Port) { " (Port: $($service.Port))" } else { "" }
    Write-Host "$($service.Name): $($service.Status)$portInfo" -ForegroundColor $statusColor
    
    if ($service.Error -and $Verbose) {
        Write-Host "  Error: $($service.Error)" -ForegroundColor Red
    }
}

# Show quick access URLs
Write-Host "`n🌐 QUICK ACCESS URLS" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "Vault API:          http://localhost:8080" -ForegroundColor White
Write-Host "Vault API Docs:     http://localhost:8080/docs" -ForegroundColor White
Write-Host "Obsidian API:       http://localhost:27123" -ForegroundColor White
Write-Host "Qdrant Dashboard:   http://localhost:6333/dashboard" -ForegroundColor White
Write-Host "Grafana:           http://localhost:3000 (admin/admin123)" -ForegroundColor White
Write-Host "Prometheus:        http://localhost:9090" -ForegroundColor White

# Show quick commands
Write-Host "`n🚀 QUICK COMMANDS" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host scripts/ Enhanced RAG:  python test-enhanced-rag.py" -ForegroundColor White
Write-Host scripts/ Issues:       .\scripts\debug-integrations.ps1 -Fix" -ForegroundColor White
Write-Host "Performance Test:   .\scripts\test-complete-suite.ps1 -Performance" -ForegroundColor White
Write-Host "Stop All Services:  docker-compose down && Get-Job | Stop-Job" -ForegroundColor White

# Final status
$runningServices = ($services | Where-Object { $_.Status -eq "Running" -or $_.Status -eq "Already Running" }).Count
$totalServices = $services.Count
$successRate = if ($totalServices -gt 0) { ($runningServices / $totalServices) * 100 } else { 0 }

Write-Host "`n🎯 LAUNCH SUMMARY" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host "Services Running: $runningServices/$totalServices (${successRate:F1}%)" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

if ($errors.Count -gt 0) {
    Write-Host "`n⚠️ Errors encountered:" -ForegroundColor Yellow
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
    Write-Host "`nRun with -Verbose for detailed error information" -ForegroundColor Gray
}

if ($successRate -ge 80) {
    Write-Host "`n🎉 System launched successfully! Ready for use." -ForegroundColor Green
} elseif ($successRate -ge 60) {
    Write-Host "`n⚠️ System partially launched. Some services may need attention." -ForegroundColor Yellow
} else {
    Write-Host "`n🚨 System launch incomplete. Run debug script to fix issues." -ForegroundColor Red
}

Write-Host "`n✅ Launch complete!" -ForegroundColor Green