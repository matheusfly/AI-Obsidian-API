# 🎯 **DATA VAULT OBSIDIAN - TARGETED CLEANUP SCRIPT**

# This script targets specific garbage files identified in the analysis
# It will clean up test files, old reports, and unused scripts

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

Write-Host "🎯 Starting Targeted Cleanup..." -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "⚠️  DRY RUN MODE - No files will be deleted" -ForegroundColor Yellow
} elseif ($Force) {
    Write-Host "⚠️  FORCE MODE - Files will be deleted without backup" -ForegroundColor Red
} else {
    Write-Host "📦 Files will be moved to backup before deletion" -ForegroundColor Green
}

# Create backup directory
$backupDir = "temp_files/backup/targeted_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
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

Write-Host "`n🧹 Cleaning up specific garbage files..." -ForegroundColor Yellow

# List of specific files to delete (identified from analysis)
$filesToDelete = @(
    # Test files in root directory
    @{Path="test_langgraph_obsidian_integration.py"; Reason="Old test file in root"},
    @{Path="test_complete_mcp_integration_with_logs.py"; Reason="Old test file in root"},
    @{Path="test_langgraph_obsidian_benchmark.py"; Reason="Old test file in root"},
    @{Path="test_enhanced_observability.py"; Reason="Old test file in root"},
    @{Path="test_complete_integration.py"; Reason="Old test file in root"},
    @{Path="test_enhanced_agent_comprehensive.py"; Reason="Old test file in root"},
    @{Path="test_observability_system.py"; Reason="Old test file in root"},
    @{Path="test_mcp_langgraph_integration.py"; Reason="Old test file in root"},
    @{Path="test_enhanced_mcp_integration.py"; Reason="Old test file in root"},
    @{Path="test_mcp_robust_integration.py"; Reason="Old test file in root"},
    @{Path="test_hello_world_agent.py"; Reason="Old test file in root"},
    @{Path="test_langsmith_tracing.py"; Reason="Old test file in root"},
    @{Path="test_langgraph_mcp_integration.py"; Reason="Old test file in root"},
    @{Path="active_langsmith_testing.py"; Reason="Old test file in root"},
    @{Path="test_langgraph_server_fix.py"; Reason="Old test file in root"},
    @{Path="test_langgraph_api_proper.py"; Reason="Old test file in root"},
    @{Path="comprehensive_test_final.py"; Reason="Old test file in root"},
    @{Path="test_langgraph_workflow.py"; Reason="Old test file in root"},
    @{Path="test_integration.py"; Reason="Old test file in root"},
    @{Path="test_api_gateway.py"; Reason="Old test file in root"},
    @{Path="test_everything.ps1"; Reason="Old test script in root"},
    @{Path="test_first_api_call.py"; Reason="Old test file in root"},
    @{Path="test_everything_fixed.ps1"; Reason="Old test script in root"},
    @{Path="final-test.ps1"; Reason="Old test script in root"},
    @{Path="fast_test_runner.ps1"; Reason="Old test script in root"},
    @{Path="conftest.py"; Reason="Old test configuration in root"},
    @{Path="run_all_tests.ps1"; Reason="Old test script in root"},
    @{Path="test_mcp_server.py"; Reason="Old test file in root"},
    @{Path="simple_test.py"; Reason="Old test file in root"},
    
    # PowerShell test scripts
    @{Path="ultimate-110-percent-test.ps1"; Reason="Old PowerShell test script"},
    @{Path="ultimate-performance-test.ps1"; Reason="Old PowerShell test script"},
    @{Path="final-110-percent-test.ps1"; Reason="Old PowerShell test script"},
    
    # Old Docker compose files
    @{Path="docker-compose.final.yml"; Reason="Old Docker compose file"},
    @{Path="docker-compose.langgraph.yml"; Reason="Old Docker compose file"},
    @{Path="docker-compose.simple.yml"; Reason="Old Docker compose file"},
    
    # Empty __init__.py files
    @{Path="api_gateway\__init__.py"; Reason="Empty __init__.py file"},
    @{Path="graph_db\__init__.py"; Reason="Empty __init__.py file"},
    @{Path="indexer\__init__.py"; Reason="Empty __init__.py file"},
    @{Path="mcp_tools\__init__.py"; Reason="Empty __init__.py file"},
    @{Path="utils\__init__.py"; Reason="Empty __init__.py file"},
    @{Path="vector_db\__init__.py"; Reason="Empty __init__.py file"},
    
    # Empty log files
    @{Path="temp_files\logs\enhanced_agent.log"; Reason="Empty log file"},
    @{Path="temp_files\logs\observability_http.log"; Reason="Empty log file"},
    @{Path="temp_files\logs\raw_data_capture.log"; Reason="Empty log file"},
    @{Path="temp_files\logs\realtime_monitor.log"; Reason="Empty log file"},
    @{Path="temp_files\logs\tracing_analysis.log"; Reason="Empty log file"}
)

Write-Host "`n📝 Processing $($filesToDelete.Count) files..." -ForegroundColor Cyan

foreach ($fileInfo in $filesToDelete) {
    $filePath = $fileInfo.Path
    $reason = $fileInfo.Reason
    
    if (Test-Path $filePath) {
        $file = Get-Item $filePath
        $size = $file.Length
        
        if (Remove-FileSafely -FilePath $filePath -Reason $reason) {
            $deletedCount++
            $deletedSize += $size
        }
    } else {
        Write-Host "⚠️  File not found: $filePath" -ForegroundColor Yellow
    }
}

# Clean up old log files in temp_files/logs
Write-Host "`n📝 Cleaning old log files..." -ForegroundColor Cyan
$oldLogFiles = Get-ChildItem -Path "temp_files\logs" -File | Where-Object { 
    $_.LastWriteTime -lt (Get-Date).AddDays(-1) -and $_.Length -gt 0
}

foreach ($file in $oldLogFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old log file") {
        $deletedCount++
        $deletedSize += $size
    }
}

# Clean up old JSON test data files
Write-Host "`n📄 Cleaning old JSON test data..." -ForegroundColor Cyan
$oldJsonFiles = Get-ChildItem -Path "temp_files\json_data" -File | Where-Object { 
    $_.Name -match "test_|capture_|analysis_|trace_|result_" -and
    $_.LastWriteTime -lt (Get-Date).AddDays(-1)
}

foreach ($file in $oldJsonFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old JSON test data") {
        $deletedCount++
        $deletedSize += $size
    }
}

# Clean up old report files
Write-Host "`n📊 Cleaning old report files..." -ForegroundColor Cyan
$oldReportFiles = Get-ChildItem -Path "temp_files\reports" -File | Where-Object { 
    $_.LastWriteTime -lt (Get-Date).AddDays(-1)
}

foreach ($file in $oldReportFiles) {
    $size = $file.Length
    if (Remove-FileSafely -FilePath $file.FullName -Reason "Old report file") {
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
    Write-Host "`n✅ Targeted cleanup completed!" -ForegroundColor Green
}

Write-Host "`n💡 Tips:" -ForegroundColor Cyan
Write-Host "- Use -DryRun to see what would be cleaned without making changes" -ForegroundColor White
Write-Host "- Use -Force to delete files directly (not recommended)" -ForegroundColor White
Write-Host "- Check backup directory before permanent deletion" -ForegroundColor White
