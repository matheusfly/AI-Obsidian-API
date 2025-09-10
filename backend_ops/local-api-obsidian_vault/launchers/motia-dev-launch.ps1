# ⚡ Motia Development Server Quick Launch Script (PowerShell)
# One-click launch of Motia Development Server with custom configuration

param(
    [int]$Port = 3000,
    [string]$Host = "localhost",
    [string]$Config = "./motia.config.js"
)

Write-Host "⚡ Launching Motia Development Server..." -ForegroundColor Green
Write-Host "📍 Port: $Port" -ForegroundColor Blue
Write-Host "🌐 Host: $Host" -ForegroundColor Blue
Write-Host "⚙️  Config: $Config" -ForegroundColor Blue

# Check if config exists
if (-not (Test-Path $Config)) {
    Write-Host "⚠️  Config file not found, using defaults" -ForegroundColor Yellow
    npx motia dev --port $Port --host $Host --open
} else {
    npx motia dev --config $Config --port $Port --host $Host --open
}
