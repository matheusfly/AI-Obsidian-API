Write-Host "🚀 FORCE STARTING ALL SERVICES" -ForegroundColor Red
Write-Host "===============================" -ForegroundColor Red

# Kill everything first
Write-Host "Killing existing processes..." -ForegroundColor Yellow
Get-Job | Stop-Job -ErrorAction SilentlyContinue 2>$null
Get-Job | Remove-Job -Force 2>$null
taskkill /F /IM python.exe 2>$null
taskkill /F /IM node.exe 2>$null

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow
try {
    $python = python --version
    Write-Host "✅ Python: $python" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    exit 1
}

try {
    $node = node --version
    Write-Host "✅ Node.js: $node" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies quickly
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
cd vault-api
py -3.12 -m pip install --upgrade pip setuptools wheel --quiet
py -3.12 -m pip install --no-build-isolation -r requirements.txt --quiet
cd ..

cd obsidian-api
npm install --silent
cd ..

cd motia-project
npm install --silent
cd ..

cd flyde-project
npm install --silent
cd ..

# Force start services with explicit paths
Write-Host "`nForce starting services..." -ForegroundColor Yellow

# Start Vault API
Write-Host "Starting Vault API..." -ForegroundColor Cyan
$vaultApiDir = "D:\codex\master_code\backend_ops\local-api-obsidian_vault\vault-api"
$uvicornArgs = "-3.12 -m uvicorn main:app --host 127.0.0.1 --port 18081 --log-level debug"
# Ensure logs directory exists
if (-not (Test-Path "$vaultApiDir\logs")) { New-Item -ItemType Directory -Path "$vaultApiDir\logs" | Out-Null }
Start-Job -Name "VaultAPI" -ScriptBlock {
    param($dir, $args)
    Set-Location $dir
    # Ensure Vault API talks to local Obsidian API on new port
    $env:OBSIDIAN_API_URL = "http://127.0.0.1:27124"
    $p = Start-Process -FilePath "py" -ArgumentList $args -WorkingDirectory $dir -RedirectStandardOutput "$dir\logs\uvicorn.out.log" -RedirectStandardError "$dir\logs\uvicorn.err.log" -PassThru
    Wait-Process -Id $p.Id
} -ArgumentList $vaultApiDir, $uvicornArgs | Out-Null

Start-Sleep -Seconds 3

# Start Obsidian API
Write-Host "Starting Obsidian API..." -ForegroundColor Cyan
Start-Job -Name "ObsidianAPI" -ScriptBlock {
    Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\obsidian-api"
    $env:API_PORT = "27124"
    node server.js
} | Out-Null

Start-Sleep -Seconds 3

# Start Motia
Write-Host "Starting Motia..." -ForegroundColor Cyan
Start-Job -Name "Motia" -ScriptBlock {
    Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\motia-project"
    $env:MOTIA_PORT = "33000"
    npm run dev
} | Out-Null

Start-Sleep -Seconds 3

# Start Flyde
Write-Host "Starting Flyde..." -ForegroundColor Cyan
Start-Job -Name "Flyde" -ScriptBlock {
    Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\flyde-project"
    $env:PORT = "33001"
    npm run dev
} | Out-Null

Write-Host "`nWaiting 30 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check what's running
Write-Host "`n📊 SERVICE STATUS:" -ForegroundColor Cyan
Get-Job | Format-Table -Property Id, Name, State

Write-Host "`n🔍 PORT CHECK:" -ForegroundColor Cyan
$ports = @(
    @{Port=18081; Name="Vault API"},
    @{Port=27124; Name="Obsidian API"},
    @{Port=33000; Name="Motia"},
    @{Port=33001; Name="Flyde"}
)

foreach ($service in $ports) {
    $test = Test-NetConnection -ComputerName localhost -Port $service.Port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($test) {
        Write-Host "✅ $($service.Name) (Port $($service.Port)): OPEN" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.Name) (Port $($service.Port)): CLOSED" -ForegroundColor Red
    }
}

Write-Host "`n🌐 TESTING ENDPOINTS:" -ForegroundColor Cyan
try {
$vault = Invoke-RestMethod -Uri "http://localhost:18081/health" -TimeoutSec 5
    Write-Host "✅ Vault API: RESPONDING" -ForegroundColor Green
} catch {
    Write-Host "❌ Vault API: NOT RESPONDING" -ForegroundColor Red
}

try {
$obsidian = Invoke-RestMethod -Uri "http://localhost:27124/health" -TimeoutSec 5
    Write-Host "✅ Obsidian API: RESPONDING" -ForegroundColor Green
} catch {
    Write-Host "❌ Obsidian API: NOT RESPONDING" -ForegroundColor Red
}

Write-Host "`n🎯 ACCESS URLS:" -ForegroundColor Green
Write-Host "Vault API Docs: http://localhost:18081/docs" -ForegroundColor White
Write-Host "Vault API Health: http://localhost:18081/health" -ForegroundColor White
Write-Host "Obsidian API: http://localhost:27124" -ForegroundColor White
Write-Host "Motia: http://localhost:33000" -ForegroundColor White
Write-Host "Flyde: http://localhost:33001" -ForegroundColor White

Write-Host "`n🔧 MANAGEMENT:" -ForegroundColor Yellow
Write-Host scripts/ Status: Get-Job" -ForegroundColor Gray
Write-Host "Stop All: Get-Job | Stop-Job" -ForegroundColor Gray
Write-Host "View Logs: Receive-Job -Name VaultAPI" -ForegroundColor Gray

Write-Host "`n✅ FORCE START COMPLETE!" -ForegroundColor Green