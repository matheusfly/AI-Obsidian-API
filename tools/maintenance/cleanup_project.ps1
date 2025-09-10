# 🧹 **DATA VAULT OBSIDIAN - PROJECT CLEANUP SCRIPT**

# This script helps maintain the organized project structure
# Run this script regularly to keep the project clean

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false,
    [int]$LogDays = 7,
    [int]$ReportDays = 30
)

Write-Host "🧹 Starting Data Vault Obsidian Project Cleanup..." -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Function to move files safely
function Move-FileSafely {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Description
    )
    
    if (Test-Path $Source) {
        if ($DryRun) {
            Write-Host "DRY RUN: Would move $Source to $Destination" -ForegroundColor Yellow
        } else {
            try {
                Move-Item -Path $Source -Destination $Destination -Force
                Write-Host "✅ Moved $Description" -ForegroundColor Green
            } catch {
                Write-Host "❌ Failed to move $Source`: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}

# Function to clean old files
function Remove-OldFiles {
    param(
        [string]$Path,
        [int]$Days,
        [string]$Pattern,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        $cutoffDate = (Get-Date).AddDays(-$Days)
        $oldFiles = Get-ChildItem -Path $Path -Filter $Pattern | Where-Object { $_.LastWriteTime -lt $cutoffDate }
        
        if ($oldFiles.Count -gt 0) {
            if ($DryRun) {
                Write-Host "DRY RUN: Would remove $($oldFiles.Count) old $Description files" -ForegroundColor Yellow
            } else {
                $oldFiles | Remove-Item -Force
                Write-Host "🗑️ Removed $($oldFiles.Count) old $Description files" -ForegroundColor Green
            }
        } else {
            Write-Host "✅ No old $Description files to clean" -ForegroundColor Green
        }
    }
}

# Create directories if they don't exist
$directories = @(
    "temp_files\logs",
    "temp_files\reports", 
    "temp_files\test_results",
    "temp_files\json_data",
    "temp_files\scripts",
    "temp_files\backup"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "📁 Created directory: $dir" -ForegroundColor Blue
    }
}

Write-Host "`n🔄 Organizing files..." -ForegroundColor Cyan

# Move log files
Write-Host "📝 Moving log files..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "*.log" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "temp_files\logs\$($_.Name)" -Description "log file: $($_.Name)"
}

# Move report files
Write-Host "📊 Moving report files..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "*_REPORT*.md" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "temp_files\reports\$($_.Name)" -Description "report file: $($_.Name)"
}

# Move JSON data files
Write-Host "📄 Moving JSON data files..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "*.json" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "temp_files\json_data\$($_.Name)" -Description "JSON file: $($_.Name)"
}

# Move test scripts
Write-Host "🧪 Moving test scripts..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "test_*.py" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "test_suites\$($_.Name)" -Description "test script: $($_.Name)"
}

Get-ChildItem -Path "." -Filter "test_*.ps1" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "test_suites\$($_.Name)" -Description "test script: $($_.Name)"
}

# Move monitoring tools
Write-Host "📊 Moving monitoring tools..." -ForegroundColor Yellow
$monitoringFiles = @(
    "raw_data_capture.py",
    "realtime_log_monitor.py", 
    "tracing_analysis.py",
    "comprehensive_logging_suite.py",
    "monitoring_dashboard.py",
    "active_langsmith_testing.py",
    "simple_test.py"
)

foreach ($file in $monitoringFiles) {
    Move-FileSafely -Source $file -Destination "monitoring_tools\$file" -Description "monitoring tool: $file"
}

# Move core services
Write-Host "🔧 Moving core services..." -ForegroundColor Yellow
$coreServiceFiles = @(
    "langgraph_studio*.py",
    "run_langgraph_dev.py",
    "start_langgraph_dev.py"
)

foreach ($pattern in $coreServiceFiles) {
    Get-ChildItem -Path "." -Filter $pattern | ForEach-Object {
        Move-FileSafely -Source $_.FullName -Destination "core_services\$($_.Name)" -Description "core service: $($_.Name)"
    }
}

# Move deployment scripts
Write-Host "🚀 Moving deployment scripts..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "main_script*.ps1" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "deployment\$($_.Name)" -Description "deployment script: $($_.Name)"
}

Get-ChildItem -Path "." -Filter "uv_build_*.py" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "deployment\$($_.Name)" -Description "deployment script: $($_.Name)"
}

Get-ChildItem -Path "." -Filter "uv_build_*.ps1" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "deployment\$($_.Name)" -Description "deployment script: $($_.Name)"
}

# Move examples
Write-Host "💡 Moving examples..." -ForegroundColor Yellow
$exampleFiles = @(
    "mock_obsidian_api.py",
    "shadcn_dashboard.html"
)

foreach ($file in $exampleFiles) {
    Move-FileSafely -Source $file -Destination "examples\$file" -Description "example: $file"
}

# Move documentation
Write-Host "📚 Moving documentation..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "*.md" | Where-Object { $_.Name -ne "README.md" -and $_.Name -ne "PROJECT_ORGANIZATION.md" } | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "documentation\$($_.Name)" -Description "documentation: $($_.Name)"
}

# Move requirements
Write-Host "📦 Moving requirements..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Filter "requirements*.txt" | ForEach-Object {
    Move-FileSafely -Source $_.FullName -Destination "requirements\$($_.Name)" -Description "requirements: $($_.Name)"
}

Write-Host "`n🧹 Cleaning old files..." -ForegroundColor Cyan

# Clean old log files
Remove-OldFiles -Path "temp_files\logs" -Days $LogDays -Pattern "*.log" -Description "log"

# Clean old report files
Remove-OldFiles -Path "temp_files\reports" -Days $ReportDays -Pattern "*.md" -Description "report"

# Clean old JSON files
Remove-OldFiles -Path "temp_files\json_data" -Days $LogDays -Pattern "*.json" -Description "JSON data"

Write-Host "`n📊 Cleanup Summary:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

# Count files in each directory
$directories = @(
    "temp_files\logs",
    "temp_files\reports",
    "temp_files\test_results", 
    "temp_files\json_data",
    "test_suites",
    "monitoring_tools",
    "core_services",
    "deployment",
    "documentation",
    "examples",
    "requirements"
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        $fileCount = (Get-ChildItem -Path $dir -File).Count
        Write-Host "📁 $dir`: $fileCount files" -ForegroundColor White
    }
}

Write-Host "`n✅ Project cleanup completed!" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n⚠️ This was a DRY RUN - no files were actually moved or deleted" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to perform actual cleanup" -ForegroundColor Yellow
}

Write-Host "`n💡 Tips:" -ForegroundColor Cyan
Write-Host "- Run this script regularly to maintain organization" -ForegroundColor White
Write-Host "- Use -DryRun to see what would be cleaned without making changes" -ForegroundColor White
Write-Host "- Adjust -LogDays and -ReportDays parameters as needed" -ForegroundColor White
Write-Host "- Check temp_files\ directory for organized temporary files" -ForegroundColor White
