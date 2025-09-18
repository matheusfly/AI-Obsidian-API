@echo off
echo ================================================================
echo 🚀 QUICK TEST - WORKING CLI CHAT SYSTEM
echo ================================================================
echo.

echo Step 1: Building Working CLI Chat...
go build -o working-cli-chat.exe WORKING_CLI_CHAT.go
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)
echo ✅ Build successful

echo.
echo Step 2: Starting Working CLI Chat...
echo.
echo 💬 CLI Chat will start now. Try these commands:
echo   - test          (Test API connection)
echo   - list          (List vault files)
echo   - search <query> (Search vault)
echo   - status        (Show system status)
echo   - health        (Health check)
echo   - help          (Show all commands)
echo   - quit          (Exit)
echo.
echo Press any key to start...
pause

.\working-cli-chat.exe
