# 📊 Performance Monitoring Script (PowerShell)
# Real-time monitoring for backend integration system

param(
    [int]$Interval = 5,
    [int]$Duration = 300,
    [string]$OutputFile = "",
    [switch]$RealTime,
    [switch]$Export,
    [switch]$Help
)

# Color definitions
$Colors = @{
    Green = "Green"
    Blue = "Blue"
    Yellow = "Yellow"
    Red = "Red"
    Magenta = "Magenta"
    Cyan = "Cyan"
    White = "White"
}

function Show-Banner {
    Write-Host "📊 Performance Monitoring System" -ForegroundColor $Colors.Magenta
    Write-Host "===============================" -ForegroundColor $Colors.Magenta
    Write-Host "Real-time monitoring for backend services" -ForegroundColor $Colors.White
    Write-Host ""
}

function Show-Help {
    Write-Host "📚 Usage:" -ForegroundColor $Colors.Yellow
    Write-Host ""
    Write-Host "🔧 BASIC MONITORING:" -ForegroundColor $Colors.Green
    Write-Host "  scripts/-performance.ps1                    # Monitor for 5 minutes" -ForegroundColor $Colors.Cyan
    Write-Host "  scripts/-performance.ps1 -RealTime          # Real-time monitoring" -ForegroundColor $Colors.Cyan
    Write-Host "  scripts/-performance.ps1 -Interval 10       # 10-second intervals" -ForegroundColor $Colors.Cyan
    Write-Host "  scripts/-performance.ps1 -Duration 600      # Monitor for 10 minutes" -ForegroundColor $Colors.Cyan
    Write-Host ""
    Write-Host "📊 EXPORT OPTIONS:" -ForegroundColor $Colors.Green
    Write-Host "  scripts/-performance.ps1 -Export            # Export to CSV" -ForegroundColor $Colors.Cyan
    Write-Host "  scripts/-performance.ps1 -OutputFile perf.csv # Custom output file" -ForegroundColor $Colors.Cyan
    Write-Host ""
}

function Get-SystemMetrics {
    $metrics = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        CPU = [math]::Round((Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples[0].CookedValue, 2)
        Memory = [math]::Round((Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue, 2)
        Disk = [math]::Round((Get-Counter '\PhysicalDisk(_Total)\% Disk Time').CounterSamples[0].CookedValue, 2)
        Network = [math]::Round((Get-Counter '\Network Interface(*)\Bytes Total/sec').CounterSamples | Measure-Object -Property CookedValue -Sum).Sum / 1024 / 1024, 2)
    }
    
    return $metrics
}

function Get-DockerMetrics {
    $dockerMetrics = @{}
    
    try {
        $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-Object -Skip 1
        
        foreach ($container in $containers) {
            $parts = $container -split "\t"
            if ($parts.Count -ge 2) {
                $name = $parts[0]
                $status = $parts[1]
                
                # Get container stats
                $stats = docker stats --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" $name 2>$null
                if ($stats) {
                    $statParts = $stats | Select-Object -Skip 1 | ForEach-Object { $_ -split "\t" }
                    if ($statParts.Count -ge 5) {
                        $dockerMetrics[$name] = @{
                            Status = $status
                            CPU = $statParts[0]
                            Memory = $statParts[1]
                            MemoryPercent = $statParts[2]
                            Network = $statParts[3]
                            Disk = $statParts[4]
                        }
                    }
                }
            }
        }
    } catch {
        Write-Host "⚠️  Error getting Docker metrics: $($_.Exception.Message)" -ForegroundColor $Colors.Yellow
    }
    
    return $dockerMetrics
}

function Get-ServiceMetrics {
    $serviceMetrics = @{}
    
    $services = @(
        @{ Name = "Obsidian API"; Port = 27123; Path = "/health" },
        @{ Name = "Flyde Studio"; Port = 3001; Path = "/health" },
        @{ Name = "Motia Dev"; Port = 3000; Path = "/health" },
        @{ Name = servicesservices/n8n"; Port = 5678; Path = "/healthz" },
        @{ Name = "Vault API"; Port = 8080; Path = "/health" },
        @{ Name = "Ollama"; Port = 11434; Path = "/api/tags" },
        @{ Name = "ChromaDB"; Port = 8000; Path = "/api/v1/heartbeat" },
        @{ Name = "Prometheus"; Port = 9090; Path = "/-/healthy" },
        @{ Name = "Grafana"; Port = 3000; Path = "/api/health" }
    )
    
    foreach ($service in $services) {
        try {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)$($service.Path)" -TimeoutSec 5 -ErrorAction Stop
            $stopwatch.Stop()
            
            $serviceMetrics[$service.Name] = @{
                Status = "Healthy"
                ResponseTime = $stopwatch.ElapsedMilliseconds
                StatusCode = $response.StatusCode
                LastCheck = Get-Date -Format "HH:mm:ss"
            }
        } catch {
            $serviceMetrics[$service.Name] = @{
                Status = "Unhealthy"
                ResponseTime = 0
                StatusCode = 0
                LastCheck = Get-Date -Format "HH:mm:ss"
                Error = $_.Exception.Message
            }
        }
    }
    
    return $serviceMetrics
}

function Display-Metrics {
    param($SystemMetrics, $DockerMetrics, $ServiceMetrics)
    
    # Clear screen for real-time monitoring
    if ($RealTime) {
        Clear-Host
        Show-Banner
    }
    
    Write-Host "📊 Performance Metrics - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor $Colors.Yellow
    Write-Host "=================================================" -ForegroundColor $Colors.Yellow
    Write-Host ""
    
    # System Metrics
    Write-Host "🖥️  System Metrics:" -ForegroundColor $Colors.Green
    Write-Host "  CPU Usage: $($SystemMetrics.CPU)%" -ForegroundColor $(if ($SystemMetrics.CPU -gt 80) { $Colors.Red } else { $Colors.Cyan })
    Write-Host "  Available Memory: $($SystemMetrics.Memory) MB" -ForegroundColor $(if ($SystemMetrics.Memory -lt 1000) { $Colors.Red } else { $Colors.Cyan })
    Write-Host "  Disk Usage: $($SystemMetrics.Disk)%" -ForegroundColor $(if ($SystemMetrics.Disk -gt 80) { $Colors.Red } else { $Colors.Cyan })
    Write-Host "  Network: $($SystemMetrics.Network) MB/s" -ForegroundColor $Colors.Cyan
    Write-Host ""
    
    # Docker Metrics
    Write-Host "🐳 Docker Container Metrics:" -ForegroundColor $Colors.Green
    foreach ($container in $DockerMetrics.Keys) {
        $metrics = $DockerMetrics[$container]
        Write-Host "  📦 $container:" -ForegroundColor $Colors.Cyan
        Write-Host "    Status: $($metrics.Status)" -ForegroundColor $(if ($metrics.Status -like "*Up*") { $Colors.Green } else { $Colors.Red })
        Write-Host "    CPU: $($metrics.CPU)" -ForegroundColor $Colors.White
        Write-Host "    Memory: $($metrics.Memory) ($($metrics.MemoryPercent))" -ForegroundColor $Colors.White
        Write-Host "    Network: $($metrics.Network)" -ForegroundColor $Colors.White
        Write-Host "    Disk: $($metrics.Disk)" -ForegroundColor $Colors.White
    }
    Write-Host ""
    
    # Service Metrics
    Write-Host "🌐 Service Health Metrics:" -ForegroundColor $Colors.Green
    foreach ($service in $ServiceMetrics.Keys) {
        $metrics = $ServiceMetrics[$service]
        $statusColor = if ($metrics.Status -eq "Healthy") { $Colors.Green } else { $Colors.Red }
        $responseColor = if ($metrics.ResponseTime -lt 100) { $Colors.Green } elseif ($metrics.ResponseTime -lt 500) { $Colors.Yellow } else { $Colors.Red }
        
        Write-Host "  🔗 $service:" -ForegroundColor $Colors.Cyan
        Write-Host "    Status: $($metrics.Status)" -ForegroundColor $statusColor
        Write-Host "    Response Time: $($metrics.ResponseTime)ms" -ForegroundColor $responseColor
        Write-Host "    Last Check: $($metrics.LastCheck)" -ForegroundColor $Colors.White
        
        if ($metrics.Error) {
            Write-Host "    Error: $($metrics.Error)" -ForegroundColor $Colors.Red
        }
    }
    Write-Host ""
}

function Export-Metrics {
    param($AllMetrics, $OutputFile)
    
    if (-not $OutputFile) {
        $OutputFile = "performance-metrics-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
    }
    
    Write-Host "📄 Exporting metrics to: $OutputFile" -ForegroundColor $Colors.Green
    
    $csvData = @()
    foreach ($metric in $AllMetrics) {
        $csvData += [PSCustomObject]@{
            Timestamp = $metric.Timestamp
            CPU = $metric.System.CPU
            Memory = $metric.System.Memory
            Disk = $metric.System.Disk
            Network = $metric.System.Network
            ObsidianAPI_Status = $metric.Services."Obsidian API".Status
            ObsidianAPI_ResponseTime = $metric.Services."Obsidian API".ResponseTime
            FlydeStudio_Status = $metric.Services."Flyde Studio".Status
            FlydeStudio_ResponseTime = $metric.Services."Flyde Studio".ResponseTime
            MotiaDev_Status = $metric.Services."Motia Dev".Status
            MotiaDev_ResponseTime = $metric.Services."Motia Dev".ResponseTime
            N8N_Status = $metric.Services.servicesservices/n8n".Status
            N8N_ResponseTime = $metric.Services.servicesservices/n8n".ResponseTime
        }
    }
    
    $csvData | Export-Csv -Path $OutputFile -NoTypeInformation
    Write-Host "✅ Metrics exported successfully!" -ForegroundColor $Colors.Green
}

function Monitor-Performance {
    $allMetrics = @()
    $startTime = Get-Date
    $endTime = $startTime.AddSeconds($Duration)
    
    Write-Host "🚀 Starting performance monitoring..." -ForegroundColor $Colors.Green
    Write-Host "⏱️  Duration: $Duration seconds" -ForegroundColor $Colors.Blue
    Write-Host "🔄 Interval: $Interval seconds" -ForegroundColor $Colors.Blue
    Write-Host ""
    
    if ($RealTime) {
        Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor $Colors.Yellow
        Write-Host ""
    }
    
    try {
        while ((Get-Date) -lt $endTime) {
            $systemMetrics = Get-SystemMetrics
            $dockerMetrics = Get-DockerMetrics
            $serviceMetrics = Get-ServiceMetrics
            
            $combinedMetrics = @{
                Timestamp = $systemMetrics.Timestamp
                System = $systemMetrics
                Docker = $dockerMetrics
                Services = $serviceMetrics
            }
            
            $allMetrics += $combinedMetrics
            
            Display-Metrics $systemMetrics $dockerMetrics $serviceMetrics
            
            if ($RealTime) {
                Start-Sleep -Seconds $Interval
            } else {
                $remaining = ($endTime - (Get-Date)).TotalSeconds
                if ($remaining -gt 0) {
                    Write-Host "⏳ Next check in $Interval seconds... (Remaining: $([math]::Round($remaining))s)" -ForegroundColor $Colors.Yellow
                    Start-Sleep -Seconds $Interval
                }
            }
        }
    } catch {
        Write-Host "❌ Monitoring interrupted: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    Write-Host ""
    Write-Host "📊 Monitoring completed!" -ForegroundColor $Colors.Green
    Write-Host "📈 Total samples collected: $($allMetrics.Count)" -ForegroundColor $Colors.Cyan
    
    if ($Export) {
        Export-Metrics $allMetrics $OutputFile
    }
    
    # Summary
    if ($allMetrics.Count -gt 0) {
        Write-Host ""
        Write-Host "📋 Performance Summary:" -ForegroundColor $Colors.Yellow
        Write-Host "======================" -ForegroundColor $Colors.Yellow
        
        $avgCPU = ($allMetrics | Measure-Object -Property System.CPU -Average).Average
        $avgMemory = ($allMetrics | Measure-Object -Property System.Memory -Average).Average
        $maxCPU = ($allMetrics | Measure-Object -Property System.CPU -Maximum).Maximum
        $minMemory = ($allMetrics | Measure-Object -Property System.Memory -Minimum).Minimum
        
        Write-Host "  Average CPU Usage: $([math]::Round($avgCPU, 2))%" -ForegroundColor $Colors.Cyan
        Write-Host "  Peak CPU Usage: $([math]::Round($maxCPU, 2))%" -ForegroundColor $Colors.Cyan
        Write-Host "  Average Available Memory: $([math]::Round($avgMemory, 2)) MB" -ForegroundColor $Colors.Cyan
        Write-Host "  Minimum Available Memory: $([math]::Round($minMemory, 2)) MB" -ForegroundColor $Colors.Cyan
        
        # Service availability
        $healthyServices = 0
        $totalServices = 0
        foreach ($metric in $allMetrics) {
            foreach ($service in $metric.Services.Keys) {
                $totalServices++
                if ($metric.Services[$service].Status -eq "Healthy") {
                    $healthyServices++
                }
            }
        }
        
        if ($totalServices -gt 0) {
            $availability = ($healthyServices / $totalServices) * 100
            Write-Host "  Service Availability: $([math]::Round($availability, 2))%" -ForegroundColor $Colors.Cyan
        }
    }
}

# Main execution
Show-Banner

if ($Help) {
    Show-Help
} else {
    Monitor-Performance
}
