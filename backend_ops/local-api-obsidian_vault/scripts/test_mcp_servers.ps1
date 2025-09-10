# This script verifies local prerequisites for starting some MCP servers and performs quick health checks.
# It does NOT print or store any secrets.

param(
  [switch]$SkipDocker
)

$ErrorActionPreference = 'Stop'

function Check-Cmd($name, $args) {
  try {
    & $name $args | Out-Null
    return $true
  } catch {
    return $false
  }
}

Write-Host scripts/ing prerequisites..."

$hasNode = Check-Cmd node '-v'
$hasNpx  = Check-Cmd npx '-v'
$hasUvx  = Check-Cmd uvx '-V'
$hasDocker = $false
if (-not $SkipDocker) { $hasDocker = Check-Cmd docker '--version' }

Write-Host " node:  " ($hasNode  ? 'OK' : 'Missing')
Write-Host " npx:   " ($hasNpx   ? 'OK' : 'Missing')
Write-Host " uvx:   " ($hasUvx   ? 'OK' : 'Missing')
if (-not $SkipDocker) { Write-Host " docker:" ($hasDocker ? 'OK' : 'Missing') }

if (-not ($hasNode -and $hasNpx)) {
  Write-Warning "Node.js and npx are required for several MCP servers (github, sequential-thinking, etc.)"
}
if (-not $hasUvx) {
  Write-Warning "uvx is required for mcp-server-fetch."
}
if (-not $SkipDocker -and -not $hasDocker) {
  Write-Warning "Docker is required for the redis MCP container."
}

Write-Host "\nQuick SSE check for byterover-mcp (should return HTTP 200)..."
try {
  $resp = (Invoke-WebRequest -Uri "https://mcp.byterover.dev/mcp?machineId=1f07a91e-5ce8-6950-b300-56b817457f07" -Method Head -TimeoutSec 10 -ErrorAction Stop)
  Write-Host (" byterover-mcp: {0}" -f $resp.StatusCode)
} catch {
  Write-Warning " byterover-mcp SSE check failed: $($_.Exception.Message)"
}

Write-Host "\nLightweight start/stop smoke tests (no auth servers):"

if ($hasNpx) {
  try {
    Write-Host " starting sequential-thinking (3s)..."
    $p = Start-Process -FilePath 'npx' -ArgumentList @('-y','@modelcontextprotocol/server-sequential-thinking') -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Stop-Process -Id $p.Id -Force
    Write-Host " sequential-thinking: OK"
  } catch {
    Write-Warning " sequential-thinking failed to start: $($_.Exception.Message)"
  }
}

if ($hasUvx) {
  try {
    Write-Host " starting fetch (3s)..."
    $p2 = Start-Process -FilePath 'uvx' -ArgumentList @('mcp-server-fetch') -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Stop-Process -Id $p2.Id -Force
    Write-Host " fetch: OK"
  } catch {
    Write-Warning " fetch failed to start: $($_.Exception.Message)"
  }
}

Write-Host "\nDone. You can now paste the JSON config into Warp > MCP Servers and start servers there."

