# 🎯 FINAL COMPREHENSIVE FIX - Get Everything Running
# Comprehensive fix to get all services running properly

Write-Host "🎯 FINAL COMPREHENSIVE FIX" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta
Write-Host "Getting Everything Running Properly" -ForegroundColor White
Write-Host ""

# Kill everything first
Write-Host "🛑 Stopping all existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "cmd" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "✅ All processes stopped" -ForegroundColor Green

# Wait a moment
Start-Sleep -Seconds 3

# Start services with proper error handling
Write-Host ""
Write-Host "🚀 Starting services with enhanced error handling..." -ForegroundColor Yellow

# 1. Start Flyde
Write-Host "  🎨 Starting Flyde Studio..." -ForegroundColor Cyan
try {
    $flydeJob = Start-Job -ScriptBlock {
        Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\flyde-project"
        npm run dev
    } -Name "Flyde"
    Write-Host "    ✅ Flyde started (Job ID: $($flydeJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Flyde: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Start Motia
Write-Host "  ⚡ Starting Motia Integration..." -ForegroundColor Cyan
try {
    $motiaJob = Start-Job -ScriptBlock {
        Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\motia-project"
        npm run dev
    } -Name "Motia"
    Write-Host "    ✅ Motia started (Job ID: $($motiaJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Motia: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Start Obsidian API
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

# 4. Start Vault API with Python 3.12
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

# Wait for services to start
Write-Host ""
Write-Host "⏳ Waiting for services to start (60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Comprehensive testing
Write-Host ""
Write-Host "🧪 Comprehensive Service Testing..." -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow

$services = @(
    @{ Name = "Flyde Studio"; Port = 3001; Url = "http://localhost:3001/health" }
    @{ Name = "Motia Integration"; Port = 3000; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian API"; Port = 27123; Url = "http://localhost:27123/health" }
    @{ Name = "Vault API"; Port = 8080; Url = "http://localhost:8080/health" }
)

$results = @{}
$successCount = 0

foreach ($service in $services) {
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Status: HEALTHY" -ForegroundColor Green
            Write-Host "  📊 Response: $($response.StatusCode)" -ForegroundColor Green
            $results[$service.Name] = $true
            $successCount++
        } else {
            Write-Host "  ⚠️ Status: UNEXPECTED RESPONSE" -ForegroundColor Yellow
            Write-Host "  📊 Response: $($response.StatusCode)" -ForegroundColor Yellow
            $results[$service.Name] = $false
        }
    } catch {
        Write-Host "  ❌ Status: NOT RESPONDING" -ForegroundColor Red
        Write-Host "  🔍 Error: $($_.Exception.Message)" -ForegroundColor Red
        $results[$service.Name] = $false
    }
}

# Calculate success rate
$totalServices = $services.Count
$successRate = [Math]::Round(($successCount / $totalServices) * 100, 1)

# Final status report
Write-Host ""
Write-Host "📊 FINAL COMPREHENSIVE FIX RESULTS" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "🎯 Overall Status:" -ForegroundColor White
Write-Host "  Total Services: $totalServices" -ForegroundColor White
Write-Host "  Running: $successCount/$totalServices" -ForegroundColor White
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})

Write-Host ""
Write-Host "🔍 Service Details:" -ForegroundColor White
foreach ($result in $results.GetEnumerator()) {
    $status = if ($result.Value) { "✅ RUNNING" } else { "❌ NOT RUNNING" }
    $color = if ($result.Value) { "Green" } else { "Red" }
    Write-Host "  $($result.Key): $status" -ForegroundColor $color
}

Write-Host ""
Write-Host "🔗 Quick Access Links:" -ForegroundColor White
Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault API: http://localhost:8080" -ForegroundColor Cyan

if ($successRate -ge 80) {
    Write-Host ""
    Write-Host "🎉 COMPREHENSIVE FIX SUCCESSFUL!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "🚀 All services are now running!" -ForegroundColor Green
    Write-Host "🎨 Start building visual workflows!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ SOME SERVICES STILL NEED ATTENTION" -ForegroundColor Yellow
    Write-Host "=====================================" -ForegroundColor Yellow
    Write-Host "🔧 Check the status above and restart if needed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Open Flyde Studio at http://localhost:3001" -ForegroundColor Cyan
Write-Host "  2. Open Motia Workbench at http://localhost:3000" -ForegroundColor Cyan
Write-Host "  3. Start building visual workflows!" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 FINAL COMPREHENSIVE FIX COMPLETE!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
