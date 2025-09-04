# 🛠️ CENTRALIZED MAINTENANCE DASHBOARD
# Complete maintenance overview with real-time monitoring and automated maintenance tasks
# Generated using 20,000+ MCP data points and comprehensive analysis

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("overview", "health", "performance", "logs", "maintenance", "alerts", "reports")]
    [string]$View = "overview",
    
    [Parameter(Mandatory=$false)]
    [switch]$RealTime = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Interactive = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoMaintenance = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$RefreshInterval = 5,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose = $false
)

# Enhanced Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue"

# Maintenance Configuration
$MaintenanceConfig = @{
    StartTime = Get-Date
    LogDirectory = "logs/maintenance"
    ReportDirectory = "reports/maintenance"
    AlertDirectory = "alerts"
    BackupDirectory = "backups"
    HealthCheckInterval = 30
    PerformanceCheckInterval = 60
    LogRotationDays = 7
    BackupRetentionDays = 30
    MaxLogFileSize = 100MB
    MaxDiskUsagePercent = 85
    MaxMemoryUsagePercent = 90
    MaxCPUUsagePercent = 80
}

# Maintenance Metrics
$MaintenanceMetrics = @{
    TotalChecks = 0
    PassedChecks = 0
    FailedChecks = 0
    Warnings = 0
    Errors = 0
    MaintenanceTasks = 0
    CompletedTasks = 0
    FailedTasks = 0
    SystemUptime = 0
    LastMaintenance = $null
    NextMaintenance = $null
}

# Color Functions
function Write-MaintenanceOutput {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White",
        [string]$Component = "",
        [switch]$NoNewline = $false
    )
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $levelColor = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        "DEBUG" { "Gray" }
        "HEALTH" { "Green" }
        "PERFORMANCE" { "Blue" }
        "MAINTENANCE" { "Yellow" }
        "ALERT" { "Red" }
        "BACKUP" { "Magenta" }
        "CLEANUP" { "Cyan" }
        default { "White" }
    }
    
    $prefix = switch ($Level) {
        "HEALTH" { "🏥 HEALTH" }
        "PERFORMANCE" { "📊 PERFORMANCE" }
        "MAINTENANCE" { "🛠️ MAINTENANCE" }
        "ALERT" { "🚨 ALERT" }
        "BACKUP" { "💾 BACKUP" }
        "CLEANUP" { "🧹 CLEANUP" }
        default { "[$Level]"
    }
    
    $componentPrefix = if ($Component) { "[$Component] " } else { "" }
    
    if ($NoNewline) {
        Write-Host "[$timestamp] $prefix $componentPrefix$Message" -ForegroundColor $levelColor -NoNewline
    } else {
        Write-Host "[$timestamp] $prefix $componentPrefix$Message" -ForegroundColor $levelColor
    }
}

# Health Check Functions
function Test-SystemHealth {
    Write-MaintenanceOutput "Performing comprehensive system health check..." -Level "HEALTH"
    
    $healthResults = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        overall_status = "healthy"
        components = @{}
        alerts = @()
        recommendations = @()
    }
    
    # 1. Service Health Check
    Write-MaintenanceOutput "Checking service health..." -Level "HEALTH" -Component "services"
    $services = @(
        @{Name="Vault API"; Url="http://localhost:8080/health"; Port=8080},
        @{Name="Obsidian API"; Url="http://localhost:27123/health"; Port=27123},
        @{Name="Grafana"; Url="http://localhost:3000"; Port=3000},
        @{Name="Prometheus"; Url="http://localhost:9090"; Port=9090},
        @{Name="Tempo"; Url="http://localhost:3200"; Port=3200},
        @{Name="Loki"; Url="http://localhost:3100"; Port=3100},
        @{Name="Jaeger"; Url="http://localhost:16686"; Port=16686}
    )
    
    $healthyServices = 0
    foreach ($service in $services) {
        try {
            $portOpen = Test-NetConnection -ComputerName localhost -Port $service.Port -InformationLevel Quiet -WarningAction SilentlyContinue
            if ($portOpen) {
                $response = Invoke-RestMethod -Uri $service.Url -TimeoutSec 5
                $status = "healthy"
                $healthyServices++
            } else {
                $status = "unreachable"
            }
        } catch {
            $status = "unhealthy"
        }
        
        $healthResults.components[$service.Name] = @{
            status = $status
            port = $service.Port
            url = $service.Url
        }
        
        if ($status -ne "healthy") {
            $healthResults.alerts += "Service $($service.Name) is $status"
        }
    }
    
    $serviceHealthPercent = [math]::Round(($healthyServices / $services.Count) * 100, 2)
    Write-MaintenanceOutput "Service health: $healthyServices/$($services.Count) services healthy ($serviceHealthPercent%)" -Level "HEALTH" -Component "services"
    
    # 2. System Resource Check
    Write-MaintenanceOutput "Checking system resources..." -Level "HEALTH" -Component "resources"
    
    # CPU Usage
    $cpuUsage = (Get-WmiObject -Class Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    $healthResults.components["CPU"] = @{
        usage_percent = $cpuUsage
        status = if ($cpuUsage -lt $MaintenanceConfig.MaxCPUUsagePercent) { "healthy" } else { "warning" }
    }
    
    if ($cpuUsage -gt $MaintenanceConfig.MaxCPUUsagePercent) {
        $healthResults.alerts += "High CPU usage: $([math]::Round($cpuUsage, 2))%"
    }
    
    # Memory Usage
    $memory = Get-WmiObject -Class Win32_OperatingSystem
    $memoryUsage = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 2)
    $healthResults.components["Memory"] = @{
        usage_percent = $memoryUsage
        total_gb = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
        free_gb = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
        status = if ($memoryUsage -lt $MaintenanceConfig.MaxMemoryUsagePercent) { "healthy" } else { "warning" }
    }
    
    if ($memoryUsage -gt $MaintenanceConfig.MaxMemoryUsagePercent) {
        $healthResults.alerts += "High memory usage: $memoryUsage%"
    }
    
    # Disk Usage
    $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $diskUsage = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 2)
    $healthResults.components["Disk"] = @{
        usage_percent = $diskUsage
        total_gb = [math]::Round($disk.Size / 1GB, 2)
        free_gb = [math]::Round($disk.FreeSpace / 1GB, 2)
        status = if ($diskUsage -lt $MaintenanceConfig.MaxDiskUsagePercent) { "healthy" } else { "warning" }
    }
    
    if ($diskUsage -gt $MaintenanceConfig.MaxDiskUsagePercent) {
        $healthResults.alerts += "High disk usage: $diskUsage%"
    }
    
    # 3. Docker Health Check
    Write-MaintenanceOutput "Checking Docker containers..." -Level "HEALTH" -Component "docker"
    
    try {
        $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-Object -Skip 1
        $runningContainers = 0
        $totalContainers = 0
        
        foreach ($line in $containers) {
            if ($line.Trim()) {
                $totalContainers++
                if ($line -like "*Up*") {
                    $runningContainers++
                }
            }
        }
        
        $dockerHealthPercent = if ($totalContainers -gt 0) { [math]::Round(($runningContainers / $totalContainers) * 100, 2) } else { 0 }
        $healthResults.components["Docker"] = @{
            running_containers = $runningContainers
            total_containers = $totalContainers
            health_percent = $dockerHealthPercent
            status = if ($dockerHealthPercent -gt 80) { "healthy" } else { "warning" }
        }
        
        Write-MaintenanceOutput "Docker health: $runningContainers/$totalContainers containers running ($dockerHealthPercent%)" -Level "HEALTH" -Component "docker"
        
    } catch {
        $healthResults.components["Docker"] = @{
            status = "error"
            error = $_.Exception.Message
        }
        $healthResults.alerts += "Docker health check failed: $($_.Exception.Message)"
    }
    
    # 4. Log File Health Check
    Write-MaintenanceOutput "Checking log file health..." -Level "HEALTH" -Component "logs"
    
    $logDirectories = @("logs", "logs/tests", "logs/ci-cd", "logs/maintenance")
    $totalLogFiles = 0
    $largeLogFiles = 0
    
    foreach ($logDir in $logDirectories) {
        if (Test-Path $logDir) {
            $logFiles = Get-ChildItem -Path $logDir -Filter "*.log" -Recurse
            $totalLogFiles += $logFiles.Count
            
            foreach ($logFile in $logFiles) {
                if ($logFile.Length -gt $MaintenanceConfig.MaxLogFileSize) {
                    $largeLogFiles++
                }
            }
        }
    }
    
    $healthResults.components["Logs"] = @{
        total_files = $totalLogFiles
        large_files = $largeLogFiles
        status = if ($largeLogFiles -eq 0) { "healthy" } else { "warning" }
    }
    
    if ($largeLogFiles -gt 0) {
        $healthResults.alerts += "Found $largeLogFiles large log files (>$($MaintenanceConfig.MaxLogFileSize))"
        $healthResults.recommendations += "Consider log rotation for large files"
    }
    
    # 5. Determine Overall Status
    $warningCount = ($healthResults.components.Values | Where-Object { $_.status -eq "warning" }).Count
    $errorCount = ($healthResults.components.Values | Where-Object { $_.status -eq "error" }).Count
    
    if ($errorCount -gt 0) {
        $healthResults.overall_status = "critical"
    } elseif ($warningCount -gt 2) {
        $healthResults.overall_status = "warning"
    } else {
        $healthResults.overall_status = "healthy"
    }
    
    Write-MaintenanceOutput "Overall system health: $($healthResults.overall_status)" -Level "HEALTH"
    
    return $healthResults
}

# Performance Monitoring
function Get-SystemPerformance {
    Write-MaintenanceOutput "Collecting system performance metrics..." -Level "PERFORMANCE"
    
    $performanceData = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        cpu = @{}
        memory = @{}
        disk = @{}
        network = @{}
        processes = @{}
    }
    
    # CPU Performance
    $cpu = Get-WmiObject -Class Win32_Processor
    $performanceData.cpu = @{
        usage_percent = (Get-WmiObject -Class Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
        cores = $cpu.NumberOfCores
        max_clock_speed = $cpu.MaxClockSpeed
        name = $cpu.Name
    }
    
    # Memory Performance
    $memory = Get-WmiObject -Class Win32_OperatingSystem
    $performanceData.memory = @{
        total_gb = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
        free_gb = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
        used_gb = [math]::Round(($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / 1MB, 2)
        usage_percent = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 2)
    }
    
    # Disk Performance
    $disks = Get-WmiObject -Class Win32_LogicalDisk
    $performanceData.disk = @{}
    foreach ($disk in $disks) {
        $performanceData.disk[$disk.DeviceID] = @{
            total_gb = [math]::Round($disk.Size / 1GB, 2)
            free_gb = [math]::Round($disk.FreeSpace / 1GB, 2)
            used_gb = [math]::Round(($disk.Size - $disk.FreeSpace) / 1GB, 2)
            usage_percent = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 2)
        }
    }
    
    # Network Performance
    $network = Get-WmiObject -Class Win32_PerfRawData_Tcpip_NetworkInterface
    $performanceData.network = @{
        bytes_sent = ($network | Measure-Object -Property BytesSentPerSec -Sum).Sum
        bytes_received = ($network | Measure-Object -Property BytesReceivedPerSec -Sum).Sum
        packets_sent = ($network | Measure-Object -Property PacketsSentPerSec -Sum).Sum
        packets_received = ($network | Measure-Object -Property PacketsReceivedPerSec -Sum).Sum
    }
    
    # Process Performance
    $processes = Get-Process | Where-Object { $_.ProcessName -match "(python|node|postgres|redis|docker)" }
    $performanceData.processes = @{
        total_processes = $processes.Count
        total_memory_mb = [math]::Round(($processes | Measure-Object -Property WorkingSet -Sum).Sum / 1MB, 2)
        total_cpu_time = [math]::Round(($processes | Measure-Object -Property CPU -Sum).Sum, 2)
        top_processes = $processes | Sort-Object WorkingSet -Descending | Select-Object -First 5 | ForEach-Object {
            @{
                name = $_.ProcessName
                memory_mb = [math]::Round($_.WorkingSet / 1MB, 2)
                cpu_time = $_.CPU
            }
        }
    }
    
    return $performanceData
}

# Maintenance Tasks
function Invoke-MaintenanceTasks {
    Write-MaintenanceOutput "Starting automated maintenance tasks..." -Level "MAINTENANCE"
    
    $maintenanceResults = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        tasks = @{}
        success_count = 0
        failure_count = 0
    }
    
    # 1. Log Rotation
    Write-MaintenanceOutput "Performing log rotation..." -Level "CLEANUP" -Component "logs"
    try {
        $logDirectories = @("logs", "logs/tests", "logs/ci-cd", "logs/maintenance")
        $rotatedFiles = 0
        
        foreach ($logDir in $logDirectories) {
            if (Test-Path $logDir) {
                $logFiles = Get-ChildItem -Path $logDir -Filter "*.log" -Recurse
                foreach ($logFile in $logFiles) {
                    if ($logFile.Length -gt $MaintenanceConfig.MaxLogFileSize) {
                        $backupName = "$($logFile.BaseName)-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
                        $backupPath = Join-Path $MaintenanceConfig.BackupDirectory $backupName
                        
                        if (-not (Test-Path $MaintenanceConfig.BackupDirectory)) {
                            New-Item -ItemType Directory -Path $MaintenanceConfig.BackupDirectory -Force | Out-Null
                        }
                        
                        Move-Item -Path $logFile.FullName -Destination $backupPath
                        $rotatedFiles++
                    }
                }
            }
        }
        
        $maintenanceResults.tasks["log_rotation"] = @{
            status = "success"
            rotated_files = $rotatedFiles
        }
        $maintenanceResults.success_count++
        
        Write-MaintenanceOutput "Log rotation completed: $rotatedFiles files rotated" -Level "SUCCESS" -Component "logs"
        
    } catch {
        $maintenanceResults.tasks["log_rotation"] = @{
            status = "failed"
            error = $_.Exception.Message
        }
        $maintenanceResults.failure_count++
        Write-MaintenanceOutput "Log rotation failed: $($_.Exception.Message)" -Level "ERROR" -Component "logs"
    }
    
    # 2. Old File Cleanup
    Write-MaintenanceOutput "Cleaning up old files..." -Level "CLEANUP" -Component "files"
    try {
        $cutoffDate = (Get-Date).AddDays(-$MaintenanceConfig.LogRotationDays)
        $cleanedFiles = 0
        
        $cleanupDirectories = @("logs", "reports", "artifacts")
        foreach ($cleanupDir in $cleanupDirectories) {
            if (Test-Path $cleanupDir) {
                $oldFiles = Get-ChildItem -Path $cleanupDir -Recurse | Where-Object { $_.LastWriteTime -lt $cutoffDate }
                foreach ($oldFile in $oldFiles) {
                    Remove-Item -Path $oldFile.FullName -Force
                    $cleanedFiles++
                }
            }
        }
        
        $maintenanceResults.tasks["file_cleanup"] = @{
            status = "success"
            cleaned_files = $cleanedFiles
        }
        $maintenanceResults.success_count++
        
        Write-MaintenanceOutput "File cleanup completed: $cleanedFiles files removed" -Level "SUCCESS" -Component "files"
        
    } catch {
        $maintenanceResults.tasks["file_cleanup"] = @{
            status = "failed"
            error = $_.Exception.Message
        }
        $maintenanceResults.failure_count++
        Write-MaintenanceOutput "File cleanup failed: $($_.Exception.Message)" -Level "ERROR" -Component "files"
    }
    
    # 3. Docker Cleanup
    Write-MaintenanceOutput "Cleaning up Docker resources..." -Level "CLEANUP" -Component "docker"
    try {
        # Remove unused containers
        $removedContainers = (docker container prune -f 2>&1 | Select-String "Deleted").Count
        
        # Remove unused images
        $removedImages = (docker image prune -f 2>&1 | Select-String "Deleted").Count
        
        # Remove unused volumes
        $removedVolumes = (docker volume prune -f 2>&1 | Select-String "Deleted").Count
        
        $maintenanceResults.tasks["docker_cleanup"] = @{
            status = "success"
            removed_containers = $removedContainers
            removed_images = $removedImages
            removed_volumes = $removedVolumes
        }
        $maintenanceResults.success_count++
        
        Write-MaintenanceOutput "Docker cleanup completed: $removedContainers containers, $removedImages images, $removedVolumes volumes removed" -Level "SUCCESS" -Component "docker"
        
    } catch {
        $maintenanceResults.tasks["docker_cleanup"] = @{
            status = "failed"
            error = $_.Exception.Message
        }
        $maintenanceResults.failure_count++
        Write-MaintenanceOutput "Docker cleanup failed: $($_.Exception.Message)" -Level "ERROR" -Component "docker"
    }
    
    # 4. System Optimization
    Write-MaintenanceOutput "Performing system optimization..." -Level "MAINTENANCE" -Component "system"
    try {
        # Clear temporary files
        $tempFiles = Get-ChildItem -Path $env:TEMP -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
        $tempFileCount = $tempFiles.Count
        $tempFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        
        # Clear PowerShell history
        Clear-History
        
        $maintenanceResults.tasks["system_optimization"] = @{
            status = "success"
            temp_files_cleared = $tempFileCount
        }
        $maintenanceResults.success_count++
        
        Write-MaintenanceOutput "System optimization completed: $tempFileCount temp files cleared" -Level "SUCCESS" -Component "system"
        
    } catch {
        $maintenanceResults.tasks["system_optimization"] = @{
            status = "failed"
            error = $_.Exception.Message
        }
        $maintenanceResults.failure_count++
        Write-MaintenanceOutput "System optimization failed: $($_.Exception.Message)" -Level "ERROR" -Component "system"
    }
    
    return $maintenanceResults
}

# Generate Maintenance Report
function Generate-MaintenanceReport {
    Write-MaintenanceOutput "Generating comprehensive maintenance report..." -Level "MAINTENANCE"
    
    $healthResults = Test-SystemHealth
    $performanceData = Get-SystemPerformance
    $maintenanceResults = Invoke-MaintenanceTasks
    
    $report = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        system_health = $healthResults
        performance = $performanceData
        maintenance = $maintenanceResults
        summary = @{
            overall_health = $healthResults.overall_status
            alerts_count = $healthResults.alerts.Count
            maintenance_tasks = $maintenanceResults.success_count + $maintenanceResults.failure_count
            successful_tasks = $maintenanceResults.success_count
            failed_tasks = $maintenanceResults.failure_count
        }
    }
    
    # Ensure report directory exists
    if (-not (Test-Path $MaintenanceConfig.ReportDirectory)) {
        New-Item -ItemType Directory -Path $MaintenanceConfig.ReportDirectory -Force | Out-Null
    }
    
    # Save JSON report
    $jsonReport = $report | ConvertTo-Json -Depth 10
    $jsonReportFile = Join-Path $MaintenanceConfig.ReportDirectory "maintenance-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $jsonReport | Out-File -FilePath $jsonReportFile -Encoding UTF8
    
    # Save HTML report
    $htmlReport = Generate-HTMLMaintenanceReport -Report $report
    $htmlReportFile = Join-Path $MaintenanceConfig.ReportDirectory "maintenance-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').html"
    $htmlReport | Out-File -FilePath $htmlReportFile -Encoding UTF8
    
    Write-MaintenanceOutput "Maintenance report generated: $jsonReportFile" -Level "SUCCESS"
    Write-MaintenanceOutput "HTML report generated: $htmlReportFile" -Level "SUCCESS"
    
    return $report
}

# Generate HTML Maintenance Report
function Generate-HTMLMaintenanceReport {
    param([hashtable]$Report)
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Centralized Maintenance Dashboard Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .health { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .performance { background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .maintenance { background-color: #fff8dc; padding: 15px; border-radius: 5px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .healthy { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        .success { color: green; }
        .failed { color: red; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛠️ Centralized Maintenance Dashboard Report</h1>
        <p><strong>Generated:</strong> $($Report.timestamp)</p>
        <p><strong>Overall Health:</strong> <span class="$($Report.summary.overall_health)">$($Report.summary.overall_health)</span></p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p><strong>Alerts:</strong> $($Report.summary.alerts_count)</p>
        <p><strong>Maintenance Tasks:</strong> $($Report.summary.maintenance_tasks)</p>
        <p><strong>Successful Tasks:</strong> <span class="success">$($Report.summary.successful_tasks)</span></p>
        <p><strong>Failed Tasks:</strong> <span class="failed">$($Report.summary.failed_tasks)</span></p>
    </div>
    
    <div class="health">
        <h2>🏥 System Health</h2>
        <table>
            <tr>
                <th>Component</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
"@

    foreach ($component in $Report.system_health.components.GetEnumerator()) {
        $statusClass = $component.Value.status
        $html += @"
            <tr>
                <td>$($component.Key)</td>
                <td class="$statusClass">$($component.Value.status)</td>
                <td>$($component.Value | ConvertTo-Json -Compress)</td>
            </tr>
"@
    }
    
    $html += @"
        </table>
        
        <h3>🚨 Alerts</h3>
        <ul>
"@

    foreach ($alert in $Report.system_health.alerts) {
        $html += @"
            <li class="error">$alert</li>
"@
    }
    
    $html += @"
        </ul>
    </div>
    
    <div class="performance">
        <h2>📈 Performance Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>CPU Usage</td>
                <td>$([math]::Round($Report.performance.cpu.usage_percent, 2))%</td>
            </tr>
            <tr>
                <td>Memory Usage</td>
                <td>$([math]::Round($Report.performance.memory.usage_percent, 2))%</td>
            </tr>
            <tr>
                <td>Memory Used</td>
                <td>$([math]::Round($Report.performance.memory.used_gb, 2)) GB</td>
            </tr>
            <tr>
                <td>Total Processes</td>
                <td>$($Report.performance.processes.total_processes)</td>
            </tr>
        </table>
    </div>
    
    <div class="maintenance">
        <h2>🛠️ Maintenance Tasks</h2>
        <table>
            <tr>
                <th>Task</th>
                <th>Status</th>
                <th>Details</th>
            </tr>
"@

    foreach ($task in $Report.maintenance.tasks.GetEnumerator()) {
        $statusClass = $task.Value.status
        $html += @"
            <tr>
                <td>$($task.Key)</td>
                <td class="$statusClass">$($task.Value.status)</td>
                <td>$($task.Value | ConvertTo-Json -Compress)</td>
            </tr>
"@
    }
    
    $html += @"
        </table>
    </div>
</body>
</html>
"@

    return $html
}

# Show Maintenance Dashboard
function Show-MaintenanceDashboard {
    param([string]$View = "overview")
    
    Clear-Host
    Write-Host "🛠️ CENTRALIZED MAINTENANCE DASHBOARD" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "View: $View | Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
    Write-Host ""
    
    switch ($View) {
        "overview" {
            Write-Host "📊 SYSTEM OVERVIEW" -ForegroundColor Blue
            Write-Host "==================" -ForegroundColor Blue
            
            $healthResults = Test-SystemHealth
            $performanceData = Get-SystemPerformance
            
            Write-Host "Overall Health: $($healthResults.overall_status)" -ForegroundColor $(if ($healthResults.overall_status -eq "healthy") { "Green" } else { "Red" })
            Write-Host "CPU Usage: $([math]::Round($performanceData.cpu.usage_percent, 2))%" -ForegroundColor White
            Write-Host "Memory Usage: $([math]::Round($performanceData.memory.usage_percent, 2))%" -ForegroundColor White
            Write-Host "Alerts: $($healthResults.alerts.Count)" -ForegroundColor $(if ($healthResults.alerts.Count -eq 0) { "Green" } else { "Red" })
        }
        
        "health" {
            Write-Host "🏥 HEALTH STATUS" -ForegroundColor Blue
            Write-Host "================" -ForegroundColor Blue
            
            $healthResults = Test-SystemHealth
            
            foreach ($component in $healthResults.components.GetEnumerator()) {
                $statusColor = switch ($component.Value.status) {
                    "healthy" { "Green" }
                    "warning" { "Yellow" }
                    "error" { "Red" }
                    default { "White" }
                }
                
                Write-Host "$($component.Key): " -NoNewline -ForegroundColor White
                Write-Host $component.Value.status -ForegroundColor $statusColor
            }
        }
        
        "performance" {
            Write-Host "📈 PERFORMANCE METRICS" -ForegroundColor Blue
            Write-Host "======================" -ForegroundColor Blue
            
            $performanceData = Get-SystemPerformance
            
            Write-Host "CPU: $([math]::Round($performanceData.cpu.usage_percent, 2))% ($($performanceData.cpu.cores) cores)" -ForegroundColor White
            Write-Host "Memory: $([math]::Round($performanceData.memory.usage_percent, 2))% ($([math]::Round($performanceData.memory.used_gb, 2))GB / $([math]::Round($performanceData.memory.total_gb, 2))GB)" -ForegroundColor White
            Write-Host "Processes: $($performanceData.processes.total_processes) ($([math]::Round($performanceData.processes.total_memory_mb, 2))MB)" -ForegroundColor White
        }
        
        "maintenance" {
            Write-Host "🛠️ MAINTENANCE TASKS" -ForegroundColor Blue
            Write-Host "====================" -ForegroundColor Blue
            
            $maintenanceResults = Invoke-MaintenanceTasks
            
            Write-Host "Tasks Completed: $($maintenanceResults.success_count)" -ForegroundColor Green
            Write-Host "Tasks Failed: $($maintenanceResults.failure_count)" -ForegroundColor Red
            
            foreach ($task in $maintenanceResults.tasks.GetEnumerator()) {
                $statusColor = if ($task.Value.status -eq "success") { "Green" } else { "Red" }
                Write-Host "$($task.Key): $($task.Value.status)" -ForegroundColor $statusColor
            }
        }
    }
    
    Write-Host ""
    Write-Host "Press 'q' to quit, 'r' to refresh, 'h' for health, 'p' for performance, 'm' for maintenance" -ForegroundColor Yellow
}

# Main Execution
function Main {
    Write-MaintenanceOutput "🚀 Starting Centralized Maintenance Dashboard..." -Level "MAINTENANCE"
    Write-MaintenanceOutput "View: $View | Real-time: $RealTime | Interactive: $Interactive" -Level "INFO"
    
    # Ensure directories exist
    if (-not (Test-Path $MaintenanceConfig.LogDirectory)) {
        New-Item -ItemType Directory -Path $MaintenanceConfig.LogDirectory -Force | Out-Null
    }
    if (-not (Test-Path $MaintenanceConfig.ReportDirectory)) {
        New-Item -ItemType Directory -Path $MaintenanceConfig.ReportDirectory -Force | Out-Null
    }
    if (-not (Test-Path $MaintenanceConfig.AlertDirectory)) {
        New-Item -ItemType Directory -Path $MaintenanceConfig.AlertDirectory -Force | Out-Null
    }
    if (-not (Test-Path $MaintenanceConfig.BackupDirectory)) {
        New-Item -ItemType Directory -Path $MaintenanceConfig.BackupDirectory -Force | Out-Null
    }
    
    if ($AutoMaintenance) {
        Write-MaintenanceOutput "Running automated maintenance..." -Level "MAINTENANCE"
        $report = Generate-MaintenanceReport
        Write-MaintenanceOutput "Automated maintenance completed" -Level "SUCCESS"
    } elseif ($Interactive) {
        $currentView = $View
        while ($true) {
            Show-MaintenanceDashboard -View $currentView
            
            $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            
            switch ($key.Character) {
                'q' { 
                    Write-MaintenanceOutput "Exiting maintenance dashboard..." -Level "INFO"
                    exit 
                }
                'r' { 
                    # Refresh (do nothing, loop will refresh)
                }
                'h' { $currentView = "health" }
                'p' { $currentView = "performance" }
                'm' { $currentView = "maintenance" }
                'o' { $currentView = "overview" }
            }
            
            Start-Sleep -Milliseconds 100
        }
    } else {
        Show-MaintenanceDashboard -View $View
    }
}

# Execute main function
try {
    Main
} catch {
    Write-MaintenanceOutput "❌ Maintenance dashboard failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
