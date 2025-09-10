# Comprehensive Cleanup Script for Data Vault Obsidian
# This script identifies and removes unusual files while preserving essential ones

param(
    [switch]$DryRun = $false,
    [switch]$Detailed = $false
)

Write-Host "🧹 COMPREHENSIVE CLEANUP SCRIPT" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be deleted" -ForegroundColor Yellow
}

# Define essential files that should NEVER be deleted
$EssentialFiles = @(
    "README.md",
    "PROJECT_ORGANIZATION.md",
    "docker-compose.yml",
    "requirements.txt",
    "pyproject.toml",
    "uv.lock",
    "mcp.json",
    "langgraph.json"
)

# Define essential directories
$EssentialDirs = @(
    "core_services",
    "monitoring_tools", 
    "test_suites",
    "documentation",
    "deployment",
    "examples",
    "requirements",
    "temp_files",
    "reports",
    "docs",
    "mcp_tools",
    "langgraph_workflows",
    "api_gateway",
    "config",
    "data",
    "data_pipeline",
    "graph_db",
    "indexer",
    "langgraph_project",
    "langgraph_server",
    "logs",
    "monitoring",
    "tests",
    "utils",
    "vector_db",
    "vault",
    "context-cache",
    "image"
)

# Define patterns for unusual files
$UnusualPatterns = @(
    "*test*test*",           # Multiple test in name
    "*final*final*",         # Multiple final in name
    "*ultimate*ultimate*",   # Multiple ultimate in name
    "*110*110*",             # Multiple 110 in name
    "*achievement*achievement*", # Multiple achievement in name
    "*110-percent*110-percent*", # Multiple 110-percent in name
    "*hotfix*hotfix*",       # Multiple hotfix in name
    "*simple*simple*",       # Multiple simple in name
    "*debug*debug*",         # Multiple debug in name
    "*diagnostic*diagnostic*" # Multiple diagnostic in name
)

# Define duplicate script patterns
$DuplicateScripts = @(
    "achieve-110-percent-final.ps1",
    "achieve-110-percent.ps1", 
    "final-110-percent-achievement.ps1",
    "final-110-percent-test.ps1",
    "mission-accomplished-110.ps1",
    "ultimate-110-achievement.ps1",
    "ultimate-110-percent-achievement.ps1",
    "ultimate-110-percent-cli.ps1",
    "ultimate-110-percent-final.ps1",
    "ultimate-110-percent-test.ps1",
    "ultimate-performance-test.ps1",
    "build-v0_1.ps1",
    "build-v0_2.ps1", 
    "build-v0_3.ps1",
    "simple-hotfix.ps1",
    "hotfix-deploy.ps1",
    "simple-observability-setup.ps1",
    "setup-observability-simple.ps1",
    "setup-observability-complete.ps1",
    "ultimate-observability-setup.ps1",
    "simple-agent-revival.ps1",
    "agent-revival-no-emoji.ps1",
    "ultimate-agent-revival.ps1",
    "simple-start.ps1",
    "start-all-services.ps1",
    "quick-diagnostic.ps1",
    "quick-fix.ps1",
    "debug-system.ps1",
    "ultimate-diagnostic-and-fix.ps1",
    "final-test-suite.ps1",
    "final-test.ps1",
    "run-tests-debug.ps1",
    "test-mcp.ps1"
)

# Create backup directory
$BackupDir = "temp_files\backup\comprehensive_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$FilesToDelete = @()
$FilesToKeep = @()

Write-Host "`n🔍 ANALYZING FILES..." -ForegroundColor Yellow

# Check root directory for unusual files
Get-ChildItem -Path "." -File | ForEach-Object {
    $file = $_
    $isUnusual = $false
    $reason = ""
    
    # Check if it's essential
    if ($EssentialFiles -contains $file.Name) {
        $FilesToKeep += $file
        return
    }
    
    # Check for unusual patterns
    foreach ($pattern in $UnusualPatterns) {
        if ($file.Name -like $pattern) {
            $isUnusual = $true
            $reason = "Matches unusual pattern: $pattern"
            break
        }
    }
    
    # Check for duplicate scripts
    if ($DuplicateScripts -contains $file.Name) {
        $isUnusual = $true
        $reason = "Duplicate script file"
    }
    
    # Check for old test files (older than 7 days)
    if ($file.Name -like "*test*" -and $file.LastWriteTime -lt (Get-Date).AddDays(-7)) {
        $isUnusual = $true
        $reason = "Old test file (older than 7 days)"
    }
    
    # Check for empty files
    if ($file.Length -eq 0) {
        $isUnusual = $true
        $reason = "Empty file"
    }
    
    if ($isUnusual) {
        $FilesToDelete += @{
            File = $file
            Reason = $reason
        }
    } else {
        $FilesToKeep += $file
    }
}

# Check scripts directory specifically
Write-Host "`n🔍 ANALYZING SCRIPTS DIRECTORY..." -ForegroundColor Yellow

Get-ChildItem -Path "scripts" -File | ForEach-Object {
    $file = $_
    $isUnusual = $false
    $reason = ""
    
    # Check for duplicate scripts
    if ($DuplicateScripts -contains $file.Name) {
        $isUnusual = $true
        $reason = "Duplicate script file"
    }
    
    # Check for unusual patterns
    foreach ($pattern in $UnusualPatterns) {
        if ($file.Name -like $pattern) {
            $isUnusual = $true
            $reason = "Matches unusual pattern: $pattern"
            break
        }
    }
    
    # Check for old test files
    if ($file.Name -like "*test*" -and $file.LastWriteTime -lt (Get-Date).AddDays(-7)) {
        $isUnusual = $true
        $reason = "Old test file (older than 7 days)"
    }
    
    # Check for very similar names (potential duplicates)
    $similarFiles = Get-ChildItem -Path "scripts" -File | Where-Object { 
        $_.Name -ne $file.Name -and 
        $_.Name -replace '[0-9_-]', '' -eq $file.Name -replace '[0-9_-]', ''
    }
    
    if ($similarFiles.Count -gt 0) {
        $isUnusual = $true
        $reason = "Similar file exists: $($similarFiles[0].Name)"
    }
    
    if ($isUnusual) {
        $FilesToDelete += @{
            File = $file
            Reason = $reason
        }
    } else {
        $FilesToKeep += $file
    }
}

# Display results
Write-Host "`n📊 CLEANUP ANALYSIS RESULTS" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "Files to keep: $($FilesToKeep.Count)" -ForegroundColor Green
Write-Host "Files to delete: $($FilesToDelete.Count)" -ForegroundColor Red

if ($Detailed) {
    Write-Host "`n📋 FILES TO KEEP:" -ForegroundColor Green
    $FilesToKeep | ForEach-Object { Write-Host "  ✅ $($_.Name)" -ForegroundColor Green }
}

Write-Host "`n🗑️ FILES TO DELETE:" -ForegroundColor Red
$FilesToDelete | ForEach-Object { 
    Write-Host "  ❌ $($_.File.Name) - $($_.Reason)" -ForegroundColor Red 
}

# Perform cleanup
if ($FilesToDelete.Count -gt 0) {
    if ($DryRun) {
        Write-Host "`n🔍 DRY RUN: Would delete $($FilesToDelete.Count) files" -ForegroundColor Yellow
    } else {
        Write-Host "`n🗑️ DELETING FILES..." -ForegroundColor Red
        
        $deletedCount = 0
        $failedCount = 0
        
        foreach ($item in $FilesToDelete) {
            try {
                # Move to backup first
                $backupPath = Join-Path $BackupDir $item.File.Name
                Move-Item -Path $item.File.FullName -Destination $backupPath -Force
                Write-Host "  ✅ Moved to backup: $($item.File.Name)" -ForegroundColor Green
                $deletedCount++
            } catch {
                Write-Host "  ❌ Failed to move $($item.File.Name): $($_.Exception.Message)" -ForegroundColor Red
                $failedCount++
            }
        }
        
        Write-Host "`n📊 CLEANUP COMPLETED" -ForegroundColor Cyan
        Write-Host "Files moved to backup: $deletedCount" -ForegroundColor Green
        Write-Host "Failed to move: $failedCount" -ForegroundColor Red
        Write-Host "Backup location: $BackupDir" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n✅ No unusual files found to delete!" -ForegroundColor Green
}

Write-Host "`n🎯 CLEANUP COMPLETE!" -ForegroundColor Cyan
