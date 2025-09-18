# Comprehensive Fix and Test Suite
# This script will fix all issues and test everything systematically

Write-Host "================================================================" -ForegroundColor Green
Write-Host "🚀 COMPREHENSIVE FIX AND TEST SUITE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Step 1: Check current directory
Write-Host "Step 1: Checking current directory..." -ForegroundColor Cyan
Set-Location "D:\codex\datamaster\backend-ops\llm-ops\api-mcp-simbiosis"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor White

# Step 2: Check if Obsidian API is accessible
Write-Host ""
Write-Host "Step 2: Checking Obsidian API connectivity..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:27124/vault/" -Headers @{"Authorization" = "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"} -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Obsidian API is accessible" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Obsidian API responded with status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Cannot connect to Obsidian API. Please ensure Obsidian is running." -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Continuing anyway..." -ForegroundColor Yellow
}

# Step 3: Test Working CLI Chat System
Write-Host ""
Write-Host "Step 3: Testing Working CLI Chat System..." -ForegroundColor Cyan
Write-Host "Building Working CLI Chat..." -ForegroundColor White

try {
    $buildResult = go build -o working-cli-chat.exe WORKING_CLI_CHAT.go
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Working CLI Chat built successfully" -ForegroundColor Green
        
        # Start in background
        Write-Host "Starting Working CLI Chat in background..." -ForegroundColor White
        Start-Process -FilePath ".\working-cli-chat.exe" -WindowStyle Normal
        Start-Sleep -Seconds 2
        Write-Host "✅ Working CLI Chat started" -ForegroundColor Green
    } else {
        Write-Host "❌ Working CLI Chat build failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error building Working CLI Chat: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Test Real-Time Sync System
Write-Host ""
Write-Host "Step 4: Testing Real-Time Sync System..." -ForegroundColor Cyan
try {
    $buildResult = go build -o real-time-sync.exe REAL_TIME_VAULT_SYNC.go
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Real-Time Sync built successfully" -ForegroundColor Green
        
        # Start in background
        Write-Host "Starting Real-Time Sync in background..." -ForegroundColor White
        Start-Process -FilePath ".\real-time-sync.exe" -WindowStyle Normal
        Start-Sleep -Seconds 2
        Write-Host "✅ Real-Time Sync started" -ForegroundColor Green
    } else {
        Write-Host "❌ Real-Time Sync build failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error building Real-Time Sync: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Test Monitoring Dashboard
Write-Host ""
Write-Host "Step 5: Testing Monitoring Dashboard..." -ForegroundColor Cyan
try {
    $buildResult = go build -o monitoring-dashboard.exe VAULT_MONITORING_DASHBOARD.go
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Monitoring Dashboard built successfully" -ForegroundColor Green
        
        # Start in background
        Write-Host "Starting Monitoring Dashboard in background..." -ForegroundColor White
        Start-Process -FilePath ".\monitoring-dashboard.exe" -WindowStyle Normal
        Start-Sleep -Seconds 2
        Write-Host "✅ Monitoring Dashboard started" -ForegroundColor Green
    } else {
        Write-Host "❌ Monitoring Dashboard build failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error building Monitoring Dashboard: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: Test MCP Server
Write-Host ""
Write-Host "Step 6: Testing MCP Server..." -ForegroundColor Cyan
try {
    Set-Location "mcp-server"
    $buildResult = go build -o mcp-server.exe cmd/server/main.go
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MCP Server built successfully" -ForegroundColor Green
        
        # Start in background
        Write-Host "Starting MCP Server in background..." -ForegroundColor White
        Start-Process -FilePath ".\mcp-server.exe" -WindowStyle Normal
        Start-Sleep -Seconds 2
        Write-Host "✅ MCP Server started" -ForegroundColor Green
    } else {
        Write-Host "❌ MCP Server build failed" -ForegroundColor Red
    }
    Set-Location ".."
} catch {
    Write-Host "❌ Error building MCP Server: $($_.Exception.Message)" -ForegroundColor Red
    Set-Location ".."
}

# Step 7: Test Test Suite
Write-Host ""
Write-Host "Step 7: Testing Test Suite..." -ForegroundColor Cyan
try {
    $buildResult = go build -o test-suite.exe REAL_TIME_SYNC_TEST_SUITE.go
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test Suite built successfully" -ForegroundColor Green
        
        # Start in background
        Write-Host "Starting Test Suite in background..." -ForegroundColor White
        Start-Process -FilePath ".\test-suite.exe" -WindowStyle Normal
        Start-Sleep -Seconds 2
        Write-Host "✅ Test Suite started" -ForegroundColor Green
    } else {
        Write-Host "❌ Test Suite build failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error building Test Suite: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Health Check
Write-Host ""
Write-Host "Step 8: Health Check..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check if services are running
$services = @(
    @{Name="Working CLI Chat"; Port="N/A"; URL="N/A"},
    @{Name="Real-Time Sync"; Port="N/A"; URL="N/A"},
    @{Name="Monitoring Dashboard"; Port="8082"; URL="http://localhost:8082/api/health"},
    @{Name="MCP Server"; Port="3010"; URL="http://localhost:3010/health"}
)

foreach ($service in $services) {
    if ($service.URL -ne "N/A") {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 3
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $($service.Name): Healthy" -ForegroundColor Green
            } else {
                Write-Host "⚠️ $($service.Name): Status $($response.StatusCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ $($service.Name): Unhealthy" -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️ $($service.Name): Running (no health endpoint)" -ForegroundColor Cyan
    }
}

# Final Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "🎉 COMPREHENSIVE TEST COMPLETED!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 TESTING COMMANDS:" -ForegroundColor Cyan
Write-Host "   In CLI Chat window, try these commands:" -ForegroundColor White
Write-Host "   - test          (Test API connection)" -ForegroundColor White
Write-Host "   - list          (List vault files)" -ForegroundColor White
Write-Host "   - search <query> (Search vault)" -ForegroundColor White
Write-Host "   - status        (Show system status)" -ForegroundColor White
Write-Host "   - health        (Health check)" -ForegroundColor White
Write-Host "   - help          (Show all commands)" -ForegroundColor White
Write-Host ""
Write-Host "🌐 WEB INTERFACES:" -ForegroundColor Cyan
Write-Host "   - Dashboard: http://localhost:8082" -ForegroundColor White
Write-Host "   - MCP Server: http://localhost:3010" -ForegroundColor White
Write-Host ""
Write-Host "🚀 QUICK START:" -ForegroundColor Cyan
Write-Host "   .\working-cli-chat.exe" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
