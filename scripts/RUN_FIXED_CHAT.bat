@echo off
echo ================================================================
echo 🚀 RUNNING FIXED CHAT SYSTEM
echo ================================================================
echo.

echo Building Working Chat Fixed...
go build -o working-chat-fixed.exe WORKING_CHAT_FIXED.go
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)
echo ✅ Build successful

echo.
echo Starting Working Chat Fixed System...
echo.
echo 💬 This version has the correct JSON parsing for the Obsidian API
echo 💬 Try these commands:
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

.\working-chat-fixed.exe
