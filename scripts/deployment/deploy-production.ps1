# Production Deployment Script for Data Vault Obsidian
# This script deploys the production-ready observability stack

param(
    [string]$Environment = "production",
    [switch]$SkipBackup,
    [switch]$Force,
    [string]$ConfigFile = "config/production.env"
)

Write-Host "🚀 Starting Production Deployment for Data Vault Obsidian" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Config File: $ConfigFile" -ForegroundColor Yellow

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script requires administrator privileges. Please run as administrator."
    exit 1
}

# Load environment variables
if (Test-Path $ConfigFile) {
    Write-Host "📋 Loading environment variables from $ConfigFile" -ForegroundColor Blue
    Get-Content $ConfigFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
} else {
    Write-Warning "Config file $ConfigFile not found. Using default values."
}

# Validate required environment variables
$requiredVars = @(
    "GRAFANA_ADMIN_PASSWORD",
    "GRAFANA_SECRET_KEY",
    "REDIS_PASSWORD",
    "PROMETHEUS_PASSWORD"
)

$missingVars = @()
foreach ($var in $requiredVars) {
    if (-not [Environment]::GetEnvironmentVariable($var)) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Error "Missing required environment variables: $($missingVars -join ', ')"
    Write-Host "Please set these variables in $ConfigFile" -ForegroundColor Red
    exit 1
}

# Create backup if not skipping
if (-not $SkipBackup) {
    Write-Host "💾 Creating backup before deployment..." -ForegroundColor Blue
    $backupDir = "backups/$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Backup Docker volumes
    Write-Host "  - Backing up Docker volumes..." -ForegroundColor Gray
    docker run --rm -v obsidian-chroma-prod_chroma_data:/data -v "${PWD}/${backupDir}:/backup" alpine tar czf /backup/chroma_data.tar.gz -C /data .
    docker run --rm -v obsidian-redis-prod_redis_data:/data -v "${PWD}/${backupDir}:/backup" alpine tar czf /backup/redis_data.tar.gz -C /data .
    docker run --rm -v obsidian-prometheus-prod_prometheus_data:/data -v "${PWD}/${backupDir}:/backup" alpine tar czf /backup/prometheus_data.tar.gz -C /data .
    docker run --rm -v obsidian-grafana-prod_grafana_data:/data -v "${PWD}/${backupDir}:/backup" alpine tar czf /backup/grafana_data.tar.gz -C /data .
    
    Write-Host "  ✅ Backup created in $backupDir" -ForegroundColor Green
}

# Stop existing services
Write-Host "🛑 Stopping existing services..." -ForegroundColor Blue
docker-compose -f docker-compose.production.yml down

# Pull latest images
Write-Host "📥 Pulling latest images..." -ForegroundColor Blue
docker-compose -f docker-compose.production.yml pull

# Build custom images
Write-Host "🔨 Building custom images..." -ForegroundColor Blue
docker-compose -f docker-compose.production.yml build --no-cache

# Start services
Write-Host "🚀 Starting production services..." -ForegroundColor Blue
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Blue
$maxWait = 300 # 5 minutes
$waitTime = 0
$allHealthy = $false

while (-not $allHealthy -and $waitTime -lt $maxWait) {
    Start-Sleep -Seconds 10
    $waitTime += 10
    
    $services = @("chroma", "redis", "data-pipeline", "prometheus", "grafana")
    $healthyServices = 0
    
    foreach ($service in $services) {
        $health = docker inspect "obsidian-${service}-prod" --format='{{.State.Health.Status}}' 2>$null
        if ($health -eq "healthy") {
            $healthyServices++
        }
    }
    
    if ($healthyServices -eq $services.Count) {
        $allHealthy = $true
        Write-Host "  ✅ All services are healthy!" -ForegroundColor Green
    } else {
        Write-Host "  ⏳ $healthyServices/$($services.Count) services healthy..." -ForegroundColor Yellow
    }
}

if (-not $allHealthy) {
    Write-Warning "Some services may not be fully healthy. Check logs with: docker-compose -f docker-compose.production.yml logs"
}

# Verify services
Write-Host "🔍 Verifying services..." -ForegroundColor Blue

# Test Grafana
try {
    $grafanaResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -TimeoutSec 10
    if ($grafanaResponse.StatusCode -eq 200) {
        Write-Host "  ✅ Grafana is accessible" -ForegroundColor Green
    }
} catch {
    Write-Warning "  ⚠️ Grafana may not be fully ready yet"
}

# Test Prometheus
try {
    $prometheusResponse = Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -TimeoutSec 10
    if ($prometheusResponse.StatusCode -eq 200) {
        Write-Host "  ✅ Prometheus is accessible" -ForegroundColor Green
    }
} catch {
    Write-Warning "  ⚠️ Prometheus may not be fully ready yet"
}

# Test Data Pipeline
try {
    $pipelineResponse = Invoke-WebRequest -Uri "http://localhost:8003/health" -TimeoutSec 10
    if ($pipelineResponse.StatusCode -eq 200) {
        Write-Host "  ✅ Data Pipeline is accessible" -ForegroundColor Green
    }
} catch {
    Write-Warning "  ⚠️ Data Pipeline may not be fully ready yet"
}

# Display service URLs
Write-Host "`n🌐 Service URLs:" -ForegroundColor Green
Write-Host "  Grafana Dashboard: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "  Data Pipeline API: http://localhost:8003" -ForegroundColor Cyan
Write-Host "  Nginx Proxy: http://localhost" -ForegroundColor Cyan

Write-Host "`n🔐 Default Credentials:" -ForegroundColor Yellow
Write-Host "  Grafana: admin / $($env:GRAFANA_ADMIN_PASSWORD)" -ForegroundColor Gray
Write-Host "  Prometheus: admin / $($env:PROMETHEUS_PASSWORD)" -ForegroundColor Gray

Write-Host "`n📊 Monitoring Commands:" -ForegroundColor Blue
Write-Host "  View logs: docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor Gray
Write-Host "  Check status: docker-compose -f docker-compose.production.yml ps" -ForegroundColor Gray
Write-Host "  Restart service: docker-compose -f docker-compose.production.yml restart <service>" -ForegroundColor Gray

Write-Host "`n✅ Production deployment completed!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Configure SSL certificates in config/nginx/ssl/" -ForegroundColor Gray
Write-Host "  2. Set up monitoring notifications" -ForegroundColor Gray
Write-Host "  3. Configure backup schedules" -ForegroundColor Gray
Write-Host "  4. Review security settings" -ForegroundColor Gray

