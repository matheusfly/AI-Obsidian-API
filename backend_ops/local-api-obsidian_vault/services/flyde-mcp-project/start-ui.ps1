# MCP Flyde Interactive UI Launcher
# PowerShell script for Windows

Write-Host "🚀 Starting MCP Flyde Interactive UI..." -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

# Try different ports if 3000 is busy
$ports = @(3000, 3001, 3002, 3003, 3004, 3005)
$success = $false

foreach ($port in $ports) {
    Write-Host "🌐 Trying port $port..." -ForegroundColor Yellow
    
    # Check if port is available
    $portCheck = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if (-not $portCheck) {
        Write-Host "✅ Port $port is available!" -ForegroundColor Green
        
        # Set environment variable and start server
        $env:PORT = $port
        Write-Host "🚀 Starting server on port $port..." -ForegroundColor Green
        
        try {
            node examples/web-ui/server.js
            $success = $true
            break
        }
        catch {
            Write-Host "❌ Failed to start on port $port: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "❌ Port $port is busy, trying next..." -ForegroundColor Red
    }
}

if (-not $success) {
    Write-Host "❌ All ports are busy. Please close other applications using ports 3000-3005" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "✅ Server started successfully!" -ForegroundColor Green
Write-Host "🌐 Open your browser to: http://localhost:$env:PORT" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow