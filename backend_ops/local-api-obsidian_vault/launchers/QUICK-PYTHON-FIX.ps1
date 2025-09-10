# 🚀 QUICK PYTHON FIX - Use Python 3.12 for Vault API
# Quick solution to fix Python 3.13 compatibility issues

Write-Host "🚀 QUICK PYTHON FIX" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta
Write-Host "Using Python 3.12 for Vault API" -ForegroundColor White
Write-Host ""

# Find Python 3.12
$python312 = "C:\Program Files\Python312\python.exe"

if (-not (Test-Path $python312)) {
    Write-Host "❌ Python 3.12 not found at: $python312" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found Python 3.12 at: $python312" -ForegroundColor Green

# Kill existing processes
Write-Host ""
Write-Host "🛑 Stopping existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force

# Fix Vault API with Python 3.12
Write-Host ""
Write-Host "🔧 Fixing Vault API with Python 3.12..." -ForegroundColor Yellow

if (Test-Path servicesservices/vault-api") {
    Set-Location vault-api
    
    # Upgrade pip and setuptools with Python 3.12
    Write-Host "  🔧 Upgrading pip and setuptools..." -ForegroundColor Cyan
    & $python312 -m pip install --upgrade pip setuptools wheel --quiet
    
    # Install requirements with Python 3.12
    Write-Host "  🔧 Installing requirements..." -ForegroundColor Cyan
    & $python312 -m pip install -r requirements.txt --quiet
    
    Set-Location ..
    Write-Host "  ✅ Vault API dependencies installed with Python 3.12" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ vault-api directory not found" -ForegroundColor Yellow
}

# Start all services
Write-Host ""
Write-Host "🚀 Starting all services..." -ForegroundColor Yellow

# Start Vault API with Python 3.12
Write-Host "  🏛️ Starting Vault API with Python 3.12..." -ForegroundColor Cyan
try {
    $vaultJob = Start-Job -ScriptBlock {
        Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\vault-api"
        & "C:\Program Files\Python312\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
    } -Name "VaultAPI"
    Write-Host "    ✅ Vault API started (Job ID: $($vaultJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Vault API: $($_.Exception.Message)" -ForegroundColor Red
}

# Start Flyde
Write-Host "  🎨 Starting Flyde..." -ForegroundColor Cyan
try {
    $flydeJob = Start-Job -ScriptBlock {
        Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\flyde-project"
        npm run dev
    } -Name "Flyde"
    Write-Host "    ✅ Flyde started (Job ID: $($flydeJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Flyde: $($_.Exception.Message)" -ForegroundColor Red
}

# Start Motia
Write-Host "  ⚡ Starting Motia..." -ForegroundColor Cyan
try {
    $motiaJob = Start-Job -ScriptBlock {
        Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\motia-project"
        npm run dev
    } -Name "Motia"
    Write-Host "    ✅ Motia started (Job ID: $($motiaJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Motia: $($_.Exception.Message)" -ForegroundColor Red
}

# Start Obsidian API
Write-Host "  📝 Starting Obsidian API..." -ForegroundColor Cyan
try {
    $obsidianJob = Start-Job -ScriptBlock {
        Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\obsidian-api"
        npx motia dev --port 27123
    } -Name "ObsidianAPI"
    Write-Host "    ✅ Obsidian API started (Job ID: $($obsidianJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Obsidian API: $($_.Exception.Message)" -ForegroundColor Red
}

# Wait and test
Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Test services
Write-Host ""
Write-Host "🧪 Testing services..." -ForegroundColor Yellow

$services = @(
    @{ Name = "Vault API"; Url = "http://localhost:8080/health" }
    @{ Name = "Flyde"; Url = "http://localhost:3001/health" }
    @{ Name = "Motia"; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian API"; Url = "http://localhost:27123/health" }
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $($service.Name): HEALTHY" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ $($service.Name): Status $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ $($service.Name): NOT RESPONDING" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 QUICK PYTHON FIX COMPLETE!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Quick Access:" -ForegroundColor White
Write-Host "  🏛️ Vault API: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 All services should now be running with Python 3.12!" -ForegroundColor Green
