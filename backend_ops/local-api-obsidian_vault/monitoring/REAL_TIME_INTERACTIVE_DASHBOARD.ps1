# Real-Time Interactive Dashboard for Comprehensive Observability
# Live monitoring with interactive controls and advanced visualizations

param(
    [string]$Mode = "full",  # full, compact, ai-focused, backend-focused
    [switch]$AutoRefresh = $true,
    [int]$RefreshInterval = 5,  # seconds
    [string]$Theme = "dark",  # dark, light, auto
    [switch]$SoundAlerts = $false,
    [string]$LogLevel = "INFO"  # DEBUG, INFO, WARNING, ERROR
)

# Color schemes
$Themes = @{
    dark = @{
        background = "Black"
        foreground = "White"
        primary = "Cyan"
        success = "Green"
        warning = "Yellow"
        error = "Red"
        info = "Blue"
        accent = "Magenta"
    }
    light = @{
        background = "White"
        foreground = "Black"
        primary = "DarkCyan"
        success = "DarkGreen"
        warning = "DarkYellow"
        error = "DarkRed"
        info = "DarkBlue"
        accent = "DarkMagenta"
    }
}

# Global configuration
$Config = @{
    Services = @(
        "vault-api", "obsidian-api", "n8n", "postgres", "redis", 
        "ollama", "chromadb", "qdrant", "prometheus", "grafana",
        "nginx", "embedding-service", "advanced-indexer", 
        "motia-integration", "flyde-integration"
    )
    AIServices = @(
        "ollama", "embedding-service", "advanced-indexer", 
        "qdrant", "motia-integration", "flyde-integration"
    )
    BackendServices = @(
        "vault-api", "obsidian-api", "n8n", "postgres", "redis", "nginx"
    )
    MonitoringServices = @(
        "prometheus", "grafana"
    )
    RefreshInterval = $RefreshInterval
    AutoRefresh = $AutoRefresh
    SoundAlerts = $SoundAlerts
    LogLevel = $LogLevel
}

# Initialize theme
$Colors = $Themes[$Theme]

# Dashboard state
$DashboardState = @{
    StartTime = Get-Date
    LastRefresh = Get-Date
    RefreshCount = 0
    Alerts = @()
    PerformanceHistory = @()
    ServiceStatus = @{}
    SystemMetrics = @{}
    AIMetrics = @{}
    WorkflowMetrics = @{}
    IsRunning = $true
}

function Write-DashboardLog {
    param([string]$Message, [string]$Level = "INFO")
    
    $Timestamp = Get-Date -Format "HH:mm:ss.fff"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    # Filter by log level
    $LogLevels = @{ "DEBUG" = 0; "INFO" = 1; "WARNING" = 2; "ERROR" = 3 }
    if ($LogLevels[$Level] -lt $LogLevels[$Config.LogLevel]) { return }
    
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor $Colors.error }
        "WARNING" { Write-Host $LogMessage -ForegroundColor $Colors.warning }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor $Colors.success }
        "INFO" { Write-Host $LogMessage -ForegroundColor $Colors.info }
        "DEBUG" { Write-Host $LogMessage -ForegroundColor $Colors.accent }
    }
}

function Get-SystemMetrics {
    try {
        $CPU = Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 1
        $Memory = Get-Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 1
        $Disk = Get-Counter "\LogicalDisk(C:)\% Free Space" -SampleInterval 1 -MaxSamples 1
        
        return @{
            CPU_Usage = [math]::Round($CPU.CounterSamples[0].CookedValue, 2)
            Memory_Available_MB = [math]::Round($Memory.CounterSamples[0].CookedValue, 2)
            Memory_Total_GB = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
            Memory_Usage_Percent = [math]::Round((1 - ($Memory.CounterSamples[0].CookedValue / (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory * 1024)) * 100, 2)
            Disk_Free_Percent = [math]::Round($Disk.CounterSamples[0].CookedValue, 2)
            Timestamp = Get-Date
        }
    }
    catch {
        Write-DashboardLog "Failed to collect system metrics: $($_.Exception.Message)" "ERROR"
        return @{}
    }
}

function Get-ServiceStatus {
    param([string]$ServiceName)
    
    try {
        $ContainerInfo = docker ps --filter "name=$ServiceName" --format "{{.Status}},{{.Names}},{{.Image}}" 2>$null
        if ($ContainerInfo) {
            $StatusData = $ContainerInfo -split ","
            return @{
                Name = $ServiceName
                Status = "Running"
                Health = "Healthy"
                ContainerName = $StatusData[1]
                Image = $StatusData[2]
                LastChecked = Get-Date
            }
        } else {
            return @{
                Name = $ServiceName
                Status = "Not Running"
                Health = "Unhealthy"
                ContainerName = ""
                Image = ""
                LastChecked = Get-Date
            }
        }
    }
    catch {
        Write-DashboardLog "Failed to get status for $ServiceName : $($_.Exception.Message)" "ERROR"
        return @{
            Name = $ServiceName
            Status = "Error"
            Health = "Error"
            ContainerName = ""
            Image = ""
            LastChecked = Get-Date
        }
    }
}

function Get-AIMetrics {
    $AIMetrics = @{
        Timestamp = Get-Date
        Ollama = @{}
        EmbeddingService = @{}
        VectorSearch = @{}
        AgentInteractions = @{}
        ModelCalls = 0
        TokenUsage = 0
        ResponseTime = 0
    }
    
    try {
        # Get Ollama metrics
        $OllamaStats = docker stats ollama --no-stream --format "{{.CPUPerc}},{{.MemUsage}},{{.NetIO}}" 2>$null
        if ($OllamaStats) {
            $OllamaData = $OllamaStats -split ","
            $AIMetrics.Ollama = @{
                CPU_Percent = $OllamaData[0] -replace "%", ""
                Memory_Usage = $OllamaData[1]
                Network_IO = $OllamaData[2]
                Status = "Running"
            }
        }
        
        # Get Embedding Service metrics
        $EmbeddingStats = docker stats embedding-service --no-stream --format "{{.CPUPerc}},{{.MemUsage}}" 2>$null
        if ($EmbeddingStats) {
            $EmbeddingData = $EmbeddingStats -split ","
            $AIMetrics.EmbeddingService = @{
                CPU_Percent = $EmbeddingData[0] -replace "%", ""
                Memory_Usage = $EmbeddingData[1]
                Status = "Running"
            }
        }
        
        # Get Qdrant metrics
        $QdrantStats = docker stats qdrant --no-stream --format "{{.CPUPerc}},{{.MemUsage}}" 2>$null
        if ($QdrantStats) {
            $QdrantData = $QdrantStats -split ","
            $AIMetrics.VectorSearch = @{
                CPU_Percent = $QdrantData[0] -replace "%", ""
                Memory_Usage = $QdrantData[1]
                Status = "Running"
            }
        }
        
        # Simulate AI agent metrics (in real implementation, this would come from the AI observability service)
        $AIMetrics.AgentInteractions = @{
            ActiveAgents = Get-Random -Minimum 1 -Maximum 10
            CompletedTasks = Get-Random -Minimum 50 -Maximum 200
            FailedTasks = Get-Random -Minimum 0 -Maximum 5
            AverageResponseTime = Get-Random -Minimum 500 -Maximum 3000
        }
        
        $AIMetrics.ModelCalls = Get-Random -Minimum 100 -Maximum 1000
        $AIMetrics.TokenUsage = Get-Random -Minimum 5000 -Maximum 50000
        
    }
    catch {
        Write-DashboardLog "Failed to collect AI metrics: $($_.Exception.Message)" "ERROR"
    }
    
    return $AIMetrics
}

function Show-Header {
    Clear-Host
    $Uptime = (Get-Date) - $DashboardState.StartTime
    
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.primary
    Write-Host "║                    REAL-TIME INTERACTIVE OBSERVABILITY DASHBOARD                    ║" -ForegroundColor $Colors.primary
    Write-Host "╠══════════════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor $Colors.primary
    Write-Host "║ Mode: $($Mode.PadRight(15)) │ Uptime: $($Uptime.ToString('hh\:mm\:ss').PadRight(10)) │ Refresh: $($Config.RefreshInterval)s │ Count: $($DashboardState.RefreshCount.ToString().PadLeft(6)) ║" -ForegroundColor $Colors.foreground
    Write-Host "║ Theme: $($Theme.PadRight(12)) │ Auto: $($Config.AutoRefresh.ToString().PadRight(5)) │ Sound: $($Config.SoundAlerts.ToString().PadRight(5)) │ Level: $($Config.LogLevel.PadRight(5)) ║" -ForegroundColor $Colors.foreground
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.primary
    Write-Host ""
}

function Show-SystemMetrics {
    Write-Host "🖥️  SYSTEM METRICS" -ForegroundColor $Colors.accent
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Colors.primary
    
    $SystemMetrics = $DashboardState.SystemMetrics
    
    if ($SystemMetrics.Count -gt 0) {
        # CPU Usage with color coding
        $CPUColor = if ($SystemMetrics.CPU_Usage -gt 80) { $Colors.error } 
                   elseif ($SystemMetrics.CPU_Usage -gt 60) { $Colors.warning } 
                   else { $Colors.success }
        
        Write-Host "CPU Usage:     " -NoNewline -ForegroundColor $Colors.foreground
        Write-Host "$($SystemMetrics.CPU_Usage.ToString().PadLeft(6))%" -ForegroundColor $CPUColor
        Write-Host "               " -NoNewline
        Write-Host "[" -NoNewline -ForegroundColor $Colors.primary
        $BarLength = [math]::Round($SystemMetrics.CPU_Usage / 2)
        for ($i = 0; $i -lt 50; $i++) {
            if ($i -lt $BarLength) {
                Write-Host "█" -NoNewline -ForegroundColor $CPUColor
            } else {
                Write-Host "░" -NoNewline -ForegroundColor $Colors.primary
            }
        }
        Write-Host "]" -ForegroundColor $Colors.primary
        
        # Memory Usage
        $MemoryColor = if ($SystemMetrics.Memory_Usage_Percent -gt 85) { $Colors.error } 
                      elseif ($SystemMetrics.Memory_Usage_Percent -gt 70) { $Colors.warning } 
                      else { $Colors.success }
        
        Write-Host "Memory Usage:  " -NoNewline -ForegroundColor $Colors.foreground
        Write-Host "$($SystemMetrics.Memory_Usage_Percent.ToString().PadLeft(6))%" -ForegroundColor $MemoryColor
        Write-Host "               " -NoNewline
        Write-Host "[" -NoNewline -ForegroundColor $Colors.primary
        $BarLength = [math]::Round($SystemMetrics.Memory_Usage_Percent / 2)
        for ($i = 0; $i -lt 50; $i++) {
            if ($i -lt $BarLength) {
                Write-Host "█" -NoNewline -ForegroundColor $MemoryColor
            } else {
                Write-Host "░" -NoNewline -ForegroundColor $Colors.primary
            }
        }
        Write-Host "]" -ForegroundColor $Colors.primary
        
        Write-Host "Memory Total:  $($SystemMetrics.Memory_Total_GB.ToString().PadLeft(6)) GB" -ForegroundColor $Colors.info
        Write-Host "Memory Free:   $($SystemMetrics.Memory_Available_MB.ToString().PadLeft(6)) MB" -ForegroundColor $Colors.info
        Write-Host "Disk Free:     $($SystemMetrics.Disk_Free_Percent.ToString().PadLeft(6))%" -ForegroundColor $Colors.info
    } else {
        Write-Host "System metrics not available" -ForegroundColor $Colors.warning
    }
    
    Write-Host ""
}

function Show-ServiceStatus {
    Write-Host "🔧 SERVICE STATUS" -ForegroundColor $Colors.accent
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Colors.primary
    
    $ServicesToShow = switch ($Mode) {
        "ai-focused" { $Config.AIServices }
        "backend-focused" { $Config.BackendServices }
        "monitoring" { $Config.MonitoringServices }
        default { $Config.Services }
    }
    
    $HealthyCount = 0
    $UnhealthyCount = 0
    $ErrorCount = 0
    
    foreach ($Service in $ServicesToShow) {
        $Status = $DashboardState.ServiceStatus[$Service]
        if (-not $Status) {
            $Status = Get-ServiceStatus -ServiceName $Service
            $DashboardState.ServiceStatus[$Service] = $Status
        }
        
        $StatusColor = switch ($Status.Health) {
            "Healthy" { $Colors.success; $HealthyCount++ }
            "Unhealthy" { $Colors.error; $UnhealthyCount++ }
            "Error" { $Colors.error; $ErrorCount++ }
            default { $Colors.warning }
        }
        
        $StatusIcon = switch ($Status.Health) {
            "Healthy" { "✅" }
            "Unhealthy" { "❌" }
            "Error" { "⚠️" }
            default { "⏳" }
        }
        
        Write-Host "$StatusIcon $($Service.PadRight(20)) " -NoNewline -ForegroundColor $Colors.foreground
        Write-Host "$($Status.Status.PadRight(15)) " -NoNewline -ForegroundColor $StatusColor
        Write-Host "$($Status.Health)" -ForegroundColor $StatusColor
    }
    
    Write-Host ""
    Write-Host "Summary: " -NoNewline -ForegroundColor $Colors.foreground
    Write-Host "Healthy: $HealthyCount " -NoNewline -ForegroundColor $Colors.success
    Write-Host "Unhealthy: $UnhealthyCount " -NoNewline -ForegroundColor $Colors.error
    Write-Host "Errors: $ErrorCount" -ForegroundColor $Colors.error
    Write-Host ""
}

function Show-AIMetrics {
    if ($Mode -eq "ai-focused" -or $Mode -eq "full") {
        Write-Host "🤖 AI METRICS" -ForegroundColor $Colors.accent
        Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Colors.primary
        
        $AIMetrics = $DashboardState.AIMetrics
        
        if ($AIMetrics.Count -gt 0) {
            # Ollama metrics
            if ($AIMetrics.Ollama.Count -gt 0) {
                Write-Host "Ollama:        " -NoNewline -ForegroundColor $Colors.foreground
                Write-Host "CPU: $($AIMetrics.Ollama.CPU_Percent)% " -NoNewline -ForegroundColor $Colors.info
                Write-Host "Memory: $($AIMetrics.Ollama.Memory_Usage) " -NoNewline -ForegroundColor $Colors.info
                Write-Host "Status: $($AIMetrics.Ollama.Status)" -ForegroundColor $Colors.success
            }
            
            # Embedding Service metrics
            if ($AIMetrics.EmbeddingService.Count -gt 0) {
                Write-Host "Embedding:     " -NoNewline -ForegroundColor $Colors.foreground
                Write-Host "CPU: $($AIMetrics.EmbeddingService.CPU_Percent)% " -NoNewline -ForegroundColor $Colors.info
                Write-Host "Memory: $($AIMetrics.EmbeddingService.Memory_Usage) " -NoNewline -ForegroundColor $Colors.info
                Write-Host "Status: $($AIMetrics.EmbeddingService.Status)" -ForegroundColor $Colors.success
            }
            
            # Vector Search metrics
            if ($AIMetrics.VectorSearch.Count -gt 0) {
                Write-Host "Vector Search: " -NoNewline -ForegroundColor $Colors.foreground
                Write-Host "CPU: $($AIMetrics.VectorSearch.CPU_Percent)% " -NoNewline -ForegroundColor $Colors.info
                Write-Host "Memory: $($AIMetrics.VectorSearch.Memory_Usage) " -NoNewline -ForegroundColor $Colors.info
                Write-Host "Status: $($AIMetrics.VectorSearch.Status)" -ForegroundColor $Colors.success
            }
            
            # Agent Interactions
            if ($AIMetrics.AgentInteractions.Count -gt 0) {
                Write-Host ""
                Write-Host "Agent Interactions:" -ForegroundColor $Colors.foreground
                Write-Host "  Active Agents:    $($AIMetrics.AgentInteractions.ActiveAgents)" -ForegroundColor $Colors.info
                Write-Host "  Completed Tasks:  $($AIMetrics.AgentInteractions.CompletedTasks)" -ForegroundColor $Colors.success
                Write-Host "  Failed Tasks:     $($AIMetrics.AgentInteractions.FailedTasks)" -ForegroundColor $Colors.error
                Write-Host "  Avg Response:     $($AIMetrics.AgentInteractions.AverageResponseTime)ms" -ForegroundColor $Colors.info
            }
            
            Write-Host ""
            Write-Host "Model Calls:    $($AIMetrics.ModelCalls)" -ForegroundColor $Colors.info
            Write-Host "Token Usage:    $($AIMetrics.TokenUsage)" -ForegroundColor $Colors.info
        } else {
            Write-Host "AI metrics not available" -ForegroundColor $Colors.warning
        }
        
        Write-Host ""
    }
}

function Show-Alerts {
    if ($DashboardState.Alerts.Count -gt 0) {
        Write-Host "🚨 ALERTS" -ForegroundColor $Colors.accent
        Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Colors.primary
        
        foreach ($Alert in $DashboardState.Alerts) {
            $AlertColor = switch ($Alert.Severity) {
                "Critical" { $Colors.error }
                "Warning" { $Colors.warning }
                default { $Colors.info }
            }
            
            $AlertIcon = switch ($Alert.Severity) {
                "Critical" { "🔴" }
                "Warning" { "🟡" }
                default { "🔵" }
            }
            
            Write-Host "$AlertIcon [$($Alert.Timestamp)] $($Alert.Message)" -ForegroundColor $AlertColor
        }
        
        Write-Host ""
    }
}

function Show-PerformanceHistory {
    if ($DashboardState.PerformanceHistory.Count -gt 0) {
        Write-Host "📊 PERFORMANCE HISTORY" -ForegroundColor $Colors.accent
        Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Colors.primary
        
        $RecentHistory = $DashboardState.PerformanceHistory | Select-Object -Last 10
        
        foreach ($Entry in $RecentHistory) {
            $TimeStr = $Entry.Timestamp.ToString("HH:mm:ss")
            $CPUStr = $Entry.CPU_Usage.ToString("F1").PadLeft(5)
            $MemStr = $Entry.Memory_Usage_Percent.ToString("F1").PadLeft(5)
            
            Write-Host "$TimeStr │ CPU: $CPUStr% │ Memory: $MemStr%" -ForegroundColor $Colors.info
        }
        
        Write-Host ""
    }
}

function Show-Controls {
    Write-Host "🎮 CONTROLS" -ForegroundColor $Colors.accent
    Write-Host "──────────────────────────────────────────────────────────────────────────────────────" -ForegroundColor $Colors.primary
    Write-Host "Press 'q' to quit │ 'r' to refresh │ 's' to toggle sound │ 't' to change theme" -ForegroundColor $Colors.foreground
    Write-Host "Press '1-4' for modes │ 'a' for AI focus │ 'b' for backend focus │ 'm' for monitoring" -ForegroundColor $Colors.foreground
    Write-Host ""
}

function Update-DashboardData {
    Write-DashboardLog "Updating dashboard data..." "DEBUG"
    
    # Update system metrics
    $DashboardState.SystemMetrics = Get-SystemMetrics
    
    # Update AI metrics
    $DashboardState.AIMetrics = Get-AIMetrics
    
    # Update service status (only for services that need updating)
    $ServicesToUpdate = switch ($Mode) {
        "ai-focused" { $Config.AIServices }
        "backend-focused" { $Config.BackendServices }
        "monitoring" { $Config.MonitoringServices }
        default { $Config.Services }
    }
    
    foreach ($Service in $ServicesToUpdate) {
        if (-not $DashboardState.ServiceStatus[$Service] -or 
            ((Get-Date) - $DashboardState.ServiceStatus[$Service].LastChecked).TotalSeconds -gt 30) {
            $DashboardState.ServiceStatus[$Service] = Get-ServiceStatus -ServiceName $Service
        }
    }
    
    # Add to performance history
    if ($DashboardState.SystemMetrics.Count -gt 0) {
        $DashboardState.PerformanceHistory += $DashboardState.SystemMetrics
        if ($DashboardState.PerformanceHistory.Count -gt 50) {
            $DashboardState.PerformanceHistory = $DashboardState.PerformanceHistory | Select-Object -Last 50
        }
    }
    
    # Check for alerts
    $NewAlerts = @()
    
    # System alerts
    if ($DashboardState.SystemMetrics.CPU_Usage -gt 80) {
        $NewAlerts += @{
            Timestamp = Get-Date -Format "HH:mm:ss"
            Severity = "Warning"
            Message = "High CPU usage: $($DashboardState.SystemMetrics.CPU_Usage)%"
        }
    }
    
    if ($DashboardState.SystemMetrics.Memory_Usage_Percent -gt 85) {
        $NewAlerts += @{
            Timestamp = Get-Date -Format "HH:mm:ss"
            Severity = "Critical"
            Message = "High memory usage: $($DashboardState.SystemMetrics.Memory_Usage_Percent)%"
        }
    }
    
    # Service alerts
    foreach ($Service in $DashboardState.ServiceStatus.Values) {
        if ($Service.Health -eq "Unhealthy" -or $Service.Health -eq "Error") {
            $NewAlerts += @{
                Timestamp = Get-Date -Format "HH:mm:ss"
                Severity = "Warning"
                Message = "Service $($Service.Name) is $($Service.Health)"
            }
        }
    }
    
    # Add new alerts
    $DashboardState.Alerts += $NewAlerts
    
    # Keep only recent alerts
    if ($DashboardState.Alerts.Count -gt 20) {
        $DashboardState.Alerts = $DashboardState.Alerts | Select-Object -Last 20
    }
    
    # Play sound for critical alerts
    if ($Config.SoundAlerts -and $NewAlerts.Count -gt 0) {
        $CriticalAlerts = $NewAlerts | Where-Object { $_.Severity -eq "Critical" }
        if ($CriticalAlerts.Count -gt 0) {
            [System.Console]::Beep(1000, 500)
        }
    }
    
    $DashboardState.LastRefresh = Get-Date
    $DashboardState.RefreshCount++
}

function Handle-UserInput {
    if ([Console]::KeyAvailable) {
        $Key = [Console]::ReadKey($true)
        
        switch ($Key.KeyChar) {
            'q' { 
                $DashboardState.IsRunning = $false
                Write-DashboardLog "Quitting dashboard..." "INFO"
            }
            'r' { 
                Update-DashboardData
                Write-DashboardLog "Manual refresh triggered" "INFO"
            }
            's' { 
                $Config.SoundAlerts = -not $Config.SoundAlerts
                Write-DashboardLog "Sound alerts: $($Config.SoundAlerts)" "INFO"
            }
            't' { 
                $Config.Theme = if ($Config.Theme -eq "dark") { "light" } else { "dark" }
                $script:Colors = $Themes[$Config.Theme]
                Write-DashboardLog "Theme changed to: $($Config.Theme)" "INFO"
            }
            '1' { $script:Mode = "full"; Write-DashboardLog "Mode: Full" "INFO" }
            '2' { $script:Mode = "compact"; Write-DashboardLog "Mode: Compact" "INFO" }
            '3' { $script:Mode = "ai-focused"; Write-DashboardLog "Mode: AI Focused" "INFO" }
            '4' { $script:Mode = "backend-focused"; Write-DashboardLog "Mode: Backend Focused" "INFO" }
            'a' { $script:Mode = "ai-focused"; Write-DashboardLog "Mode: AI Focused" "INFO" }
            'b' { $script:Mode = "backend-focused"; Write-DashboardLog "Mode: Backend Focused" "INFO" }
            'm' { $script:Mode = "monitoring"; Write-DashboardLog "Mode: Monitoring" "INFO" }
        }
    }
}

function Show-Dashboard {
    Show-Header
    Show-SystemMetrics
    Show-ServiceStatus
    Show-AIMetrics
    Show-Alerts
    Show-PerformanceHistory
    Show-Controls
}

# Main dashboard loop
function Start-Dashboard {
    Write-DashboardLog "Starting Real-Time Interactive Dashboard..." "INFO"
    Write-DashboardLog "Mode: $Mode | Auto-refresh: $AutoRefresh | Interval: $RefreshInterval seconds" "INFO"
    
    # Initial data collection
    Update-DashboardData
    
    # Main loop
    while ($DashboardState.IsRunning) {
        try {
            # Handle user input
            Handle-UserInput
            
            # Update data if needed
            if ($Config.AutoRefresh -and 
                ((Get-Date) - $DashboardState.LastRefresh).TotalSeconds -ge $Config.RefreshInterval) {
                Update-DashboardData
            }
            
            # Show dashboard
            Show-Dashboard
            
            # Wait for next cycle
            Start-Sleep -Milliseconds 100
            
        } catch {
            Write-DashboardLog "Error in dashboard loop: $($_.Exception.Message)" "ERROR"
            Start-Sleep -Seconds 1
        }
    }
    
    Write-DashboardLog "Dashboard stopped" "INFO"
    Write-Host "Thank you for using the Real-Time Interactive Dashboard!" -ForegroundColor $Colors.success
}

# Start the dashboard
Start-Dashboard
