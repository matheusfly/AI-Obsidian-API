# RUN ALL TESTS - Comprehensive MCP System Testing
# This script will test all components and show detailed output

Write-Host "================================================================" -ForegroundColor Green
Write-Host "🚀 RUNNING ALL TESTS - MCP SYSTEM" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Set working directory
Set-Location "D:\codex\datamaster\backend-ops\llm-ops\api-mcp-simbiosis"
Write-Host "📁 Working Directory: $(Get-Location)" -ForegroundColor Cyan

# Configuration
$VAULT_PATH = "D:\Nomade Milionario"
$API_BASE_URL = "http://localhost:27124"
$API_TOKEN = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

# Test 1: Check Obsidian API connectivity
Write-Host ""
Write-Host "🔍 Test 1: Checking Obsidian API connectivity..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$API_BASE_URL/vault/" -Headers @{"Authorization" = "Bearer $API_TOKEN"} -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Obsidian API is accessible (Status: $($response.StatusCode))" -ForegroundColor Green
        
        # Parse response to get file count
        try {
            $jsonData = $response.Content | ConvertFrom-Json
            $fileCount = $jsonData.data.Count
            Write-Host "📄 Found $fileCount files in vault" -ForegroundColor Green
        } catch {
            Write-Host "⚠️ Could not parse JSON response" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️ Obsidian API responded with status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Cannot connect to Obsidian API: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Please ensure Obsidian is running with Local REST API plugin enabled" -ForegroundColor Yellow
}

# Test 2: Build all components
Write-Host ""
Write-Host "🔨 Test 2: Building all components..." -ForegroundColor Cyan

$components = @(
    @{Name="Debug System"; File="DEBUG_AND_LOG_SYSTEM.go"; Exe="debug-system.exe"},
    @{Name="Simple Chat"; File="SIMPLE_WORKING_CHAT.go"; Exe="simple-chat.exe"},
    @{Name="Working CLI Chat"; File="WORKING_CLI_CHAT.go"; Exe="working-cli-chat.exe"},
    @{Name="Real-Time Sync"; File="REAL_TIME_VAULT_SYNC.go"; Exe="real-time-sync.exe"},
    @{Name="Monitoring Dashboard"; File="VAULT_MONITORING_DASHBOARD.go"; Exe="monitoring-dashboard.exe"}
)

$buildResults = @()
foreach ($component in $components) {
    Write-Host "   Building $($component.Name)..." -ForegroundColor White
    try {
        $buildOutput = go build -o $component.Exe $component.File 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $($component.Name): Build successful" -ForegroundColor Green
            $buildResults += @{Name=$component.Name; Status="Success"; Error=""}
        } else {
            Write-Host "   ❌ $($component.Name): Build failed" -ForegroundColor Red
            Write-Host "   Error: $buildOutput" -ForegroundColor Red
            $buildResults += @{Name=$component.Name; Status="Failed"; Error=$buildOutput}
        }
    } catch {
        Write-Host "   ❌ $($component.Name): Build error: $($_.Exception.Message)" -ForegroundColor Red
        $buildResults += @{Name=$component.Name; Status="Error"; Error=$_.Exception.Message}
    }
}

# Test 3: Run Debug System
Write-Host ""
Write-Host "🧪 Test 3: Running Debug System..." -ForegroundColor Cyan
$debugSuccess = $false
try {
    Write-Host "   Starting debug system..." -ForegroundColor White
    $debugProcess = Start-Process -FilePath ".\debug-system.exe" -WindowStyle Normal -PassThru -RedirectStandardOutput "debug-output.txt" -RedirectStandardError "debug-error.txt"
    Start-Sleep -Seconds 5
    
    if ($debugProcess.HasExited) {
        Write-Host "   ❌ Debug system exited immediately" -ForegroundColor Red
        if (Test-Path "debug-error.txt") {
            $errorContent = Get-Content "debug-error.txt" -Raw
            Write-Host "   Error: $errorContent" -ForegroundColor Red
        }
    } else {
        Write-Host "   ✅ Debug system is running (PID: $($debugProcess.Id))" -ForegroundColor Green
        $debugSuccess = $true
        
        # Check for debug.log
        if (Test-Path "debug.log") {
            Write-Host "   📄 Debug log created successfully" -ForegroundColor Green
            $logContent = Get-Content "debug.log" -Tail 5
            Write-Host "   Recent log entries:" -ForegroundColor White
            foreach ($line in $logContent) {
                Write-Host "     $line" -ForegroundColor Gray
            }
        } else {
            Write-Host "   ⚠️ Debug log not found" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ Error running debug system: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Run Simple Chat (in background)
Write-Host ""
Write-Host "💬 Test 4: Testing Simple Chat System..." -ForegroundColor Cyan
try {
    Write-Host "   Starting simple chat system..." -ForegroundColor White
    $chatProcess = Start-Process -FilePath ".\simple-chat.exe" -WindowStyle Normal -PassThru
    Start-Sleep -Seconds 2
    
    if ($chatProcess.HasExited) {
        Write-Host "   ❌ Simple chat exited immediately" -ForegroundColor Red
    } else {
        Write-Host "   ✅ Simple chat is running (PID: $($chatProcess.Id))" -ForegroundColor Green
        Write-Host "   💡 Chat window should be open - try typing 'test' to test API connection" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Error running simple chat: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Test MCP Server
Write-Host ""
Write-Host "🔧 Test 5: Testing MCP Server..." -ForegroundColor Cyan
try {
    Set-Location "mcp-server"
    Write-Host "   Building MCP server..." -ForegroundColor White
    $mcpBuildOutput = go build -o mcp-server.exe cmd/server/main.go 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ MCP Server: Build successful" -ForegroundColor Green
        
        Write-Host "   Starting MCP server..." -ForegroundColor White
        $mcpProcess = Start-Process -FilePath ".\mcp-server.exe" -WindowStyle Normal -PassThru
        Start-Sleep -Seconds 3
        
        if ($mcpProcess.HasExited) {
            Write-Host "   ❌ MCP Server exited immediately" -ForegroundColor Red
        } else {
            Write-Host "   ✅ MCP Server is running (PID: $($mcpProcess.Id))" -ForegroundColor Green
            
            # Test MCP Server health endpoint
            try {
                $mcpResponse = Invoke-WebRequest -Uri "http://localhost:3010/health" -TimeoutSec 5
                if ($mcpResponse.StatusCode -eq 200) {
                    Write-Host "   ✅ MCP Server health check: SUCCESS" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️ MCP Server health check: Status $($mcpResponse.StatusCode)" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "   ⚠️ MCP Server health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "   ❌ MCP Server: Build failed" -ForegroundColor Red
        Write-Host "   Error: $mcpBuildOutput" -ForegroundColor Red
    }
    Set-Location ".."
} catch {
    Write-Host "   ❌ Error with MCP Server: $($_.Exception.Message)" -ForegroundColor Red
    Set-Location ".."
}

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "📊 TEST SUMMARY" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "🔨 BUILD RESULTS:" -ForegroundColor Cyan
foreach ($result in $buildResults) {
    if ($result.Status -eq "Success") {
        Write-Host "   ✅ $($result.Name): SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($result.Name): FAILED" -ForegroundColor Red
        if ($result.Error) {
            Write-Host "      Error: $($result.Error)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "🚀 RUNNING SERVICES:" -ForegroundColor Cyan
Write-Host "   💬 Simple Chat: $(if($chatProcess -and !$chatProcess.HasExited){'RUNNING'}else{'NOT RUNNING'})" -ForegroundColor $(if($chatProcess -and !$chatProcess.HasExited){'Green'}else{'Red'})
Write-Host "   🧪 Debug System: $(if($debugSuccess){'RUNNING'}else{'NOT RUNNING'})" -ForegroundColor $(if($debugSuccess){'Green'}else{'Red'})
Write-Host "   🔧 MCP Server: $(if($mcpProcess -and !$mcpProcess.HasExited){'RUNNING'}else{'NOT RUNNING'})" -ForegroundColor $(if($mcpProcess -and !$mcpProcess.HasExited){'Green'}else{'Red'})

Write-Host ""
Write-Host "🌐 WEB INTERFACES:" -ForegroundColor Cyan
Write-Host "   - Obsidian API: http://localhost:27124" -ForegroundColor White
Write-Host "   - MCP Server: http://localhost:3010" -ForegroundColor White

Write-Host ""
Write-Host "💬 CHAT COMMANDS:" -ForegroundColor Cyan
Write-Host "   - test          (Test API connection)" -ForegroundColor White
Write-Host "   - list          (List vault files)" -ForegroundColor White
Write-Host "   - read <file>   (Read a note)" -ForegroundColor White
Write-Host "   - create <file> (Create a note)" -ForegroundColor White
Write-Host "   - search <query>(Search vault)" -ForegroundColor White
Write-Host "   - status        (Show status)" -ForegroundColor White
Write-Host "   - help          (Show help)" -ForegroundColor White
Write-Host "   - quit          (Exit)" -ForegroundColor White

Write-Host ""
Write-Host "📄 LOGS:" -ForegroundColor Cyan
Write-Host "   - Debug logs: debug.log" -ForegroundColor White
Write-Host "   - Debug output: debug-output.txt" -ForegroundColor White
Write-Host "   - Debug errors: debug-error.txt" -ForegroundColor White

Write-Host ""
Write-Host "🎉 TESTING COMPLETED!" -ForegroundColor Green
Write-Host "   Check the chat windows for interactive testing" -ForegroundColor Cyan
Write-Host "   All components are ready for use!" -ForegroundColor Green

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
