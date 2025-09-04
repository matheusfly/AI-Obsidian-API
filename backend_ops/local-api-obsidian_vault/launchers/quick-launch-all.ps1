# 🚀 Quick Launch All Services (PowerShell)
# Launches Flyde, Motia, and backend services

param(
    [switch]$Help
)

# Color definitions
$Colors = @{
    Green = "Green"
    Blue = "Blue"
    Yellow = "Yellow"
    Red = "Red"
    Magenta = "Magenta"
    Cyan = "Cyan"
    White = "White"
}

function Show-Banner {
    Write-Host "🚀 Quick Launch All Services" -ForegroundColor $Colors.Magenta
    Write-Host "============================" -ForegroundColor $Colors.Magenta
    Write-Host "Launching Flyde, Motia, and backend services" -ForegroundColor $Colors.White
    Write-Host ""
}

function Show-Help {
    Write-Host "Usage: .\quick-launch-all.ps1" -ForegroundColor $Colors.Cyan
    Write-Host ""
    Write-Host "This script will:" -ForegroundColor $Colors.White
    Write-Host "  • Start Flyde Studio on port 3001" -ForegroundColor $Colors.Green
    Write-Host "  • Start Motia Dev on port 3000" -ForegroundColor $Colors.Green
    Write-Host "  • Start Obsidian API on port 27123" -ForegroundColor $Colors.Green
    Write-Host "  • Test all services" -ForegroundColor $Colors.Green
    Write-Host ""
}

function Test-Service {
    param([string]$Name, [string]$Url)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $Name`: Healthy" -ForegroundColor $Colors.Green
            return $true
        }
    } catch {
        Write-Host "  ❌ $Name`: Not responding" -ForegroundColor $Colors.Red
        return $false
    }
    return $false
}

function Start-Service {
    param([string]$Name, [string]$Path, [string]$Command)
    
    Write-Host "🚀 Starting $Name..." -ForegroundColor $Colors.Cyan
    
    try {
        Push-Location $Path
        Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$Path'; $Command" -WindowStyle Minimized
        Pop-Location
        Write-Host "  ✅ $Name started" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ❌ Failed to start $Name" -ForegroundColor $Colors.Red
    }
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Show-Banner

Write-Host "🎯 Starting Services..." -ForegroundColor $Colors.Yellow
Write-Host "=====================" -ForegroundColor $Colors.Yellow

# Start services
Start-Service "Flyde Studio" "flyde-project" "npm run dev"
Start-Sleep -Seconds 3

Start-Service "Motia Dev" "motia-project" "npm run dev"
Start-Sleep -Seconds 3

Start-Service "Obsidian API" servicesservices/obsidian-api" "npx motia dev"
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🧪 Testing Services..." -ForegroundColor $Colors.Yellow
Write-Host "=====================" -ForegroundColor $Colors.Yellow

# Test services
$flydeHealthy = Test-Service "Flyde Studio" "http://localhost:3001/health"
$motiaHealthy = Test-Service "Motia Dev" "http://localhost:3000/health"
$obsidianHealthy = Test-Service "Obsidian API" "http://localhost:27123/health"

Write-Host ""
Write-Host "📊 Service Status Summary" -ForegroundColor $Colors.Magenta
Write-Host "=========================" -ForegroundColor $Colors.Magenta

if ($flydeHealthy) {
    Write-Host "🎨 Flyde Studio: http://localhost:3001" -ForegroundColor $Colors.Green
    Write-Host "   • Health: http://localhost:3001/health" -ForegroundColor $Colors.Cyan
    Write-Host "   • Flows: http://localhost:3001/flows" -ForegroundColor $Colors.Cyan
}

if ($motiaHealthy) {
    Write-Host "⚡ Motia Dev: http://localhost:3000" -ForegroundColor $Colors.Green
    Write-Host "   • Health: http://localhost:3000/health" -ForegroundColor $Colors.Cyan
    Write-Host "   • API: http://localhost:3000/api" -ForegroundColor $Colors.Cyan
}

if ($obsidianHealthy) {
    Write-Host "📝 Obsidian API: http://localhost:27123" -ForegroundColor $Colors.Green
    Write-Host "   • Health: http://localhost:27123/health" -ForegroundColor $Colors.Cyan
}

Write-Host ""
Write-Host "🎉 Launch Complete!" -ForegroundColor $Colors.Magenta
Write-Host "===================" -ForegroundColor $Colors.Magenta

if ($flydeHealthy -and $motiaHealthy -and $obsidianHealthy) {
    Write-Host "✅ All services are running successfully!" -ForegroundColor $Colors.Green
} else {
    Write-Host "⚠️  Some services may need additional time to start" -ForegroundColor $Colors.Yellow
    Write-Host "   Run '.\backend-integration-test.ps1 -Integration' to test again" -ForegroundColor $Colors.Cyan
}

Write-Host ""
Write-Host "🔗 Quick Access URLs:" -ForegroundColor $Colors.White
Write-Host "  • Flyde Studio: http://localhost:3001" -ForegroundColor $Colors.Cyan
Write-Host "  • Motia Dev: http://localhost:3000" -ForegroundColor $Colors.Cyan
Write-Host "  • Obsidian API: http://localhost:27123" -ForegroundColor $Colors.Cyan
