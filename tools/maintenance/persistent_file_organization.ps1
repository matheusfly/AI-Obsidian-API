# Persistent File Organization Script
# This script maintains persistent file and folder organization based on project rules

param(
    [switch]$DryRun = $false,
    [switch]$Detailed = $false,
    [string]$FeatureName = "",
    [string]$Action = "organize"  # organize, create_temp, move_to_definitive
)

# Import configuration
. "$PSScriptRoot\cleanup_config.ps1"

Write-Host "🗂️ PERSISTENT FILE ORGANIZATION SYSTEM" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be moved" -ForegroundColor Yellow
}

# Create comprehensive folder structure
$FolderStructure = @{
    "scripts" = @{
        "temp" = @{
            "active_tests" = "Active testing scripts"
            "feature_development" = "Feature development scripts"
            "experimental" = "Experimental scripts"
            "backup" = "Backup scripts"
            "generated_scripts" = "Auto-generated scripts"
        }
    }
    "temp_files" = @{
        "logs" = "Temporary log files"
        "reports" = "Temporary report files"
        "test_results" = "Temporary test results"
        "json_data" = "Temporary JSON data"
        "scripts" = "Temporary scripts"
        "backup" = "Backup files"
    }
    "reports" = @{
        "success_reports" = "Success reports"
        "changelogs" = "Changelog entries"
        "analysis" = "Analysis reports"
        "testing" = "Testing reports"
        "deployment" = "Deployment reports"
    }
}

# Function to create folder structure
function New-FolderStructure {
    param([hashtable]$Structure, [string]$BasePath = ".")
    
    foreach ($folder in $Structure.GetEnumerator()) {
        $folderPath = Join-Path $BasePath $folder.Key
        if (-not (Test-Path $folderPath)) {
            New-Item -ItemType Directory -Path $folderPath -Force | Out-Null
            Write-Host "  ✅ Created: $folderPath" -ForegroundColor Green
        }
        
        if ($folder.Value -is [hashtable]) {
            New-FolderStructure -Structure $folder.Value -BasePath $folderPath
        }
    }
}

# Function to create feature-specific temp folder
function New-FeatureTempFolder {
    param([string]$FeatureName)
    
    if ([string]::IsNullOrEmpty($FeatureName)) {
        Write-Host "  ❌ Feature name is required for temp folder creation" -ForegroundColor Red
        return
    }
    
    $FeatureTempDirs = @(
        "scripts\temp\feature_development\$FeatureName",
        "scripts\temp\active_tests\$FeatureName",
        "temp_files\feature_development\$FeatureName",
        "temp_files\logs\$FeatureName",
        "temp_files\reports\$FeatureName"
    )
    
    foreach ($dir in $FeatureTempDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "  ✅ Created feature temp folder: $dir" -ForegroundColor Green
        }
    }
}

# Function to move files to definitive locations
function Move-FilesToDefinitive {
    param([string]$FeatureName)
    
    $DefinitiveMappings = @{
        "core_services" = @("*.py", "*.js", "*.ts")
        "monitoring_tools" = @("*monitor*.py", "*logging*.py", "*tracing*.py")
        "test_suites" = @("test_*.py", "*_test.py", "test_*.ps1")
        "deployment" = @("*.ps1", "deploy*.py", "build*.py")
        "mcp_tools" = @("*mcp*.py", "*server*.py")
        "langgraph_workflows" = @("*agent*.py", "*workflow*.py")
        "utils" = @("util*.py", "helper*.py", "common*.py")
    }
    
    $MovedCount = 0
    
    foreach ($mapping in $DefinitiveMappings.GetEnumerator()) {
        $targetDir = $mapping.Key
        $patterns = $mapping.Value
        
        foreach ($pattern in $patterns) {
            $files = Get-ChildItem -Path "." -File -Filter $pattern -Recurse | Where-Object { 
                $_.DirectoryName -notlike "*$targetDir*" -and 
                $_.DirectoryName -like "*$FeatureName*" 
            }
            
            foreach ($file in $files) {
                try {
                    $destPath = Join-Path $targetDir $file.Name
                    if (-not $DryRun) {
                        Move-Item -Path $file.FullName -Destination $destPath -Force
                        Write-Host "  ✅ Moved to definitive: $($file.Name) → $targetDir" -ForegroundColor Green
                    } else {
                        Write-Host "  🔍 DRY RUN: Would move $($file.Name) → $targetDir" -ForegroundColor Yellow
                    }
                    $MovedCount++
                } catch {
                    Write-Host "  ❌ Failed to move $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        }
    }
    
    return $MovedCount
}

# Function to clean up temp files
function Clean-TempFiles {
    param([string]$FeatureName = "")
    
    $TempPatterns = @(
        "*.tmp",
        "*.temp", 
        "*.log",
        "*~",
        "*.bak"
    )
    
    $CleanedCount = 0
    
    foreach ($pattern in $TempPatterns) {
        $tempFiles = Get-ChildItem -Path "." -File -Filter $pattern -Recurse | Where-Object {
            if ([string]::IsNullOrEmpty($FeatureName)) {
                $_.DirectoryName -like "*temp*"
            } else {
                $_.DirectoryName -like "*$FeatureName*" -and $_.DirectoryName -like "*temp*"
            }
        }
        
        foreach ($file in $tempFiles) {
            try {
                if (-not $DryRun) {
                    Remove-Item -Path $file.FullName -Force
                    Write-Host "  ✅ Cleaned temp file: $($file.Name)" -ForegroundColor Green
                } else {
                    Write-Host "  🔍 DRY RUN: Would clean $($file.Name)" -ForegroundColor Yellow
                }
                $CleanedCount++
            } catch {
                Write-Host "  ❌ Failed to clean $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    
    return $CleanedCount
}

# Main execution based on action
switch ($Action.ToLower()) {
    "organize" {
        Write-Host "`n📁 CREATING FOLDER STRUCTURE..." -ForegroundColor Yellow
        New-FolderStructure -Structure $FolderStructure
        
        Write-Host "`n🧹 CLEANING TEMP FILES..." -ForegroundColor Yellow
        $cleanedCount = Clean-TempFiles
        Write-Host "  Cleaned $cleanedCount temp files" -ForegroundColor Green
    }
    
    "create_temp" {
        Write-Host "`n📁 CREATING FEATURE TEMP FOLDERS..." -ForegroundColor Yellow
        New-FeatureTempFolder -FeatureName $FeatureName
    }
    
    "move_to_definitive" {
        Write-Host "`n📦 MOVING FILES TO DEFINITIVE LOCATIONS..." -ForegroundColor Yellow
        $movedCount = Move-FilesToDefinitive -FeatureName $FeatureName
        Write-Host "  Moved $movedCount files to definitive locations" -ForegroundColor Green
    }
    
    default {
        Write-Host "`n❌ Unknown action: $Action" -ForegroundColor Red
        Write-Host "Valid actions: organize, create_temp, move_to_definitive" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n✅ PERSISTENT FILE ORGANIZATION COMPLETED!" -ForegroundColor Green
