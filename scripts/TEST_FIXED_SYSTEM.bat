@echo off
echo ================================================================
echo 🚀 TESTING FIXED MCP SYSTEM
echo ================================================================
echo.

echo Step 1: Building Fixed Components...
go build -o simple-chat-fixed.exe SIMPLE_WORKING_CHAT.go
if %errorlevel% neq 0 (
    echo ❌ Simple Chat build failed
    pause
    exit /b 1
)
echo ✅ Simple Chat build successful

go build -o debug-system-fixed.exe DEBUG_AND_LOG_SYSTEM.go
if %errorlevel% neq 0 (
    echo ❌ Debug System build failed
    pause
    exit /b 1
)
echo ✅ Debug System build successful

echo.
echo Step 2: Testing API Connection with PowerShell...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://127.0.0.1:27124/vault/' -Headers @{'Authorization' = 'Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70'} -SkipCertificateCheck -TimeoutSec 10; Write-Host '✅ Obsidian API is accessible (Status:' $response.StatusCode ')' } catch { Write-Host '❌ Obsidian API not accessible:' $_.Exception.Message }"

echo.
echo Step 3: Running Debug System Test...
echo Starting debug system test...
start "Debug System Test" cmd /k "debug-system-fixed.exe"

echo.
echo Step 4: Starting Fixed Simple Chat...
echo Starting fixed chat system...
start "Fixed Simple Chat" cmd /k "simple-chat-fixed.exe"

echo.
echo ================================================================
echo 🎉 FIXED SYSTEM TESTING COMPLETED!
echo ================================================================
echo.
echo ✅ Fixed Simple Chat: Started in new window
echo ✅ Debug System Test: Started in new window
echo.
echo 💬 In the Fixed Chat window, try these commands:
echo   - test          (Test API connection - should work now!)
echo   - list          (List vault files)
echo   - read <file>   (Read a note)
echo   - create <file> (Create a note)
echo   - search <query>(Search vault)
echo   - status        (Show status)
echo   - help          (Show help)
echo   - quit          (Exit)
echo.
echo 🔧 FIXES APPLIED:
echo   - Changed API URL from http://localhost:27124 to https://127.0.0.1:27124
echo   - Added SSL certificate skipping for HTTPS connections
echo   - Updated HTTP client configuration
echo.
echo Press any key to continue...
pause
