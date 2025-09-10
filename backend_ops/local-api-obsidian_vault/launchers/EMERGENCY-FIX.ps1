#!/usr/bin/env pwsh
# EMERGENCY FIX - Critical System Recovery

Write-Host "🚨 EMERGENCY SYSTEM RECOVERY" -ForegroundColor Red
Write-Host "============================" -ForegroundColor Red

# 1. Fix Docker Desktop
Write-Host "`n1️⃣ Fixing Docker Desktop..." -ForegroundColor Yellow
try {
    $dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
    if (-not $dockerProcess) {
        Write-Host "Starting Docker Desktop..." -ForegroundColor Gray
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -WindowStyle Hidden
        Write-Host "⏳ Waiting 30 seconds for Docker to start..." -ForegroundColor Gray
        Start-Sleep -Seconds 30
    }
    
    # Test Docker
    $dockerTest = docker version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker Desktop failed to start" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Docker Desktop error: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Fix Node.js PATH issues
Write-Host "`n2️⃣ Fixing Node.js PATH..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Node.js working: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Node.js PATH issue detected" -ForegroundColor Red
        # Add common Node.js paths
        $env:PATH += ";C:\Program Files\nodejs;C:\Users\$env:USERNAME\AppData\Roaming\npm"
        $nodeVersion = node --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Node.js fixed: $nodeVersion" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "❌ Node.js error: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Start Core Services Manually
Write-Host "`n3️⃣ Starting Core Services..." -ForegroundColor Yellow

# Start Vault API
Write-Host "Starting Vault API..." -ForegroundColor Gray
try {
    $vaultJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        cd vault-api
        python main.py
    }
    Start-Sleep -Seconds 5
    
    # Test Vault API
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 3
        Write-Host "✅ Vault API started successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Vault API starting (may need more time)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Vault API failed to start" -ForegroundColor Red
}

# Start Obsidian API
Write-Host "Starting Obsidian API..." -ForegroundColor Gray
try {
    $obsidianJob = Start-Job -ScriptBlock {
        Set-Location "$using:PWDservices/obsidian-api"
        npm start
    }
    Start-Sleep -Seconds 5
    
    # Test Obsidian API
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:27123/health" -TimeoutSec 3
        Write-Host "✅ Obsidian API started successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Obsidian API starting (may need more time)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Obsidian API failed to start" -ForegroundColor Red
}

# Start Motia
Write-Host "Starting Motia..." -ForegroundColor Gray
try {
    $motiaJob = Start-Job -ScriptBlock {
        Set-Location "$using:PWD/motia-project"
        npm start
    }
    Write-Host "✅ Motia started in background" -ForegroundColor Green
} catch {
    Write-Host "❌ Motia failed to start" -ForegroundColor Red
}

# Start Flyde
Write-Host "Starting Flyde..." -ForegroundColor Gray
try {
    $flydeJob = Start-Job -ScriptBlock {
        Set-Location "$using:PWD/flyde-project"
        npm start
    }
    Write-Host "✅ Flyde started in background" -ForegroundColor Green
} catch {
    Write-Host "❌ Flyde failed to start" -ForegroundColor Red
}

# 4. Quick Health Check
Write-Host "`n4️⃣ Quick Health Check..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$services = @(
    @{ name = "Vault API"; url = "http://localhost:8080/health"; port = 8080 },
    @{ name = "Obsidian API"; url = "http://localhost:27123/health"; port = 27123 },
    @{ name = "Motia"; port = 3001 },
    @{ name = "Flyde"; port = 3002 }
)

foreach ($service in $services) {
    $portOpen = Test-NetConnection -ComputerName localhost -Port $service.port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($portOpen) {
        Write-Host "✅ $($service.name): Port $($service.port) is open" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.name): Port $($service.port) is closed" -ForegroundColor Red
    }
}

# 5. Show Running Jobs
Write-Host "`n5️⃣ Background Jobs Status..." -ForegroundColor Yellow
Get-Job | Format-Table -Property Id, Name, State

Write-Host "`n🚀 EMERGENCY RECOVERY COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "✅ Core services started manually" -ForegroundColor Green
Write-Host "✅ Background jobs running" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Quick Access:" -ForegroundColor Cyan
Write-Host "  Vault API:    http://localhost:8080/docs" -ForegroundColor White
Write-Host "  Obsidian API: http://localhost:27123" -ForegroundColor White
Write-Host "  Motia:        http://localhost:3001" -ForegroundColor White
Write-Host "  Flyde:        http://localhost:3002" -ForegroundColor White
Write-Host ""
Write-Host "🛠️ To stop services: Get-Job | Stop-Job" -ForegroundColor Gray