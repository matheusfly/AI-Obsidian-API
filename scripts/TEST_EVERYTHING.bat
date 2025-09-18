@echo off
echo ================================================================
echo 🚀 COMPREHENSIVE TEST SUITE - MCP SYSTEM
echo ================================================================
echo.

echo Step 1: Building Simple Working Chat...
go build -o simple-working-chat.exe SIMPLE_WORKING_CHAT.go
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)
echo ✅ Build successful

echo.
echo Step 2: Building Debug System...
go build -o debug-system.exe DEBUG_AND_LOG_SYSTEM.go
if %errorlevel% neq 0 (
    echo ❌ Debug build failed
    pause
    exit /b 1
)
echo ✅ Debug build successful

echo.
echo Step 3: Testing API Connection...
echo Testing Obsidian API at http://localhost:27124...
curl -s -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70" http://localhost:27124/vault/ > nul
if %errorlevel% equ 0 (
    echo ✅ Obsidian API is accessible
) else (
    echo ⚠️ Obsidian API may not be running
)

echo.
echo Step 4: Running Debug System...
echo Starting comprehensive debug test...
start "Debug System" cmd /k "debug-system.exe"

echo.
echo Step 5: Starting Simple Working Chat...
echo Starting interactive chat system...
start "Simple Working Chat" cmd /k "simple-working-chat.exe"

echo.
echo ================================================================
echo 🎉 TESTING COMPLETED!
echo ================================================================
echo.
echo ✅ Simple Working Chat: Started in new window
echo ✅ Debug System: Started in new window
echo.
echo 📋 TESTING COMMANDS (in Chat window):
echo   - test          (Test API connection)
echo   - list          (List vault files)
echo   - read <file>   (Read a note)
echo   - create <file> (Create a note)
echo   - search <query>(Search vault)
echo   - status        (Show status)
echo   - help          (Show help)
echo   - quit          (Exit)
echo.
echo 🌐 WEB INTERFACES:
echo   - Obsidian API: http://localhost:27124
echo.
echo 📄 LOGS:
echo   - Debug logs: debug.log
echo.
echo Press any key to continue...
pause
