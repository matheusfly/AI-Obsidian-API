@echo off
echo ========================================
echo  MCP INTERACTIVE CLI - REAL DATA
echo ========================================

echo.
echo Building Interactive CLI...
go build -o interactive_cli_real.exe scripts/interactive_cli.go

echo.
echo Starting Interactive CLI...
.\interactive_cli_real.exe

pause