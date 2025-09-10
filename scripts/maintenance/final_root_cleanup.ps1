# Final Root Folder Cleanup and Backup Cleaning Script
# This script completes the cleanup of the root directory and backup files

param(
    [switch]$DryRun = $false,
    [switch]$Detailed = $false,
    [switch]$Force = $false
)

Write-Host "🧹 FINAL ROOT FOLDER CLEANUP" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be moved or deleted" -ForegroundColor Yellow
}

# Files to move to proper locations
$FilesToMove = @{
    # Move remaining reports to docs/development
    "PERSISTENT_FILE_ORGANIZATION_SUCCESS_REPORT.md" = "docs/development/"
    "PRODUCTION_RESTRUCTURING_SUCCESS_REPORT.md" = "docs/development/"
    "PROJECT_ORGANIZATION.md" = "docs/development/"
    
    # Move architecture design to docs/architecture
    "PRODUCTION_ARCHITECTURE_DESIGN.md" = "docs/architecture/"
    
    # Move requirements files to root (they belong there)
    "requirements-langgraph.txt" = "."
    "requirements-mcp.txt" = "."
    "requirements-minimal-api.txt" = "."
    "requirements-minimal.txt" = "."
    "requirements.txt" = "."
    
    # Move scripts to proper locations
    "organize_remaining_files.ps1" = "scripts/maintenance/"
    "restructure_to_production.ps1" = "scripts/maintenance/"
    
    # Move langgraph_project to apps/studio-app (it was missed)
    "langgraph_project" = "apps/studio-app/"
}

# Files to delete (temporary/duplicate files)
$FilesToDelete = @(
    # Old log files in root logs directory
    "logs/deployment-20250905-232055.log",
    "logs/deployment-20250905-232241.log", 
    "logs/deployment-20250905-232312.log",
    "logs/deployment-20250905-232347.log",
    "logs/deployment-20250905-232456.log",
    "logs/deployment-20250905-232457.log"
)

# Directories to clean up
$DirectoriesToClean = @{
    # Clean up backup directories
    "backup_restructure_20250906_114202" = "Remove entire backup directory"
    
    # Clean up empty directories
    "logs/application" = "Remove if empty"
    "logs/system" = "Remove if empty"
    "logs/audit" = "Remove if empty"
}

$MovedCount = 0
$DeletedCount = 0
$CleanedCount = 0
$FailedCount = 0

Write-Host "`n📁 MOVING FILES TO PROPER LOCATIONS..." -ForegroundColor Yellow

# Move files to proper locations
foreach ($file in $FilesToMove.GetEnumerator()) {
    $sourcePath = $file.Key
    $targetDir = $file.Value
    
    if (Test-Path $sourcePath) {
        try {
            if (-not $DryRun) {
                if ($targetDir -eq ".") {
                    # File is already in root, just ensure it's in the right place
                    Write-Host "  ✅ Already in root: $sourcePath" -ForegroundColor Green
                } else {
                    # Move file to target directory
                    $targetPath = Join-Path $targetDir (Split-Path $sourcePath -Leaf)
                    if (-not (Test-Path $targetDir)) {
                        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                    }
                    Move-Item -Path $sourcePath -Destination $targetPath -Force
                    Write-Host "  ✅ Moved: $sourcePath → $targetPath" -ForegroundColor Green
                }
            } else {
                Write-Host "  🔍 DRY RUN: Would move $sourcePath → $targetDir" -ForegroundColor Yellow
            }
            $MovedCount++
        } catch {
            Write-Host "  ❌ Failed to move $sourcePath`: $($_.Exception.Message)" -ForegroundColor Red
            $FailedCount++
        }
    } else {
        Write-Host "  ⚠️ Warning: File '$sourcePath' not found, skipping." -ForegroundColor Yellow
    }
}

Write-Host "`n🗑️ DELETING TEMPORARY FILES..." -ForegroundColor Yellow

# Delete temporary files
foreach ($file in $FilesToDelete) {
    if (Test-Path $file) {
        try {
            if (-not $DryRun) {
                Remove-Item -Path $file -Force
                Write-Host "  ✅ Deleted: $file" -ForegroundColor Green
            } else {
                Write-Host "  🔍 DRY RUN: Would delete $file" -ForegroundColor Yellow
            }
            $DeletedCount++
        } catch {
            Write-Host "  ❌ Failed to delete $file`: $($_.Exception.Message)" -ForegroundColor Red
            $FailedCount++
        }
    }
}

Write-Host "`n🧹 CLEANING UP DIRECTORIES..." -ForegroundColor Yellow

# Clean up directories
foreach ($dir in $DirectoriesToClean.GetEnumerator()) {
    $dirPath = $dir.Key
    $action = $dir.Value
    
    if (Test-Path $dirPath) {
        try {
            if (-not $DryRun) {
                if ($action -eq "Remove entire backup directory") {
                    Remove-Item -Path $dirPath -Recurse -Force
                    Write-Host "  ✅ Removed backup directory: $dirPath" -ForegroundColor Green
                } elseif ($action -eq "Remove if empty") {
                    $items = Get-ChildItem -Path $dirPath -Force
                    if ($items.Count -eq 0) {
                        Remove-Item -Path $dirPath -Force
                        Write-Host "  ✅ Removed empty directory: $dirPath" -ForegroundColor Green
                    } else {
                        Write-Host "  ⚠️ Directory not empty, keeping: $dirPath" -ForegroundColor Yellow
                    }
                }
            } else {
                Write-Host "  🔍 DRY RUN: Would $action - $dirPath" -ForegroundColor Yellow
            }
            $CleanedCount++
        } catch {
            Write-Host "  ❌ Failed to clean $dirPath`: $($_.Exception.Message)" -ForegroundColor Red
            $FailedCount++
        }
    }
}

# Clean up any remaining empty directories
Write-Host "`n🔍 CLEANING UP EMPTY DIRECTORIES..." -ForegroundColor Yellow

$EmptyDirs = @(
    "logs/application",
    "logs/system", 
    "logs/audit",
    "src/domain/entities/obsidian",
    "src/domain/entities/langgraph",
    "src/domain/entities/mcp",
    "src/domain/value_objects",
    "src/domain/services",
    "src/domain/repositories",
    "src/infrastructure/messaging",
    "src/infrastructure/monitoring",
    "src/presentation/cli/commands",
    "src/presentation/cli/utils",
    "src/presentation/web/admin",
    "src/presentation/web/dashboard",
    "src/presentation/web/studio",
    "src/application/dto",
    "src/application/interfaces",
    "infrastructure/kubernetes",
    "infrastructure/terraform",
    "apps/cli-app",
    "apps/dashboard-app",
    "tools/formatting",
    "tools/linting",
    "tools/monitoring",
    "tools/testing",
    "tests/e2e",
    "tests/fixtures",
    "tests/performance",
    "docs/api",
    "docs/deployment",
    "docs/user",
    "scripts/build",
    "scripts/dev",
    "scripts/test",
    "data/backups"
)

foreach ($dir in $EmptyDirs) {
    if (Test-Path $dir) {
        $items = Get-ChildItem -Path $dir -Force -ErrorAction SilentlyContinue
        if ($items -eq $null -or $items.Count -eq 0) {
            try {
                if (-not $DryRun) {
                    Remove-Item -Path $dir -Force
                    Write-Host "  ✅ Removed empty directory: $dir" -ForegroundColor Green
                } else {
                    Write-Host "  🔍 DRY RUN: Would remove empty directory: $dir" -ForegroundColor Yellow
                }
                $CleanedCount++
            } catch {
                Write-Host "  ❌ Failed to remove $dir`: $($_.Exception.Message)" -ForegroundColor Red
                $FailedCount++
            }
        }
    }
}

# Final cleanup summary
Write-Host "`n📊 FINAL CLEANUP SUMMARY" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Files moved: $MovedCount" -ForegroundColor Green
Write-Host "Files deleted: $DeletedCount" -ForegroundColor Green
Write-Host "Directories cleaned: $CleanedCount" -ForegroundColor Green
Write-Host "Operations failed: $FailedCount" -ForegroundColor Red

if ($DryRun) {
    Write-Host "`n🔍 DRY RUN COMPLETED - No files were actually moved or deleted" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ FINAL ROOT CLEANUP COMPLETED!" -ForegroundColor Green
    Write-Host "Root folder has been cleaned and organized" -ForegroundColor Green
}

# Show final root directory structure
Write-Host "`n📁 FINAL ROOT DIRECTORY STRUCTURE:" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

if (-not $DryRun) {
    Get-ChildItem -Path "." -Directory | Sort-Object Name | ForEach-Object {
        Write-Host "📁 $($_.Name)/" -ForegroundColor Blue
    }
    
    Get-ChildItem -Path "." -File | Sort-Object Name | ForEach-Object {
        Write-Host "📄 $($_.Name)" -ForegroundColor Green
    }
}
