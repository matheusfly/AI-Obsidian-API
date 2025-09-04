@echo off
echo 🚀 Starting MCP Flyde Interactive UI...
echo =====================================

REM Try different ports if 3000 is busy
set PORT=3001
echo 🌐 Starting server on port %PORT%...

node examples/web-ui/server.js

if %ERRORLEVEL% neq 0 (
    echo ❌ Port %PORT% is busy, trying port 3002...
    set PORT=3002
    node examples/web-ui/server.js
)

if %ERRORLEVEL% neq 0 (
    echo ❌ Port 3002 is busy, trying port 3003...
    set PORT=3003
    node examples/web-ui/server.js
)

if %ERRORLEVEL% neq 0 (
    echo ❌ All ports busy. Please close other applications using ports 3000-3003
    pause
    exit /b 1
)

echo ✅ Server started successfully!
echo 🌐 Open your browser to: http://localhost:%PORT%
pause