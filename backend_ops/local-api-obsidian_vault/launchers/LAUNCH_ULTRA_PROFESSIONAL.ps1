# LAUNCH_ULTRA_PROFESSIONAL.ps1
# Ultra Professional MCP Visualization System Launcher

Write-Host "🚀 LAUNCHING ULTRA PROFESSIONAL MCP VISUALIZATION SYSTEM..." -ForegroundColor Cyan
Write-Host "📊 Corporate-grade visualization with comprehensive MCP data crawling..." -ForegroundColor Yellow

# Define the docker-compose file
$composeFile = "docker-compose.jsoncrack-fixed.yml"

# Stop existing services to ensure a clean start
Write-Host "`n🔄 Stopping existing services..." -ForegroundColor Yellow
docker-compose -f $composeFile down --remove-orphans

# Start services in detached mode
Write-Host "🚀 Starting ultra professional services..." -ForegroundColor Green
docker-compose -f $composeFile up -d --build vault-api-visual

Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check service status
Write-Host "`n🔍 Checking ultra professional service status..." -ForegroundColor Cyan
$vaultApiStatus = (docker-compose -f $composeFile ps -q vault-api-visual | ForEach-Object { docker inspect --format '{{.State.Health.Status}}' $_ })
$jsonViewerStatus = (docker-compose -f $composeFile ps -q json-viewer | ForEach-Object { docker inspect --format '{{.State.Health.Status}}' $_ })
$jsonCrackStatus = (docker-compose -f $composeFile ps -q jsoncrack | ForEach-Object { docker inspect --format '{{.State.Health.Status}}' $_ })

if ($vaultApiStatus -eq "healthy") {
    Write-Host "  ✅ Vault API (Ultra Professional) is running" -ForegroundColor Green
} else {
    Write-Host "  ❌ Vault API is not healthy (Status: $vaultApiStatus)" -ForegroundColor Red
}
if ($jsonViewerStatus -eq "healthy") {
    Write-Host "  ✅ JSON Viewer is running" -ForegroundColor Green
} else {
    Write-Host "  ❌ JSON Viewer is not healthy (Status: $jsonViewerStatus)" -ForegroundColor Red
}
if ($jsonCrackStatus -eq "healthy") {
    Write-Host "  ✅ JSON Crack is running" -ForegroundColor Green
} else {
    Write-Host "  ❌ JSON Crack is not healthy (Status: $jsonCrackStatus)" -ForegroundColor Red
}

# Define URLs
$ULTRA_PROFESSIONAL_URL = "http://localhost:8081/ultra/professional-dashboard"
$MCP_CRAWLER_URL = "http://localhost:8081/ultra/mcp-crawler"
$COMPREHENSIVE_DATA_URL = "http://localhost:8081/ultra/comprehensive-data"
$ENHANCED_DASHBOARD_URL = "http://localhost:8081/enhanced/dashboard"
$SYSTEM_OVERVIEW_URL = "http://localhost:8081/system/overview"
$VAULT_API_URL = "http://localhost:8081"
$API_DOCS_URL = "http://localhost:8081/docs"

Write-Host "`n🎨 ULTRA PROFESSIONAL VISUALIZATION ACCESS POINTS:" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 Ultra Professional Dashboard:  $ULTRA_PROFESSIONAL_URL" -ForegroundColor White
Write-Host "🔍 MCP Data Crawler:              $MCP_CRAWLER_URL" -ForegroundColor White
Write-Host "📊 Comprehensive Data:            $COMPREHENSIVE_DATA_URL" -ForegroundColor White
Write-Host "🎨 Enhanced Dashboard:            $ENHANCED_DASHBOARD_URL" -ForegroundColor White
Write-Host "📊 System Overview:               $SYSTEM_OVERVIEW_URL" -ForegroundColor White
Write-Host "🔗 Vault API:                     $VAULT_API_URL" -ForegroundColor White
Write-Host "📚 API Documentation:             $API_DOCS_URL" -ForegroundColor White

Write-Host "`n🎨 ULTRA PROFESSIONAL FEATURES:" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "✨ 4 Professional Color Palettes (Corporate Blue, Modern Dark, Premium Gold, Tech Cyber)" -ForegroundColor White
Write-Host "🎨 Multiple Layout Options (Grid, Masonry, Timeline, Hierarchy)" -ForegroundColor White
Write-Host "📱 Fully Responsive Design for All Devices" -ForegroundColor White
Write-Host "🔄 Real-time Data Updates and Auto-refresh" -ForegroundColor White
Write-Host "📊 Comprehensive MCP Data Crawling and Presentation" -ForegroundColor White
Write-Host "🎯 Interactive Components with Smooth Animations" -ForegroundColor White
Write-Host "📈 Professional Performance Metrics and Statistics" -ForegroundColor White

Write-Host "`n🎨 ULTRA PROFESSIONAL API ENDPOINTS:" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "🚀 /ultra/professional-dashboard  - Ultra Professional Dashboard with themes" -ForegroundColor White
Write-Host "🔍 /ultra/mcp-crawler            - Comprehensive MCP data crawling" -ForegroundColor White
Write-Host "📊 /ultra/comprehensive-data     - Complete system data for presentation" -ForegroundColor White
Write-Host "🎨 /enhanced/dashboard           - Enhanced visualization dashboard" -ForegroundColor White
Write-Host "📊 /system/overview              - System overview dashboard" -ForegroundColor White

Write-Host "`n🎨 PROFESSIONAL THEMES AVAILABLE:" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "💼 Corporate Blue:  ?theme=corporate_blue" -ForegroundColor White
Write-Host "🌙 Modern Dark:     ?theme=modern_dark" -ForegroundColor White
Write-Host "👑 Premium Gold:    ?theme=premium_gold" -ForegroundColor White
Write-Host "🤖 Tech Cyber:      ?theme=tech_cyber" -ForegroundColor White

Write-Host "`n🎨 QUICK ACTIONS:" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Write-Host "🚀 Opening Ultra Professional Dashboard..." -ForegroundColor Green
Start-Process $ULTRA_PROFESSIONAL_URL

Write-Host "`n🎉 ULTRA PROFESSIONAL SYSTEM LAUNCHED!" -ForegroundColor Green
Write-Host "✨ Your corporate-grade, professional visualization system is ready!" -ForegroundColor Cyan
Write-Host "🎨 Experience the most beautiful and comprehensive MCP visualization!" -ForegroundColor Yellow

Write-Host "`n💡 PRO TIPS:" -ForegroundColor Yellow
Write-Host "=============" -ForegroundColor Yellow
Write-Host "• Use different themes for different presentations" -ForegroundColor White
Write-Host "• The MCP crawler fetches comprehensive protocol data" -ForegroundColor White
Write-Host "• All data updates in real-time with professional metrics" -ForegroundColor White
Write-Host "• Export capabilities for professional reports" -ForegroundColor White

