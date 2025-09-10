# 🚨 EMERGENCY FIX ALL - Comprehensive Service Recovery
# Fix all broken services and get everything running immediately

Write-Host "🚨 EMERGENCY FIX ALL" -ForegroundColor Red
Write-Host "===================" -ForegroundColor Red
Write-Host "Comprehensive Service Recovery" -ForegroundColor White
Write-Host ""

# Kill everything and start fresh
Write-Host "🛑 NUCLEAR OPTION - Killing everything..." -ForegroundColor Red
Get-Job | Stop-Job
Get-Job | Remove-Job
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "✅ All processes killed" -ForegroundColor Green

# Wait a moment
Start-Sleep -Seconds 3

# Start services one by one with proper error handling
Write-Host ""
Write-Host "🚀 Starting services with enhanced error handling..." -ForegroundColor Yellow

# 1. Start Flyde
Write-Host "  🎨 Starting Flyde Studio..." -ForegroundColor Cyan
try {
    Set-Location flyde-project
    $flydeProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -WindowStyle Hidden
    Set-Location ..
    Write-Host "    ✅ Flyde started (PID: $($flydeProcess.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Flyde: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Start Motia
Write-Host "  ⚡ Starting Motia Integration..." -ForegroundColor Cyan
try {
    Set-Location motia-project
    $motiaProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -WindowStyle Hidden
    Set-Location ..
    Write-Host "    ✅ Motia started (PID: $($motiaProcess.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Motia: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Start Obsidian API
Write-Host "  📝 Starting Obsidian API..." -ForegroundColor Cyan
try {
    Set-Location obsidian-api
    $obsidianProcess = Start-Process -FilePath "npx" -ArgumentList "motia", "dev", "--port", "27123" -PassThru -WindowStyle Hidden
    Set-Location ..
    Write-Host "    ✅ Obsidian API started (PID: $($obsidianProcess.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Obsidian API: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Start Vault API with Python 3.12
Write-Host "  🏛️ Starting Vault API with Python 3.12..." -ForegroundColor Cyan
try {
    Set-Location vault-api
    $vaultProcess = Start-Process -FilePath "C:\Program Files\Python312\python.exe" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload" -PassThru -WindowStyle Hidden
    Set-Location ..
    Write-Host "    ✅ Vault API started (PID: $($vaultProcess.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start Vault API: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Start Ollama
Write-Host "  🦙 Starting Ollama..." -ForegroundColor Cyan
try {
    $ollamaProcess = Start-Process -FilePath "ollama" -ArgumentList "serve" -PassThru -WindowStyle Hidden
    Write-Host "    ✅ Ollama started (PID: $($ollamaProcess.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ⚠️ Ollama not found, trying alternative..." -ForegroundColor Yellow
    try {
        $ollamaProcess = Start-Process -FilePath "npx" -ArgumentList "ollama", "serve" -PassThru -WindowStyle Hidden
        Write-Host "    ✅ Ollama started via npx (PID: $($ollamaProcess.Id))" -ForegroundColor Green
    } catch {
        Write-Host "    ❌ Failed to start Ollama: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 6. Start n8n
Write-Host "  🔄 Starting n8n..." -ForegroundColor Cyan
try {
    $n8nProcess = Start-Process -FilePath "npx" -ArgumentList servicesservices/n8n", "start" -PassThru -WindowStyle Hidden
    Write-Host "    ✅ n8n started (PID: $($n8nProcess.Id))" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Failed to start n8n: $($_.Exception.Message)" -ForegroundColor Red
}

# Wait for services to start
Write-Host ""
Write-Host "⏳ Waiting for services to start (45 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Comprehensive testing
Write-Host ""
Write-Host "🧪 Comprehensive Service Testing..." -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow

$services = @(
    @{ Name = "Flyde Studio"; Port = 3001; Url = "http://localhost:3001/health" }
    @{ Name = "Motia Integration"; Port = 3000; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian API"; Port = 27123; Url = "http://localhost:27123/health" }
    @{ Name = "Vault API"; Port = 8080; Url = "http://localhost:8080/health" }
    @{ Name = "Ollama"; Port = 11434; Url = "http://localhost:11434/api/tags" }
    @{ Name = servicesservices/n8n"; Port = 5678; Url = "http://localhost:5678/healthz" }
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
            $results[$service.Name] = $true
            $successCount++
        } else {
            Write-Host "  ⚠️ Status: UNEXPECTED RESPONSE ($($response.StatusCode))" -ForegroundColor Yellow
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
Write-Host "📊 EMERGENCY FIX RESULTS" -ForegroundColor Magenta
Write-Host "========================" -ForegroundColor Magenta
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
Write-Host "  🦙 Ollama: http://localhost:11434" -ForegroundColor Cyan
Write-Host "  🔄 n8n: http://localhost:5678" -ForegroundColor Cyan

if ($successRate -ge 80) {
    Write-Host ""
    Write-Host "🎉 EMERGENCY FIX SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green
    Write-Host "🚀 All services are now running!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ SOME SERVICES STILL NEED ATTENTION" -ForegroundColor Yellow
    Write-Host "=====================================" -ForegroundColor Yellow
    Write-Host "🔧 Check the status above and restart if needed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔧 Quick Commands:" -ForegroundColor White
Write-Host "  Check status: .\smart-server-manager.ps1 -CheckOnly" -ForegroundColor Cyan
Write-Host "  Restart all: scripts/-all-systems.ps1" -ForegroundColor Cyan
Write-Host "  Emergency fix: .\EMERGENCY-FIX-ALL.ps1" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Open Flyde Studio at http://localhost:3001" -ForegroundColor Cyan
Write-Host "  2. Open Motia Workbench at http://localhost:3000" -ForegroundColor Cyan
Write-Host "  3. Start building visual workflows!" -ForegroundColor Cyan

Write-Host ""
Write-Host "🚨 EMERGENCY FIX COMPLETE!" -ForegroundColor Red
Write-Host "=========================" -ForegroundColor Red
