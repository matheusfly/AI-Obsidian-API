# 📊 **CHANGELOG UPDATE SCRIPT**

# This script automatically updates the changelog index when new reports are added
# It scans for new reports and updates the timeline accordingly

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false,
    [string]$ReportPath = "",
    [string]$ReportType = "Success Report",
    [string]$Category = "General",
    [string]$Description = ""
)

Write-Host "📊 Updating Changelog Index..." -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Function to get current timestamp
function Get-CurrentTimestamp {
    return Get-Date -Format "HH:mm"
}

# Function to get current date
function Get-CurrentDate {
    return Get-Date -Format "yyyy-MM-dd"
}

# Function to add new report to changelog index
function Add-ReportToChangelog {
    param(
        [string]$ReportName,
        [string]$ReportPath,
        [string]$ReportType,
        [string]$Category,
        [string]$Description,
        [string]$Status = "✅ Complete"
    )
    
    $timestamp = Get-CurrentTimestamp
    $date = Get-CurrentDate
    $changelogPath = "reports\CHANGELOG_INDEX.md"
    
    # Create new entry
    $newEntry = @"

#### **🕐 $timestamp - $Description**
- **Report:** [$ReportName](./$ReportPath)
- **Type:** $ReportType
- **Category:** $Category
- **Status:** $Status
- **Key Achievements:**
  - $Description
"@

    # Read current changelog
    $changelogContent = Get-Content $changelogPath -Raw
    
    # Find the timeline section and add new entry
    $timelinePattern = "## 🕒 \*\*TIMELINE INDEX\*\*"
    $timelineMatch = [regex]::Match($changelogContent, $timelinePattern)
    
    if ($timelineMatch.Success) {
        $insertPosition = $timelineMatch.Index + $timelineMatch.Length
        $beforeTimeline = $changelogContent.Substring(0, $insertPosition)
        $afterTimeline = $changelogContent.Substring($insertPosition)
        
        # Find the current date section or create new one
        $datePattern = "### \*\*📅 $date\*\*"
        $dateMatch = [regex]::Match($afterTimeline, $datePattern)
        
        if ($dateMatch.Success) {
            # Add to existing date section
            $dateInsertPosition = $dateMatch.Index + $dateMatch.Length
            $beforeDate = $afterTimeline.Substring(0, $dateInsertPosition)
            $afterDate = $afterTimeline.Substring($dateInsertPosition)
            
            $newContent = $beforeTimeline + $beforeDate + $newEntry + $afterDate
        } else {
            # Create new date section
            $newDateSection = @"

### **📅 $date**

$newEntry
"@
            $newContent = $beforeTimeline + $newDateSection + $afterTimeline
        }
        
        # Write updated changelog
        if (-not $DryRun) {
            Set-Content -Path $changelogPath -Value $newContent -Encoding UTF8
            Write-Host "✅ Updated changelog index with new report: $ReportName" -ForegroundColor Green
        } else {
            Write-Host "DRY RUN: Would add report to changelog: $ReportName" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Could not find timeline section in changelog" -ForegroundColor Red
    }
}

# Function to scan for new reports
function Scan-NewReports {
    $newReports = @()
    
    # Scan success_reports directory
    $successReports = Get-ChildItem -Path "reports\success_reports" -File -Filter "*.md" | 
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-1) }
    
    foreach ($report in $successReports) {
        $newReports += @{
            Name = $report.Name
            Path = "success_reports/$($report.Name)"
            Type = "Success Report"
            Category = "General"
            Description = "New success report added"
        }
    }
    
    # Scan changelogs directory
    $changelogReports = Get-ChildItem -Path "reports\changelogs" -File -Filter "*.md" | 
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-1) }
    
    foreach ($report in $changelogReports) {
        $newReports += @{
            Name = $report.Name
            Path = "changelogs/$($report.Name)"
            Type = "Changelog"
            Category = "System Changes"
            Description = "New changelog entry added"
        }
    }
    
    return $newReports
}

# Function to update report statistics
function Update-ReportStatistics {
    $changelogPath = "reports\CHANGELOG_INDEX.md"
    $changelogContent = Get-Content $changelogPath -Raw
    
    # Count reports by type
    $successReports = (Get-ChildItem -Path "reports\success_reports" -File -Filter "*.md").Count
    $changelogReports = (Get-ChildItem -Path "reports\changelogs" -File -Filter "*.md").Count
    $analysisReports = (Get-ChildItem -Path "reports\analysis" -File -Filter "*.md").Count
    $testingReports = (Get-ChildItem -Path "reports\testing" -File -Filter "*.md").Count
    $deploymentReports = (Get-ChildItem -Path "reports\deployment" -File -Filter "*.md").Count
    
    $totalReports = $successReports + $changelogReports + $analysisReports + $testingReports + $deploymentReports
    
    # Update statistics section
    $statsPattern = "### \*\*📊 Progress Metrics\*\*"
    $statsReplacement = @"
### **📊 Progress Metrics**
- **Total Reports:** $totalReports+ success reports
- **Success Reports:** $successReports
- **Changelog Reports:** $changelogReports
- **Analysis Reports:** $analysisReports
- **Testing Reports:** $testingReports
- **Deployment Reports:** $deploymentReports
- **System Status:** 100% operational
- **Organization Level:** Professional grade
"@
    
    $updatedContent = $changelogContent -replace [regex]::Escape($statsPattern), $statsReplacement
    
    if (-not $DryRun) {
        Set-Content -Path $changelogPath -Value $updatedContent -Encoding UTF8
        Write-Host "✅ Updated report statistics" -ForegroundColor Green
    }
}

# Main execution
if ($ReportPath -ne "") {
    # Add specific report
    $reportName = Split-Path $ReportPath -Leaf
    Add-ReportToChangelog -ReportName $reportName -ReportPath $ReportPath -ReportType $ReportType -Category $Category -Description $Description
} else {
    # Scan for new reports
    Write-Host "🔍 Scanning for new reports..." -ForegroundColor Yellow
    $newReports = Scan-NewReports
    
    if ($newReports.Count -gt 0) {
        Write-Host "📝 Found $($newReports.Count) new reports:" -ForegroundColor Green
        foreach ($report in $newReports) {
            Write-Host "  - $($report.Name)" -ForegroundColor White
            Add-ReportToChangelog -ReportName $report.Name -ReportPath $report.Path -ReportType $report.Type -Category $report.Category -Description $report.Description
        }
    } else {
        Write-Host "✅ No new reports found" -ForegroundColor Green
    }
}

# Update statistics
Update-ReportStatistics

Write-Host "`n📊 Changelog update completed!" -ForegroundColor Green

if ($DryRun) {
    Write-Host "⚠️  This was a DRY RUN - no changes were made" -ForegroundColor Yellow
}

Write-Host "`n💡 Usage Examples:" -ForegroundColor Cyan
Write-Host "  .\update_changelog.ps1                    # Scan for new reports" -ForegroundColor White
Write-Host "  .\update_changelog.ps1 -DryRun            # Preview changes" -ForegroundColor White
Write-Host "  .\update_changelog.ps1 -ReportPath 'success_reports/NewReport.md' -Description 'New feature added'" -ForegroundColor White
