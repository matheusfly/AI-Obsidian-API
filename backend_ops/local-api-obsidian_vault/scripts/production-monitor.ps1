# 🏥 PRODUCTION MONITORING SYSTEM
# Comprehensive health checks, performance monitoring, and alerting
# Version: 3.0.0 - Production Ready

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("full", "health", "performance", "security", "logs")]
    [string]$Mode = "full",
    
    [Parameter(Mandatory=$false)]
    [switch]$Continuous = $false,
    
    [Parameter(Mandatory=$false)]
    [int]$Interval = 30,
    
    [Parameter(Mandatory=$false)]
    [string]$LogFile = "monitoring.log",
    
    [Parameter(Mandatory=$false)]
    [switch]$Alert = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$WebhookUrl = ""
)

# Performance Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Monitoring Configuration
$MonitoringConfig = @{
    HealthCheckTimeout = 10
    PerformanceThresholds = @{
        CPU = 80
        Memory = 85
        Disk = 90
        ResponseTime = 5000
    }
    AlertThresholds = @{
        CPU = 90
        Memory = 95
        Disk = 95
        ResponseTime = 10000
    }
    Services = @(
        @{ Name = "vault-api"; URL = "http://localhost:8080/health"; Port = 8080 }
        @{ Name = "obsidian-api"; URL = "http://localhost:27123/health"; Port = 27123 }
        @{ Name = "n8n"; URL = "http://localhost:5678/healthz"; Port = 5678 }
        @{ Name = "postgres"; URL = "localhost:5432"; Port = 5432 }
        @{ Name = "redis"; URL = "localhost:6379"; Port = 6379 }
        @{ Name = "chromadb"; URL = "http://localhost:8000/api/v1/heartbeat"; Port = 8000 }
        @{ Name = "ollama"; URL = "http://localhost:11434/api/tags"; Port = 11434 }
        @{ Name = "prometheus"; URL = "http://localhost:9090/-/healthy"; Port = 9090 }
        @{ Name = "grafana"; URL = "http://localhost:3004/api/health"; Port = 3004 }
    )
}

# Performance Metrics Storage
$PerformanceMetrics = @{
    StartTime = Get-Date
    Checks = @()
    Alerts = @()
    SystemStats = @{}
}

# Logging Functions
function Write-MonitorLog {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Service = "MONITOR"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "[$timestamp] [$Level] [$Service] $Message"
    
    # Console output
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        "DEBUG" { "Gray" }
        default { "White" }
    }
    
    Write-Host $logEntry -ForegroundColor $color
    
    # File logging
    Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
}

function Write-Banner {
    Write-MonitorLog @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🏥 PRODUCTION MONITORING SYSTEM 🏥                       ║
║                         Version 3.0.0 - Production Ready                    ║
║                    Mode: $Mode | Continuous: $Continuous | Interval: $Interval ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Level "INFO"
}

# Health Check Functions
function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [string]$HealthUrl,
        [int]$Port
    )
    
    $startTime = Get-Date
    
    try {
        # Test port connectivity first
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connect = $tcpClient.BeginConnect("localhost", $Port, $null, $null)
        $wait = $connect.AsyncWaitHandle.WaitOne($MonitoringConfig.HealthCheckTimeout * 1000, $false)
        
        if (-not $wait) {
            $tcpClient.Close()
            return @{
                Service = $ServiceName
                Status = "DOWN"
                ResponseTime = -1
                Error = "Port $Port not accessible"
                Timestamp = Get-Date
            }
        }
        
        $tcpClient.EndConnect($connect)
        $tcpClient.Close()
        
        # Test HTTP endpoint if URL provided
        if ($HealthUrl -and $HealthUrl.StartsWith("http")) {
            $response = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec $MonitoringConfig.HealthCheckTimeout -ErrorAction Stop
        }
        
        $responseTime = ((Get-Date) - $startTime).TotalMilliseconds
        
        return @{
            Service = $ServiceName
            Status = "UP"
            ResponseTime = [math]::Round($responseTime, 2)
            Error = $null
            Timestamp = Get-Date
        }
        
    } catch {
        $responseTime = ((Get-Date) - $startTime).TotalMilliseconds
        
        return @{
            Service = $ServiceName
            Status = "DOWN"
            ResponseTime = [math]::Round($responseTime, 2)
            Error = $_.Exception.Message
            Timestamp = Get-Date
        }
    }
}

function Get-SystemPerformance {
    $cpu = Get-Counter -Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 1
    $memory = Get-Counter -Counter "\Memory\Available MBytes"
    $disk = Get-Counter -Counter "\LogicalDisk(C:)\% Free Space"
    
    $processes = Get-Process | Where-Object { $_.ProcessName -match "(python|node|postgres|redis|ollama)" }
    $totalMemory = ($processes | Measure-Object -Property WorkingSet -Sum).Sum / 1MB
    
    return @{
        CPU = [math]::Round($cpu.CounterSamples[0].CookedValue, 2)
        MemoryAvailable = [math]::Round($memory.CounterSamples[0].CookedValue, 2)
        MemoryUsed = [math]::Round($totalMemory, 2)
        DiskFree = [math]::Round($disk.CounterSamples[0].CookedValue, 2)
        ProcessCount = $processes.Count
        Timestamp = Get-Date
    }
}

function Test-SecurityChecks {
    $securityIssues = @()
    
    # Check for exposed ports
    $netstat = netstat -an | Select-String "LISTENING"
    $exposedPorts = $netstat | Where-Object { $_ -match ":80|:443|:8080|:3000|:5432|:6379" }
    
    if ($exposedPorts.Count -gt 0) {
        $securityIssues += "Exposed ports detected: $($exposedPorts -join ', ')"
    }
    
    # Check for weak passwords in environment
    $envVars = Get-ChildItem Env: | Where-Object { $_.Name -match "PASSWORD|SECRET|KEY" }
    foreach ($var in $envVars) {
        if ($var.Value.Length -lt 8) {
            $securityIssues += "Weak password detected in $($var.Name)"
        }
    }
    
    # Check for running services as administrator
    $processes = Get-Process | Where-Object { $_.ProcessName -match "(python|node)" }
    foreach ($proc in $processes) {
        try {
            $owner = (Get-WmiObject -Class Win32_Process -Filter "ProcessId = $($proc.Id)").GetOwner()
            if ($owner.Domain -eq "BUILTIN" -and $owner.User -eq "Administrator") {
                $securityIssues += "Service $($proc.ProcessName) running as Administrator"
            }
        } catch {
            # Ignore access denied errors
        }
    }
    
    return $securityIssues
}

function Send-Alert {
    param(
        [string]$Message,
        [string]$Severity = "WARNING"
    )
    
    $alert = @{
        Timestamp = Get-Date
        Severity = $Severity
        Message = $Message
        SystemStats = $PerformanceMetrics.SystemStats
    }
    
    $PerformanceMetrics.Alerts += $alert
    Write-MonitorLog "🚨 ALERT [$Severity]: $Message" -Level "ERROR"
    
    # Send webhook if configured
    if ($WebhookUrl -and $Alert) {
        try {
            $payload = @{
                text = "🚨 Production Alert: $Message"
                attachments = @(
                    @{
                        color = if ($Severity -eq "CRITICAL") { "danger" } else { "warning" }
                        fields = @(
                            @{
                                title = "Severity"
                                value = $Severity
                                short = $true
                            },
                            @{
                                title = "Timestamp"
                                value = $alert.Timestamp.ToString("yyyy-MM-dd HH:mm:ss")
                                short = $true
                            },
                            @{
                                title = "System Stats"
                                value = "CPU: $($PerformanceMetrics.SystemStats.CPU)% | Memory: $($PerformanceMetrics.SystemStats.MemoryUsed)MB"
                                short = $false
                            }
                        )
                    }
                )
            } | ConvertTo-Json -Depth 3
            
            Invoke-RestMethod -Uri $WebhookUrl -Method Post -Body $payload -ContentType "application/json"
        } catch {
            Write-MonitorLog "Failed to send webhook alert: $($_.Exception.Message)" -Level "ERROR"
        }
    }
}

function Start-HealthMonitoring {
    Write-MonitorLog "🏥 Starting health monitoring..." -Level "INFO"
    
    $healthyServices = 0
    $totalServices = $MonitoringConfig.Services.Count
    
    foreach ($service in $MonitoringConfig.Services) {
        $result = Test-ServiceHealth -ServiceName $service.Name -HealthUrl $service.URL -Port $service.Port
        $PerformanceMetrics.Checks += $result
        
        if ($result.Status -eq "UP") {
            $healthyServices++
            Write-MonitorLog "✅ $($service.Name): UP ($($result.ResponseTime)ms)" -Level "SUCCESS"
        } else {
            Write-MonitorLog "❌ $($service.Name): DOWN - $($result.Error)" -Level "ERROR"
            Send-Alert -Message "Service $($service.Name) is down: $($result.Error)" -Severity "CRITICAL"
        }
    }
    
    $healthPercentage = [math]::Round(($healthyServices / $totalServices) * 100, 2)
    Write-MonitorLog "📊 Health Status: $healthyServices/$totalServices services healthy ($healthPercentage%)" -Level "INFO"
    
    if ($healthPercentage -lt 80) {
        Send-Alert -Message "System health below 80%: $healthPercentage%" -Severity "WARNING"
    }
    
    return $healthPercentage
}

function Start-PerformanceMonitoring {
    Write-MonitorLog "📊 Starting performance monitoring..." -Level "INFO"
    
    $stats = Get-SystemPerformance
    $PerformanceMetrics.SystemStats = $stats
    
    Write-MonitorLog "📊 System Performance:" -Level "INFO"
    Write-MonitorLog "   CPU: $($stats.CPU)%" -Level "INFO"
    Write-MonitorLog "   Memory Available: $($stats.MemoryAvailable)MB" -Level "INFO"
    Write-MonitorLog "   Memory Used: $($stats.MemoryUsed)MB" -Level "INFO"
    Write-MonitorLog "   Disk Free: $($stats.DiskFree)%" -Level "INFO"
    Write-MonitorLog "   Process Count: $($stats.ProcessCount)" -Level "INFO"
    
    # Check thresholds
    if ($stats.CPU -gt $MonitoringConfig.AlertThresholds.CPU) {
        Send-Alert -Message "High CPU usage: $($stats.CPU)%" -Severity "CRITICAL"
    } elseif ($stats.CPU -gt $MonitoringConfig.PerformanceThresholds.CPU) {
        Send-Alert -Message "Elevated CPU usage: $($stats.CPU)%" -Severity "WARNING"
    }
    
    if ($stats.MemoryUsed -gt ($stats.MemoryAvailable * 0.95)) {
        Send-Alert -Message "High memory usage: $($stats.MemoryUsed)MB used" -Severity "CRITICAL"
    }
    
    if ($stats.DiskFree -lt (100 - $MonitoringConfig.AlertThresholds.Disk)) {
        Send-Alert -Message "Low disk space: $($stats.DiskFree)% free" -Severity "CRITICAL"
    }
}

function Start-SecurityMonitoring {
    Write-MonitorLog "🔒 Starting security monitoring..." -Level "INFO"
    
    $securityIssues = Test-SecurityChecks
    
    if ($securityIssues.Count -gt 0) {
        foreach ($issue in $securityIssues) {
            Write-MonitorLog "⚠️ Security Issue: $issue" -Level "WARN"
            Send-Alert -Message "Security issue detected: $issue" -Severity "WARNING"
        }
    } else {
        Write-MonitorLog "✅ No security issues detected" -Level "SUCCESS"
    }
}

function Start-LogMonitoring {
    Write-MonitorLog "📝 Starting log monitoring..." -Level "INFO"
    
    $logFiles = @(
        "logs/vault-api/app.log",
        "logs/obsidian-api/app.log",
        "logs/n8n/app.log",
        "logs/postgres/postgres.log",
        "logs/redis/redis.log"
    )
    
    foreach ($logFile in $logFiles) {
        if (Test-Path $logFile) {
            $recentErrors = Get-Content $logFile -Tail 100 | Select-String "ERROR|FATAL|CRITICAL" | Select-Object -Last 5
            
            if ($recentErrors) {
                Write-MonitorLog "⚠️ Recent errors in $logFile:" -Level "WARN"
                foreach ($error in $recentErrors) {
                    Write-MonitorLog "   $error" -Level "WARN"
                }
            }
        }
    }
}

function Show-MonitoringReport {
    $totalTime = (Get-Date) - $PerformanceMetrics.StartTime
    
    Write-MonitorLog "📋 Monitoring Report:" -Level "INFO"
    Write-MonitorLog "   Duration: $($totalTime.TotalMinutes.ToString('F2')) minutes" -Level "INFO"
    Write-MonitorLog "   Health Checks: $($PerformanceMetrics.Checks.Count)" -Level "INFO"
    Write-MonitorLog "   Alerts Generated: $($PerformanceMetrics.Alerts.Count)" -Level "INFO"
    
    if ($PerformanceMetrics.Alerts.Count -gt 0) {
        Write-MonitorLog "🚨 Recent Alerts:" -Level "WARN"
        foreach ($alert in $PerformanceMetrics.Alerts | Select-Object -Last 5) {
            Write-MonitorLog "   [$($alert.Severity)] $($alert.Message)" -Level "WARN"
        }
    }
}

# Main Execution
function Main {
    Write-Banner
    
    do {
        $startTime = Get-Date
        
        switch ($Mode) {
            "health" {
                Start-HealthMonitoring | Out-Null
            }
            "performance" {
                Start-PerformanceMonitoring
            }
            "security" {
                Start-SecurityMonitoring
            }
            "logs" {
                Start-LogMonitoring
            }
            "full" {
                Start-HealthMonitoring | Out-Null
                Start-PerformanceMonitoring
                Start-SecurityMonitoring
                Start-LogMonitoring
            }
        }
        
        if ($Continuous) {
            $elapsed = (Get-Date) - $startTime
            $sleepTime = [math]::Max(1, $Interval - $elapsed.TotalSeconds)
            Write-MonitorLog "⏳ Next check in $($sleepTime.ToString('F1')) seconds..." -Level "DEBUG"
            Start-Sleep -Seconds $sleepTime
        }
        
    } while ($Continuous)
    
    Show-MonitoringReport
}

# Execute main function
Main

