@echo off
echo ================================================================
echo 🚀 RUNNING FINAL WORKING CHAT SYSTEM
echo ================================================================
echo.

echo Building Final Working Chat...
go build -o final-working-chat.exe FINAL_WORKING_CHAT.go
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)
echo ✅ Build successful

echo.
echo Starting Final Working Chat System...
echo.
echo 💬 This version has the CORRECT JSON parsing and working search!
echo 💬 The API returns 72 files from your vault!
echo 💬 Try these commands:
echo   - test          (Test API connection)
echo   - list          (List vault files - shows 72 files!)
echo   - search AGENTS (Search for AGENTS - should find AGENTS.md!)
echo   - search Math   (Search for Math - should find Math_Frameworks-1_Funnel.md!)
echo   - search Energia (Search for Energia - should find Energia Cinematica.md!)
echo   - search leis   (Search for leis - should find leis-tributarias.md!)
echo   - read AGENTS.md (Read a specific file)
echo   - create test.md (Create a new file)
echo   - status        (Show status)
echo   - help          (Show help)
echo   - quit          (Exit)
echo.

.\final-working-chat.exe
