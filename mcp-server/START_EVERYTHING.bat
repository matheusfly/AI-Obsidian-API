@echo off
echo ========================================
echo  MCP SERVER - REAL DATA INTEGRATION
echo ========================================

echo.
echo 1. Building server with nil logger fixes...
go build -o server-real.exe cmd/server/main.go

echo.
echo 2. Starting server...
start /B .\server-real.exe

echo.
echo 3. Waiting for server to start...
timeout /t 3 /nobreak > nul

echo.
echo 4. Testing server...
curl http://localhost:3010/health
echo.

echo.
echo 5. Starting Interactive CLI...
go build -o interactive_cli_real.exe scripts/interactive_cli.go
.\interactive_cli_real.exe

echo.
echo ========================================
echo  READY TO USE!
echo ========================================
pause