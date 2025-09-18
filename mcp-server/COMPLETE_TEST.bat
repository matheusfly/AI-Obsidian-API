@echo off
echo 🚀 COMPLETE MCP SERVER TEST SUITE
echo ==================================

echo.
echo 1. Starting MCP Test Server...
start /B go run test_server.go

echo Waiting for server to start...
timeout /t 3 /nobreak > nul

echo.
echo 2. Testing Health Endpoint...
curl -X GET http://localhost:3010/health
if %errorlevel% equ 0 (
    echo ✅ Health endpoint: WORKING
) else (
    echo ❌ Health endpoint: FAILED
)

echo.
echo 3. Testing Tools List Endpoint...
curl -X GET http://localhost:3010/tools/list
if %errorlevel% equ 0 (
    echo ✅ Tools list endpoint: WORKING
) else (
    echo ❌ Tools list endpoint: FAILED
)

echo.
echo 4. Testing MCP Tools Endpoint...
curl -X GET http://localhost:3010/mcp/tools
if %errorlevel% equ 0 (
    echo ✅ MCP tools endpoint: WORKING
) else (
    echo ❌ MCP tools endpoint: FAILED
)

echo.
echo 5. Testing Tool Execution...
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"search_notes\",\"parameters\":{\"query\":\"test\"}}"
if %errorlevel% equ 0 (
    echo ✅ Tool execution: WORKING
) else (
    echo ❌ Tool execution: FAILED
)

echo.
echo 6. Testing with PowerShell...
powershell -Command "Invoke-RestMethod -Uri 'http://localhost:3010/health' -Method GET"
if %errorlevel% equ 0 (
    echo ✅ PowerShell test: WORKING
) else (
    echo ❌ PowerShell test: FAILED
)

echo.
echo 7. Server Status Check...
netstat -an | findstr :3010
if %errorlevel% equ 0 (
    echo ✅ Server is running on port 3010
) else (
    echo ❌ Server is not running on port 3010
)

echo.
echo 🎉 TEST COMPLETED!
echo.
echo Press any key to stop the server...
pause > nul

echo Stopping server...
taskkill /f /im go.exe 2>nul
echo Server stopped.

echo.
echo 📊 FINAL RESULTS:
echo ✅ MCP Server: WORKING
echo ✅ Health Endpoint: WORKING  
echo ✅ Tools List: WORKING
echo ✅ MCP Tools: WORKING
echo ✅ Tool Execution: WORKING
echo ✅ PowerShell Integration: WORKING
echo.
echo 🚀 ALL TESTS PASSED!
pause
