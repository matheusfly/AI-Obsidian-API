@echo off
echo 🚀 Launching Flyde UI with Active MCP Debugging and Playwright Testing
echo =====================================================================

echo.
echo 🔍 Starting MCP Debug Monitor...
start "MCP Debug Monitor" cmd /k "node mcp-debug-monitor.js"

echo.
echo 🌐 Starting Flyde Web Server...
start "Flyde Web Server" cmd /k "node mcp-web-server.js"

echo.
echo ⏳ Waiting for servers to start...
timeout /t 5 /nobreak > nul

echo.
echo 🎭 Starting Playwright Browser Testing...
start "Playwright Tests" cmd /k "node flyde-playwright-test.js"

echo.
echo 🎮 Opening Flyde UI in browser...
timeout /t 3 /nobreak > nul
start http://localhost:3000

echo.
echo ✅ All systems launched!
echo ========================
echo 🌐 Flyde UI: http://localhost:3000
echo 🔍 MCP Debug Monitor: Active
echo 🎭 Playwright Testing: Running
echo 📊 Check the console windows for real-time output
echo.
echo Press any key to stop all processes...
pause > nul

echo.
echo 🛑 Stopping all processes...
taskkill /f /im node.exe > nul 2>&1
echo ✅ All processes stopped