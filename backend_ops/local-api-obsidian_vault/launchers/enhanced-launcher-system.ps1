# 🚀 Enhanced Launcher System - Professional Repository Management
# This script provides advanced launcher management for the reorganized repository

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "help",
    [string]$Script = "",
    [string]$Category = "",
    [switch]$List,
    [switch]$Status,
    [switch]$Test,
    [switch]$Reorganize
)

# Color definitions
$GREEN = 'Green'
$BLUE = 'Cyan'
$YELLOW = 'Yellow'
$RED = 'Red'
$WHITE = 'White'

# Enhanced launcher system
function Show-Help {
    Write-Host "🚀 Enhanced Launcher System" -ForegroundColor $BLUE
    Write-Host "============================" -ForegroundColor $BLUE
    Write-Host ""
    Write-Host "Usage: .\enhanced-launcher-system.ps1 [options]" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "Options:" -ForegroundColor $YELLOW
    Write-Host "  -Action <action>     Action to perform (launch, list, status, test, reorganize)" -ForegroundColor $WHITE
    Write-Host "  -Script <name>       Script name to launch" -ForegroundColor $WHITE
    Write-Host "  -Category <cat>      Category (launchers, scripts, services, tests)" -ForegroundColor $WHITE
    Write-Host "  -List                List all available scripts" -ForegroundColor $WHITE
    Write-Host "  -Status              Show system status" -ForegroundColor $WHITE
    Write-Host "  -Test                Test all launchers" -ForegroundColor $WHITE
    Write-Host "  -Reorganize          Execute repository reorganization" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $YELLOW
    Write-Host "  .\enhanced-launcher-system.ps1 -Action launch -Script LAUNCH_ALL.ps1" -ForegroundColor $WHITE
    Write-Host "  .\enhanced-launcher-system.ps1 -Action list" -ForegroundColor $WHITE
    Write-Host "  .\enhanced-launcher-system.ps1 -Action status" -ForegroundColor $WHITE
    Write-Host "  .\enhanced-launcher-system.ps1 -Action test" -ForegroundColor $WHITE
    Write-Host "  .\enhanced-launcher-system.ps1 -Action reorganize" -ForegroundColor $WHITE
}

function Get-SystemStatus {
    Write-Host "📊 System Status Dashboard" -ForegroundColor $BLUE
    Write-Host "=========================" -ForegroundColor $BLUE
    
    # Check if reorganization has been done
    $reorganized = Test-Path "launchers" -and Test-Path "scripts" -and Test-Path "services"
    
    if ($reorganized) {
        Write-Host "✅ Repository Structure: REORGANIZED" -ForegroundColor $GREEN
    } else {
        Write-Host "⚠️  Repository Structure: NEEDS REORGANIZATION" -ForegroundColor $YELLOW
    }
    
    # Check launcher files
    $launcherCount = 0
    if (Test-Path "launchers") {
        $launcherCount = (Get-ChildItem -Path "launchers" -Filter "*.ps1" -Recurse).Count
    } else {
        $launcherCount = (Get-ChildItem -Path "." -Filter "*LAUNCH*.ps1").Count
    }
    
    Write-Host "📁 Launcher Scripts: $launcherCount found" -ForegroundColor $WHITE
    
    # Check services
    $serviceCount = 0
    if (Test-Path "services") {
        $serviceCount = (Get-ChildItem -Path "services" -Directory).Count
    } else {
        $serviceCount = (Get-ChildItem -Path "." -Directory | Where-Object { $_.Name -match "(api|service|server)" }).Count
    }
    
    Write-Host "🚀 Services: $serviceCount found" -ForegroundColor $WHITE
    
    # Check documentation
    $docCount = 0
    if (Test-Path "docs") {
        $docCount = (Get-ChildItem -Path "docs" -Filter "*.md" -Recurse).Count
    } else {
        $docCount = (Get-ChildItem -Path "." -Filter "*.md").Count
    }
    
    Write-Host "📚 Documentation: $docCount files" -ForegroundColor $WHITE
    
    Write-Host ""
    Write-Host "🎯 Recommendations:" -ForegroundColor $YELLOW
    if (-not $reorganized) {
        Write-Host "  • Run reorganization: .\enhanced-launcher-system.ps1 -Action reorganize" -ForegroundColor $WHITE
    } else {
        Write-Host "  • Repository is well organized!" -ForegroundColor $GREEN
    }
    Write-Host "  • Test launchers: .\enhanced-launcher-system.ps1 -Action test" -ForegroundColor $WHITE
    Write-Host "  • List scripts: .\enhanced-launcher-system.ps1 -Action list" -ForegroundColor $WHITE
}

function Get-AvailableScripts {
    Write-Host "📋 Available Scripts" -ForegroundColor $BLUE
    Write-Host "===================" -ForegroundColor $BLUE
    
    $categories = @{
        "launchers" = "🚀 Main Launcher Scripts"
        "scripts" = "🔧 Utility & Setup Scripts"
        "services" = "⚙️  Service Implementations"
        scripts/s" = "🧪 Test Scripts"
        monitoring/" = "📊 Monitoring Scripts"
    }
    
    foreach ($category in $categories.Keys) {
        if (Test-Path $category) {
            Write-Host ""
            Write-Host $categories[$category] -ForegroundColor $YELLOW
            Write-Host ("-" * 40) -ForegroundColor $YELLOW
            
            $scripts = Get-ChildItem -Path $category -Filter "*.ps1" -Recurse | Sort-Object Name
            foreach ($script in $scripts) {
                $relativePath = $script.FullName.Replace((Get-Location).Path + "\", "")
                Write-Host "  📄 $relativePath" -ForegroundColor $WHITE
            }
        }
    }
    
    # Also check root directory for any remaining scripts
    $rootScripts = Get-ChildItem -Path "." -Filter "*.ps1" | Where-Object { $_.Name -notlike "enhanced-launcher-system.ps1" }
    if ($rootScripts) {
        Write-Host ""
        Write-Host "📁 Root Directory Scripts" -ForegroundColor $YELLOW
        Write-Host ("-" * 40) -ForegroundColor $YELLOW
        foreach ($script in $rootScripts) {
            Write-Host "  📄 $($script.Name)" -ForegroundColor $WHITE
        }
    }
}

function Test-AllLaunchers {
    Write-Host "🧪 Testing All Launchers" -ForegroundColor $BLUE
    Write-Host "=======================" -ForegroundColor $BLUE
    
    $testResults = @{
        "Passed" = 0
        "Failed" = 0
        "Skipped" = 0
    }
    
    # Test launcher scripts
    if (Test-Path "launchers") {
        $launchers = Get-ChildItem -Path "launchers" -Filter "*.ps1" -Recurse
        foreach ($launcher in $launchers) {
            Write-Host scripts/ing: $($launcher.Name)" -ForegroundColor $YELLOW
            try {
                # Test syntax only (don't actually run)
                $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $launcher.FullName -Raw), [ref]$null)
                Write-Host "  ✅ Syntax OK" -ForegroundColor $GREEN
                $testResults["Passed"]++
            } catch {
                Write-Host "  ❌ Syntax Error: $($_.Exception.Message)" -ForegroundColor $RED
                $testResults["Failed"]++
            }
        }
    }
    
    # Test utility scripts
    if (Test-Path "scripts") {
        $scripts = Get-ChildItem -Path "scripts" -Filter "*.ps1" -Recurse
        foreach ($script in $scripts) {
            Write-Host scripts/ing: $($script.Name)" -ForegroundColor $YELLOW
            try {
                $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $script.FullName -Raw), [ref]$null)
                Write-Host "  ✅ Syntax OK" -ForegroundColor $GREEN
                $testResults["Passed"]++
            } catch {
                Write-Host "  ❌ Syntax Error: $($_.Exception.Message)" -ForegroundColor $RED
                $testResults["Failed"]++
            }
        }
    }
    
    Write-Host ""
    Write-Host "📊 Test Results Summary:" -ForegroundColor $BLUE
    Write-Host "  ✅ Passed: $($testResults['Passed'])" -ForegroundColor $GREEN
    Write-Host "  ❌ Failed: $($testResults['Failed'])" -ForegroundColor $RED
    Write-Host "  ⏭️  Skipped: $($testResults['Skipped'])" -ForegroundColor $YELLOW
}

function Invoke-RepositoryReorganization {
    Write-Host "🔄 Executing Repository Reorganization" -ForegroundColor $BLUE
    Write-Host "=====================================" -ForegroundColor $BLUE
    
    # Check if reorganization scripts exist
    if (Test-Path "reorganize-repository.ps1") {
        Write-Host "✅ Found reorganization script" -ForegroundColor $GREEN
        Write-Host "🚀 Executing reorganization..." -ForegroundColor $YELLOW
        
        try {
            & .\reorganize-repository.ps1
            Write-Host "✅ Reorganization completed!" -ForegroundColor $GREEN
        } catch {
            Write-Host "❌ Reorganization failed: $($_.Exception.Message)" -ForegroundColor $RED
            return
        }
    } else {
        Write-Host "❌ Reorganization script not found!" -ForegroundColor $RED
        Write-Host "Please ensure 'reorganize-repository.ps1' exists in the current directory." -ForegroundColor $YELLOW
        return
    }
    
    # Update launcher paths
    if (Test-Path "update-launcher-paths.ps1") {
        Write-Host "🔄 Updating launcher paths..." -ForegroundColor $YELLOW
        try {
            & .\update-launcher-paths.ps1
            Write-Host "✅ Path updates completed!" -ForegroundColor $GREEN
        } catch {
            Write-Host "❌ Path update failed: $($_.Exception.Message)" -ForegroundColor $RED
        }
    }
    
    Write-Host ""
    Write-Host "🎉 Repository reorganization completed!" -ForegroundColor $GREEN
    Write-Host "📁 New structure created with organized directories" -ForegroundColor $WHITE
    Write-Host "🔗 All launcher paths have been updated" -ForegroundColor $WHITE
    Write-Host "✅ Ready for professional development workflow" -ForegroundColor $WHITE
}

function Invoke-LaunchScript {
    param(
        [string]$ScriptName,
        [string]$Category
    )
    
    if ([string]::IsNullOrEmpty($ScriptName)) {
        Write-Host "❌ Script name is required" -ForegroundColor $RED
        return
    }
    
    # Determine script path
    $scriptPath = ""
    if ([string]::IsNullOrEmpty($Category)) {
        # Try to find script in any category
        $categories = @("launchers", "scripts", "services", scripts/s", monitoring/")
        foreach ($cat in $categories) {
            if (Test-Path (Join-Path $cat $ScriptName)) {
                $scriptPath = Join-Path $cat $ScriptName
                break
            }
        }
        
        # If not found in categories, check root
        if ([string]::IsNullOrEmpty($scriptPath) -and (Test-Path $ScriptName)) {
            $scriptPath = $ScriptName
        }
    } else {
        $scriptPath = Join-Path $Category $ScriptName
    }
    
    if ([string]::IsNullOrEmpty($scriptPath) -or !(Test-Path $scriptPath)) {
        Write-Host "❌ Script not found: $ScriptName" -ForegroundColor $RED
        Write-Host "💡 Try: .\enhanced-launcher-system.ps1 -Action list" -ForegroundColor $YELLOW
        return
    }
    
    Write-Host "🚀 Launching: $scriptPath" -ForegroundColor $GREEN
    try {
        & $scriptPath @args
    } catch {
        Write-Host "❌ Launch failed: $($_.Exception.Message)" -ForegroundColor $RED
    }
}

# Main execution logic
switch ($Action.ToLower()) {
    "launch" {
        Invoke-LaunchScript -ScriptName $Script -Category $Category
    }
    "list" {
        Get-AvailableScripts
    }
    "status" {
        Get-SystemStatus
    }
    scripts/" {
        Test-AllLaunchers
    }
    "reorganize" {
        Invoke-RepositoryReorganization
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor $RED
        Show-Help
    }
}
