#!/usr/bin/env pwsh
# QUICK START - Native Windows (No Docker)

Write-Host "🚀 QUICK START - NATIVE MODE" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# Kill any existing processes
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Job | Stop-Job -PassThru | Remove-Job -Force 2>$null
taskkill /F /IM python.exe 2>$null
taskkill /F /IM node.exe 2>$null

# Start services in correct order
Write-Host "`n1️⃣ Starting Vault API..." -ForegroundColor Green
Start-Job -Name "VaultAPI" -ScriptBlock {
    Set-Location "$using:PWDservices/vault-api"
    python main.py
} | Out-Null

Write-Host "2️⃣ Starting Obsidian API..." -ForegroundColor Green
Start-Job -Name "ObsidianAPI" -ScriptBlock {
    Set-Location "$using:PWDservices/obsidian-api"
    npm start
} | Out-Null

Write-Host "3️⃣ Starting Motia..." -ForegroundColor Green
Start-Job -Name "Motia" -ScriptBlock {
    Set-Location "$using:PWD/motia-project"
    npm start
} | Out-Null

Write-Host "4️⃣ Starting Flyde..." -ForegroundColor Green
Start-Job -Name "Flyde" -ScriptBlock {
    Set-Location "$using:PWD/flyde-project"
    npm start
} | Out-Null

# Wait and test
Write-Host "`n⏳ Waiting 15 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "`n🔍 Testing Services..." -ForegroundColor Cyan
$results = @()

# Test each service
@(
    @{ name = "Vault API"; url = "http://localhost:8080/health" },
    @{ name = "Obsidian API"; url = "http://localhost:27123/health" }
) | ForEach-Object {
    try {
        Invoke-RestMethod -Uri $_.url -TimeoutSec 3 | Out-Null
        Write-Host "✅ $($_.name): Running" -ForegroundColor Green
        $results += "✅ $($_.name)"
    } catch {
        Write-Host "❌ $($_.name): Failed" -ForegroundColor Red
        $results += "❌ $($_.name)"
    }
}

# Test ports
@(
    @{ name = "Motia"; port = 3001 },
    @{ name = "Flyde"; port = 3002 }
) | ForEach-Object {
    $portOpen = Test-NetConnection -ComputerName localhost -Port $_.port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($portOpen) {
        Write-Host "✅ $($_.name): Port $($_.port) open" -ForegroundColor Green
        $results += "✅ $($_.name)"
    } else {
        Write-Host "❌ $($_.name): Port $($_.port) closed" -ForegroundColor Red
        $results += "❌ $($_.name)"
    }
}

Write-Host "`n📊 SYSTEM STATUS" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Get-Job | Format-Table -Property Id, Name, State

Write-Host "`n🌐 ACCESS URLS" -ForegroundColor Cyan
Write-Host "==============" -ForegroundColor Cyan
Write-Host "Vault API:    http://localhost:8080/docs" -ForegroundColor White
Write-Host "Obsidian API: http://localhost:27123" -ForegroundColor White
Write-Host "Motia:        http://localhost:3001" -ForegroundColor White
Write-Host "Flyde:        http://localhost:3002" -ForegroundColor White

$successCount = ($results | Where-Object { $_ -like "✅*" }).Count
Write-Host "`n🎯 SUCCESS RATE: $successCount/4 services running" -ForegroundColor $(if ($successCount -ge 3) { "Green" } else { "Yellow" })

Write-Host "`n🛠️ MANAGEMENT COMMANDS" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host "Stop All:     Get-Job | Stop-Job" -ForegroundColor Gray
Write-Host scripts/ Status: Get-Job" -ForegroundColor Gray
Write-Host "View Logs:    Receive-Job -Name VaultAPI" -ForegroundColor Gray