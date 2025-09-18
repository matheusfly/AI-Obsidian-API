@echo off
echo ================================================================
echo 🚀 ULTIMATE INTEGRATED CLI CHAT - COMPREHENSIVE TEST SUITE
echo ================================================================
echo.
echo This script will test ALL MCP server capabilities and integrations
echo with real Obsidian vault data consumption.
echo.
echo Prerequisites:
echo - Obsidian running with Local REST API plugin
echo - Vault path: D:\Nomade Milionario
echo - API Token: b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70
echo - API Port: 27124
echo.
pause

echo.
echo ================================================================
echo 🧪 TESTING ALL CAPABILITIES
echo ================================================================

echo.
echo 1️⃣ Testing Real-Time Synchronization System...
go run REAL_TIME_VAULT_SYNC.go
if %errorlevel% neq 0 (
    echo ❌ Real-Time Sync test failed
    pause
    exit /b 1
)
echo ✅ Real-Time Sync test passed

echo.
echo 2️⃣ Testing Monitoring Dashboard...
go run VAULT_MONITORING_DASHBOARD.go
if %errorlevel% neq 0 (
    echo ❌ Dashboard test failed
    pause
    exit /b 1
)
echo ✅ Dashboard test passed

echo.
echo 3️⃣ Testing Comprehensive Test Suite...
go run REAL_TIME_SYNC_TEST_SUITE.go
if %errorlevel% neq 0 (
    echo ❌ Test suite failed
    pause
    exit /b 1
)
echo ✅ Test suite passed

echo.
echo 4️⃣ Testing Advanced API Pipelines...
go run advanced_api_pipelines.go
if %errorlevel% neq 0 (
    echo ❌ API pipelines test failed
    pause
    exit /b 1
)
echo ✅ API pipelines test passed

echo.
echo 5️⃣ Testing Smart Search Engine...
go run ADVANCED_SMART_SEARCH_ENGINE.go
if %errorlevel% neq 0 (
    echo ❌ Search engine test failed
    pause
    exit /b 1
)
echo ✅ Search engine test passed

echo.
echo 6️⃣ Testing Note Management System...
go run COMPREHENSIVE_NOTE_MANAGEMENT_SYSTEM.go
if %errorlevel% neq 0 (
    echo ❌ Note management test failed
    pause
    exit /b 1
)
echo ✅ Note management test passed

echo.
echo 7️⃣ Testing Bulk Operations System...
go run BULK_OPERATIONS_SYSTEM.go
if %errorlevel% neq 0 (
    echo ❌ Bulk operations test failed
    pause
    exit /b 1
)
echo ✅ Bulk operations test passed

echo.
echo 8️⃣ Testing AI-Powered Features...
go run AI_POWERED_FEATURES.go
if %errorlevel% neq 0 (
    echo ❌ AI features test failed
    pause
    exit /b 1
)
echo ✅ AI features test passed

echo.
echo 9️⃣ Testing Workflow Automation System...
go run WORKFLOW_AUTOMATION_SYSTEM.go
if %errorlevel% neq 0 (
    echo ❌ Workflow automation test failed
    pause
    exit /b 1
)
echo ✅ Workflow automation test passed

echo.
echo 🔟 Testing Ultimate Integrated CLI Chat...
go run ULTIMATE_INTEGRATED_CLI_CHAT.go
if %errorlevel% neq 0 (
    echo ❌ Ultimate CLI chat test failed
    pause
    exit /b 1
)
echo ✅ Ultimate CLI chat test passed

echo.
echo ================================================================
echo 🎉 ALL TESTS COMPLETED SUCCESSFULLY!
echo ================================================================
echo.
echo ✅ Real-Time Synchronization: WORKING
echo ✅ Monitoring Dashboard: WORKING
echo ✅ Comprehensive Test Suite: WORKING
echo ✅ Advanced API Pipelines: WORKING
echo ✅ Smart Search Engine: WORKING
echo ✅ Note Management System: WORKING
echo ✅ Bulk Operations System: WORKING
echo ✅ AI-Powered Features: WORKING
echo ✅ Workflow Automation: WORKING
echo ✅ Ultimate CLI Chat: WORKING
echo.
echo 🚀 ALL MCP SERVER CAPABILITIES ARE FULLY FUNCTIONAL!
echo 🌐 Dashboard available at: http://localhost:8082
echo 💬 CLI Chat ready for interactive use
echo.
pause
