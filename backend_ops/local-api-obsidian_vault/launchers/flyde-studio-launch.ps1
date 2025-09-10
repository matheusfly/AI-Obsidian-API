# 🎨 Flyde Studio Quick Launch Script (PowerShell)
# One-click launch of Flyde Studio with custom configuration

param(
    [int]$Port = 3001,
    [string]$Host = "localhost",
    [string]$Config = "./flyde.config.js"
)

Write-Host "🎨 Launching Flyde Studio..." -ForegroundColor Green
Write-Host "📍 Port: $Port" -ForegroundColor Blue
Write-Host "🌐 Host: $Host" -ForegroundColor Blue
Write-Host "⚙️  Config: $Config" -ForegroundColor Blue

# Check if config exists
if (-not (Test-Path $Config)) {
    Write-Host "⚠️  Config file not found, using defaults" -ForegroundColor Yellow
    npx flyde studio --port $Port --host $Host --open
} else {
    npx flyde studio --config $Config --port $Port --host $Host --open
}
