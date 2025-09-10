# 📊 **REPORT ANALYSIS SCRIPT**

# This script analyzes all reports in the reports directory and provides insights
# about the project's evolution, timeline, and progress

param(
    [switch]$Detailed = $false,
    [switch]$Export = $false,
    [string]$OutputPath = "reports\analysis\report_analysis_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
)

Write-Host "📊 Analyzing Reports..." -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

# Function to analyze a single report
function Analyze-Report {
    param([string]$FilePath)
    
    $file = Get-Item $FilePath
    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    
    $analysis = @{
        Name = $file.Name
        Path = $file.FullName
        Size = $file.Length
        LastWrite = $file.LastWriteTime
        Age = (Get-Date) - $file.LastWriteTime
        Extension = $file.Extension
        WordCount = 0
        LineCount = 0
        HasTimeline = $false
        HasLinks = $false
        HasImages = $false
        Categories = @()
        Keywords = @()
        Status = "Unknown"
    }
    
    if ($content) {
        # Basic content analysis
        $analysis.WordCount = ($content -split '\s+').Count
        $analysis.LineCount = ($content -split "`n").Count
        
        # Check for timeline indicators
        $analysis.HasTimeline = $content -match "🕐|timeline|Timeline|TIMELINE"
        $analysis.HasLinks = $content -match "\[.*\]\(.*\)|http"
        $analysis.HasImages = $content -match "!\[.*\]\(.*\)|\.png|\.jpg|\.gif"
        
        # Extract categories
        if ($content -match "Category:\s*(.+?)(?:\n|$|Status:)") {
            $analysis.Categories += $matches[1].Trim()
        }
        
        # Extract status
        if ($content -match "Status:\s*(.+?)(?:\n|$)") {
            $analysis.Status = $matches[1].Trim()
        }
        
        # Extract keywords (common technical terms)
        $keywords = @("success", "complete", "error", "test", "deployment", "analysis", "integration", "system", "project", "documentation")
        foreach ($keyword in $keywords) {
            if ($content -match $keyword) {
                $analysis.Keywords += $keyword
            }
        }
    }
    
    return $analysis
}

# Function to generate timeline analysis
function Get-TimelineAnalysis {
    $changelogPath = "reports\CHANGELOG_INDEX.md"
    if (Test-Path $changelogPath) {
        $content = Get-Content $changelogPath -Raw
        $timeline = @{
            TotalEntries = 0
            DateRange = @{}
            Categories = @{}
            StatusCounts = @{}
            RecentActivity = @()
        }
        
        # Count timeline entries
        $timeline.TotalEntries = ([regex]::Matches($content, "🕐")).Count
        
        # Extract dates and activities
        $dateMatches = [regex]::Matches($content, "### \*\*📅 (.+?)\*\*")
        foreach ($match in $dateMatches) {
            $date = $match.Groups[1].Value
            $timeline.DateRange[$date] = 0
        }
        
        # Count entries per date
        $entryMatches = [regex]::Matches($content, "🕐 (.+?) - (.+?)(?:\n|$)")
        foreach ($match in $entryMatches) {
            $time = $match.Groups[1].Value
            $description = $match.Groups[2].Value
            $timeline.RecentActivity += @{
                Time = $time
                Description = $description
            }
        }
        
        return $timeline
    }
    return $null
}

# Function to generate project evolution insights
function Get-ProjectEvolution {
    $allReports = Get-ChildItem -Path "reports" -Recurse -File -Filter "*.md"
    $evolution = @{
        TotalReports = $allReports.Count
        ReportTypes = @{}
        Timeline = @{}
        Progress = @{}
        Insights = @()
    }
    
    # Analyze by directory
    $directories = @("success_reports", "changelogs", "analysis", "testing", "deployment")
    foreach ($dir in $directories) {
        $reports = Get-ChildItem -Path "reports\$dir" -File -Filter "*.md" -ErrorAction SilentlyContinue
        $evolution.ReportTypes[$dir] = $reports.Count
    }
    
    # Analyze timeline progression
    $reportsByDate = $allReports | Group-Object { $_.LastWriteTime.Date.ToString("yyyy-MM-dd") }
    foreach ($group in $reportsByDate) {
        $evolution.Timeline[$group.Name] = $group.Count
    }
    
    # Generate insights
    $totalSize = ($allReports | Measure-Object -Property Length -Sum).Sum
    $evolution.Progress["TotalSize"] = [math]::Round($totalSize / 1MB, 2)
    $evolution.Progress["AverageSize"] = [math]::Round($totalSize / $allReports.Count / 1KB, 2)
    
    # Most active day
    $mostActiveDay = $reportsByDate | Sort-Object Count -Descending | Select-Object -First 1
    if ($mostActiveDay) {
        $evolution.Insights += "Most active day: $($mostActiveDay.Name) with $($mostActiveDay.Count) reports"
    }
    
    # Report type distribution
    $mostCommonType = $evolution.ReportTypes.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1
    if ($mostCommonType) {
        $evolution.Insights += "Most common report type: $($mostCommonType.Key) with $($mostCommonType.Value) reports"
    }
    
    return $evolution
}

Write-Host "`n🔍 Scanning reports directory..." -ForegroundColor Yellow

# Get all reports
$allReports = Get-ChildItem -Path "reports" -Recurse -File -Filter "*.md"
Write-Host "📁 Found $($allReports.Count) reports" -ForegroundColor Green

# Analyze each report
$reportAnalyses = @()
foreach ($report in $allReports) {
    Write-Progress -Activity "Analyzing reports" -Status "Processing $($report.Name)" -PercentComplete (($allReports.IndexOf($report) / $allReports.Count) * 100)
    $analysis = Analyze-Report -FilePath $report.FullName
    $reportAnalyses += $analysis
}
Write-Progress -Activity "Analyzing reports" -Completed

# Generate timeline analysis
Write-Host "`n📅 Analyzing timeline..." -ForegroundColor Yellow
$timelineAnalysis = Get-TimelineAnalysis

# Generate project evolution
Write-Host "`n🚀 Analyzing project evolution..." -ForegroundColor Yellow
$projectEvolution = Get-ProjectEvolution

# Generate summary report
Write-Host "`n📊 Analysis Summary:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

Write-Host "`n📁 Report Statistics:" -ForegroundColor White
Write-Host "  Total Reports: $($allReports.Count)" -ForegroundColor Gray
Write-Host "  Total Size: $([math]::Round(($allReports | Measure-Object -Property Length -Sum).Sum / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host "  Average Size: $([math]::Round(($allReports | Measure-Object -Property Length -Sum).Sum / $allReports.Count / 1KB, 2)) KB" -ForegroundColor Gray

Write-Host "`n📊 Report Types:" -ForegroundColor White
foreach ($type in $projectEvolution.ReportTypes.GetEnumerator()) {
    Write-Host "  $($type.Key): $($type.Value) reports" -ForegroundColor Gray
}

if ($timelineAnalysis) {
    Write-Host "`n📅 Timeline Analysis:" -ForegroundColor White
    Write-Host "  Total Timeline Entries: $($timelineAnalysis.TotalEntries)" -ForegroundColor Gray
    Write-Host "  Recent Activities: $($timelineAnalysis.RecentActivity.Count)" -ForegroundColor Gray
}

Write-Host "`n💡 Key Insights:" -ForegroundColor White
foreach ($insight in $projectEvolution.Insights) {
    Write-Host "  • $insight" -ForegroundColor Yellow
}

# Detailed analysis
if ($Detailed) {
    Write-Host "`n🔍 Detailed Report Analysis:" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor Cyan
    
    $reportAnalyses | Sort-Object LastWrite -Descending | ForEach-Object {
        $age = if ($_.Age.Days -gt 0) { "$($_.Age.Days) days ago" } else { "Today" }
        Write-Host "`n📄 $($_.Name):" -ForegroundColor White
        Write-Host "  Size: $([math]::Round($_.Size / 1KB, 2)) KB" -ForegroundColor Gray
        Write-Host "  Age: $age" -ForegroundColor Gray
        Write-Host "  Words: $($_.WordCount)" -ForegroundColor Gray
        Write-Host "  Lines: $($_.LineCount)" -ForegroundColor Gray
        Write-Host "  Status: $($_.Status)" -ForegroundColor Gray
        if ($_.Categories.Count -gt 0) {
            Write-Host "  Categories: $($_.Categories -join ', ')" -ForegroundColor Gray
        }
        if ($_.Keywords.Count -gt 0) {
            Write-Host "  Keywords: $($_.Keywords -join ', ')" -ForegroundColor Gray
        }
    }
}

# Export analysis
if ($Export) {
    $analysisData = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        ReportAnalyses = $reportAnalyses
        TimelineAnalysis = $timelineAnalysis
        ProjectEvolution = $projectEvolution
        Summary = @{
            TotalReports = $allReports.Count
            TotalSize = [math]::Round(($allReports | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
            AverageSize = [math]::Round(($allReports | Measure-Object -Property Length -Sum).Sum / $allReports.Count / 1KB, 2)
        }
    }
    
    $analysisData | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8
    Write-Host "`n💾 Analysis exported to: $OutputPath" -ForegroundColor Green
}

Write-Host "`n✅ Report analysis completed!" -ForegroundColor Green

Write-Host "`n💡 Usage Examples:" -ForegroundColor Cyan
Write-Host "  .\analyze_reports.ps1                    # Basic analysis" -ForegroundColor White
Write-Host "  .\analyze_reports.ps1 -Detailed          # Detailed analysis" -ForegroundColor White
Write-Host "  .\analyze_reports.ps1 -Export            # Export to JSON" -ForegroundColor White
Write-Host "  .\analyze_reports.ps1 -Detailed -Export  # Full analysis with export" -ForegroundColor White
