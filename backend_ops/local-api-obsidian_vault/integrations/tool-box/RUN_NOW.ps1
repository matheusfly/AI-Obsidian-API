# 🚀 RUN NOW - Immediate Documentation Scraping
# Quick launcher that works immediately

Write-Host "🚀 RUN NOW - Documentation Scraper" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if we're in the right directory
$CurrentDir = Get-Location
$ExpectedDir = "D:\codex\master_code\backend_ops\local-api-obsidian_vault\tool-box"

if ($CurrentDir.Path -ne $ExpectedDir) {
    Write-Host "📍 Changing to tool-box directory..." -ForegroundColor Yellow
    Set-Location $ExpectedDir
}

Write-Host "📍 Current directory: $(Get-Location)" -ForegroundColor Blue

# Check Python
Write-Host "`n🔧 Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Install requests if needed
Write-Host "`n📥 Installing requests..." -ForegroundColor Yellow
try {
    python -m pip install requests beautifulsoup4 --quiet
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Run the simple scraper
Write-Host "`n🚀 Starting documentation scraping..." -ForegroundColor Yellow
Write-Host "This will scrape all tools: Motia, Flyde, ChartDB, JSON Crack" -ForegroundColor Cyan

try {
    python SIMPLE_SCRAPER.py
    Write-Host "`n🎉 Scraping completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "`n❌ Scraping failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Check the generated JSON file for results" -ForegroundColor White
Write-Host "   2. Run: .\LAUNCH_ALL_TOOLS.ps1 Setup" -ForegroundColor White
Write-Host "   3. Run: .\LAUNCH_ALL_TOOLS.ps1 All" -ForegroundColor White

Write-Host "`n✅ Script completed!" -ForegroundColor Green