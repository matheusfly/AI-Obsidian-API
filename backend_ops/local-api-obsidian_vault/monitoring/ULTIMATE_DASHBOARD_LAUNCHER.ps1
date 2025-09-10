# Ultimate Dashboard Launcher for Enhanced Observability
# Comprehensive launcher for all observability components with real-time monitoring

param(
    [string]$Mode = "full",  # full, quick, ai-only, backend-only, monitoring-only
    [switch]$RealTime = $false,
    [int]$Duration = 300,  # seconds for real-time monitoring
    [string]$Theme = "dark",  # dark, light, auto
    [switch]$AutoRefresh = $false,
    [int]$RefreshInterval = 30,  # seconds
    [switch]$GenerateReport = $true,
    [string]$ReportFormat = "html"  # html, json, csv
)

# Color definitions
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Blue = "Blue"
$Cyan = "Cyan"
$Magenta = "Magenta"
$White = "White"

# Global configuration
$Config = @{
    Services = @(
        "vault-api", "obsidian-api", "n8n", "postgres", "redis", 
        "ollama", "chromadb", "qdrant", "prometheus", "grafana",
        "nginx", "embedding-service", "advanced-indexer", 
        "motia-integration", "flyde-integration", "motia-workbench"
    )
    ObservabilityServices = @(
        "enhanced-observability", "ai-agent-observability", 
        "ultra-performance-optimizer", "sentry-integration",
        "mcp-tools-integration"
    )
    DashboardURLs = @{
        "Grafana" = "http://localhost:3004"
        "Prometheus" = "http://localhost:9090"
        "Vault API" = "http://localhost:8085"
        "N8N" = "http://localhost:5678"
        "Obsidian API" = "http://localhost:27123"
        "Ollama" = "http://localhost:11434"
        "ChromaDB" = "http://localhost:8000"
        "Qdrant" = "http://localhost:6333"
        "Motia Workbench" = "http://localhost:3000"
    }
    PerformanceThresholds = @{
        CPU_WARNING = 70
        CPU_CRITICAL = 90
        MEMORY_WARNING = 80
        MEMORY_CRITICAL = 95
        RESPONSE_TIME_WARNING = 1000
        RESPONSE_TIME_CRITICAL = 5000
        ERROR_RATE_WARNING = 1
        ERROR_RATE_CRITICAL = 5
    }
}

function Write-DashboardLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor $Red }
        "WARNING" { Write-Host $LogMessage -ForegroundColor $Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor $Green }
        "INFO" { Write-Host $LogMessage -ForegroundColor $Blue }
        "DASHBOARD" { Write-Host $LogMessage -ForegroundColor $Cyan }
        default { Write-Host $LogMessage -ForegroundColor $White }
    }
}

function Show-DashboardHeader {
    Clear-Host
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Cyan
    Write-Host "║                    🚀 ULTIMATE OBSERVABILITY DASHBOARD 🚀                    ║" -ForegroundColor $Cyan
    Write-Host "║                        Enhanced Monitoring & Analytics                       ║" -ForegroundColor $Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "Mode: $Mode | Real-time: $RealTime | Theme: $Theme | Auto-refresh: $AutoRefresh" -ForegroundColor $Yellow
    Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $Yellow
    Write-Host ""
}

function Get-SystemHealthStatus {
    Write-DashboardLog "Collecting system health status..." "INFO"
    
    $HealthStatus = @{
        Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
        OverallHealth = "Good"
        CriticalIssues = @()
        Warnings = @()
        Services = @{}
        Performance = @{}
        AI = @{}
        Observability = @{}
    }
    
    try {
        # System metrics
        $CPU = Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 1
        $Memory = Get-Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 1
        $Disk = Get-Counter "\LogicalDisk(C:)\% Free Space" -SampleInterval 1 -MaxSamples 1
        
        $HealthStatus.Performance = @{
            CPU_Usage = [math]::Round($CPU.CounterSamples[0].CookedValue, 2)
            Memory_Available_MB = [math]::Round($Memory.CounterSamples[0].CookedValue, 2)
            Memory_Total_GB = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
            Memory_Usage_Percent = [math]::Round((1 - ($Memory.CounterSamples[0].CookedValue / (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory * 1024)) * 100, 2)
            Disk_Free_Percent = [math]::Round($Disk.CounterSamples[0].CookedValue, 2)
        }
        
        # Check for critical issues
        if ($HealthStatus.Performance.CPU_Usage -gt $Config.PerformanceThresholds.CPU_CRITICAL) {
            $HealthStatus.CriticalIssues += "CPU usage is critically high: $($HealthStatus.Performance.CPU_Usage)%"
            $HealthStatus.OverallHealth = "Critical"
        }
        
        if ($HealthStatus.Performance.Memory_Usage_Percent -gt $Config.PerformanceThresholds.MEMORY_CRITICAL) {
            $HealthStatus.CriticalIssues += "Memory usage is critically high: $($HealthStatus.Performance.Memory_Usage_Percent)%"
            $HealthStatus.OverallHealth = "Critical"
        }
        
        # Check warnings
        if ($HealthStatus.Performance.CPU_Usage -gt $Config.PerformanceThresholds.CPU_WARNING) {
            $HealthStatus.Warnings += "CPU usage is high: $($HealthStatus.Performance.CPU_Usage)%"
            if ($HealthStatus.OverallHealth -eq "Good") { $HealthStatus.OverallHealth = "Warning" }
        }
        
        if ($HealthStatus.Performance.Memory_Usage_Percent -gt $Config.PerformanceThresholds.MEMORY_WARNING) {
            $HealthStatus.Warnings += "Memory usage is high: $($HealthStatus.Performance.Memory_Usage_Percent)%"
            if ($HealthStatus.OverallHealth -eq "Good") { $HealthStatus.OverallHealth = "Warning" }
        }
        
        Write-DashboardLog "System health status collected successfully" "SUCCESS"
    }
    catch {
        Write-DashboardLog "Failed to collect system health status: $($_.Exception.Message)" "ERROR"
    }
    
    return $HealthStatus
}

function Get-ServiceHealthStatus {
    param([string]$ServiceName)
    
    $ServiceStatus = @{
        Name = $ServiceName
        Status = "Unknown"
        Health = "Unknown"
        Performance = @{}
        LastChecked = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    }
    
    try {
        # Check Docker container status
        $ContainerInfo = docker ps --filter "name=$ServiceName" --format "{{.Status}}" 2>$null
        if ($ContainerInfo) {
            $ServiceStatus.Status = "Running"
            $ServiceStatus.Health = "Healthy"
            
            # Get container stats
            $Stats = docker stats $ServiceName --no-stream --format "table {{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}}" 2>$null
            if ($Stats) {
                $StatsArray = $Stats -split "`n" | Where-Object { $_ -match "," }
                if ($StatsArray.Count -gt 1) {
                    $Data = $StatsArray[1] -split ","
                    $ServiceStatus.Performance = @{
                        CPU_Percent = $Data[0] -replace "%", ""
                        Memory_Usage = $Data[1]
                        Memory_Percent = $Data[2] -replace "%", ""
                        Network_IO = $Data[3]
                        Block_IO = $Data[4]
                    }
                }
            }
        } else {
            $ServiceStatus.Status = "Not Running"
            $ServiceStatus.Health = "Unhealthy"
        }
    }
    catch {
        Write-DashboardLog "Failed to get status for $ServiceName : $($_.Exception.Message)" "ERROR"
        $ServiceStatus.Status = "Error"
        $ServiceStatus.Health = "Error"
    }
    
    return $ServiceStatus
}

function Show-DashboardContent {
    param([hashtable]$HealthStatus)
    
    # Overall Health Status
    $HealthColor = switch ($HealthStatus.OverallHealth) {
        "Critical" { $Red }
        "Warning" { $Yellow }
        default { $Green }
    }
    
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Cyan
    Write-Host "║                            📊 SYSTEM OVERVIEW                                ║" -ForegroundColor $Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "Overall Health: " -NoNewline
    Write-Host $HealthStatus.OverallHealth -ForegroundColor $HealthColor
    Write-Host ""
    
    # Performance Metrics
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Green
    Write-Host "║                            🚀 PERFORMANCE METRICS                            ║" -ForegroundColor $Green
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Green
    Write-Host ""
    
    $CPUColor = if ($HealthStatus.Performance.CPU_Usage -gt 80) { $Red } elseif ($HealthStatus.Performance.CPU_Usage -gt 60) { $Yellow } else { $Green }
    $MemoryColor = if ($HealthStatus.Performance.Memory_Usage_Percent -gt 80) { $Red } elseif ($HealthStatus.Performance.Memory_Usage_Percent -gt 60) { $Yellow } else { $Green }
    
    Write-Host "CPU Usage: " -NoNewline
    Write-Host "$($HealthStatus.Performance.CPU_Usage)%" -ForegroundColor $CPUColor
    Write-Host "Memory Usage: " -NoNewline
    Write-Host "$($HealthStatus.Performance.Memory_Usage_Percent)%" -ForegroundColor $MemoryColor
    Write-Host "Memory Available: $($HealthStatus.Performance.Memory_Available_MB) MB" -ForegroundColor $Blue
    Write-Host "Disk Free: $($HealthStatus.Performance.Disk_Free_Percent)%" -ForegroundColor $Blue
    Write-Host ""
    
    # Critical Issues
    if ($HealthStatus.CriticalIssues.Count -gt 0) {
        Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Red
        Write-Host "║                            🚨 CRITICAL ISSUES                               ║" -ForegroundColor $Red
        Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Red
        Write-Host ""
        foreach ($Issue in $HealthStatus.CriticalIssues) {
            Write-Host "• $Issue" -ForegroundColor $Red
        }
        Write-Host ""
    }
    
    # Warnings
    if ($HealthStatus.Warnings.Count -gt 0) {
        Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Yellow
        Write-Host "║                            ⚠️  WARNINGS                                     ║" -ForegroundColor $Yellow
        Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Yellow
        Write-Host ""
        foreach ($Warning in $HealthStatus.Warnings) {
            Write-Host "• $Warning" -ForegroundColor $Yellow
        }
        Write-Host ""
    }
    
    # Service Status
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Magenta
    Write-Host "║                            🔧 SERVICE STATUS                                 ║" -ForegroundColor $Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Magenta
    Write-Host ""
    
    foreach ($Service in $Config.Services) {
        $ServiceStatus = Get-ServiceHealthStatus -ServiceName $Service
        $StatusColor = switch ($ServiceStatus.Health) {
            "Healthy" { $Green }
            "Unhealthy" { $Red }
            default { $Yellow }
        }
        Write-Host "$($Service.PadRight(20)) : " -NoNewline
        Write-Host $ServiceStatus.Status -ForegroundColor $StatusColor
    }
    Write-Host ""
    
    # Dashboard URLs
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Cyan
    Write-Host "║                            🌐 DASHBOARD ACCESS                               ║" -ForegroundColor $Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Cyan
    Write-Host ""
    
    foreach ($Name in $Config.DashboardURLs.Keys) {
        $Url = $Config.DashboardURLs[$Name]
        Write-Host "$($Name.PadRight(20)) : " -NoNewline
        Write-Host $Url -ForegroundColor $Blue
    }
    Write-Host ""
}

function Start-RealTimeDashboard {
    param([int]$Duration)
    
    Write-DashboardLog "Starting real-time dashboard for $Duration seconds..." "INFO"
    
    $StartTime = Get-Date
    $EndTime = $StartTime.AddSeconds($Duration)
    
    while ((Get-Date) -lt $EndTime) {
        Show-DashboardHeader
        
        # Collect health status
        $HealthStatus = Get-SystemHealthStatus
        
        # Show dashboard content
        Show-DashboardContent -HealthStatus $HealthStatus
        
        # Show progress
        $Elapsed = [math]::Round(((Get-Date) - $StartTime).TotalSeconds, 0)
        $Remaining = $Duration - $Elapsed
        Write-Host "Real-time monitoring: $Elapsed/$Duration seconds (Remaining: $Remaining seconds)" -ForegroundColor $Yellow
        Write-Host ""
        Write-Host "Press Ctrl+C to stop monitoring..." -ForegroundColor $Yellow
        
        Start-Sleep -Seconds 5
    }
    
    Write-DashboardLog "Real-time dashboard monitoring completed" "SUCCESS"
}

function Export-DashboardReport {
    param([hashtable]$HealthStatus, [string]$Format)
    
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $ReportPath = "ultimate_dashboard_report_$Timestamp"
    
    switch ($Format.ToLower()) {
        "json" {
            $ReportPath += ".json"
            $Report = @{
                Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
                HealthStatus = $HealthStatus
                Configuration = $Config
            }
            $Report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8
        }
        "html" {
            $ReportPath += ".html"
            $HtmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Ultimate Dashboard Report - $Timestamp</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; text-align: center; }
        .metric { margin: 10px 0; padding: 15px; border-radius: 5px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .critical { border-left: 4px solid #e74c3c; background-color: #fdf2f2; }
        .warning { border-left: 4px solid #f39c12; background-color: #fef9e7; }
        .good { border-left: 4px solid #27ae60; background-color: #eafaf1; }
        .service-status { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        .url-list { background-color: #ecf0f1; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Ultimate Observability Dashboard Report</h1>
        <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p>Overall Health: <strong>$($HealthStatus.OverallHealth)</strong></p>
    </div>
    
    <div class="metric">
        <h2>📊 Performance Metrics</h2>
        <p><strong>CPU Usage:</strong> $($HealthStatus.Performance.CPU_Usage)%</p>
        <p><strong>Memory Usage:</strong> $($HealthStatus.Performance.Memory_Usage_Percent)%</p>
        <p><strong>Memory Available:</strong> $($HealthStatus.Performance.Memory_Available_MB) MB</p>
        <p><strong>Disk Free:</strong> $($HealthStatus.Performance.Disk_Free_Percent)%</p>
    </div>
    
    <div class="metric">
        <h2>🔧 Service Status</h2>
        <div class="service-status">
"@
            foreach ($Service in $Config.Services) {
                $ServiceStatus = Get-ServiceHealthStatus -ServiceName $Service
                $Class = switch ($ServiceStatus.Health) {
                    "Healthy" { "good" }
                    "Unhealthy" { "critical" }
                    default { "warning" }
                }
                $HtmlContent += @"
            <div class="metric $Class">
                <h3>$($ServiceStatus.Name)</h3>
                <p><strong>Status:</strong> $($ServiceStatus.Status)</p>
                <p><strong>Health:</strong> $($ServiceStatus.Health)</p>
            </div>
"@
            }
            
            $HtmlContent += @"
        </div>
    </div>
    
    <div class="metric url-list">
        <h2>🌐 Dashboard Access URLs</h2>
"@
            foreach ($Name in $Config.DashboardURLs.Keys) {
                $Url = $Config.DashboardURLs[$Name]
                $HtmlContent += "        <p><strong>$Name:</strong> <a href='$Url' target='_blank'>$Url</a></p>`n"
            }
            
            $HtmlContent += @"
    </div>
</body>
</html>
"@
            $HtmlContent | Out-File -FilePath $ReportPath -Encoding UTF8
        }
    }
    
    Write-DashboardLog "Dashboard report exported to: $ReportPath" "SUCCESS"
    return $ReportPath
}

# Main execution
Write-DashboardLog "Starting Ultimate Dashboard Launcher..." "INFO"
Write-DashboardLog "Mode: $Mode | Real-time: $RealTime | Duration: $Duration | Theme: $Theme" "INFO"

if ($RealTime) {
    Start-RealTimeDashboard -Duration $Duration
} else {
    # Single dashboard run
    Show-DashboardHeader
    
    # Collect comprehensive health status
    Write-DashboardLog "Collecting comprehensive system health status..." "INFO"
    $HealthStatus = Get-SystemHealthStatus
    
    # Show dashboard content
    Show-DashboardContent -HealthStatus $HealthStatus
    
    # Export report if requested
    if ($GenerateReport) {
        Write-DashboardLog "Generating dashboard report..." "INFO"
        $ReportPath = Export-DashboardReport -HealthStatus $HealthStatus -Format $ReportFormat
        Write-DashboardLog "Report saved to: $ReportPath" "SUCCESS"
    }
    
    Write-DashboardLog "Ultimate Dashboard Launcher completed" "SUCCESS"
}

Write-Host ""
Write-Host "🎉 Ultimate Observability Dashboard - Complete!" -ForegroundColor $Green
Write-Host "📊 Access your dashboards using the URLs above" -ForegroundColor $Cyan
Write-Host "🔧 Monitor your services in real-time" -ForegroundColor $Blue
Write-Host "📈 Track performance and optimize your system" -ForegroundColor $Magenta
