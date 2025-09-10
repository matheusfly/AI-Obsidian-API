# 🔍 **DATA VAULT OBSIDIAN - COMPREHENSIVE USABILITY ANALYSIS**

# This script performs a deep analysis of file usage and identifies garbage files
# that can be safely deleted to improve system performance and maintainability

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false,
    [int]$DaysOld = 30,
    [switch]$Detailed = $false
)

Write-Host "🔍 Starting Comprehensive Usability Analysis..." -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Function to analyze file usage
function Analyze-FileUsage {
    param([string]$FilePath)
    
    $file = Get-Item $FilePath
    $analysis = @{
        Name = $file.Name
        Path = $file.FullName
        Size = $file.Length
        LastAccess = $file.LastAccessTime
        LastWrite = $file.LastWriteTime
        Age = (Get-Date) - $file.LastWriteTime
        Extension = $file.Extension
        IsUsed = $false
        UsageReason = ""
        CanDelete = $false
        DeleteReason = ""
    }
    
    # Check if file is referenced in other files
    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if ($content) {
        # Check for imports, references, or dependencies
        $references = @()
        
        # Check Python imports
        if ($file.Extension -eq ".py") {
            $imports = [regex]::Matches($content, "import\s+(\w+)|from\s+(\w+)\s+import")
            foreach ($match in $imports) {
                $references += $match.Groups[1].Value
            }
        }
        
        # Check PowerShell references
        if ($file.Extension -eq ".ps1") {
            $refs = [regex]::Matches($content, "\.\\\w+\.ps1|\.\\\w+\.py")
            foreach ($match in $refs) {
                $references += $match.Value
            }
        }
        
        # Check JSON references
        if ($file.Extension -eq ".json") {
            $refs = [regex]::Matches($content, '"[^"]*\.(py|ps1|json|md)"')
            foreach ($match in $refs) {
                $references += $match.Value
            }
        }
        
        if ($references.Count -gt 0) {
            $analysis.IsUsed = $true
            $analysis.UsageReason = "Referenced by: $($references -join ', ')"
        }
    }
    
    return $analysis
}

# Function to check if file is essential for system operation
function Test-EssentialFile {
    param([string]$FilePath)
    
    $essentialPatterns = @(
        "main_script_final.ps1",
        "comprehensive_logging_suite.py",
        "raw_data_capture.py",
        "realtime_log_monitor.py",
        "tracing_analysis.py",
        "mcp_integration_server.py",
        "http_observability_server.py",
        "mcp_debug_dashboard.py",
        "langgraph_studio_server.py",
        "graph.py",
        "langgraph.json",
        "README.md",
        "PROJECT_ORGANIZATION.md",
        "cleanup_project.ps1",
        "usability_analysis.ps1"
    )
    
    $fileName = Split-Path $FilePath -Leaf
    
    foreach ($pattern in $essentialPatterns) {
        if ($fileName -like "*$pattern*") {
            return $true
        }
    }
    
    return $false
}

# Function to categorize files
function Categorize-File {
    param([string]$FilePath)
    
    $file = Get-Item $FilePath
    $category = "unknown"
    $canDelete = $false
    $reason = ""
    
    # Test files
    if ($file.Name -match "^test_|_test\.|test\.|\.test\.") {
        $category = "test"
        if ($file.Age.Days -gt $DaysOld) {
            $canDelete = $true
            $reason = "Old test file"
        }
    }
    
    # Log files
    elseif ($file.Extension -eq ".log") {
        $category = "log"
        if ($file.Age.Days -gt 7) {
            $canDelete = $true
            $reason = "Old log file"
        }
    }
    
    # Report files
    elseif ($file.Name -match "_REPORT_|_SUCCESS_|_ANALYSIS_|_FINAL_") {
        $category = "report"
        if ($file.Age.Days -gt $DaysOld) {
            $canDelete = $true
            $reason = "Old report file"
        }
    }
    
    # JSON data files
    elseif ($file.Extension -eq ".json" -and $file.Name -match "capture_|analysis_|test_|trace_") {
        $category = "data"
        if ($file.Age.Days -gt $DaysOld) {
            $canDelete = $true
            $reason = "Old data file"
        }
    }
    
    # Backup files
    elseif ($file.Name -match "backup|bak|old|temp|tmp") {
        $category = "backup"
        $canDelete = $true
        $reason = "Backup/temporary file"
    }
    
    # Duplicate files
    elseif ($file.Name -match "\(1\)|\(2\)|_copy|_duplicate") {
        $category = "duplicate"
        $canDelete = $true
        $reason = "Duplicate file"
    }
    
    # Empty files
    elseif ($file.Length -eq 0) {
        $category = "empty"
        $canDelete = $true
        $reason = "Empty file"
    }
    
    # Old scripts
    elseif ($file.Extension -eq ".ps1" -and $file.Name -match "old|backup|temp|test") {
        $category = "old_script"
        if ($file.Age.Days -gt $DaysOld) {
            $canDelete = $true
            $reason = "Old script file"
        }
    }
    
    return @{
        Category = $category
        CanDelete = $canDelete
        Reason = $reason
    }
}

Write-Host "`n📊 Analyzing files..." -ForegroundColor Yellow

# Get all files in the project
$allFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.FullName -notlike "*\.git\*" -and 
    $_.FullName -notlike "*\node_modules\*" -and
    $_.FullName -notlike "*\__pycache__\*" -and
    $_.FullName -notlike "*\.venv\*"
}

$analysisResults = @()
$deletableFiles = @()
$totalSize = 0
$deletableSize = 0

foreach ($file in $allFiles) {
    Write-Progress -Activity "Analyzing files" -Status "Processing $($file.Name)" -PercentComplete (($allFiles.IndexOf($file) / $allFiles.Count) * 100)
    
    $analysis = Analyze-FileUsage -FilePath $file.FullName
    $category = Categorize-File -FilePath $file.FullName
    $isEssential = Test-EssentialFile -FilePath $file.FullName
    
    $analysis.Category = $category.Category
    $analysis.CanDelete = $category.CanDelete -and -not $isEssential
    $analysis.DeleteReason = if ($isEssential) { "Essential system file" } else { $category.Reason }
    
    $analysisResults += $analysis
    $totalSize += $file.Length
    
    if ($analysis.CanDelete) {
        $deletableFiles += $analysis
        $deletableSize += $file.Length
    }
}

Write-Progress -Activity "Analyzing files" -Completed

Write-Host "`n📈 Analysis Results:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

# Group by category
$categories = $analysisResults | Group-Object Category | Sort-Object Count -Descending

foreach ($category in $categories) {
    $categorySize = ($category.Group | Measure-Object -Property Size -Sum).Sum
    $deletableInCategory = $category.Group | Where-Object { $_.CanDelete }
    $deletableCount = $deletableInCategory.Count
    $deletableCategorySize = ($deletableInCategory | Measure-Object -Property Size -Sum).Sum
    
    Write-Host "`n📁 $($category.Name):" -ForegroundColor White
    Write-Host "   Total files: $($category.Count)" -ForegroundColor Gray
    Write-Host "   Total size: $([math]::Round($categorySize / 1MB, 2)) MB" -ForegroundColor Gray
    Write-Host "   Deletable: $deletableCount files ($([math]::Round($deletableCategorySize / 1MB, 2)) MB)" -ForegroundColor $(if ($deletableCount -gt 0) { "Yellow" } else { "Green" })
}

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "===========" -ForegroundColor Cyan
Write-Host "Total files analyzed: $($allFiles.Count)" -ForegroundColor White
Write-Host "Total size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor White
Write-Host "Deletable files: $($deletableFiles.Count)" -ForegroundColor Yellow
Write-Host "Deletable size: $([math]::Round($deletableSize / 1MB, 2)) MB" -ForegroundColor Yellow
Write-Host "Space savings: $([math]::Round(($deletableSize / $totalSize) * 100, 1))%" -ForegroundColor Green

if ($Detailed) {
    Write-Host "`n🔍 Detailed Deletable Files:" -ForegroundColor Cyan
    Write-Host "===========================" -ForegroundColor Cyan
    
    $deletableFiles | Sort-Object Size -Descending | ForEach-Object {
        $sizeMB = [math]::Round($_.Size / 1MB, 2)
        Write-Host "🗑️  $($_.Name) ($sizeMB MB) - $($_.DeleteReason)" -ForegroundColor Yellow
    }
}

if ($deletableFiles.Count -gt 0) {
    Write-Host "`n🧹 Cleanup Options:" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    
    if ($DryRun) {
        Write-Host "DRY RUN - No files will be deleted" -ForegroundColor Yellow
        Write-Host "Run without -DryRun to perform actual cleanup" -ForegroundColor Yellow
    } else {
        if ($Force) {
            Write-Host "⚠️  FORCE MODE - Files will be deleted without confirmation" -ForegroundColor Red
        } else {
            Write-Host "Files will be moved to temp_files/backup/ before deletion" -ForegroundColor Green
        }
        
        $response = Read-Host "Do you want to proceed with cleanup? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Write-Host "`n🗑️  Starting cleanup..." -ForegroundColor Yellow
            
            $backupDir = "temp_files/backup/$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
            
            $deletedCount = 0
            $deletedSize = 0
            
            foreach ($file in $deletableFiles) {
                try {
                    if (-not $Force) {
                        # Move to backup first
                        $backupPath = Join-Path $backupDir $file.Name
                        Move-Item -Path $file.Path -Destination $backupPath -Force
                        Write-Host "📦 Moved to backup: $($file.Name)" -ForegroundColor Blue
                    } else {
                        # Delete directly
                        Remove-Item -Path $file.Path -Force
                        Write-Host "🗑️  Deleted: $($file.Name)" -ForegroundColor Red
                    }
                    
                    $deletedCount++
                    $deletedSize += $file.Size
                } catch {
                    Write-Host "❌ Failed to process $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
                }
            }
            
            Write-Host "`n✅ Cleanup completed!" -ForegroundColor Green
            Write-Host "Files processed: $deletedCount" -ForegroundColor White
            Write-Host "Space freed: $([math]::Round($deletedSize / 1MB, 2)) MB" -ForegroundColor Green
            
            if (-not $Force) {
                Write-Host "Backup location: $backupDir" -ForegroundColor Blue
            }
        } else {
            Write-Host "Cleanup cancelled" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "`n✅ No deletable files found - project is already clean!" -ForegroundColor Green
}

Write-Host "`n💡 Tips:" -ForegroundColor Cyan
Write-Host "- Use -Detailed to see specific files that can be deleted" -ForegroundColor White
Write-Host "- Use -DryRun to see what would be cleaned without making changes" -ForegroundColor White
Write-Host "- Use -Force to delete files directly (not recommended)" -ForegroundColor White
Write-Host "- Adjust -DaysOld to change the age threshold for old files" -ForegroundColor White

Write-Host "`n🔍 Usability analysis completed!" -ForegroundColor Green
