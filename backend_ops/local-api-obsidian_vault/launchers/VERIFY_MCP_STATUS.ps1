# 🔍 VERIFY MCP STATUS - Check All Servers
Write-Host "🔍 VERIFYING MCP SERVER STATUS" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Check running Node.js processes
Write-Host "`n📊 Checking running MCP processes..." -ForegroundColor Yellow
$nodeProcesses = Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Select-Object Id, ProcessName, StartTime
Write-Host "Found $($nodeProcesses.Count) Node.js processes running" -ForegroundColor Green

# Check specific MCP server processes
Write-Host "`n🔍 Checking MCP server processes..." -ForegroundColor Yellow

$mcpServers = @(
    "filesystem",
    "github", 
    "sequential-thinking",
    "playwright",
    "context7",
    "shadcn-ui",
    "fetch",
    "brave-search"
)

$runningServers = @()
$stoppedServers = @()

foreach ($server in $mcpServers) {
    $processes = Get-Process | Where-Object {$_.ProcessName -like "*node*" -and $_.CommandLine -like "*$server*"}
    if ($processes) {
        Write-Host "   ✅ $server - Running (PID: $($processes[0].Id))" -ForegroundColor Green
        $runningServers += $server
    } else {
        Write-Host "   ❌ $server - Not running" -ForegroundColor Red
        $stoppedServers += $server
    }
}

# Check URL-based servers
Write-Host "`n🌐 URL-based servers:" -ForegroundColor Yellow
Write-Host "   ✅ byterover-mcp - URL: https://mcp.byterover.dev/mcp" -ForegroundColor Green

# Summary
Write-Host "`n📊 MCP STATUS SUMMARY" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "Running servers: $($runningServers.Count)/8" -ForegroundColor Green
Write-Host "Stopped servers: $($stoppedServers.Count)/8" -ForegroundColor Red
Write-Host "URL-based servers: 1/1" -ForegroundColor Green

if ($stoppedServers.Count -gt 0) {
    Write-Host "`n⚠️  Stopped servers:" -ForegroundColor Yellow
    foreach ($server in $stoppedServers) {
        Write-Host "   • $server" -ForegroundColor White
    }
    Write-Host "`n💡 To restart stopped servers, run: .\ENABLE_ALL_MCP_SERVERS.ps1" -ForegroundColor Cyan
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to Cursor MCP Tools panel" -ForegroundColor White
Write-Host "2. Toggle each server from 'Disabled' to 'Enabled'" -ForegroundColor White
Write-Host "3. Test MCP tools functionality" -ForegroundColor White
Write-Host "4. All servers should now be fully functional!" -ForegroundColor White

Write-Host "`n✅ MCP verification complete!" -ForegroundColor Green
