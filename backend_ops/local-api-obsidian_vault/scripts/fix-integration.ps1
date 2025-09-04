# Fix Integration Issues and Launch Complete System
param(
    [switch]$Force = $false,
    [switch]$Rebuild = $false
)

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    $colors = @{"Green"="Green";"Red"="Red";"Yellow"="Yellow";"Blue"="Blue";"Cyan"="Cyan";"White"="White"}
    Write-Host $Message -ForegroundColor $colors[$Color]
}

Write-Status "🔧 FIXING INTEGRATION ISSUES" "Cyan"
Write-Status "=" * 50 "Blue"

# Step 1: Stop all services
Write-Status "🛑 Stopping existing services..." "Yellow"
docker-compose down

# Step 2: Clean up if rebuild requested
if ($Rebuild) {
    Write-Status "🧹 Cleaning Docker images..." "Yellow"
    docker-compose down --rmi all --volumes --remove-orphans
}

# Step 3: Build and start services
Write-Status "🔨 Building and starting services..." "Blue"
docker-compose up -d --build

# Step 4: Wait for services
Write-Status "⏳ Waiting for services to initialize..." "Yellow"
Start-Sleep -Seconds 30

# Step 5: Test each service
Write-Status "🔍 Testing service integration..." "Blue"

$services = @(
    @{Name="Vault API"; URL="http://localhost:8080/health"; Port=8080},
    @{Name="Obsidian API"; URL="http://localhost:27123/health"; Port=27123},
    @{Name=servicesservices/n8n"; URL="http://localhost:5678/healthz"; Port=5678}
)

$healthyServices = 0
foreach ($service in $services) {
    try {
        $response = Invoke-RestMethod -Uri $service.URL -TimeoutSec 10
        Write-Status "✅ $($service.Name) is healthy" "Green"
        $healthyServices++
    } catch {
        Write-Status "❌ $($service.Name) failed: $($_.Exception.Message)" "Red"
        
        # Check if port is in use
        $portInUse = Get-NetTCPConnection -LocalPort $service.Port -ErrorAction SilentlyContinue
        if ($portInUse) {
            Write-Status "   Port $($service.Port) is in use" "Yellow"
        } else {
            Write-Status "   Port $($service.Port) is not listening" "Red"
        }
    }
}

# Step 6: Test OpenAPI endpoints
Write-Status "📡 Testing OpenAPI endpoints..." "Blue"

$openApiEndpoints = @(
    "http://localhost:8080/openapi.json",
    "http://localhost:8080/docs"
)

foreach ($endpoint in $openApiEndpoints) {
    try {
        $response = Invoke-RestMethod -Uri $endpoint -TimeoutSec 5
        Write-Status "✅ OpenAPI endpoint working: $endpoint" "Green"
    } catch {
        Write-Status "❌ OpenAPI endpoint failed: $endpoint" "Red"
    }
}

# Step 7: Test MCP Tools
Write-Status "🛠️ Testing MCP Tools integration..." "Blue"
try {
    $tools = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools" -TimeoutSec 10
    Write-Status "✅ MCP Tools available: $($tools.total)" "Green"
    
    # Test a tool call
    $toolCall = @{
        tool = "list_files"
        arguments = @{path = "brain_dump"}
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $toolCall -ContentType "application/json" -TimeoutSec 10
    
    if ($result.success) {
        Write-Status "✅ MCP Tool call successful" "Green"
    } else {
        Write-Status "❌ MCP Tool call failed: $($result.error)" "Red"
    }
} catch {
    Write-Status "❌ MCP Tools test failed: $($_.Exception.Message)" "Red"
}

# Step 8: Test Vault Operations
Write-Status "📂 Testing vault operations..." "Blue"
try {
    $vaultInfo = Invoke-RestMethod -Uri "http://localhost:27123/vault/info" -TimeoutSec 10
    Write-Status "✅ Vault accessible: $($vaultInfo.markdownFiles) markdown files" "Green"
    
    # Test reading AGENTS.md
    $agentsFile = Invoke-RestMethod -Uri "http://localhost:27123scripts/les/AGENTS.md" -TimeoutSec 10
    Write-Status "✅ AGENTS.md readable: $($agentsFile.size) bytes" "Green"
} catch {
    Write-Status "❌ Vault operations failed: $($_.Exception.Message)" "Red"
}

# Step 9: Update plugin configuration
Write-Status "🔌 Updating plugin configuration..." "Blue"
$pluginConfigPath = "D:\Nomade Milionario\.obsidian\plugins\openapi-renderer\config.json"

if (Test-Path $pluginConfigPath) {
    try {
        $config = Get-Content $pluginConfigPath | ConvertFrom-Json
        
        # Update API endpoints with correct URLs
        $config.apiEndpoints[0].url = "http://localhost:8080/openapi.json"
        $config.apiEndpoints[1].url = "http://localhost:27123/openapi.json"
        
        # Enable performance monitoring
        $config.settings.performanceMonitoring = $true
        $config.settings.showHealthStatus = $true
        
        # Update monitoring endpoints
        $config.monitoring.endpoints = @(
            "http://localhost:8080/health",
            "http://localhost:27123/health",
            "http://localhost:8080/metrics"
        )
        
        $config | ConvertTo-Json -Depth 10 | Set-Content $pluginConfigPath
        Write-Status "✅ Plugin configuration updated" "Green"
    } catch {
        Write-Status "❌ Plugin configuration update failed: $($_.Exception.Message)" "Red"
    }
} else {
    Write-Status "❌ Plugin configuration not found at: $pluginConfigPath" "Red"
}

# Step 10: Performance test
Write-Status "⚡ Running performance tests..." "Blue"
$performanceResults = @()

for ($i = 1; $i -le 5; $i++) {
    try {
        $start = Get-Date
        $response = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 5
        $end = Get-Date
        $duration = ($end - $start).TotalMilliseconds
        $performanceResults += $duration
        Write-Status "   Test $i`: $([math]::Round($duration, 2))ms" "White"
    } catch {
        Write-Status "   Test $i`: FAILED" "Red"
    }
}

if ($performanceResults.Count -gt 0) {
    $avgResponse = ($performanceResults | Measure-Object -Average).Average
    Write-Status "✅ Average response time: $([math]::Round($avgResponse, 2))ms" "Green"
    
    if ($avgResponse -lt 100) {
        Write-Status "🚀 Performance: EXCELLENT" "Green"
    } elseif ($avgResponse -lt 500) {
        Write-Status "⚡ Performance: GOOD" "Yellow"
    } else {
        Write-Status "🐌 Performance: NEEDS IMPROVEMENT" "Red"
    }
}

# Final status report
Write-Status "`n🎯 INTEGRATION STATUS REPORT" "Cyan"
Write-Status "=" * 50 "Blue"

Write-Status "Services Status:" "Yellow"
Write-Status "   Healthy Services: $healthyServices/3" "White"

Write-Status "`nAPI Endpoints:" "Yellow"
Write-Status "   Vault API: http://localhost:8080" "White"
Write-Status "   API Docs: http://localhost:8080/docs" "White"
Write-Status "   Obsidian API: http://localhost:27123" "White"
Write-Status "   OpenAPI Spec: http://localhost:8080/openapi.json" "White"

Write-Status "`nPlugin Integration:" "Yellow"
Write-Status "   Config Path: $pluginConfigPath" "White"
Write-Status "   Plugin Status: $(if(Test-Path $pluginConfigPath){config/URED'}else{'MISSING'})" "White"

Write-Status "`nNext Steps:" "Yellow"
Write-Status "   1. Restart Obsidian to reload plugin" "White"
Write-Status "   2. Test API calls from within Obsidian" "White"
Write-Status "   3. Run: .\scripts\vault-cli.ps1 -Interactive" "White"

if ($healthyServices -eq 3) {
    Write-Status "`n🎉 INTEGRATION COMPLETE! System is ready." "Green"
} else {
    Write-Status "`n⚠️ INTEGRATION INCOMPLETE. Check failed services above." "Yellow"
}