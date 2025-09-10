# 🎉 FINAL ACTIVATION - Comprehensive Service Status & Activation
# Final script to check, activate, and provide status of all visual development tools

Write-Host "🎉 FINAL ACTIVATION" -ForegroundColor Magenta
Write-Host "==================" -ForegroundColor Magenta
Write-Host "Comprehensive Service Status & Activation" -ForegroundColor White
Write-Host ""

# Kill any existing jobs
Write-Host "🛑 Cleaning up existing jobs..." -ForegroundColor Yellow
Get-Job | Stop-Job
Get-Job | Remove-Job

# Kill existing processes
Write-Host "🛑 Stopping existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force

# Start services with proper error handling
Write-Host ""
Write-Host "🚀 Starting Services with Enhanced Error Handling..." -ForegroundColor Yellow

# Start Flyde
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

# Start Motia
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

# Wait for services to start
Write-Host ""
Write-Host "⏳ Waiting for services to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Comprehensive testing
Write-Host ""
Write-Host "🧪 Comprehensive Service Testing..." -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow

$services = @(
    @{ Name = "Flyde Studio"; Port = 3001; Url = "http://localhost:3001/health"; Description = "Visual Flow Programming" }
    @{ Name = "Motia Integration"; Port = 3000; Url = "http://localhost:3000/health"; Description = "Workflow Automation" }
    @{ Name = "Obsidian API"; Port = 27123; Url = "http://localhost:27123/health"; Description = "Knowledge Management" }
    @{ Name = "Vault API"; Port = 8080; Url = "http://localhost:8080/health"; Description = data/ Management" }
)

$results = @{}
$successCount = 0

foreach ($service in $services) {
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    Write-Host "  Port: $($service.Port)" -ForegroundColor White
    Write-Host "  Description: $($service.Description)" -ForegroundColor White
    
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
Write-Host "📊 FINAL STATUS REPORT" -ForegroundColor Magenta
Write-Host "=====================" -ForegroundColor Magenta
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

Write-Host ""
Write-Host "🎨 Visual Development Tools:" -ForegroundColor White
Write-Host "  🎨 Flyde Studio: Visual flow-based programming" -ForegroundColor Cyan
Write-Host "  ⚡ Motia Workbench: Workflow automation and API management" -ForegroundColor Cyan

Write-Host ""
Write-Host "📝 Backend Services:" -ForegroundColor White
Write-Host "  📝 Obsidian API: Knowledge management and note-taking" -ForegroundColor Cyan
Write-Host "  🏛️ Vault API: Data management and storage" -ForegroundColor Cyan

if ($successRate -ge 80) {
    Write-Host ""
    Write-Host "🎉 ACTIVATION SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================" -ForegroundColor Green
    Write-Host "🚀 All visual development tools are ready!" -ForegroundColor Green
    Write-Host "🎨 Start building amazing visual workflows!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ SOME SERVICES NEED ATTENTION" -ForegroundColor Yellow
    Write-Host "===============================" -ForegroundColor Yellow
    Write-Host "🔧 Check the status above and restart if needed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔧 Quick Commands:" -ForegroundColor White
Write-Host "  Check status: .\smart-server-manager.ps1 -CheckOnly" -ForegroundColor Cyan
Write-Host "  Restart all: scripts/-all-systems.ps1" -ForegroundColor Cyan
Write-Host "  Debug issues: .\advanced-debug-suite.ps1 -All" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Open Flyde Studio at http://localhost:3001" -ForegroundColor Cyan
Write-Host "  2. Open Motia Workbench at http://localhost:3000" -ForegroundColor Cyan
Write-Host "  3. Start building visual workflows!" -ForegroundColor Cyan
Write-Host "  4. Integrate with your existing backend services" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 FINAL ACTIVATION COMPLETE!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
