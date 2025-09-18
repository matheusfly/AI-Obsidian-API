# Ultimate Integrated CLI Chat - Comprehensive Test Suite
# Tests ALL MCP server capabilities with real Obsidian vault data

Write-Host "================================================================" -ForegroundColor Green
Write-Host "🚀 ULTIMATE INTEGRATED CLI CHAT - COMPREHENSIVE TEST SUITE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "This script will test ALL MCP server capabilities and integrations" -ForegroundColor Cyan
Write-Host "with real Obsidian vault data consumption." -ForegroundColor Cyan
Write-Host ""
Write-Host "Prerequisites:" -ForegroundColor Yellow
Write-Host "- Obsidian running with Local REST API plugin" -ForegroundColor White
Write-Host "- Vault path: D:\Nomade Milionario" -ForegroundColor White
Write-Host "- API Token: b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70" -ForegroundColor White
Write-Host "- API Port: 27124" -ForegroundColor White
Write-Host ""

# Check if Obsidian API is accessible
Write-Host "🔍 Checking Obsidian API connectivity..." -ForegroundColor Cyan
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
    Read-Host "Press Enter to continue anyway or Ctrl+C to exit"
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "🧪 TESTING ALL CAPABILITIES" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green

# Function to run a test
function Test-Capability {
    param(
        [string]$Name,
        [string]$Command,
        [string]$Description
    )
    
    Write-Host ""
    Write-Host "🔹 Testing $Name..." -ForegroundColor Cyan
    Write-Host "   $Description" -ForegroundColor Gray
    
    try {
        $result = Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $Name test passed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "   ❌ $Name test failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "   ❌ $Name test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test all capabilities
$tests = @(
    @{
        Name = "Real-Time Synchronization System"
        Command = "go run REAL_TIME_VAULT_SYNC.go"
        Description = "Tests real-time file monitoring and sync capabilities"
    },
    @{
        Name = "Monitoring Dashboard"
        Command = "go run VAULT_MONITORING_DASHBOARD.go"
        Description = "Tests web-based monitoring interface"
    },
    @{
        Name = "Comprehensive Test Suite"
        Command = "go run REAL_TIME_SYNC_TEST_SUITE.go"
        Description = "Tests all synchronization features comprehensively"
    },
    @{
        Name = "Advanced API Pipelines"
        Command = "go run advanced_api_pipelines.go"
        Description = "Tests robust API calling algorithms"
    },
    @{
        Name = "Smart Search Engine"
        Command = "go run ADVANCED_SMART_SEARCH_ENGINE.go"
        Description = "Tests semantic, fuzzy, and regex search capabilities"
    },
    @{
        Name = "Note Management System"
        Command = "go run COMPREHENSIVE_NOTE_MANAGEMENT_SYSTEM.go"
        Description = "Tests CRUD operations and note management"
    },
    @{
        Name = "Bulk Operations System"
        Command = "go run BULK_OPERATIONS_SYSTEM.go"
        Description = "Tests bulk tagging, linking, and organization"
    },
    @{
        Name = "AI-Powered Features"
        Command = "go run AI_POWERED_FEATURES.go"
        Description = "Tests DeepSeek-R1:8B integration and AI capabilities"
    },
    @{
        Name = "Workflow Automation System"
        Command = "go run WORKFLOW_AUTOMATION_SYSTEM.go"
        Description = "Tests workflow creation and automation"
    },
    @{
        Name = "Ultimate Integrated CLI Chat"
        Command = "go run ULTIMATE_INTEGRATED_CLI_CHAT.go"
        Description = "Tests complete CLI chat system with all integrations"
    }
)

$passedTests = 0
$totalTests = $tests.Count

foreach ($test in $tests) {
    if (Test-Capability -Name $test.Name -Command $test.Command -Description $test.Description) {
        $passedTests++
    }
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "📊 TEST RESULTS SUMMARY" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $($totalTests - $passedTests)" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($passedTests / $totalTests) * 100, 1))%" -ForegroundColor Cyan

if ($passedTests -eq $totalTests) {
    Write-Host ""
    Write-Host "🎉 ALL TESTS COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Real-Time Synchronization: WORKING" -ForegroundColor Green
    Write-Host "✅ Monitoring Dashboard: WORKING" -ForegroundColor Green
    Write-Host "✅ Comprehensive Test Suite: WORKING" -ForegroundColor Green
    Write-Host "✅ Advanced API Pipelines: WORKING" -ForegroundColor Green
    Write-Host "✅ Smart Search Engine: WORKING" -ForegroundColor Green
    Write-Host "✅ Note Management System: WORKING" -ForegroundColor Green
    Write-Host "✅ Bulk Operations System: WORKING" -ForegroundColor Green
    Write-Host "✅ AI-Powered Features: WORKING" -ForegroundColor Green
    Write-Host "✅ Workflow Automation: WORKING" -ForegroundColor Green
    Write-Host "✅ Ultimate CLI Chat: WORKING" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 ALL MCP SERVER CAPABILITIES ARE FULLY FUNCTIONAL!" -ForegroundColor Green
    Write-Host "🌐 Dashboard available at: http://localhost:8082" -ForegroundColor Cyan
    Write-Host "💬 CLI Chat ready for interactive use" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠️ Some tests failed. Please check the output above for details." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "🎯 ONE-LINER COMMANDS FOR TESTING" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Quick test commands:" -ForegroundColor Cyan
Write-Host "  go run ULTIMATE_INTEGRATED_CLI_CHAT.go" -ForegroundColor White
Write-Host "  go run REAL_TIME_VAULT_SYNC.go" -ForegroundColor White
Write-Host "  go run VAULT_MONITORING_DASHBOARD.go" -ForegroundColor White
Write-Host "  go run REAL_TIME_SYNC_TEST_SUITE.go" -ForegroundColor White
Write-Host ""
Write-Host "Interactive CLI Chat commands to try:" -ForegroundColor Cyan
Write-Host "  list                    - List all files in vault" -ForegroundColor White
Write-Host "  search <query>          - Search vault content" -ForegroundColor White
Write-Host "  read <filename>         - Read a specific note" -ForegroundColor White
Write-Host "  create <filename>      - Create a new note" -ForegroundColor White
Write-Host "  status                  - Show system status" -ForegroundColor White
Write-Host "  health                  - Health check" -ForegroundColor White
Write-Host "  dashboard              - Open monitoring dashboard" -ForegroundColor White
Write-Host "  help                   - Show all commands" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
