@echo off
echo ========================================
echo  TEST ALL ENDPOINTS - REAL DATA
echo ========================================

echo.
echo 1. Testing health endpoint...
curl http://localhost:3010/health
echo.

echo.
echo 2. Testing tools list...
curl http://localhost:3010/tools/list
echo.

echo.
echo 3. Testing list files tool...
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"list_files_in_vault\",\"parameters\":{}}"
echo.

echo.
echo 4. Testing search tool...
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"search_vault\",\"parameters\":{\"query\":\"test\"}}"
echo.

echo.
echo 5. Testing read note tool...
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"read_note\",\"parameters\":{\"filename\":\"AGENTS.md\"}}"
echo.

echo.
echo ========================================
echo  ALL TESTS COMPLETE!
echo ========================================
pause

