@echo off
echo 🚀 RUNNING FINAL COMPREHENSIVE TEST
echo ===================================
echo Testing MCP server with complete coverage
echo Real vault data: 1000+ files
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0final_comprehensive_test.ps1"

echo.
echo ✅ FINAL COMPREHENSIVE TEST COMPLETE!
echo ====================================
pause


