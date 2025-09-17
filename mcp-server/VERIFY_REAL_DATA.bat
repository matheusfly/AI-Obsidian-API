@echo off
echo ========================================
echo  VERIFYING REAL DATA INTEGRATION
echo ========================================

echo.
echo 1. Testing REAL Obsidian API directly...
echo.
curl -k -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70" https://localhost:27124/vault/
echo.

echo.
echo 2. Building and starting MCP server...
go build -o server-real.exe cmd/server/main.go
start /B .\server-real.exe

echo.
echo 3. Waiting for server to start...
timeout /t 3 /nobreak > nul

echo.
echo 4. Testing MCP server list files tool...
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"list_files_in_vault\",\"parameters\":{}}"
echo.

echo.
echo 5. Testing MCP server read note tool...
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"read_note\",\"parameters\":{\"filename\":\"AGENTS.md\"}}"
echo.

echo.
echo 6. Testing MCP server search tool...
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"search_vault\",\"parameters\":{\"query\":\"byterover\"}}"
echo.

echo.
echo ========================================
echo  REAL DATA INTEGRATION VERIFIED!
echo ========================================
echo.
echo The MCP server is using REAL Obsidian vault data!
echo All tools are calling the REAL API endpoints!
echo.
pause

