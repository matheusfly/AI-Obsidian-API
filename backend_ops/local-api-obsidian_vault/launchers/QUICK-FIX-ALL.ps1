# 🚀 QUICK FIX ALL - Simple Direct Fix
# Get all critical servers running for plugin functionality

Write-Host "🚀 QUICK FIX ALL" -ForegroundColor Green
Write-Host "================" -ForegroundColor Green
Write-Host ""

# Kill everything
Write-Host "🛑 Killing everything..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait
Start-Sleep -Seconds 3

# Start all services
Write-Host "🚀 Starting all services..." -ForegroundColor Yellow

# Flyde
Write-Host "  🎨 Starting Flyde..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd flyde-project && npm run dev" -WindowStyle Hidden

# Motia
Write-Host "  ⚡ Starting Motia..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd motia-project && npm run dev" -WindowStyle Hidden

# Obsidian API
Write-Host "  📝 Starting Obsidian API..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd obsidian-api && npx motia dev --port 27123" -WindowStyle Hidden

# Vault API
Write-Host "  🏛️ Starting Vault API..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd vault-api && C:\Program Files\Python312\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload" -WindowStyle Hidden

# Wait
Write-Host ""
Write-Host "⏳ Waiting 60 seconds for all services..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Test all services
Write-Host ""
Write-Host "🧪 Testing all services..." -ForegroundColor Yellow

$services = @(
    @{ Name = "Flyde Studio"; Url = "http://localhost:3001/health" }
    @{ Name = "Motia Workbench"; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian API"; Url = "http://localhost:27123/health" }
    @{ Name = "Vault API"; Url = "http://localhost:8080/health" }
)

$running = 0
$total = $services.Count

foreach ($service in $services) {
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $($service.Name): HEALTHY" -ForegroundColor Green
            $running++
        } else {
            Write-Host "  ❌ $($service.Name): ERROR $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ $($service.Name): NOT RESPONDING" -ForegroundColor Red
    }
}

# Results
Write-Host ""
Write-Host "📊 RESULTS: $running/$total services running" -ForegroundColor $(if($running -eq $total) {"Green"} else {"Yellow"})

if ($running -eq $total) {
    Write-Host ""
    Write-Host "🎉 ALL SERVERS RUNNING!" -ForegroundColor Green
    Write-Host "======================" -ForegroundColor Green
    Write-Host "🚀 Plugins can now work properly!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ SOME SERVERS NOT RUNNING!" -ForegroundColor Red
    Write-Host "============================" -ForegroundColor Red
    Write-Host "🔧 Plugins may not work properly!" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔗 Test these URLs:" -ForegroundColor White
Write-Host "  🎨 Flyde: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault: http://localhost:8080" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 QUICK FIX ALL COMPLETE!" -ForegroundColor Green
