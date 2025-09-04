# 🔄 RESTART CURSOR FOR MCP - Complete Activation
Write-Host "🔄 RESTARTING CURSOR TO ACTIVATE MCP SERVERS" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Step 1: Verify MCP configuration exists
Write-Host "`n📍 Step 1: Verifying MCP configuration..." -ForegroundColor Yellow

$mcpConfigPath = "D:\codex\master_code\backend_ops\local-api-obsidian_vault\.cursor\mcp.json"
if (Test-Path $mcpConfigPath) {
    Write-Host "✅ MCP configuration found" -ForegroundColor Green
    $configContent = Get-Content $mcpConfigPath -Raw
    $serverCount = ($configContent | ConvertFrom-Json).mcpServers.PSObject.Properties.Count
    Write-Host "✅ $serverCount MCP servers configured" -ForegroundColor Green
} else {
    Write-Host "❌ MCP configuration not found!" -ForegroundColor Red
    Write-Host "Run QUICK_MCP_FIX.ps1 first!" -ForegroundColor Yellow
    exit 1
}

# Step 2: Kill Cursor processes
Write-Host "`n🔄 Step 2: Stopping Cursor..." -ForegroundColor Yellow

try {
    $cursorProcesses = Get-Process | Where-Object {$_.ProcessName -like "*cursor*"}
    if ($cursorProcesses) {
        Write-Host "   Found $($cursorProcesses.Count) Cursor processes" -ForegroundColor Cyan
        $cursorProcesses | Stop-Process -Force
        Write-Host "✅ Cursor processes stopped" -ForegroundColor Green
    } else {
        Write-Host "✅ No Cursor processes running" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Could not stop all Cursor processes (continuing...)" -ForegroundColor Yellow
}

# Step 3: Wait for processes to close
Write-Host "`n⏳ Step 3: Waiting for processes to close..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 4: Start Cursor with project
Write-Host "`n🚀 Step 4: Starting Cursor with MCP configuration..." -ForegroundColor Yellow

$projectPath = "D:\codex\master_code\backend_ops\local-api-obsidian_vault"
try {
    Start-Process "cursor" -ArgumentList $projectPath
    Write-Host "✅ Cursor started with project" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start Cursor" -ForegroundColor Red
    Write-Host "Try starting Cursor manually and opening the project" -ForegroundColor Yellow
    exit 1
}

# Step 5: Wait for Cursor to load
Write-Host "`n⏳ Step 5: Waiting for Cursor to load..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 6: Final instructions
Write-Host "`n🎉 CURSOR RESTART COMPLETE!" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

Write-Host "`n✅ What happened:" -ForegroundColor Green
Write-Host "   1. MCP configuration verified" -ForegroundColor White
Write-Host "   2. Cursor processes stopped" -ForegroundColor White
Write-Host "   3. Cursor restarted with project" -ForegroundColor White
Write-Host "   4. MCP servers should now be active" -ForegroundColor White

Write-Host "`n🔍 Check these in Cursor:" -ForegroundColor Yellow
Write-Host "   1. Open MCP Tools panel (should show 18 servers)" -ForegroundColor White
Write-Host "   2. Look for filesystem, github, sequential-thinking tools" -ForegroundColor White
Write-Host "   3. Check if you can use MCP commands" -ForegroundColor White
Write-Host "   4. Test file operations and other MCP functions" -ForegroundColor White

Write-Host "`n📊 Expected MCP Servers:" -ForegroundColor Cyan
Write-Host "   • filesystem (file operations)" -ForegroundColor White
Write-Host "   • github (GitHub integration)" -ForegroundColor White
Write-Host "   • sequential-thinking (reasoning)" -ForegroundColor White
Write-Host "   • playwright (web automation)" -ForegroundColor White
Write-Host "   • context7 (context management)" -ForegroundColor White
Write-Host "   • shadcn-ui (UI components)" -ForegroundColor White
Write-Host "   • byterover-mcp (ByteRover)" -ForegroundColor White
Write-Host "   • fetch (web requests)" -ForegroundColor White
Write-Host "   • brave-search (web search)" -ForegroundColor White
Write-Host "   • postgres (PostgreSQL)" -ForegroundColor White
Write-Host "   • redis (Redis cache)" -ForegroundColor White
Write-Host "   • sqlite (SQLite database)" -ForegroundColor White
Write-Host "   • web-search (web search)" -ForegroundColor White
Write-Host "   • scrapfly (web scraping)" -ForegroundColor White
Write-Host "   • agent-ops (agent operations)" -ForegroundColor White
Write-Host "   • memory (persistent memory)" -ForegroundColor White
Write-Host "   • graphiti (graph operations)" -ForegroundColor White
Write-Host "   • aipotheosis-aci (ACI integration)" -ForegroundColor White
Write-Host "   • obsidian-vault (Obsidian notes)" -ForegroundColor White
Write-Host "   • sentry (error monitoring)" -ForegroundColor White
Write-Host "   • task-master-ai (AI task management)" -ForegroundColor White

Write-Host "`n🎯 If MCP tools still don't appear:" -ForegroundColor Yellow
Write-Host "   1. Check Cursor settings for MCP configuration" -ForegroundColor White
Write-Host "   2. Restart Cursor completely" -ForegroundColor White
Write-Host "   3. Verify .cursor/mcp.json exists in project root" -ForegroundColor White
Write-Host "   4. Check Cursor logs for MCP errors" -ForegroundColor White

Write-Host "`n✅ MCP activation complete! Check your Cursor MCP Tools panel now!" -ForegroundColor Green
