@echo off
echo 🚀 Starting MCP Server with Real Data Integration
echo ================================================
echo.
echo ✅ Server starting on port 3010
echo 📡 Connecting to Obsidian API on port 27124
echo 🗂️  Vault: D:\Nomade Milionario
echo.
echo 🧪 Test endpoints:
echo    curl http://localhost:3010/health
echo    curl http://localhost:3010/tools/list
echo.
echo 🎯 Interactive CLI: .\interactive_cli_real.exe
echo.
start .\server-real.exe

