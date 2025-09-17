@echo off
echo 🚀 STARTING COMPLETE MCP SYSTEM
echo ================================

echo 🔧 Starting MCP Server...
start /B go run mcp_server_main.go

echo ⏳ Waiting for MCP server to start...
timeout /t 5 /nobreak > nul

echo 🎯 Starting Interactive MCP Chat...
go run interactive_mcp_chat.go

pause
