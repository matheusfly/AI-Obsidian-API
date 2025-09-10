#!/usr/bin/env pwsh
# SIMPLE TEST - No Complex Parameters

Write-Host "🧪 SIMPLE INTEGRATION TEST" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

# Test 1: Basic Prerequisites
Write-Host "`n1️⃣ Prerequisites..." -ForegroundColor Yellow
try {
    $nodeVer = node --version
    Write-Host "✅ Node.js: $nodeVer" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js: Not found" -ForegroundColor Red
}

try {
    $pythonVer = python --version
    Write-Host "✅ Python: $pythonVer" -ForegroundColor Green
} catch {
    Write-Host "❌ Python: Not found" -ForegroundColor Red
}

# Test 2: Service Ports
Write-Host "`n2️⃣ Service Ports..." -ForegroundColor Yellow
$ports = @(8080, 27123, 3001, 3002)
foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($connection) {
        Write-Host "✅ Port $port: Open" -ForegroundColor Green
    } else {
        Write-Host "❌ Port $port: Closed" -ForegroundColor Red
    }
}

# Test 3: API Health (Simple)
Write-Host "`n3️⃣ API Health..." -ForegroundColor Yellow
try {
    $vault = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 3
    Write-Host "✅ Vault API: Status $($vault.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Vault API: Not responding" -ForegroundColor Red
}

try {
    $obsidian = Invoke-WebRequest -Uri "http://localhost:27123/health" -UseBasicParsing -TimeoutSec 3
    Write-Host "✅ Obsidian API: Status $($obsidian.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Obsidian API: Not responding" -ForegroundColor Red
}

# Test 4: Project Structure
Write-Host "`n4️⃣ Project Structure..." -ForegroundColor Yellow
$projects = @("motia-project", "flyde-project", "vault-api", "obsidian-api")
foreach ($project in $projects) {
    if (Test-Path $project) {
        Write-Host "✅ $project: Found" -ForegroundColor Green
    } else {
        Write-Host "❌ $project: Missing" -ForegroundColor Red
    }
}

# Test 5: Dependencies
Write-Host "`n5️⃣ Dependencies..." -ForegroundColor Yellow
foreach ($project in @("motia-project", "flyde-project", "obsidian-api")) {
    if (Test-Path "$project/node_modules") {
        Write-Host "✅ $project: Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ $project: Missing node_modules" -ForegroundColor Red
    }
}

if (Test-Path "vault-api/__pycache__") {
    Write-Host "✅ vault-api: Python cache found" -ForegroundColor Green
} else {
    Write-Host "⚠️ vault-api: No Python cache (first run)" -ForegroundColor Yellow
}

Write-Host "`n📊 SIMPLE TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host "Run EMERGENCY-FIX.ps1 to start services" -ForegroundColor White
Write-Host "Run QUICK-START-NATIVE.ps1 for native startup" -ForegroundColor White