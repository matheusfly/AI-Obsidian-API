# 📊 **MASTER CHANGELOG MANAGER**

# This script orchestrates all changelog management activities including
# scanning for new reports, updating the timeline, and generating analysis

param(
    [switch]$Scan = $false,
    [switch]$Update = $false,
    [switch]$Analyze = $false,
    [switch]$All = $false,
    [switch]$DryRun = $false,
    [switch]$Detailed = $false,
    [switch]$Export = $false
)

Write-Host "📊 Master Changelog Manager" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# Set default behavior
if (-not $Scan -and -not $Update -and -not $Analyze -and -not $All) {
    $All = $true
}

if ($All) {
    $Scan = $true
    $Update = $true
    $Analyze = $true
}

# Function to run changelog update
function Invoke-ChangelogUpdate {
    Write-Host "`n🔄 Updating Changelog..." -ForegroundColor Yellow
    Write-Host "========================" -ForegroundColor Yellow
    
    $updateScript = ".\update_changelog.ps1"
    if (Test-Path $updateScript) {
        if ($DryRun) {
            & $updateScript -DryRun
        } else {
            & $updateScript
        }
        Write-Host "✅ Changelog update completed" -ForegroundColor Green
    } else {
        Write-Host "❌ Update script not found: $updateScript" -ForegroundColor Red
    }
}

# Function to run report analysis
function Invoke-ReportAnalysis {
    Write-Host "`n📊 Analyzing Reports..." -ForegroundColor Yellow
    Write-Host "=======================" -ForegroundColor Yellow
    
    $analysisScript = ".\analyze_reports.ps1"
    if (Test-Path $analysisScript) {
        $params = @()
        if ($Detailed) { $params += "-Detailed" }
        if ($Export) { $params += "-Export" }
        
        & $analysisScript @params
        Write-Host "✅ Report analysis completed" -ForegroundColor Green
    } else {
        Write-Host "❌ Analysis script not found: $analysisScript" -ForegroundColor Red
    }
}

# Function to scan for new reports
function Invoke-ReportScan {
    Write-Host "`n🔍 Scanning for New Reports..." -ForegroundColor Yellow
    Write-Host "==============================" -ForegroundColor Yellow
    
    $newReports = @()
    $directories = @("success_reports", "changelogs", "analysis", "testing", "deployment")
    
    foreach ($dir in $directories) {
        $reports = Get-ChildItem -Path "..\$dir" -File -Filter "*.md" -ErrorAction SilentlyContinue
        $recentReports = $reports | Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-24) }
        
        if ($recentReports.Count -gt 0) {
            Write-Host "📁 $dir`: $($recentReports.Count) new reports" -ForegroundColor Green
            foreach ($report in $recentReports) {
                Write-Host "  • $($report.Name) ($($report.LastWriteTime.ToString('HH:mm')))" -ForegroundColor White
                $newReports += $report
            }
        } else {
            Write-Host "📁 $dir`: No new reports" -ForegroundColor Gray
        }
    }
    
    if ($newReports.Count -gt 0) {
        Write-Host "`n📝 Total new reports found: $($newReports.Count)" -ForegroundColor Green
        Write-Host "💡 Run with -Update to add them to the changelog" -ForegroundColor Yellow
    } else {
        Write-Host "`n✅ No new reports found in the last 24 hours" -ForegroundColor Green
    }
    
    return $newReports
}

# Function to generate changelog summary
function Get-ChangelogSummary {
    Write-Host "`n📋 Changelog Summary..." -ForegroundColor Yellow
    Write-Host "=======================" -ForegroundColor Yellow
    
    $changelogPath = "..\CHANGELOG_INDEX.md"
    if (Test-Path $changelogPath) {
        $content = Get-Content $changelogPath -Raw
        
        # Count timeline entries
        $timelineEntries = ([regex]::Matches($content, "🕐")).Count
        Write-Host "📅 Timeline Entries: $timelineEntries" -ForegroundColor White
        
        # Count report categories
        $successReports = (Get-ChildItem -Path "..\success_reports" -File -Filter "*.md" -ErrorAction SilentlyContinue).Count
        $changelogReports = (Get-ChildItem -Path "..\changelogs" -File -Filter "*.md" -ErrorAction SilentlyContinue).Count
        $analysisReports = (Get-ChildItem -Path "..\analysis" -File -Filter "*.md" -ErrorAction SilentlyContinue).Count
        $testingReports = (Get-ChildItem -Path "..\testing" -File -Filter "*.md" -ErrorAction SilentlyContinue).Count
        $deploymentReports = (Get-ChildItem -Path "..\deployment" -File -Filter "*.md" -ErrorAction SilentlyContinue).Count
        
        Write-Host "📊 Report Categories:" -ForegroundColor White
        Write-Host "  Success Reports: $successReports" -ForegroundColor Gray
        Write-Host "  Changelog Reports: $changelogReports" -ForegroundColor Gray
        Write-Host "  Analysis Reports: $analysisReports" -ForegroundColor Gray
        Write-Host "  Testing Reports: $testingReports" -ForegroundColor Gray
        Write-Host "  Deployment Reports: $deploymentReports" -ForegroundColor Gray
        
        $totalReports = $successReports + $changelogReports + $analysisReports + $testingReports + $deploymentReports
        Write-Host "  Total Reports: $totalReports" -ForegroundColor Green
    } else {
        Write-Host "❌ Changelog index not found: $changelogPath" -ForegroundColor Red
    }
}

# Function to validate changelog integrity
function Test-ChangelogIntegrity {
    Write-Host "`n🔍 Validating Changelog Integrity..." -ForegroundColor Yellow
    Write-Host "=====================================" -ForegroundColor Yellow
    
    $changelogPath = "..\CHANGELOG_INDEX.md"
    $issues = @()
    
    if (Test-Path $changelogPath) {
        $content = Get-Content $changelogPath -Raw
        
        # Check for broken links
        $linkMatches = [regex]::Matches($content, "\[([^\]]+)\]\(([^)]+)\)")
        foreach ($match in $linkMatches) {
            $linkText = $match.Groups[1].Value
            $linkPath = $match.Groups[2].Value
            
            if ($linkPath -notlike "http*" -and $linkPath -notlike "mailto:*") {
                $fullPath = Join-Path ".." $linkPath
                if (-not (Test-Path $fullPath)) {
                    $issues += "Broken link: $linkText -> $linkPath"
                }
            }
        }
        
        # Check for missing timestamps
        $timestampMatches = [regex]::Matches($content, "#### \*\*🕐")
        if ($timestampMatches.Count -eq 0) {
            $issues += "No timeline entries found"
        }
        
        # Check for missing categories
        $categoryMatches = [regex]::Matches($content, "Category:")
        if ($categoryMatches.Count -eq 0) {
            $issues += "No categories found"
        }
        
        if ($issues.Count -eq 0) {
            Write-Host "✅ Changelog integrity check passed" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Found $($issues.Count) issues:" -ForegroundColor Yellow
            foreach ($issue in $issues) {
                Write-Host "  • $issue" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "❌ Changelog index not found" -ForegroundColor Red
    }
}

# Main execution
Write-Host "🚀 Starting changelog management operations..." -ForegroundColor Cyan

if ($Scan) {
    $newReports = Invoke-ReportScan
}

if ($Update) {
    Invoke-ChangelogUpdate
}

if ($Analyze) {
    Invoke-ReportAnalysis
}

# Always run summary and integrity check
Get-ChangelogSummary
Test-ChangelogIntegrity

Write-Host "`n📊 Changelog Management Summary:" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

if ($Scan) {
    Write-Host "✅ Report scanning completed" -ForegroundColor Green
}
if ($Update) {
    Write-Host "✅ Changelog update completed" -ForegroundColor Green
}
if ($Analyze) {
    Write-Host "✅ Report analysis completed" -ForegroundColor Green
}

Write-Host "`n💡 Usage Examples:" -ForegroundColor Cyan
Write-Host "  .\master_changelog_manager.ps1 -Scan              # Scan for new reports" -ForegroundColor White
Write-Host "  .\master_changelog_manager.ps1 -Update            # Update changelog" -ForegroundColor White
Write-Host "  .\master_changelog_manager.ps1 -Analyze           # Analyze reports" -ForegroundColor White
Write-Host "  .\master_changelog_manager.ps1 -All               # Run all operations" -ForegroundColor White
Write-Host "  .\master_changelog_manager.ps1 -All -Detailed     # Run all with detailed output" -ForegroundColor White
Write-Host "  .\master_changelog_manager.ps1 -All -DryRun       # Preview all operations" -ForegroundColor White

Write-Host "`n✅ Master changelog management completed!" -ForegroundColor Green
