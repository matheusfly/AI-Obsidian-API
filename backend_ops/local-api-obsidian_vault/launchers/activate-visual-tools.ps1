# 🎨 Activate Visual Tools - One-Click Activation
# Quick script to check, start, and activate all visual development tools

Write-Host "🎨 ACTIVATING VISUAL DEVELOPMENT TOOLS" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host ""

# Run the smart server manager with full system activation
.\smart-server-manager.ps1 -FullSystem

Write-Host ""
Write-Host "🎯 VISUAL TOOLS ACTIVATION COMPLETE!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Ready to build amazing visual workflows!" -ForegroundColor Cyan
Write-Host "🎨 Flyde Studio: http://localhost:3001" -ForegroundColor Yellow
Write-Host "⚡ Motia Workbench: http://localhost:3000" -ForegroundColor Yellow
Write-Host "📝 Obsidian API: http://localhost:27123" -ForegroundColor Yellow
