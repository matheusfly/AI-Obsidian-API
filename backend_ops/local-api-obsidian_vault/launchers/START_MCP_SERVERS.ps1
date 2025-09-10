# MCP Server Startup Script
Write-Host "🚀 Starting all MCP servers..." -ForegroundColor Cyan

# Start filesystem server
Write-Host "Starting filesystem server..." -ForegroundColor Yellow
Start-Process -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-filesystem", "D:\codex\master_code\backend_ops\local-api-obsidian_vault" -WindowStyle Hidden

# Start GitHub server
Write-Host "Starting GitHub server..." -ForegroundColor Yellow
Start-Process -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-github" -WindowStyle Hidden

# Start sequential-thinking server
Write-Host "Starting sequential-thinking server..." -ForegroundColor Yellow
Start-Process -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-sequential-thinking" -WindowStyle Hidden

# Start Playwright server
Write-Host "Starting Playwright server..." -ForegroundColor Yellow
Start-Process -FilePath "npx" -ArgumentList "@playwright/mcp@latest" -WindowStyle Hidden

# Start Context7 server
Write-Host "Starting Context7 server..." -ForegroundColor Yellow
Start-Process -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-everything" -WindowStyle Hidden

# Start shadcn-ui server
Write-Host "Starting shadcn-ui server..." -ForegroundColor Yellow
Start-Process -FilePath "npx" -ArgumentList "-y", "@sherifbutt/shadcn-ui-mcp-server@latest" -WindowStyle Hidden

# Start fetch server
Write-Host "Starting fetch server..." -ForegroundColor Yellow
Start-Process -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-everything" -WindowStyle Hidden

# Start Brave Search server
Write-Host "Starting Brave Search server..." -ForegroundColor Yellow
Start-Process -FilePath "npx" -ArgumentList "-y", "@modelcontextprotocol/server-brave-search" -WindowStyle Hidden

Write-Host "✅ All MCP servers started!" -ForegroundColor Green
Write-Host "Check Cursor MCP Tools panel - servers should now be enabled!" -ForegroundColor Cyan
