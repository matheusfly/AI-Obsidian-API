# Master Cleanup Script
# This script orchestrates all cleanup operations using the configuration

param(
    [switch]$DryRun = $false,
    [switch]$Detailed = $false,
    [switch]$Force = $false,
    [string]$Mode = "comprehensive"  # comprehensive, aggressive, targeted, analysis
)

# Import configuration
. "$PSScriptRoot\cleanup_config.ps1"

# Set up logging
$LogFile = $Global:LogConfig.LogFile
$LogDir = Split-Path $LogFile -Parent
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $LogEntry
    if ($Level -eq "ERROR") {
        Write-Host $LogEntry -ForegroundColor Red
    } elseif ($Level -eq "WARNING") {
        Write-Host $LogEntry -ForegroundColor Yellow
    } else {
        Write-Host $LogEntry -ForegroundColor White
    }
}

Write-Log "Starting Master Cleanup Script" "INFO"
Write-Log "Mode: $Mode, DryRun: $DryRun, Detailed: $Detailed, Force: $Force" "INFO"

# Create backup directory
$BackupDir = Join-Path $Global:BackupConfig.BasePath "master_cleanup_$(Get-Date -Format $Global:BackupConfig.TimestampFormat)"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Log "Created backup directory: $BackupDir" "INFO"
}

# Initialize counters
$TotalFilesAnalyzed = 0
$TotalFilesRemoved = 0
$TotalFilesPreserved = 0
$TotalErrors = 0

# Function to analyze file
function Test-FileForCleanup {
    param([System.IO.FileInfo]$File)
    
    $TotalFilesAnalyzed++
    $isUnusual = $false
    $reason = ""
    
    # Check if it's essential
    if ($Global:EssentialFiles -contains $File.Name) {
        $TotalFilesPreserved++
        return @{ ShouldRemove = $false; Reason = "Essential file" }
    }
    
    # Check for unusual patterns
    foreach ($pattern in $Global:UnusualPatterns) {
        if ($File.Name -like $pattern) {
            $isUnusual = $true
            $reason = "Matches unusual pattern: $pattern"
            break
        }
    }
    
    # Check for duplicate scripts
    if ($Global:DuplicateScripts -contains $File.Name) {
        $isUnusual = $true
        $reason = "Duplicate script file"
    }
    
    # Check for empty files
    if ($File.Length -eq 0) {
        $isUnusual = $true
        $reason = "Empty file"
    }
    
    # Check for old test files
    if ($File.Name -like "*test*" -and $File.LastWriteTime -lt (Get-Date).AddDays(-$Global:AgeThresholds.OldTestFiles)) {
        $isUnusual = $true
        $reason = "Old test file (older than $($Global:AgeThresholds.OldTestFiles) days)"
    }
    
    if ($isUnusual) {
        return @{ ShouldRemove = $true; Reason = $reason }
    } else {
        $TotalFilesPreserved++
        return @{ ShouldRemove = $false; Reason = "Normal file" }
    }
}

# Function to safely remove file
function Remove-FileSafely {
    param([System.IO.FileInfo]$File, [string]$Reason)
    
    try {
        if ($Global:CleanupRules.BackupBeforeDelete) {
            $backupPath = Join-Path $BackupDir $File.Name
            Move-Item -Path $File.FullName -Destination $backupPath -Force
            Write-Log "Moved to backup: $($File.Name) - $Reason" "INFO"
        } else {
            Remove-Item -Path $File.FullName -Force
            Write-Log "Deleted: $($File.Name) - $Reason" "INFO"
        }
        $TotalFilesRemoved++
        return $true
    } catch {
        Write-Log "Failed to remove $($File.Name): $($_.Exception.Message)" "ERROR"
        $TotalErrors++
        return $false
    }
}

# Main cleanup logic based on mode
switch ($Mode.ToLower()) {
    "comprehensive" {
        Write-Log "Running comprehensive cleanup" "INFO"
        
        # Analyze root directory
        Write-Log "Analyzing root directory..." "INFO"
        Get-ChildItem -Path "." -File | ForEach-Object {
            $analysis = Test-FileForCleanup $_
            if ($analysis.ShouldRemove) {
                if (-not $DryRun) {
                    Remove-FileSafely $_ $analysis.Reason
                } else {
                    Write-Log "DRY RUN: Would remove $($_.Name) - $($analysis.Reason)" "WARNING"
                }
            }
        }
        
        # Analyze scripts directory
        if (Test-Path "scripts") {
            Write-Log "Analyzing scripts directory..." "INFO"
            Get-ChildItem -Path "scripts" -File | ForEach-Object {
                $analysis = Test-FileForCleanup $_
                if ($analysis.ShouldRemove) {
                    if (-not $DryRun) {
                        Remove-FileSafely $_ $analysis.Reason
                    } else {
                        Write-Log "DRY RUN: Would remove $($_.Name) - $($analysis.Reason)" "WARNING"
                    }
                }
            }
        }
    }
    
    "aggressive" {
        Write-Log "Running aggressive cleanup" "INFO"
        
        # Remove old files based on age thresholds
        Get-ChildItem -Path "." -File -Recurse | ForEach-Object {
            $analysis = Test-FileForCleanup $_
            if ($analysis.ShouldRemove -and $_.LastWriteTime -lt (Get-Date).AddDays(-$Global:AgeThresholds.OldTestFiles)) {
                if (-not $DryRun) {
                    Remove-FileSafely $_ "Old file (aggressive cleanup)"
                } else {
                    Write-Log "DRY RUN: Would remove old file $($_.Name)" "WARNING"
                }
            }
        }
    }
    
    "targeted" {
        Write-Log "Running targeted cleanup" "INFO"
        
        # Target specific file types
        $targetPatterns = @("*.log", "*.tmp", "*.bak", "*~")
        foreach ($pattern in $targetPatterns) {
            Get-ChildItem -Path "." -File -Filter $pattern -Recurse | ForEach-Object {
                if (-not $DryRun) {
                    Remove-FileSafely $_ "Targeted cleanup: $pattern"
                } else {
                    Write-Log "DRY RUN: Would remove $($_.Name) (targeted: $pattern)" "WARNING"
                }
            }
        }
    }
    
    "analysis" {
        Write-Log "Running analysis mode" "INFO"
        
        # Just analyze, don't remove anything
        Get-ChildItem -Path "." -File -Recurse | ForEach-Object {
            $analysis = Test-FileForCleanup $_
            Write-Log "File: $($_.Name) - $($analysis.Reason)" "INFO"
        }
    }
    
    default {
        Write-Log "Unknown mode: $Mode" "ERROR"
        exit 1
    }
}

# Generate summary report
Write-Log "Cleanup completed" "INFO"
Write-Log "Files analyzed: $TotalFilesAnalyzed" "INFO"
Write-Log "Files preserved: $TotalFilesPreserved" "INFO"
Write-Log "Files removed: $TotalFilesRemoved" "INFO"
Write-Log "Errors: $TotalErrors" "INFO"

if ($DryRun) {
    Write-Log "DRY RUN MODE - No files were actually removed" "WARNING"
} else {
    Write-Log "Backup location: $BackupDir" "INFO"
}

Write-Log "Master Cleanup Script completed" "INFO"
