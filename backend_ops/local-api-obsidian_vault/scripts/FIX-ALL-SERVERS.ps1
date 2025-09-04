# 🔧 FIX ALL SERVERS - Complete Server Recovery
# Fix all servers to ensure plugins work properly

Write-Host "🔧 FIX ALL SERVERS" -ForegroundColor Red
Write-Host "=================" -ForegroundColor Red
Write-Host "Complete Server Recovery for Plugin Functionality" -ForegroundColor White
Write-Host ""

# Kill everything completely
Write-Host "🛑 NUCLEAR OPTION - Killing everything..." -ForegroundColor Red
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "cmd" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "npm" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "npx" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "✅ All processes killed" -ForegroundColor Green

# Wait for complete cleanup
Start-Sleep -Seconds 5

# Start services with proper error handling and monitoring
Write-Host ""
Write-Host "🚀 Starting ALL services with enhanced monitoring..." -ForegroundColor Yellow

# 1. Start Flyde Studio
Write-Host "  🎨 Starting Flyde Studio..." -ForegroundColor Cyan
try {
    $flydeJob = Start-Job -ScriptBlock {
        Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\flyde-project"
        npm run dev
    } -Name "FlydeStudio"
    Write-Host "    ✅ Flyde Studio started (Job ID: $($flydeJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Flyde Studio failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Start Motia Workbench
Write-Host "  ⚡ Starting Motia Workbench..." -ForegroundColor Cyan
try {
    $motiaJob = Start-Job -ScriptBlock {
        Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\motia-project"
        npm run dev
    } -Name "MotiaWorkbench"
    Write-Host "    ✅ Motia Workbench started (Job ID: $($motiaJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Motia Workbench failed: $($_.Exception.Message)" -ForegroundColor Red
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
    Write-Host "    ❌ Obsidian API failed: $($_.Exception.Message)" -ForegroundColor Red
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
    Write-Host "    ❌ Vault API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Start Ollama (if available)
Write-Host "  🦙 Starting Ollama..." -ForegroundColor Cyan
try {
    $ollamaJob = Start-Job -ScriptBlock {
        ollama serve
    } -Name "Ollama"
    Write-Host "    ✅ Ollama started (Job ID: $($ollamaJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️ Ollama not available: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 6. Start n8n (if available)
Write-Host "  🔄 Starting n8n..." -ForegroundColor Cyan
try {
    $n8nJob = Start-Job -ScriptBlock {
        npx n8n start
    } -Name servicesservices/n8n"
    Write-Host "    ✅ n8n started (Job ID: $($n8nJob.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️ n8n not available: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Wait for services to start
Write-Host ""
Write-Host "⏳ Waiting for ALL services to start (90 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

# Comprehensive testing with retries
Write-Host ""
Write-Host "🧪 Comprehensive Service Testing with Retries..." -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Yellow

$services = @(
    @{ Name = "Flyde Studio"; Port = 3001; Url = "http://localhost:3001/health"; Critical = $true }
    @{ Name = "Motia Workbench"; Port = 3000; Url = "http://localhost:3000/health"; Critical = $true }
    @{ Name = "Obsidian API"; Port = 27123; Url = "http://localhost:27123/health"; Critical = $true }
    @{ Name = "Vault API"; Port = 8080; Url = "http://localhost:8080/health"; Critical = $true }
    @{ Name = "Ollama"; Port = 11434; Url = "http://localhost:11434/api/tags"; Critical = $false }
    @{ Name = servicesservices/n8n"; Port = 5678; Url = "http://localhost:5678/healthz"; Critical = $false }
)

$results = @{}
$successCount = 0
$criticalSuccessCount = 0

foreach ($service in $services) {
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    Write-Host "  Port: $($service.Port)" -ForegroundColor White
    Write-Host "  Critical: $($service.Critical)" -ForegroundColor $(if($service.Critical) {"Red"} else {"Yellow"})
    
    $maxRetries = 3
    $retryCount = 0
    $success = $false
    
    while ($retryCount -lt $maxRetries -and -not $success) {
        $retryCount++
        Write-Host "  Attempt $retryCount/$maxRetries..." -ForegroundColor White
        
        try {
            $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✅ Status: HEALTHY" -ForegroundColor Green
                Write-Host "  📊 Response: $($response.StatusCode)" -ForegroundColor Green
                $results[$service.Name] = $true
                $success = $true
                $successCount++
                if ($service.Critical) { $criticalSuccessCount++ }
            } else {
                Write-Host "  ⚠️ Status: UNEXPECTED RESPONSE ($($response.StatusCode))" -ForegroundColor Yellow
                if ($retryCount -eq $maxRetries) {
                    $results[$service.Name] = $false
                }
            }
        } catch {
            Write-Host "  ❌ Status: NOT RESPONDING" -ForegroundColor Red
            Write-Host "  🔍 Error: $($_.Exception.Message)" -ForegroundColor Red
            if ($retryCount -eq $maxRetries) {
                $results[$service.Name] = $false
            } else {
                Write-Host "  ⏳ Retrying in 5 seconds..." -ForegroundColor Yellow
                Start-Sleep -Seconds 5
            }
        }
    }
}

# Calculate success rates
$totalServices = $services.Count
$criticalServices = ($services | Where-Object { $_.Critical }).Count
$successRate = [Math]::Round(($successCount / $totalServices) * 100, 1)
$criticalSuccessRate = [Math]::Round(($criticalSuccessCount / $criticalServices) * 100, 1)

# Final status report
Write-Host ""
Write-Host "📊 COMPREHENSIVE SERVER STATUS REPORT" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "🎯 Overall Status:" -ForegroundColor White
Write-Host "  Total Services: $totalServices" -ForegroundColor White
Write-Host "  Running: $successCount/$totalServices" -ForegroundColor White
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if($successRate -ge 80) {"Green"} else {"Yellow"})
Write-Host ""
Write-Host "  Critical Services: $criticalServices" -ForegroundColor White
Write-Host "  Critical Running: $criticalSuccessCount/$criticalServices" -ForegroundColor White
Write-Host "  Critical Success Rate: $criticalSuccessRate%" -ForegroundColor $(if($criticalSuccessRate -ge 100) {"Green"} else {"Red"})

Write-Host ""
Write-Host "🔍 Service Details:" -ForegroundColor White
foreach ($result in $results.GetEnumerator()) {
    $status = if ($result.Value) { "✅ RUNNING" } else { "❌ NOT RUNNING" }
    $color = if ($result.Value) { "Green" } else { "Red" }
    $service = $services | Where-Object { $_.Name -eq $result.Key }
    $critical = if ($service.Critical) { " (CRITICAL)" } else { " (OPTIONAL)" }
    Write-Host "  $($result.Key)${critical}: $status" -ForegroundColor $color
}

Write-Host ""
Write-Host "🔗 Quick Access Links:" -ForegroundColor White
Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault API: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  🦙 Ollama: http://localhost:11434" -ForegroundColor Cyan
Write-Host "  🔄 n8n: http://localhost:5678" -ForegroundColor Cyan

if ($criticalSuccessRate -eq 100) {
    Write-Host ""
    Write-Host "🎉 ALL CRITICAL SERVERS RUNNING!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host "🚀 Plugins can now work properly!" -ForegroundColor Green
    Write-Host "🎨 Start building visual workflows!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ CRITICAL SERVERS NOT RUNNING!" -ForegroundColor Red
    Write-Host "=================================" -ForegroundColor Red
    Write-Host "🔧 Plugins cannot work without all critical servers!" -ForegroundColor Red
    Write-Host "🔄 Run this script again to fix the issues." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Open Flyde Studio at http://localhost:3001" -ForegroundColor Cyan
Write-Host "  2. Open Motia Workbench at http://localhost:3000" -ForegroundColor Cyan
Write-Host "  3. Test plugin functionality!" -ForegroundColor Cyan

Write-Host ""
Write-Host "🔧 FIX ALL SERVERS COMPLETE!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
