# 🚀 Master Launch Script for Flyde & Motia (PowerShell)
# One-click launch for both visual programming tools

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("flyde", "motia", "both")]
    [string]$Tool,
    
    [int]$FlydePort = 3001,
    [int]$MotiaPort = 3000,
    [string]$Host = "localhost"
)

function Show-Banner {
    Write-Host "🚀 Flyde & Motia Master Launcher" -ForegroundColor Magenta
    Write-Host "=================================" -ForegroundColor Magenta
    Write-Host ""
}

function Launch-Flyde {
    Write-Host "🎨 Launching Flyde Studio..." -ForegroundColor Green
    Write-Host "📍 Port: $FlydePort" -ForegroundColor Blue
    Write-Host "🌐 Host: $Host" -ForegroundColor Blue
    
    # Check if flyde.config.js exists
    if (Test-Path "./flyde.config.js") {
        Write-Host "⚙️  Using flyde.config.js" -ForegroundColor Blue
        npx flyde studio --config ./flyde.config.js --port $FlydePort --host $Host --open
    } else {
        Write-Host "⚠️  No config found, using defaults" -ForegroundColor Yellow
        npx flyde studio --port $FlydePort --host $Host --open
    }
}

function Launch-Motia {
    Write-Host "⚡ Launching Motia Development Server..." -ForegroundColor Green
    Write-Host "📍 Port: $MotiaPort" -ForegroundColor Blue
    Write-Host "🌐 Host: $Host" -ForegroundColor Blue
    
    # Check if motia.config.js exists
    if (Test-Path "./motia.config.js") {
        Write-Host "⚙️  Using motia.config.js" -ForegroundColor Blue
        npx motia dev --config ./motia.config.js --port $MotiaPort --host $Host --open
    } else {
        Write-Host "⚠️  No config found, using defaults" -ForegroundColor Yellow
        npx motia dev --port $MotiaPort --host $Host --open
    }
}

function Launch-Both {
    Write-Host "🚀 Launching Both Tools..." -ForegroundColor Magenta
    Write-Host ""
    
    # Launch Motia in background
    Write-Host "⚡ Starting Motia on port $MotiaPort..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-Command", "npx motia dev --port $MotiaPort --host $Host" -WindowStyle Minimized
    
    # Wait a moment
    Start-Sleep -Seconds 3
    
    # Launch Flyde in foreground
    Write-Host "🎨 Starting Flyde on port $FlydePort..." -ForegroundColor Green
    Launch-Flyde
}

# Main execution
Show-Banner

switch ($Tool) {
    "flyde" { Launch-Flyde }
    "motia" { Launch-Motia }
    "both" { Launch-Both }
}

Write-Host ""
Write-Host "🎯 Quick Commands:" -ForegroundColor Yellow
Write-Host "  .\launch-tools.ps1 -Tool flyde    # Launch Flyde Studio" -ForegroundColor Cyan
Write-Host "  .\launch-tools.ps1 -Tool motia    # Launch Motia Dev Server" -ForegroundColor Cyan
Write-Host "  .\launch-tools.ps1 -Tool both     # Launch Both Tools" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Custom Ports:" -ForegroundColor Yellow
Write-Host "  .\launch-tools.ps1 -Tool flyde -FlydePort 3002" -ForegroundColor Cyan
Write-Host "  .\launch-tools.ps1 -Tool motia -MotiaPort 3001" -ForegroundColor Cyan
