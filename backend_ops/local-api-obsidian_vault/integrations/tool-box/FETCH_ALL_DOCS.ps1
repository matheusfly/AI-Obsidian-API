# 🚀 FETCH ALL DOCS - Comprehensive Documentation Fetcher
# Complete context window builder with full pagination coverage

Write-Host "🚀 COMPREHENSIVE DOCUMENTATION FETCHER" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Fetching ALL accessible technical documentation with complete pagination" -ForegroundColor Yellow

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

# Install required dependencies
Write-Host "`n📥 Installing comprehensive dependencies..." -ForegroundColor Yellow
$dependencies = @(
    "requests",
    "aiohttp",
    "beautifulsoup4",
    "lxml",
    "asyncio"
)

foreach ($dep in $dependencies) {
    try {
        Write-Host "   Installing $dep..." -ForegroundColor Cyan
        python -m pip install $dep --quiet
    } catch {
        Write-Host "   ⚠️  Warning: Failed to install $dep" -ForegroundColor Yellow
    }
}

Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Create output directory
Write-Host "`n📁 Creating output directory..." -ForegroundColor Yellow
$outputDir = "comprehensive_docs"
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    Write-Host "✅ Output directory created: $outputDir" -ForegroundColor Green
} else {
    Write-Host "✅ Output directory exists: $outputDir" -ForegroundColor Green
}

# Run the comprehensive fetcher
Write-Host "`n🚀 Starting comprehensive documentation fetching..." -ForegroundColor Yellow
Write-Host "This will fetch ALL documentation from:" -ForegroundColor Cyan
Write-Host "   • Motia: https://www.motia.dev/docs, https://github.com/MotiaDev/motia" -ForegroundColor White
Write-Host "   • Flyde: https://flyde.dev/docs, https://github.com/flydelabs/flyde" -ForegroundColor White
Write-Host "   • ChartDB: https://chartdb.io/, https://docs.chartdb.io/, https://api.chartdb.io/" -ForegroundColor White
Write-Host "   • JSON Crack: https://jsoncrack.com/, https://github.com/AykutSarac/jsoncrack.com" -ForegroundColor White
Write-Host "`nWith complete pagination coverage for maximum context window!" -ForegroundColor Green

try {
    python COMPREHENSIVE_DOCS_FETCHER.py
    Write-Host "`n🎉 Comprehensive documentation fetching completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "`n❌ Fetcher failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check the error and try again." -ForegroundColor Yellow
}

# Show results
Write-Host "`n📊 RESULTS SUMMARY:" -ForegroundColor Cyan
if (Test-Path $outputDir) {
    $files = Get-ChildItem -Path $outputDir -Recurse | Measure-Object
    Write-Host "   Files created: $($files.Count)" -ForegroundColor White
    
    $jsonFiles = Get-ChildItem -Path $outputDir -Filter "*.json" -Recurse | Measure-Object
    Write-Host "   JSON files: $($jsonFiles.Count)" -ForegroundColor White
    
    $mdFiles = Get-ChildItem -Path $outputDir -Filter "*.md" -Recurse | Measure-Object
    Write-Host "   Markdown files: $($mdFiles.Count)" -ForegroundColor White
    
    # Show tool-specific results
    $tools = @("motia", "flyde", "chartdb", "jsoncrack")
    foreach ($tool in $tools) {
        $toolDir = Join-Path $outputDir $tool
        if (Test-Path $toolDir) {
            $toolFiles = Get-ChildItem -Path $toolDir | Measure-Object
            Write-Host "   $tool files: $($toolFiles.Count)" -ForegroundColor White
        }
    }
}

Write-Host "`n💡 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Check the 'comprehensive_docs' folder for all results" -ForegroundColor White
Write-Host "   2. Review the unified_summary.json for overview" -ForegroundColor White
Write-Host "   3. Use the individual tool JSON files for specific documentation" -ForegroundColor White
Write-Host "   4. The markdown files provide human-readable documentation" -ForegroundColor White

Write-Host "`n✅ Comprehensive documentation fetching completed!" -ForegroundColor Green
Write-Host "📁 All results saved to: $outputDir" -ForegroundColor Cyan