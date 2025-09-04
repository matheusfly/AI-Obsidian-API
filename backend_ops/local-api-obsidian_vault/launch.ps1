# 🚀 Master Launcher - Professional Repository Structure
# This launcher provides easy access to all scripts in the reorganized structure

param(
    [Parameter(Mandatory=$true)]
    [string]$Script,
    [string]$Category = "launchers"
)

$scriptPath = Join-Path $Category $Script

if (Test-Path $scriptPath) {
    Write-Host "🚀 Launching: $scriptPath" -ForegroundColor Green
    & $scriptPath @args
} else {
    Write-Host "❌ Script not found: $scriptPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available categories:" -ForegroundColor Yellow
    Write-Host "  📁 launchers  - Main launcher scripts" -ForegroundColor White
    Write-Host "  🔧 scripts    - Utility and setup scripts" -ForegroundColor White
    Write-Host "  🚀 services   - Service implementations" -ForegroundColor White
    Write-Host "  🧪 tests      - Test scripts" -ForegroundColor White
    Write-Host "  📊 monitoring - Monitoring scripts" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage examples:" -ForegroundColor Cyan
    Write-Host "  .\launch.ps1 -Script LAUNCH_ALL.ps1" -ForegroundColor White
    Write-Host "  .\launch.ps1 -Script setup-mcp-tools.ps1 -Category scripts" -ForegroundColor White
    Write-Host "  .\launch.ps1 -Script test-all-services.ps1 -Category tests" -ForegroundColor White
}