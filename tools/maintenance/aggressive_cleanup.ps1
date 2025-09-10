# 🗑️ **DATA VAULT OBSIDIAN - AGGRESSIVE CLEANUP SCRIPT**

# This script performs aggressive cleanup of garbage files, old tests, and unused files
# Use with caution - it will delete many files that might not be needed

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false,
    [int]$DaysOld = 7
)

Write-Host "🗑️ Starting Aggressive Cleanup..." -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red

if ($DryRun) {
    Write-Host "⚠️  DRY RUN MODE - No files will be deleted" -ForegroundColor Yellow
} elseif ($Force) {
    Write-Host "⚠️  FORCE MODE - Files will be deleted without backup" -ForegroundColor Red
} else {
    Write-Host "📦 Files will be moved to backup before deletion" -ForegroundColor Green
}

# Create backup directory
$backupDir = "temp_files/backup/aggressive_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
if (-not $DryRun) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

# Function to safely delete/move files
function Remove-FileSafely {
    param(
        [string]$FilePath,
        [string]$Reason
    )
    
    if (Test-Path $FilePath) {
        if ($DryRun) {
            Write-Host "DRY RUN: Would delete $FilePath - $Reason" -ForegroundColor Yellow
            return $true
        } else {
            try {
                if ($Force) {
                    Remove-Item -Path $FilePath -Force
                    Write-Host "🗑️  Deleted: $FilePath - $Reason" -ForegroundColor Red
                } else {
                    $fileName = Split-Path $FilePath -Leaf
                    $backupPath = Join-Path $backupDir $fileName
                    Move-Item -Path $FilePath -Destination $backupPath -Force
                    Write-Host "📦 Moved to backup: $FilePath - $Reason" -ForegroundColor Blue
                }
                return $true
            } catch {
                Write-Host "❌ Failed to process $FilePath`: $($_.Exception.Message)" -ForegroundColor Red
                return $false
            }
        }
    }
    return $false
}

$deletedCount = 0
$deletedSize = 0

Write-Host "`n🧹 Cleaning up files..." -ForegroundColor Yellow

# 1. Delete old test files (older than specified days)
Write-Host "`n📝 Cleaning old test files..." -ForegroundColor Cyan
$oldTestFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Name -match "^test_|_test\.|test\.|\.test\." -and 
    $_.LastWriteTime -lt (Get-Date).AddDays(-$DaysOld) -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\node_modules\*" -and
    $_.FullName -notlike "*\__pycache__\*"
}

foreach ($file in $oldTestFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old test file") {
        $deletedCount++
        $deletedSize += $size
    }
}

# 2. Delete duplicate test files
Write-Host "`n📝 Cleaning duplicate test files..." -ForegroundColor Cyan
$duplicateTestFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Name -match "test_.*\(1\)|test_.*\(2\)|test_.*_copy|test_.*_duplicate|test_.*_old|test_.*_backup" -and
    $_.FullName -notlike "*\.git\*"
}

foreach ($file in $duplicateTestFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Duplicate test file") {
        $deletedCount++
        $deletedSize += $size
    }
}

# 3. Delete old report files
Write-Host "`n📊 Cleaning old report files..." -ForegroundColor Cyan
$oldReportFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Name -match "_REPORT_|_SUCCESS_|_ANALYSIS_|_FINAL_|_COMPLETE_" -and 
    $_.LastWriteTime -lt (Get-Date).AddDays(-$DaysOld) -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\docs\*" -and
    $_.FullName -notlike "*\documentation\*"
}

foreach ($file in $oldReportFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old report file") {
        $deletedCount++
        $deletedSize += $size
    }
}

# 4. Delete old JSON test data files
Write-Host "`n📄 Cleaning old JSON test data..." -ForegroundColor Cyan
$oldJsonFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Extension -eq ".json" -and 
    $_.Name -match "test_|capture_|analysis_|trace_|result_" -and
    $_.LastWriteTime -lt (Get-Date).AddDays(-$DaysOld) -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\temp_files\*"
}

foreach ($file in $oldJsonFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old JSON test data") {
        $deletedCount++
        $deletedSize += $size
    }
}

# 5. Delete old log files
Write-Host "`n📝 Cleaning old log files..." -ForegroundColor Cyan
$oldLogFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Extension -eq ".log" -and 
    $_.LastWriteTime -lt (Get-Date).AddDays(-$DaysOld) -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\temp_files\*"
}

foreach ($file in $oldLogFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old log file") {
        $deletedCount++
        $deletedSize += $size
    }
}

# 6. Delete empty files
Write-Host "`n📄 Cleaning empty files..." -ForegroundColor Cyan
$emptyFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Length -eq 0 -and
    $_.FullName -notlike "*\.git\*"
}

foreach ($file in $emptyFiles) {
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Empty file") {
        $deletedCount++
    }
}

# 7. Delete old PowerShell test scripts
Write-Host "`n🔧 Cleaning old PowerShell test scripts..." -ForegroundColor Cyan
$oldPs1Files = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Extension -eq ".ps1" -and 
    $_.Name -match "test|Test|TEST" -and
    $_.LastWriteTime -lt (Get-Date).AddDays(-$DaysOld) -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\deployment\*" -and
    $_.FullName -notlike "*\scripts\*" -and
    $_.Name -ne "cleanup_project.ps1" -and
    $_.Name -ne "usability_analysis.ps1" -and
    $_.Name -ne "aggressive_cleanup.ps1"
}

foreach ($file in $oldPs1Files) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old PowerShell test script") {
        $deletedCount++
        $deletedSize += $size
    }
}

# 8. Delete old Python test files that are not in test_suites
Write-Host "`n🐍 Cleaning old Python test files..." -ForegroundColor Cyan
$oldPythonTestFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Extension -eq ".py" -and 
    $_.Name -match "^test_|_test\.|test\.|\.test\." -and
    $_.LastWriteTime -lt (Get-Date).AddDays(-$DaysOld) -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\test_suites\*" -and
    $_.FullName -notlike "*\monitoring_tools\*" -and
    $_.FullName -notlike "*\core_services\*" -and
    $_.FullName -notlike "*\mcp_tools\*"
}

foreach ($file in $oldPythonTestFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old Python test file") {
        $deletedCount++
        $deletedSize += $size
    }
}

# 9. Delete backup and temporary files
Write-Host "`n🗂️ Cleaning backup and temporary files..." -ForegroundColor Cyan
$backupFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Name -match "backup|bak|old|temp|tmp|copy|duplicate|\(1\)|\(2\)" -and
    $_.FullName -notlike "*\.git\*" -and
    $_.FullName -notlike "*\temp_files\*"
}

foreach ($file in $backupFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Backup/temporary file") {
        $deletedCount++
        $deletedSize += $size
    }
}

# 10. Delete old Docker files that are not needed
Write-Host "`n🐳 Cleaning old Docker files..." -ForegroundColor Cyan
$oldDockerFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { 
    $_.Name -match "docker-compose.*\.yml" -and
    $_.Name -ne "docker-compose.yml" -and
    $_.LastWriteTime -lt (Get-Date).AddDays(-$DaysOld) -and
    $_.FullName -notlike "*\.git\*"
}

foreach ($file in $oldDockerFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old Docker compose file") {
        $deletedCount++
        $deletedSize += $size
    }
}

Write-Host "`n📊 Cleanup Summary:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "Files processed: $deletedCount" -ForegroundColor White
Write-Host "Space freed: $([math]::Round($deletedSize / 1MB, 2)) MB" -ForegroundColor Green

if (-not $DryRun -and -not $Force) {
    Write-Host "Backup location: $backupDir" -ForegroundColor Blue
}

if ($DryRun) {
    Write-Host "`n⚠️  This was a DRY RUN - no files were actually deleted" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to perform actual cleanup" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ Aggressive cleanup completed!" -ForegroundColor Green
}

Write-Host "`n💡 Tips:" -ForegroundColor Cyan
Write-Host "- Use -DryRun to see what would be cleaned without making changes" -ForegroundColor White
Write-Host "- Use -Force to delete files directly (not recommended)" -ForegroundColor White
Write-Host "- Adjust -DaysOld to change the age threshold for old files" -ForegroundColor White
Write-Host "- Check backup directory before permanent deletion" -ForegroundColor White
