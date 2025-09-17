@echo off
REM MCP Server Build Script for Windows
echo Building MCP Server...

REM Create build directory
if not exist build mkdir build

REM Build the server
echo Compiling server binary...
go build -o build/mcp-server.exe ./cmd/server

if %errorlevel% equ 0 (
    echo ✅ Build successful! Binary created at: build/mcp-server.exe
    echo 📁 Binary size:
    dir build\mcp-server.exe | findstr mcp-server.exe
) else (
    echo ❌ Build failed!
    exit /b 1
)

REM Create run script
echo @echo off > build\run-server.bat
echo echo Starting MCP Server... >> build\run-server.bat
echo echo Make sure Obsidian is running with Local REST API plugin enabled >> build\run-server.bat
echo echo Make sure Ollama is running on localhost:11434 >> build\run-server.bat
echo echo. >> build\run-server.bat
echo mcp-server.exe >> build\run-server.bat
echo pause >> build\run-server.bat

echo ✅ Build script completed!
echo 🚀 To run the server: cd build && run-server.bat
pause

