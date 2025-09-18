# START EVERYTHING - Comprehensive MCP System Startup
# This script starts all components with proper error handling and logging

Write-Host "================================================================" -ForegroundColor Green
Write-Host "🚀 STARTING COMPLETE MCP SYSTEM" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Configuration
$VAULT_PATH = "D:\Nomade Milionario"
$API_BASE_URL = "http://localhost:27124"
$API_TOKEN = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

# Set working directory
Set-Location "D:\codex\datamaster\backend-ops\llm-ops\api-mcp-simbiosis"
Write-Host "📁 Working Directory: $(Get-Location)" -ForegroundColor Cyan

# Function to start a service with error handling
function Start-ServiceWithErrorHandling {
    param(
        [string]$ServiceName,
        [string]$GoFile,
        [string]$ExeName,
        [string]$Description
    )
    
    Write-Host ""
    Write-Host "🔄 Starting $ServiceName..." -ForegroundColor Cyan
    Write-Host "   $Description" -ForegroundColor Gray
    
    try {
        # Build the service
        Write-Host "   Building $ServiceName..." -ForegroundColor White
        $buildResult = go build -o $ExeName $GoFile 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ❌ Build failed: $buildResult" -ForegroundColor Red
            return $false
        }
        Write-Host "   ✅ Build successful" -ForegroundColor Green
        
        # Start the service
        Write-Host "   Starting $ServiceName..." -ForegroundColor White
        $process = Start-Process -FilePath ".\$ExeName" -WindowStyle Normal -PassThru
        Start-Sleep -Seconds 2
        
        if ($process.HasExited) {
            Write-Host "   ❌ $ServiceName exited immediately" -ForegroundColor Red
            return $false
        }
        
        Write-Host "   ✅ $ServiceName started successfully (PID: $($process.Id))" -ForegroundColor Green
        return $true
        
    } catch {
        Write-Host "   ❌ Error starting $ServiceName`: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to test API connectivity
function Test-APIConnectivity {
    Write-Host ""
    Write-Host "🔍 Testing API Connectivity..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri "$API_BASE_URL/vault/" -Headers @{"Authorization" = "Bearer $API_TOKEN"} -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Obsidian API is accessible" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ Obsidian API responded with status: $($response.StatusCode)" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Cannot connect to Obsidian API: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Please ensure Obsidian is running with Local REST API plugin enabled" -ForegroundColor Yellow
        return $false
    }
}

# Step 1: Test API connectivity
$apiConnected = Test-APIConnectivity
if (-not $apiConnected) {
    Write-Host ""
    Write-Host "⚠️ API not accessible, but continuing with startup..." -ForegroundColor Yellow
}

# Step 2: Start Debug and Log System
$debugStarted = Start-ServiceWithErrorHandling -ServiceName "Debug System" -GoFile "DEBUG_AND_LOG_SYSTEM.go" -ExeName "debug-system.exe" -Description "Comprehensive debugging and logging system"

# Step 3: Start Working CLI Chat
$cliStarted = Start-ServiceWithErrorHandling -ServiceName "Working CLI Chat" -GoFile "WORKING_CLI_CHAT.go" -ExeName "working-cli-chat.exe" -Description "Simplified but fully functional CLI chat system"

# Step 4: Start Real-Time Sync
$syncStarted = Start-ServiceWithErrorHandling -ServiceName "Real-Time Sync" -GoFile "REAL_TIME_VAULT_SYNC.go" -ExeName "real-time-sync.exe" -Description "Real-time vault synchronization and monitoring"

# Step 5: Start Monitoring Dashboard
$dashboardStarted = Start-ServiceWithErrorHandost "Monitoring Dashboard" -GoFile "VAULT_MONITORING_DASHBOARD.go" -ExeName "monitoring-dashboard.exe" -Description "Web-based monitoring dashboard"

# Step 6: Start MCP Server
Write-Host ""
Write-Host "🔄 Starting MCP Server..." -ForegroundColor Cyan
try {
    Set-Location "mcp-server"
    $mcpStarted = Start-ServiceWithErrorHandling -ServiceName "MCP Server" -GoFile "cmd/server/main.go" -ExeName "mcp-server.exe" -Description "Model Context Protocol server"
    Set-Location ".."
} catch {
    Write-Host "❌ Error with MCP Server: $($_.Exception.Message)" -ForegroundColor Red
    Set-Location ".."
    $mcpStarted = $false
}

# Step 7: Health Check
Write-Host ""
Write-Host "🏥 Health Check..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

$services = @(
    @{Name="Working CLI Chat"; Started=$cliStarted; Port="N/A"; URL="N/A"},
    @{Name="Real-Time Sync"; Started=$syncStarted; Port="N/A"; URL="N/A"},
    @{Name="Monitoring Dashboard"; Started=$dashboardStarted; Port="8082"; URL="http://localhost:8082/api/health"},
    @{Name="MCP Server"; Started=$mcpStarted; Port="3010"; URL="http://localhost:3010/health"},
    @{Name="Debug System"; Started=$debugStarted; Port="N/A"; URL="N/A"}
)

$healthyServices = 0
$totalServices = $services.Count

foreach ($service in $services) {
    if ($service.Started) {
        if ($service.URL -ne "N/A") {
            try {
                $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 3
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ $($service.Name): Healthy" -ForegroundColor Green
                    $healthyServices++
                } else {
                    Write-Host "⚠️ $($service.Name): Status $($response.StatusCode)" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "❌ $($service.Name): Unhealthy" -ForegroundColor Red
            }
        } else {
            Write-Host "✅ $($service.Name): Running" -ForegroundColor Green
            $healthyServices++
        }
    } else {
        Write-Host "❌ $($service.Name): Failed to start" -ForegroundColor Red
    }
}

# Final Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "🎉 STARTUP COMPLETED!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 SUMMARY:" -ForegroundColor Cyan
Write-Host "   Services Started: $healthyServices/$totalServices" -ForegroundColor White
Write-Host "   API Connected: $(if($apiConnected){'Yes'}else{'No'})" -ForegroundColor White
Write-Host ""
Write-Host "🌐 WEB INTERFACES:" -ForegroundColor Cyan
Write-Host "   - Monitoring Dashboard: http://localhost:8082" -ForegroundColor White
Write-Host "   - MCP Server: http://localhost:3010" -ForegroundColor White
Write-Host ""
Write-Host "💬 CLI CHAT COMMANDS:" -ForegroundColor Cyan
Write-Host "   - test          (Test API connection)" -ForegroundColor White
Write-Host "   - list          (List vault files)" -ForegroundColor White
Write-Host "   - search <query> (Search vault)" -ForegroundColor White
Write-Host "   - create <file>  (Create new note)" -ForegroundColor White
Write-Host "   - read <file>    (Read note)" -ForegroundColor White
Write-Host "   - status        (Show system status)" -ForegroundColor White
Write-Host "   - health        (Health check)" -ForegroundColor White
Write-Host "   - help          (Show all commands)" -ForegroundColor White
Write-Host "   - quit          (Exit)" -ForegroundColor White
Write-Host ""
Write-Host "🚀 QUICK START:" -ForegroundColor Cyan
Write-Host "   Open the Working CLI Chat window and type: test" -ForegroundColor White
Write-Host ""
Write-Host "📄 LOGS:" -ForegroundColor Cyan
Write-Host "   - Debug logs: debug.log" -ForegroundColor White
Write-Host "   - Service logs: Check individual service windows" -ForegroundColor White
Write-Host ""

if ($healthyServices -eq $totalServices) {
    Write-Host "🎉 ALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Some services failed to start. Check the output above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
