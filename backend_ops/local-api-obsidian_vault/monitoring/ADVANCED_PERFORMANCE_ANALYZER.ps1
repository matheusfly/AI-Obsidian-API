# Advanced Performance Analyzer for Comprehensive Observability
# This script provides deep performance analysis and optimization recommendations

param(
    [string]$Mode = "full",  # full, quick, ai-focused, backend-focused
    [switch]$RealTime = $false,
    [int]$Duration = 300,  # seconds for real-time monitoring
    [string]$OutputFormat = "json"  # json, csv, html, dashboard
)

# Color definitions
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Blue = "Blue"
$Cyan = "Cyan"
$Magenta = "Magenta"

# Global configuration
$Config = @{
    Services = @(
        "vault-api", "obsidian-api", "n8n", "postgres", "redis", 
        "ollama", "chromadb", "qdrant", "prometheus", "grafana",
        "nginx", "embedding-service", "advanced-indexer", 
        "motia-integration", "flyde-integration"
    )
    CriticalMetrics = @(
        "cpu_usage", "memory_usage", "response_time", "error_rate",
        "throughput", "queue_depth", "cache_hit_ratio", "db_connections"
    )
    AISpecificMetrics = @(
        "token_usage", "model_response_time", "agent_interactions",
        "rag_performance", "embedding_latency", "vector_search_time"
    )
    PerformanceThresholds = @{
        CPU_WARNING = 70
        CPU_CRITICAL = 90
        MEMORY_WARNING = 80
        MEMORY_CRITICAL = 95
        RESPONSE_TIME_WARNING = 1000  # ms
        RESPONSE_TIME_CRITICAL = 5000  # ms
        ERROR_RATE_WARNING = 1  # %
        ERROR_RATE_CRITICAL = 5  # %
    }
}

function Write-PerformanceLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor $Red }
        "WARNING" { Write-Host $LogMessage -ForegroundColor $Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor $Green }
        "INFO" { Write-Host $LogMessage -ForegroundColor $Blue }
        default { Write-Host $LogMessage -ForegroundColor $Cyan }
    }
}

function Get-SystemPerformanceMetrics {
    Write-PerformanceLog "Collecting system performance metrics..." "INFO"
    
    $Metrics = @{
        Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
        System = @{}
        Services = @{}
        AI = @{}
        Recommendations = @()
    }
    
    # System-level metrics
    try {
        $CPU = Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 1
        $Memory = Get-Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 1
        $Disk = Get-Counter "\LogicalDisk(C:)\% Free Space" -SampleInterval 1 -MaxSamples 1
        
        $Metrics.System = @{
            CPU_Usage = [math]::Round($CPU.CounterSamples[0].CookedValue, 2)
            Memory_Available_MB = [math]::Round($Memory.CounterSamples[0].CookedValue, 2)
            Memory_Total_GB = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
            Memory_Usage_Percent = [math]::Round((1 - ($Memory.CounterSamples[0].CookedValue / (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory * 1024)) * 100, 2)
            Disk_Free_Percent = [math]::Round($Disk.CounterSamples[0].CookedValue, 2)
        }
        
        Write-PerformanceLog "System metrics collected successfully" "SUCCESS"
    }
    catch {
        Write-PerformanceLog "Failed to collect system metrics: $($_.Exception.Message)" "ERROR"
    }
    
    return $Metrics
}

function Get-ServicePerformanceMetrics {
    param([string]$ServiceName)
    
    $ServiceMetrics = @{
        Name = $ServiceName
        Status = "Unknown"
        Performance = @{}
        Health = "Unknown"
        LastChecked = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    }
    
    try {
        # Check Docker container status
        $ContainerInfo = docker ps --filter "name=$ServiceName" --format "{{.Status}}" 2>$null
        if ($ContainerInfo) {
            $ServiceMetrics.Status = "Running"
            $ServiceMetrics.Health = "Healthy"
            
            # Get container stats
            $Stats = docker stats $ServiceName --no-stream --format "table {{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}}" 2>$null
            if ($Stats) {
                $StatsArray = $Stats -split "`n" | Where-Object { $_ -match "," }
                if ($StatsArray.Count -gt 1) {
                    $Data = $StatsArray[1] -split ","
                    $ServiceMetrics.Performance = @{
                        CPU_Percent = $Data[0] -replace "%", ""
                        Memory_Usage = $Data[1]
                        Memory_Percent = $Data[2] -replace "%", ""
                        Network_IO = $Data[3]
                        Block_IO = $Data[4]
                    }
                }
            }
        } else {
            $ServiceMetrics.Status = "Not Running"
            $ServiceMetrics.Health = "Unhealthy"
        }
    }
    catch {
        Write-PerformanceLog "Failed to get metrics for $ServiceName : $($_.Exception.Message)" "ERROR"
        $ServiceMetrics.Status = "Error"
        $ServiceMetrics.Health = "Error"
    }
    
    return $ServiceMetrics
}

function Get-AIPerformanceMetrics {
    Write-PerformanceLog "Collecting AI-specific performance metrics..." "INFO"
    
    $AIMetrics = @{
        Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
        Ollama = @{}
        EmbeddingService = @{}
        RAG = @{}
        VectorSearch = @{}
        AgentInteractions = @{}
    }
    
    try {
        # Ollama metrics
        $OllamaStats = docker stats ollama --no-stream --format "{{.CPUPerc}},{{.MemUsage}}" 2>$null
        if ($OllamaStats) {
            $OllamaData = $OllamaStats -split ","
            $AIMetrics.Ollama = @{
                CPU_Percent = $OllamaData[0] -replace "%", ""
                Memory_Usage = $OllamaData[1]
                Status = "Running"
            }
        }
        
        # Embedding service metrics
        $EmbeddingStats = docker stats embedding-service --no-stream --format "{{.CPUPerc}},{{.MemUsage}}" 2>$null
        if ($EmbeddingStats) {
            $EmbeddingData = $EmbeddingStats -split ","
            $AIMetrics.EmbeddingService = @{
                CPU_Percent = $EmbeddingData[0] -replace "%", ""
                Memory_Usage = $EmbeddingData[1]
                Status = "Running"
            }
        }
        
        # Vector search metrics (Qdrant)
        $QdrantStats = docker stats qdrant --no-stream --format "{{.CPUPerc}},{{.MemUsage}}" 2>$null
        if ($QdrantStats) {
            $QdrantData = $QdrantStats -split ","
            $AIMetrics.VectorSearch = @{
                CPU_Percent = $QdrantData[0] -replace "%", ""
                Memory_Usage = $QdrantData[1]
                Status = "Running"
            }
        }
        
        Write-PerformanceLog "AI metrics collected successfully" "SUCCESS"
    }
    catch {
        Write-PerformanceLog "Failed to collect AI metrics: $($_.Exception.Message)" "ERROR"
    }
    
    return $AIMetrics
}

function Analyze-PerformanceData {
    param([hashtable]$Metrics)
    
    $Analysis = @{
        OverallHealth = "Good"
        CriticalIssues = @()
        Warnings = @()
        Recommendations = @()
        PerformanceScore = 100
    }
    
    # Analyze system metrics
    if ($Metrics.System.CPU_Usage -gt $Config.PerformanceThresholds.CPU_CRITICAL) {
        $Analysis.CriticalIssues += "CPU usage is critically high: $($Metrics.System.CPU_Usage)%"
        $Analysis.PerformanceScore -= 30
    }
    elseif ($Metrics.System.CPU_Usage -gt $Config.PerformanceThresholds.CPU_WARNING) {
        $Analysis.Warnings += "CPU usage is high: $($Metrics.System.CPU_Usage)%"
        $Analysis.PerformanceScore -= 15
    }
    
    if ($Metrics.System.Memory_Usage_Percent -gt $Config.PerformanceThresholds.MEMORY_CRITICAL) {
        $Analysis.CriticalIssues += "Memory usage is critically high: $($Metrics.System.Memory_Usage_Percent)%"
        $Analysis.PerformanceScore -= 25
    }
    elseif ($Metrics.System.Memory_Usage_Percent -gt $Config.PerformanceThresholds.MEMORY_WARNING) {
        $Analysis.Warnings += "Memory usage is high: $($Metrics.System.Memory_Usage_Percent)%"
        $Analysis.PerformanceScore -= 10
    }
    
    # Analyze service metrics
    foreach ($Service in $Metrics.Services.Values) {
        if ($Service.Health -eq "Unhealthy") {
            $Analysis.CriticalIssues += "Service $($Service.Name) is unhealthy"
            $Analysis.PerformanceScore -= 20
        }
        
        if ($Service.Performance.CPU_Percent -and [double]$Service.Performance.CPU_Percent -gt 80) {
            $Analysis.Warnings += "Service $($Service.Name) has high CPU usage: $($Service.Performance.CPU_Percent)%"
            $Analysis.PerformanceScore -= 5
        }
    }
    
    # Generate recommendations
    if ($Analysis.CriticalIssues.Count -gt 0) {
        $Analysis.OverallHealth = "Critical"
        $Analysis.Recommendations += "Immediate attention required for critical issues"
    }
    elseif ($Analysis.Warnings.Count -gt 0) {
        $Analysis.OverallHealth = "Warning"
        $Analysis.Recommendations += "Monitor warnings and consider optimization"
    }
    
    if ($Metrics.System.CPU_Usage -gt 70) {
        $Analysis.Recommendations += "Consider scaling services or optimizing CPU-intensive operations"
    }
    
    if ($Metrics.System.Memory_Usage_Percent -gt 80) {
        $Analysis.Recommendations += "Consider increasing memory allocation or optimizing memory usage"
    }
    
    return $Analysis
}

function Start-RealTimeMonitoring {
    param([int]$Duration)
    
    Write-PerformanceLog "Starting real-time performance monitoring for $Duration seconds..." "INFO"
    
    $StartTime = Get-Date
    $EndTime = $StartTime.AddSeconds($Duration)
    
    while ((Get-Date) -lt $EndTime) {
        Clear-Host
        Write-Host "=== REAL-TIME PERFORMANCE MONITORING ===" -ForegroundColor $Cyan
        Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $Yellow
        Write-Host "Duration: $Duration seconds | Elapsed: $([math]::Round(((Get-Date) - $StartTime).TotalSeconds, 0)) seconds" -ForegroundColor $Yellow
        Write-Host ""
        
        # Collect and display metrics
        $Metrics = Get-SystemPerformanceMetrics
        
        # Display system metrics
        Write-Host "=== SYSTEM METRICS ===" -ForegroundColor $Green
        Write-Host "CPU Usage: $($Metrics.System.CPU_Usage)%" -ForegroundColor $(if ($Metrics.System.CPU_Usage -gt 80) { $Red } else { $Green })
        Write-Host "Memory Usage: $($Metrics.System.Memory_Usage_Percent)%" -ForegroundColor $(if ($Metrics.System.Memory_Usage_Percent -gt 80) { $Red } else { $Green })
        Write-Host "Memory Available: $($Metrics.System.Memory_Available_MB) MB" -ForegroundColor $Blue
        Write-Host "Disk Free: $($Metrics.System.Disk_Free_Percent)%" -ForegroundColor $Blue
        Write-Host ""
        
        # Display service status
        Write-Host "=== SERVICE STATUS ===" -ForegroundColor $Green
        foreach ($Service in $Config.Services) {
            $ServiceMetrics = Get-ServicePerformanceMetrics -ServiceName $Service
            $StatusColor = switch ($ServiceMetrics.Health) {
                "Healthy" { $Green }
                "Unhealthy" { $Red }
                default { $Yellow }
            }
            Write-Host "$Service : $($ServiceMetrics.Status)" -ForegroundColor $StatusColor
        }
        
        Write-Host ""
        Write-Host "Press Ctrl+C to stop monitoring..." -ForegroundColor $Yellow
        
        Start-Sleep -Seconds 5
    }
    
    Write-PerformanceLog "Real-time monitoring completed" "SUCCESS"
}

function Export-PerformanceReport {
    param([hashtable]$Metrics, [hashtable]$Analysis, [string]$Format)
    
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $ReportPath = "performance_report_$Timestamp"
    
    switch ($Format.ToLower()) {
        "json" {
            $ReportPath += ".json"
            $Report = @{
                Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
                Metrics = $Metrics
                Analysis = $Analysis
            }
            $Report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8
        }
        "csv" {
            $ReportPath += ".csv"
            $CsvData = @()
            foreach ($Service in $Metrics.Services.Values) {
                $CsvData += [PSCustomObject]@{
                    Service = $Service.Name
                    Status = $Service.Status
                    Health = $Service.Health
                    CPU_Percent = $Service.Performance.CPU_Percent
                    Memory_Usage = $Service.Performance.Memory_Usage
                }
            }
            $CsvData | Export-Csv -Path $ReportPath -NoTypeInformation
        }
        "html" {
            $ReportPath += ".html"
            $HtmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>Performance Report - $Timestamp</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .metric { margin: 10px 0; padding: 10px; border-left: 4px solid #007acc; }
        .critical { border-left-color: #dc3545; background-color: #f8d7da; }
        .warning { border-left-color: #ffc107; background-color: #fff3cd; }
        .good { border-left-color: #28a745; background-color: #d4edda; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Performance Report</h1>
        <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p>Overall Health: <strong>$($Analysis.OverallHealth)</strong></p>
        <p>Performance Score: <strong>$($Analysis.PerformanceScore)/100</strong></p>
    </div>
    
    <h2>System Metrics</h2>
    <div class="metric">
        <p><strong>CPU Usage:</strong> $($Metrics.System.CPU_Usage)%</p>
        <p><strong>Memory Usage:</strong> $($Metrics.System.Memory_Usage_Percent)%</p>
        <p><strong>Memory Available:</strong> $($Metrics.System.Memory_Available_MB) MB</p>
        <p><strong>Disk Free:</strong> $($Metrics.System.Disk_Free_Percent)%</p>
    </div>
    
    <h2>Service Status</h2>
"@
            foreach ($Service in $Metrics.Services.Values) {
                $Class = switch ($Service.Health) {
                    "Healthy" { "good" }
                    "Unhealthy" { "critical" }
                    default { "warning" }
                }
                $HtmlContent += @"
    <div class="metric $Class">
        <h3>$($Service.Name)</h3>
        <p><strong>Status:</strong> $($Service.Status)</p>
        <p><strong>Health:</strong> $($Service.Health)</p>
        <p><strong>CPU:</strong> $($Service.Performance.CPU_Percent)%</p>
        <p><strong>Memory:</strong> $($Service.Performance.Memory_Usage)</p>
    </div>
"@
            }
            
            $HtmlContent += @"
    
    <h2>Recommendations</h2>
    <ul>
"@
            foreach ($Recommendation in $Analysis.Recommendations) {
                $HtmlContent += "        <li>$Recommendation</li>`n"
            }
            
            $HtmlContent += @"
    </ul>
</body>
</html>
"@
            $HtmlContent | Out-File -FilePath $ReportPath -Encoding UTF8
        }
    }
    
    Write-PerformanceLog "Performance report exported to: $ReportPath" "SUCCESS"
    return $ReportPath
}

# Main execution
Write-PerformanceLog "Starting Advanced Performance Analyzer..." "INFO"
Write-PerformanceLog "Mode: $Mode | Real-time: $RealTime | Duration: $Duration | Output: $OutputFormat" "INFO"

if ($RealTime) {
    Start-RealTimeMonitoring -Duration $Duration
} else {
    # Collect comprehensive metrics
    Write-PerformanceLog "Collecting comprehensive performance metrics..." "INFO"
    
    $AllMetrics = Get-SystemPerformanceMetrics
    $AllMetrics.Services = @{}
    $AllMetrics.AI = @{}
    
    # Collect service metrics
    foreach ($Service in $Config.Services) {
        Write-PerformanceLog "Analyzing service: $Service" "INFO"
        $AllMetrics.Services[$Service] = Get-ServicePerformanceMetrics -ServiceName $Service
    }
    
    # Collect AI-specific metrics
    if ($Mode -eq "full" -or $Mode -eq "ai-focused") {
        $AllMetrics.AI = Get-AIPerformanceMetrics
    }
    
    # Analyze performance data
    Write-PerformanceLog "Analyzing performance data..." "INFO"
    $Analysis = Analyze-PerformanceData -Metrics $AllMetrics
    
    # Display results
    Write-Host ""
    Write-Host "=== PERFORMANCE ANALYSIS RESULTS ===" -ForegroundColor $Cyan
    Write-Host "Overall Health: $($Analysis.OverallHealth)" -ForegroundColor $(switch ($Analysis.OverallHealth) {
        "Critical" { $Red }
        "Warning" { $Yellow }
        default { $Green }
    })
    Write-Host "Performance Score: $($Analysis.PerformanceScore)/100" -ForegroundColor $Blue
    Write-Host ""
    
    if ($Analysis.CriticalIssues.Count -gt 0) {
        Write-Host "=== CRITICAL ISSUES ===" -ForegroundColor $Red
        foreach ($Issue in $Analysis.CriticalIssues) {
            Write-Host "• $Issue" -ForegroundColor $Red
        }
        Write-Host ""
    }
    
    if ($Analysis.Warnings.Count -gt 0) {
        Write-Host "=== WARNINGS ===" -ForegroundColor $Yellow
        foreach ($Warning in $Analysis.Warnings) {
            Write-Host "• $Warning" -ForegroundColor $Yellow
        }
        Write-Host ""
    }
    
    if ($Analysis.Recommendations.Count -gt 0) {
        Write-Host "=== RECOMMENDATIONS ===" -ForegroundColor $Green
        foreach ($Recommendation in $Analysis.Recommendations) {
            Write-Host "• $Recommendation" -ForegroundColor $Green
        }
        Write-Host ""
    }
    
    # Export report
    if ($OutputFormat -ne "console") {
        $ReportPath = Export-PerformanceReport -Metrics $AllMetrics -Analysis $Analysis -Format $OutputFormat
        Write-PerformanceLog "Report saved to: $ReportPath" "SUCCESS"
    }
}

Write-PerformanceLog "Advanced Performance Analyzer completed" "SUCCESS"
