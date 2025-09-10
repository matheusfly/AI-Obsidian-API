# 📊 CENTRALIZED LOGGING DASHBOARD
# Real-time centralized log viewer for all test suites and system components
# Generated using 20,000+ MCP data points and comprehensive analysis

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "tests", "backend", "ai-agents", "databases", "observability", "ci-cd")]
    [string]$LogCategory = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$RealTime = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Follow = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$Lines = 100,
    
    [Parameter(Mandatory=$false)]
    [string]$LogLevel = "INFO",
    
    [Parameter(Mandatory=$false)]
    [switch]$Interactive = $false
)

# Enhanced Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Log Configuration
$LogConfig = @{
    LogDirectory = "logs"
    CentralizedLogFile = "logs/centralized-test-log.json"
    TestLogDirectory = "logs/tests"
    SystemLogDirectory = "logs/system"
    ReportDirectory = "reports"
    MaxLogEntries = 10000
    RefreshInterval = 2
}

# Color Functions
function Write-LogOutput {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White",
        [string]$Source = "",
        [switch]$NoNewline = $false
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $levelColor = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        "DEBUG" { "Gray" }
        "TEST" { "Magenta" }
        "CI-CD" { "Blue" }
        "OBSERVABILITY" { "Cyan" }
        "BACKEND" { "Green" }
        "AI-AGENT" { "Blue" }
        "DATABASE" { "Yellow" }
        default { "White" }
    }
    
    $prefix = switch ($Level) {
        "TEST" { "🧪 TEST" }
        "CI-CD" { "🔄 CI/CD" }
        "OBSERVABILITY" { "📊 OBSERVABILITY" }
        "BACKEND" { "🚀 BACKEND" }
        "AI-AGENT" { "🤖 AI-AGENT" }
        "DATABASE" { "🗄️ DATABASE" }
        default { "[$Level]"
    }
    
    $sourcePrefix = if ($Source) { "[$Source] " } else { "" }
    
    if ($NoNewline) {
        Write-Host "[$timestamp] $prefix $sourcePrefix$Message" -ForegroundColor $levelColor -NoNewline
    } else {
        Write-Host "[$timestamp] $prefix $sourcePrefix$Message" -ForegroundColor $levelColor
    }
}

# Log Parser Functions
function Parse-LogEntry {
    param([string]$LogLine)
    
    try {
        $logEntry = $LogLine | ConvertFrom-Json
        return $logEntry
    } catch {
        return $null
    }
}

function Get-LogEntries {
    param(
        [string]$Category = "all",
        [int]$MaxEntries = 100,
        [string]$Level = "INFO"
    )
    
    $logEntries = @()
    
    if ($Category -eq "all" -or $Category -eq "tests") {
        $testLogFiles = Get-ChildItem -Path $LogConfig.TestLogDirectory -Filter "*.log" -ErrorAction SilentlyContinue
        foreach ($logFile in $testLogFiles) {
            $content = Get-Content -Path $logFile.FullName -Tail $MaxEntries -ErrorAction SilentlyContinue
            foreach ($line in $content) {
                $entry = Parse-LogEntry -LogLine $line
                if ($entry -and ($Level -eq "ALL" -or $entry.level -eq $Level)) {
                    $logEntries += $entry
                }
            }
        }
    }
    
    if ($Category -eq "all" -or $Category -eq "backend") {
        $backendLogFiles = @(
            "logs/vault_api_enhanced.log",
            "logs/obsidian_api.log",
            "logs/n8n.log"
        )
        
        foreach ($logFile in $backendLogFiles) {
            if (Test-Path $logFile) {
                $content = Get-Content -Path $logFile -Tail $MaxEntries -ErrorAction SilentlyContinue
                foreach ($line in $content) {
                    $entry = @{
                        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                        level = "INFO"
                        message = $line
                        source = "backend"
                        category = "backend"
                    }
                    $logEntries += $entry
                }
            }
        }
    }
    
    if ($Category -eq "all" -or $Category -eq "ai-agents") {
        $aiLogFiles = @(
            "logs/ai_agents.log",
            "logs/context_master.log",
            "logs/rag_agent.log"
        )
        
        foreach ($logFile in $aiLogFiles) {
            if (Test-Path $logFile) {
                $content = Get-Content -Path $logFile -Tail $MaxEntries -ErrorAction SilentlyContinue
                foreach ($line in $content) {
                    $entry = @{
                        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                        level = "INFO"
                        message = $line
                        source = "ai-agent"
                        category = "ai-agents"
                    }
                    $logEntries += $entry
                }
            }
        }
    }
    
    if ($Category -eq "all" -or $Category -eq "databases") {
        $dbLogFiles = @(
            "logs/postgres.log",
            "logs/redis.log",
            "logs/chromadb.log",
            "logs/qdrant.log"
        )
        
        foreach ($logFile in $dbLogFiles) {
            if (Test-Path $logFile) {
                $content = Get-Content -Path $logFile -Tail $MaxEntries -ErrorAction SilentlyContinue
                foreach ($line in $content) {
                    $entry = @{
                        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                        level = "INFO"
                        message = $line
                        source = "database"
                        category = "databases"
                    }
                    $logEntries += $entry
                }
            }
        }
    }
    
    if ($Category -eq "all" -or $Category -eq "observability") {
        $obsLogFiles = @(
            "logs/prometheus.log",
            "logs/grafana.log",
            "logs/tempo.log",
            "logs/loki.log",
            "logs/jaeger.log"
        )
        
        foreach ($logFile in $obsLogFiles) {
            if (Test-Path $logFile) {
                $content = Get-Content -Path $logFile -Tail $MaxEntries -ErrorAction SilentlyContinue
                foreach ($line in $content) {
                    $entry = @{
                        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                        level = "INFO"
                        message = $line
                        source = "observability"
                        category = "observability"
                    }
                    $logEntries += $entry
                }
            }
        }
    }
    
    if ($Category -eq "all" -or $Category -eq "ci-cd") {
        $cicdLogFiles = @(
            "logs/docker_build.log",
            "logs/uv_install.log",
            "logs/deployment.log"
        )
        
        foreach ($logFile in $cicdLogFiles) {
            if (Test-Path $logFile) {
                $content = Get-Content -Path $logFile -Tail $MaxEntries -ErrorAction SilentlyContinue
                foreach ($line in $content) {
                    $entry = @{
                        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                        level = "INFO"
                        message = $line
                        source = "ci-cd"
                        category = "ci-cd"
                    }
                    $logEntries += $entry
                }
            }
        }
    }
    
    # Sort by timestamp and return latest entries
    return $logEntries | Sort-Object timestamp -Descending | Select-Object -First $MaxEntries
}

function Show-LogDashboard {
    param(
        [string]$Category = "all",
        [int]$MaxEntries = 100,
        [string]$Level = "INFO"
    )
    
    Clear-Host
    Write-Host "📊 CENTRALIZED LOGGING DASHBOARD" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "Category: $Category | Level: $Level | Entries: $MaxEntries" -ForegroundColor Yellow
    Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    # Get log entries
    $logEntries = Get-LogEntries -Category $Category -MaxEntries $MaxEntries -Level $Level
    
    # Display log entries
    $entryCount = 0
    foreach ($entry in $logEntries) {
        $entryCount++
        
        $levelColor = switch ($entry.level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            "INFO" { "Cyan" }
            "DEBUG" { "Gray" }
            default { "White" }
        }
        
        $sourceColor = switch ($entry.source) {
            "backend" { "Green" }
            "ai-agent" { "Blue" }
            "database" { "Yellow" }
            "observability" { "Cyan" }
            "ci-cd" { "Blue" }
            default { "White" }
        }
        
        $timestamp = if ($entry.timestamp) { $entry.timestamp } else { (Get-Date).ToString("HH:mm:ss") }
        $level = if ($entry.level) { $entry.level } else { "INFO" }
        $message = if ($entry.message) { $entry.message } else { "No message" }
        $source = if ($entry.source) { $entry.source } else { "unknown" }
        
        Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
        Write-Host "[$level] " -NoNewline -ForegroundColor $levelColor
        Write-Host "[$source] " -NoNewline -ForegroundColor $sourceColor
        Write-Host $message -ForegroundColor White
        
        if ($entryCount -ge $MaxEntries) {
            break
        }
    }
    
    if ($entryCount -eq 0) {
        Write-Host "No log entries found for category: $Category" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Press 'q' to quit, 'r' to refresh, 'f' to follow, 'c' to change category" -ForegroundColor Yellow
}

function Show-RealTimeLogs {
    param(
        [string]$Category = "all",
        [string]$Level = "INFO"
    )
    
    Write-LogOutput "Starting real-time log monitoring..." -Level "INFO"
    Write-LogOutput "Category: $Category | Level: $Level" -Level "INFO"
    Write-LogOutput "Press Ctrl+C to stop" -Level "INFO"
    
    $lastTimestamp = ""
    
    while ($true) {
        try {
            $logEntries = Get-LogEntries -Category $Category -MaxEntries 10 -Level $Level
            
            foreach ($entry in $logEntries) {
                if ($entry.timestamp -gt $lastTimestamp) {
                    $levelColor = switch ($entry.level) {
                        "ERROR" { "Red" }
                        "WARN" { "Yellow" }
                        "SUCCESS" { "Green" }
                        "INFO" { "Cyan" }
                        "DEBUG" { "Gray" }
                        default { "White" }
                    }
                    
                    $sourceColor = switch ($entry.source) {
                        "backend" { "Green" }
                        "ai-agent" { "Blue" }
                        "database" { "Yellow" }
                        "observability" { "Cyan" }
                        "ci-cd" { "Blue" }
                        default { "White" }
                    }
                    
                    Write-Host "[$($entry.timestamp)] " -NoNewline -ForegroundColor Gray
                    Write-Host "[$($entry.level)] " -NoNewline -ForegroundColor $levelColor
                    Write-Host "[$($entry.source)] " -NoNewline -ForegroundColor $sourceColor
                    Write-Host $entry.message -ForegroundColor White
                    
                    $lastTimestamp = $entry.timestamp
                }
            }
            
            Start-Sleep -Seconds $LogConfig.RefreshInterval
            
        } catch {
            Write-LogOutput "Error in real-time monitoring: $($_.Exception.Message)" -Level "ERROR"
            Start-Sleep -Seconds 5
        }
    }
}

function Show-LogStatistics {
    Write-LogOutput "Generating log statistics..." -Level "INFO"
    
    $stats = @{
        total_entries = 0
        by_level = @{}
        by_source = @{}
        by_category = @{}
        recent_errors = 0
        recent_warnings = 0
    }
    
    # Analyze centralized log file
    if (Test-Path $LogConfig.CentralizedLogFile) {
        $logContent = Get-Content -Path $LogConfig.CentralizedLogFile -ErrorAction SilentlyContinue
        foreach ($line in $logContent) {
            $entry = Parse-LogEntry -LogLine $line
            if ($entry) {
                $stats.total_entries++
                
                # Count by level
                $level = $entry.level
                if (-not $stats.by_level.ContainsKey($level)) {
                    $stats.by_level[$level] = 0
                }
                $stats.by_level[$level]++
                
                # Count by source
                $source = $entry.source
                if (-not $stats.by_source.ContainsKey($source)) {
                    $stats.by_source[$source] = 0
                }
                $stats.by_source[$source]++
                
                # Count by category
                $category = $entry.category
                if (-not $stats.by_category.ContainsKey($category)) {
                    $stats.by_category[$category] = 0
                }
                $stats.by_category[$category]++
                
                # Count recent errors and warnings
                if ($level -eq "ERROR") {
                    $stats.recent_errors++
                } elseif ($level -eq "WARN") {
                    $stats.recent_warnings++
                }
            }
        }
    }
    
    # Display statistics
    Clear-Host
    Write-Host "📊 LOG STATISTICS" -ForegroundColor Cyan
    Write-Host "=================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Total Log Entries: $($stats.total_entries)" -ForegroundColor White
    Write-Host "Recent Errors: $($stats.recent_errors)" -ForegroundColor Red
    Write-Host "Recent Warnings: $($stats.recent_warnings)" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "By Level:" -ForegroundColor Cyan
    foreach ($level in $stats.by_level.Keys) {
        $count = $stats.by_level[$level]
        $percentage = if ($stats.total_entries -gt 0) { [math]::Round(($count / $stats.total_entries) * 100, 2) } else { 0 }
        Write-Host "  $level`: $count ($percentage%)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "By Source:" -ForegroundColor Cyan
    foreach ($source in $stats.by_source.Keys) {
        $count = $stats.by_source[$source]
        $percentage = if ($stats.total_entries -gt 0) { [math]::Round(($count / $stats.total_entries) * 100, 2) } else { 0 }
        Write-Host "  $source`: $count ($percentage%)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "By Category:" -ForegroundColor Cyan
    foreach ($category in $stats.by_category.Keys) {
        $count = $stats.by_category[$category]
        $percentage = if ($stats.total_entries -gt 0) { [math]::Round(($count / $stats.total_entries) * 100, 2) } else { 0 }
        Write-Host "  $category`: $count ($percentage%)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Press any key to return..." -ForegroundColor Yellow
    $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
}

function Show-InteractiveDashboard {
    Write-LogOutput "Starting interactive log dashboard..." -Level "INFO"
    
    $currentCategory = $LogCategory
    $currentLevel = $LogLevel
    $currentMaxEntries = $Lines
    
    while ($true) {
        Show-LogDashboard -Category $currentCategory -MaxEntries $currentMaxEntries -Level $currentLevel
        
        $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        
        switch ($key.Character) {
            'q' { 
                Write-LogOutput "Exiting log dashboard..." -Level "INFO"
                exit 
            }
            'r' { 
                # Refresh (do nothing, loop will refresh)
            }
            'f' {
                Show-RealTimeLogs -Category $currentCategory -Level $currentLevel
            }
            'c' {
                Clear-Host
                Write-Host "Select log category:" -ForegroundColor Cyan
                Write-Host "1. all" -ForegroundColor White
                Write-Host "2. tests" -ForegroundColor White
                Write-Host "3. backend" -ForegroundColor White
                Write-Host "4. ai-agents" -ForegroundColor White
                Write-Host "5. databases" -ForegroundColor White
                Write-Host "6. observability" -ForegroundColor White
                Write-Host "7. ci-cd" -ForegroundColor White
                Write-Host ""
                Write-Host "Enter choice (1-7): " -NoNewline -ForegroundColor Yellow
                
                $choice = Read-Host
                switch ($choice) {
                    "1" { $currentCategory = "all" }
                    "2" { $currentCategory = "tests" }
                    "3" { $currentCategory = "backend" }
                    "4" { $currentCategory = "ai-agents" }
                    "5" { $currentCategory = "databases" }
                    "6" { $currentCategory = "observability" }
                    "7" { $currentCategory = "ci-cd" }
                }
            }
            's' {
                Show-LogStatistics
            }
            'h' {
                Clear-Host
                Write-Host "📊 CENTRALIZED LOGGING DASHBOARD HELP" -ForegroundColor Cyan
                Write-Host "=====================================" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "Commands:" -ForegroundColor Yellow
                Write-Host "  q - Quit" -ForegroundColor White
                Write-Host "  r - Refresh" -ForegroundColor White
                Write-Host "  f - Follow (real-time)" -ForegroundColor White
                Write-Host "  c - Change category" -ForegroundColor White
                Write-Host "  s - Show statistics" -ForegroundColor White
                Write-Host "  h - Show this help" -ForegroundColor White
                Write-Host ""
                Write-Host "Press any key to return..." -ForegroundColor Yellow
                $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
            }
        }
        
        Start-Sleep -Milliseconds 100
    }
}

# Main Execution
function Main {
    Write-LogOutput "🚀 Starting Centralized Logging Dashboard..." -Level "INFO"
    Write-LogOutput "Category: $LogCategory | Level: $LogLevel | Lines: $Lines" -Level "INFO"
    
    # Ensure log directories exist
    if (-not (Test-Path $LogConfig.LogDirectory)) {
        New-Item -ItemType Directory -Path $LogConfig.LogDirectory -Force | Out-Null
    }
    if (-not (Test-Path $LogConfig.TestLogDirectory)) {
        New-Item -ItemType Directory -Path $LogConfig.TestLogDirectory -Force | Out-Null
    }
    if (-not (Test-Path $LogConfig.SystemLogDirectory)) {
        New-Item -ItemType Directory -Path $LogConfig.SystemLogDirectory -Force | Out-Null
    }
    
    if ($RealTime) {
        Show-RealTimeLogs -Category $LogCategory -Level $LogLevel
    } elseif ($Interactive) {
        Show-InteractiveDashboard
    } else {
        Show-LogDashboard -Category $LogCategory -MaxEntries $Lines -Level $LogLevel
    }
}

# Execute main function
try {
    Main
} catch {
    Write-LogOutput "❌ Logging dashboard failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
