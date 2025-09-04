# 🚨 EMERGENCY FIX NOW
# Quick fix to get everything running

Write-Host "🚨 EMERGENCY FIX NOW" -ForegroundColor Red
Write-Host "===================" -ForegroundColor Red
Write-Host ""

# Kill everything
Write-Host "🛑 Killing all processes..." -ForegroundColor Red
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "cmd" -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait
Start-Sleep -Seconds 3

# Start all services
Write-Host "🚀 Starting all services..." -ForegroundColor Green

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
Write-Host "⏳ Waiting 45 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# Quick test
Write-Host ""
Write-Host "🧪 Quick test..." -ForegroundColor Yellow

$services = @(
    @{ Name = "Flyde"; Url = "http://localhost:3001/health" }
    @{ Name = "Motia"; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian"; Url = "http://localhost:27123/health" }
    @{ Name = "Vault"; Url = "http://localhost:8080/health" }
)

$running = 0
foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
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

Write-Host ""
Write-Host "📊 RESULTS: $running/4 services running" -ForegroundColor $(if($running -ge 3) {"Green"} else {"Yellow"})

Write-Host ""
Write-Host "🔗 Test these URLs:" -ForegroundColor White
Write-Host "  🎨 Flyde: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault: http://localhost:8080" -ForegroundColor Cyan

if ($running -ge 3) {
    Write-Host ""
    Write-Host "🎉 EMERGENCY FIX SUCCESS!" -ForegroundColor Green
    Write-Host "🚀 Services are running!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ Some services still not running" -ForegroundColor Red
    Write-Host "🔧 Try running this script again" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 EMERGENCY FIX COMPLETE!" -ForegroundColor Green
