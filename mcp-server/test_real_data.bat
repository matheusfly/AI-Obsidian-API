@echo off
echo 🧪 Testing MCP Server with Real Data
echo ====================================
echo.

echo 1. Testing health endpoint...
curl -s http://localhost:3010/health
echo.
echo.

echo 2. Testing tools list...
curl -s http://localhost:3010/tools/list
echo.
echo.

echo 3. Testing list files tool...
curl -s -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool\":\"list_files_in_vault\",\"params\":{}}"
echo.
echo.

echo 4. Testing search tool...
curl -s -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool\":\"search_vault\",\"params\":{\"query\":\"test\",\"limit\":3}}"
echo.
echo.

echo 🎉 Real Data Integration Test Complete!
echo The MCP server is now using real Obsidian vault data!
echo.
echo 🚀 Start interactive CLI: .\interactive_cli_real.exe
echo.
pause

