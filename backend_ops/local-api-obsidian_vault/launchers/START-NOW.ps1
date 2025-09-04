# 🚀 START NOW - Simple Direct Fix
# Start services directly and test them

Write-Host "🚀 START NOW" -ForegroundColor Green
Write-Host "============" -ForegroundColor Green
Write-Host ""

# Kill everything first
Write-Host "🛑 Killing everything..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force

# Start Flyde
Write-Host "🎨 Starting Flyde..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd flyde-project && npm run dev" -WindowStyle Hidden

# Start Motia  
Write-Host "⚡ Starting Motia..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd motia-project && npm run dev" -WindowStyle Hidden

# Start Obsidian API
Write-Host "📝 Starting Obsidian API..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd obsidian-api && npx motia dev --port 27123" -WindowStyle Hidden

# Start Vault API
Write-Host "🏛️ Starting Vault API..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd vault-api && C:\Program Files\Python312\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload" -WindowStyle Hidden

Write-Host ""
Write-Host "⏳ Waiting 20 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "🧪 Testing services..." -ForegroundColor Yellow

# Test each service
$services = @(
    @{ Name = "Flyde"; Url = "http://localhost:3001/health" }
    @{ Name = "Motia"; Url = "http://localhost:3000/health" }
    @{ Name = "Obsidian API"; Url = "http://localhost:27123/health" }
    @{ Name = "Vault API"; Url = "http://localhost:8080/health" }
)

foreach ($service in $services) {
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
        Write-Host "  ✅ $($service.Name): HEALTHY ($($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $($service.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 START NOW COMPLETE!" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Test these URLs:" -ForegroundColor White
Write-Host "  🎨 Flyde: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  ⚡ Motia: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📝 Obsidian: http://localhost:27123" -ForegroundColor Cyan
Write-Host "  🏛️ Vault: http://localhost:8080" -ForegroundColor Cyan