# Comprehensive System Health Check for Obsidian Vault AI System
# Diagnoses all components and provides actionable solutions

param(
    [switch]$Detailed = $false,
    [switch]$Fix = $false,
    [switch]$Report = $false
)

$ErrorActionPreference = "SilentlyContinue"

# Colors for output
function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    $color = switch ($Status) {
        "OK" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    Write-Host "[$Status] $Message" -ForegroundColor $color
}

function Test-DockerDesktop {
    Write-Status scripts/ing Docker Desktop..." "INFO"
    
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Docker CLI available: $dockerVersion" "OK"
            
            $dockerInfo = docker info 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Status "Docker daemon running" "OK"
                return @{Status="OK"; Message="Docker Desktop is running"}
            } else {
                Write-Status "Docker daemon not running" "ERROR"
                return @{Status="ERROR"; Message="Docker Desktop not running"; Fix="Start Docker Desktop"}
            }
        } else {
            Write-Status "Docker not installed" "ERROR"
            return @{Status="ERROR"; Message="Docker not installed"; Fix=scripts/ Docker Desktop"}
        }
    } catch {
        return @{Status="ERROR"; Message="Docker check failed"; Fix=scripts/ Docker Desktop"}
    }
}

function Test-Environment {
    Write-Status scripts/ing environment configuration..." "INFO"
    
    $issues = @()
    
    # Check .env file
    if (Test-Path ".env") {
        Write-Status ".env file found" "OK"
        
        # Check critical environment variables
        $envContent = Get-Content ".env" -Raw
        $requiredVars = @("OBSIDIAN_API_KEY", "VAULT_PATH", servicesservices/n8n_USER", servicesservices/postgres_PASSWORD")
        
        foreach ($var in $requiredVars) {
            if ($envContent -match "$var=.+") {
                Write-Status "$var configured" "OK"
            } else {
                Write-Status "$var missing or empty" "WARN"
                $issues += "$var not configured"
            }
        }
    } else {
        Write-Status ".env file missing" "ERROR"
        $issues += ".env file not found"
    }
    
    # Check vault path
    $vaultPath = "D:\Nomade Milionario"
    if (Test-Path $vaultPath) {
        $noteCount = (Get-ChildItem -Path $vaultPath -Filter "*.md" -Recurse).Count
        Write-Status "Vault accessible: $noteCount notes found" "OK"
    } else {
        Write-Status "Vault path not accessible: $vaultPath" "ERROR"
        $issues += "Vault path not accessible"
    }
    
    return @{
        Status = if ($issues.Count -eq 0) {"OK"} else {"WARN"}
        Issues = $issues
        Fix = "Update .env file with correct values"
    }
}

function Test-Services {
    Write-Status scripts/ing service status..." "INFO"
    
    $services = @(
        @{Name=servicesservices/vault-api"; Port=8080; URL="http://localhost:8080/health"},
        @{Name=servicesservices/obsidian-api"; Port=27123; URL="http://localhost:27123/health"},
        @{Name=servicesservices/n8n"; Port=5678; URL="http://localhost:5678/health"},
        @{Name="grafana"; Port=3000; URL="http://localhost:3000/api/health"},
        @{Name="prometheus"; Port=9090; URL="http://localhost:9090/-/healthy"}
    )
    
    $results = @()
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 3 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Status "$($service.Name) healthy (port $($service.Port))" "OK"
                $results += @{Service=$service.Name; Status="OK"; Port=$service.Port}
            } else {
                Write-Status "$($service.Name) unhealthy (status: $($response.StatusCode))" "WARN"
                $results += @{Service=$service.Name; Status="WARN"; Port=$service.Port}
            }
        } catch {
            Write-Status "$($service.Name) not responding (port $($service.Port))" "ERROR"
            $results += @{Service=$service.Name; Status="ERROR"; Port=$service.Port}
        }
    }
    
    return $results
}

function Test-Containers {
    Write-Status scripts/ing Docker containers..." "INFO"
    
    try {
        $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Container status:" "INFO"
            Write-Host $containers
            
            $runningContainers = (docker ps -q).Count
            Write-Status "$runningContainers containers running" "OK"
            
            return @{Status="OK"; Running=$runningContainers}
        } else {
            Write-Status "Cannot check containers - Docker not running" "ERROR"
            return @{Status="ERROR"; Message="Docker not running"}
        }
    } catch {
        return @{Status="ERROR"; Message="Container check failed"}
    }
}

function Test-Ports {
    Write-Status scripts/ing port availability..." "INFO"
    
    $ports = @(8080, 27123, 5678, 3000, 9090, 5432, 6379)
    $conflicts = @()
    
    foreach ($port in $ports) {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet
        if ($connection) {
            Write-Status "Port $port in use" "OK"
        } else {
            Write-Status "Port $port available" "WARN"
            $conflicts += $port
        }
    }
    
    return @{
        Status = if ($conflicts.Count -eq 0) {"OK"} else {"WARN"}
        AvailablePorts = $conflicts
    }
}

function Generate-HealthReport {
    $report = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Docker = Test-DockerDesktop
        Environment = Test-Environment
        Services = Test-Services
        Containers = Test-Containers
        Ports = Test-Ports
    }
    
    # Generate summary
    $issues = @()
    if ($report.Docker.Status -ne "OK") { $issues += "Docker: $($report.Docker.Message)" }
    if ($report.Environment.Status -ne "OK") { $issues += "Environment: $($report.Environment.Issues -join ', ')" }
    if ($report.Containers.Status -ne "OK") { $issues += "Containers: $($report.Containers.Message)" }
    
    $report.Summary = @{
        Status = if ($issues.Count -eq 0) {"HEALTHY"} else {"ISSUES_FOUND"}
        Issues = $issues
        Recommendations = @()
    }
    
    # Add recommendations
    if ($report.Docker.Status -ne "OK") {
        $report.Summary.Recommendations += "Start Docker Desktop and ensure it's running"
    }
    if ($report.Environment.Issues.Count -gt 0) {
        $report.Summary.Recommendations += "Update .env file with missing configuration"
    }
    if ($report.Containers.Running -eq 0) {
        $report.Summary.Recommendations += "Start services with: docker-compose up -d"
    }
    
    return $report
}

function Show-QuickFixes {
    Write-Status "`n🔧 QUICK FIXES AVAILABLE:" "INFO"
    Write-Host @"
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Start Docker Desktop:                                                    │
│    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"       │
│                                                                             │
│ 2. Start all services:                                                      │
│    docker-compose up -d                                                     │
│                                                                             │
│ 3. Check service logs:                                                      │
│    docker-compose logs -f                                                   │
│                                                                             │
│ 4. Restart specific service:                                                │
│    docker-compose restart vault-api                                         │
│                                                                             │
│ 5. Full system restart:                                                     │
│    docker-compose down && docker-compose up -d                              │
└─────────────────────────────────────────────────────────────────────────────┘
"@ -ForegroundColor Cyan
}

# Main execution
Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🏥 SYSTEM HEALTH CHECK                                   ║
║                   Obsidian Vault AI System                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

$healthReport = Generate-HealthReport

if ($Report) {
    $reportPath = "health-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $healthReport | ConvertTo-Json -Depth 10 | Out-File $reportPath
    Write-Status "Health report saved to: $reportPath" "OK"
}

# Display summary
Write-Status "`n📊 SYSTEM SUMMARY:" "INFO"
Write-Status "Overall Status: $($healthReport.Summary.Status)" $(if ($healthReport.Summary.Status -eq "HEALTHY") {"OK"} else {"WARN"})

if ($healthReport.Summary.Issues.Count -gt 0) {
    Write-Status "`n⚠️  Issues Found:" "WARN"
    foreach ($issue in $healthReport.Summary.Issues) {
        Write-Status "  • $issue" "WARN"
    }
}

if ($healthReport.Summary.Recommendations.Count -gt 0) {
    Write-Status "`n💡 Recommendations:" "INFO"
    foreach ($rec in $healthReport.Summary.Recommendations) {
        Write-Status "  • $rec" "INFO"
    }
}

Show-QuickFixes

if ($Fix) {
    Write-Status "`n🔧 Attempting automatic fixes..." "INFO"
    
    # Try to start Docker Desktop if not running
    if ($healthReport.Docker.Status -ne "OK") {
        Write-Status "Starting Docker Desktop..." "INFO"
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -WindowStyle Hidden
        Start-Sleep 30
    }
    
    # Try to start services
    Write-Status "Starting services..." "INFO"
    docker-compose up -d
    
    Write-Status scripts/es applied. Run health check again to verify." "OK"
}

Write-Status "`n✅ Health check complete!" "OK"