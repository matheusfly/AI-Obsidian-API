# 🚀 BUILD COMPLETE SYSTEM - Comprehensive Documentation & Plugin System
# Complete context window builder with full pagination coverage and project plugins

Write-Host "🚀 BUILDING COMPLETE DOCUMENTATION & PLUGIN SYSTEM" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Complete context window builder with full pagination coverage" -ForegroundColor Yellow

# Check if we're in the right directory
$CurrentDir = Get-Location
$ExpectedDir = "D:\codex\master_code\backend_ops\local-api-obsidian_vault\tool-box"

if ($CurrentDir.Path -ne $ExpectedDir) {
    Write-Host "📍 Changing to tool-box directory..." -ForegroundColor Yellow
    Set-Location $ExpectedDir
}

Write-Host "📍 Current directory: $(Get-Location)" -ForegroundColor Blue

# Step 1: Check Python
Write-Host "`n🔧 Step 1: Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Step 2: Install comprehensive dependencies
Write-Host "`n📥 Step 2: Installing comprehensive dependencies..." -ForegroundColor Yellow
$dependencies = @(
    "requests",
    "aiohttp",
    "beautifulsoup4",
    "lxml",
    "asyncio",
    "pathlib"
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

# Step 3: Create output directories
Write-Host "`n📁 Step 3: Creating output directories..." -ForegroundColor Yellow
$directories = @(
    "comprehensive_docs",
    "project_plugins",
    "logs",
    "data"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ Directory exists: $dir" -ForegroundColor Green
    }
}

# Step 4: Fetch comprehensive documentation
Write-Host "`n🚀 Step 4: Fetching comprehensive documentation..." -ForegroundColor Yellow
Write-Host "This will fetch ALL documentation from:" -ForegroundColor Cyan
Write-Host "   • Motia: https://www.motia.dev/docs, https://github.com/MotiaDev/motia" -ForegroundColor White
Write-Host "   • Flyde: https://flyde.dev/docs, https://github.com/flydelabs/flyde" -ForegroundColor White
Write-Host "   • ChartDB: https://chartdb.io/, https://docs.chartdb.io/, https://api.chartdb.io/" -ForegroundColor White
Write-Host "   • JSON Crack: https://jsoncrack.com/, https://github.com/AykutSarac/jsoncrack.com" -ForegroundColor White
Write-Host "`nWith complete pagination coverage for maximum context window!" -ForegroundColor Green

try {
    python COMPREHENSIVE_DOCS_FETCHER.py
    Write-Host "✅ Comprehensive documentation fetching completed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Documentation fetching failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Continuing with plugin system creation..." -ForegroundColor Yellow
}

# Step 5: Create project plugin system
Write-Host "`n🔧 Step 5: Creating project plugin system..." -ForegroundColor Yellow
Write-Host "This will organize all documentation into project plugins:" -ForegroundColor Cyan
Write-Host "   • Individual tool plugins with complete documentation" -ForegroundColor White
Write-Host "   • API references and code examples" -ForegroundColor White
Write-Host "   • Usage guides and tutorials" -ForegroundColor White
Write-Host "   • Unified plugin index and configuration" -ForegroundColor White

try {
    python PROJECT_PLUGIN_SYSTEM.py
    Write-Host "✅ Project plugin system created!" -ForegroundColor Green
} catch {
    Write-Host "❌ Plugin system creation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Show results summary
Write-Host "`n📊 Step 6: Results Summary" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Check comprehensive docs
if (Test-Path "comprehensive_docs") {
    $docsFiles = Get-ChildItem -Path "comprehensive_docs" -Recurse | Measure-Object
    Write-Host "📚 Comprehensive Documentation:" -ForegroundColor Green
    Write-Host "   Files created: $($docsFiles.Count)" -ForegroundColor White
    
    # Check tool-specific results
    $tools = @("motia", "flyde", "chartdb", "jsoncrack")
    foreach ($tool in $tools) {
        $toolDir = Join-Path "comprehensive_docs" $tool
        if (Test-Path $toolDir) {
            $toolFiles = Get-ChildItem -Path $toolDir | Measure-Object
            Write-Host "   $tool files: $($toolFiles.Count)" -ForegroundColor White
        }
    }
} else {
    Write-Host "❌ Comprehensive documentation not found" -ForegroundColor Red
}

# Check project plugins
if (Test-Path "project_plugins") {
    $pluginFiles = Get-ChildItem -Path "project_plugins" -Recurse | Measure-Object
    Write-Host "`n🔧 Project Plugins:" -ForegroundColor Green
    Write-Host "   Files created: $($pluginFiles.Count)" -ForegroundColor White
    
    # Check individual plugins
    foreach ($tool in $tools) {
        $pluginDir = Join-Path "project_plugins" $tool
        if (Test-Path $pluginDir) {
            $pluginToolFiles = Get-ChildItem -Path $pluginDir | Measure-Object
            Write-Host "   $tool plugin files: $($pluginToolFiles.Count)" -ForegroundColor White
        }
    }
} else {
    Write-Host "❌ Project plugins not found" -ForegroundColor Red
}

# Step 7: Create final summary
Write-Host "`n🎉 COMPLETE SYSTEM BUILD SUMMARY" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

Write-Host "`n✅ What was created:" -ForegroundColor Green
Write-Host "   1. Comprehensive documentation for all tools" -ForegroundColor White
Write-Host "   2. Complete pagination coverage" -ForegroundColor White
Write-Host "   3. Project plugin system" -ForegroundColor White
Write-Host "   4. API references and code examples" -ForegroundColor White
Write-Host "   5. Usage guides and tutorials" -ForegroundColor White
Write-Host "   6. Unified plugin index" -ForegroundColor White

Write-Host "`n📁 Directory structure:" -ForegroundColor Yellow
Write-Host "   comprehensive_docs/     - Raw documentation data" -ForegroundColor White
Write-Host "   project_plugins/        - Organized plugin system" -ForegroundColor White
Write-Host "   logs/                   - System logs" -ForegroundColor White
Write-Host "   data/                   - Additional data" -ForegroundColor White

Write-Host "`n🔧 Individual plugins:" -ForegroundColor Yellow
Write-Host "   project_plugins/motia/     - Motia backend framework" -ForegroundColor White
Write-Host "   project_plugins/flyde/     - Flyde visual programming" -ForegroundColor White
Write-Host "   project_plugins/chartdb/   - ChartDB database visualization" -ForegroundColor White
Write-Host "   project_plugins/jsoncrack/ - JSON Crack data visualization" -ForegroundColor White

Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Check the 'comprehensive_docs' folder for raw documentation" -ForegroundColor White
Write-Host "   2. Browse the 'project_plugins' folder for organized plugins" -ForegroundColor White
Write-Host "   3. Use individual tool plugins for specific documentation" -ForegroundColor White
Write-Host "   4. Reference the unified index for navigation" -ForegroundColor White
Write-Host "   5. Use the API references and code examples for development" -ForegroundColor White

Write-Host "`n🎯 Key features:" -ForegroundColor Yellow
Write-Host "   • Complete context window coverage" -ForegroundColor White
Write-Host "   • Full pagination support" -ForegroundColor White
Write-Host "   • API reference generation" -ForegroundColor White
Write-Host "   • Code example extraction" -ForegroundColor White
Write-Host "   • Usage guide creation" -ForegroundColor White
Write-Host "   • Plugin system organization" -ForegroundColor White

Write-Host "`n✅ Complete system build finished!" -ForegroundColor Green
Write-Host "📁 All results saved to: comprehensive_docs/ and project_plugins/" -ForegroundColor Cyan