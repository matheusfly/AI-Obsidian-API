@echo off
echo 🚀 RUNNING REAL DATA VALIDATION TEST
echo ====================================
echo Testing REAL Obsidian vault data (1000+ files)
echo API: https://localhost:27124
echo Vault: D:\Nomade Milionario
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0final_real_data_validation.ps1"

echo.
echo ✅ REAL DATA VALIDATION COMPLETE!
echo =================================
pause
