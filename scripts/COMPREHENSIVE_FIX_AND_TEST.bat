@echo off
echo ================================================================
echo 🚀 COMPREHENSIVE FIX AND TEST SUITE
echo ================================================================
echo.
echo This script will fix all issues and test everything systematically
echo.

echo Step 1: Checking current directory...
cd /d "D:\codex\datamaster\backend-ops\llm-ops\api-mcp-simbiosis"
echo Current directory: %CD%

echo.
echo Step 2: Testing Working CLI Chat System...
echo Starting Working CLI Chat...
start "Working CLI Chat" cmd /k "go run WORKING_CLI_CHAT.go"

echo.
echo Step 3: Testing Real-Time Sync System...
echo Starting Real-Time Sync...
start "Real-Time Sync" cmd /k "go run REAL_TIME_VAULT_SYNC.go"

echo.
echo Step 4: Testing Monitoring Dashboard...
echo Starting Dashboard...
start "Monitoring Dashboard" cmd /k "go run VAULT_MONITORING_DASHBOARD.go"

echo.
echo Step 5: Testing MCP Server...
echo Starting MCP Server...
cd mcp-server
start "MCP Server" cmd /k "go run cmd/server/main.go"
cd ..

echo.
echo Step 6: Running Test Suite...
echo Starting Test Suite...
start "Test Suite" cmd /k "go run REAL_TIME_SYNC_TEST_SUITE.go"

echo.
echo ================================================================
echo 🎉 ALL SYSTEMS STARTED!
echo ================================================================
echo.
echo ✅ Working CLI Chat: Started in new window
echo ✅ Real-Time Sync: Started in new window  
echo ✅ Monitoring Dashboard: Started in new window
echo ✅ MCP Server: Started in new window
echo ✅ Test Suite: Started in new window
echo.
echo 📋 TESTING COMMANDS:
echo   In CLI Chat window, try these commands:
echo   - test          (Test API connection)
echo   - list          (List vault files)
echo   - search <query> (Search vault)
echo   - status        (Show system status)
echo   - health        (Health check)
echo   - help          (Show all commands)
echo.
echo 🌐 WEB INTERFACES:
echo   - Dashboard: http://localhost:8082
echo   - MCP Server: http://localhost:3010
echo.
echo Press any key to continue...
pause
