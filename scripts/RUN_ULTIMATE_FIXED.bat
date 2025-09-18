@echo off
echo ================================================================
echo 🚀 RUNNING ULTIMATE FIXED CHAT SYSTEM
echo ================================================================
echo.

echo Building Ultimate Fixed Chat...
go build -o ultimate-fixed-chat.exe ULTIMATE_FIXED_CHAT.go
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)
echo ✅ Build successful

echo.
echo Starting Ultimate Fixed Chat System...
echo.
echo 💬 This version tries multiple JSON structures to find files
echo 💬 Try these commands:
echo   - debug         (Debug API response and show all structures)
echo   - test          (Test API connection)
echo   - list          (List vault files - should show real files now!)
echo   - search logica (Search for logica - should find matches!)
echo   - search matematica (Search for matematica - should find matches!)
echo   - read AGENTS.md (Read a specific file)
echo   - create test.md (Create a new file)
echo   - status        (Show status)
echo   - help          (Show help)
echo   - quit          (Exit)
echo.

.\ultimate-fixed-chat.exe
