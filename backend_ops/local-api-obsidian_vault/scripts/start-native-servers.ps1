[CmdletBinding()]
param(
  [string]$VaultPath = "D:\\Nomade Milionario",
  [int]$ObsidianPort = 27123,
  [int]$VaultPort = 8080,
  [int]$WaitSec = 25
)

$ErrorActionPreference = 'Stop'

function Write-Info($m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[ OK ] $m" -ForegroundColor Green }
function Write-Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err($m)  { Write-Host "[ERR ] $m" -ForegroundColor Red }

function Test-PortOpen($port) {
  try { return (Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue) }
  catch { return $false }
}

function Wait-Endpoint($name, $url, $timeoutSec) {
  $start = Get-Date
  while ((Get-Date) - $start -lt [TimeSpan]::FromSeconds($timeoutSec)) {
    try {
      $r = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
      if ($r.StatusCode -eq 200) { Write-Ok "$name ready ($url)"; return $true }
    } catch {}
    Start-Sleep -Seconds 2
  }
  Write-Warn "$name not ready after $timeoutSec sec ($url)"
  return $false
}

# Resolve paths
$repoRoot     = Split-Path $PSScriptRoot -Parent
$obsidianDir  = Join-Path $repoRoot servicesservices/obsidian-api'
$runVaultPs1  = Join-Path $repoRoot 'run_vault_api.ps1'

Write-Info "Repo root: $repoRoot"
Write-Info "VaultPath: $VaultPath"

# Start Obsidian API (Node) if port not already listening
if (Test-PortOpen $ObsidianPort) {
  Write-Ok "Obsidian API already listening on :$ObsidianPort"
} else {
  Write-Info "Starting Obsidian API on :$ObsidianPort ..."
  if (-not (Test-Path (Join-Path $obsidianDir 'node_modules'))) {
    Write-Info scripts/ing npm deps for obsidian-api ..."
    Push-Location $obsidianDir; npm install --no-fund --no-audit; Pop-Location
  }
  $obsJob = Start-Job -Name servicesservices/obsidian-api" -ScriptBlock {
    param($dir,$vault,$port)
    $env:VAULT_PATH = $vault
    Set-Location $dir
    npm start | Write-Output
  } -ArgumentList $obsidianDir,$VaultPath,$ObsidianPort
}

# Start Vault API (FastAPI) if port not already listening
if (Test-PortOpen $VaultPort) {
  Write-Ok "Vault API already listening on :$VaultPort"
} else {
  Write-Info "Starting Vault API on :$VaultPort ..."
  $vaultJob = Start-Job -Name servicesservices/vault-api" -ScriptBlock {
    param($script,$vault,$obsPort,$vaultPort)
    & $script -VaultPath $vault -ObsidianApiUrl ("http://localhost:{0}" -f $obsPort) -Port $vaultPort -Host '0.0.0.0' | Write-Output
  } -ArgumentList $runVaultPs1,$VaultPath,$ObsidianPort,$VaultPort
}

# Wait for readiness
Write-Info "Waiting up to $WaitSec sec for services ..."
$ok1 = Wait-Endpoint "Obsidian API" ("http://localhost:{0}/health" -f $ObsidianPort) $WaitSec
$ok2 = Wait-Endpoint "Vault API"    ("http://localhost:{0}/health" -f $VaultPort)    $WaitSec

Write-Host ""
Write-Ok "Launch summary"
Write-Host "  • Obsidian API: http://localhost:$ObsidianPort/health" -ForegroundColor White
Write-Host "  • Vault API    : http://localhost:$VaultPort (docs: /docs)" -ForegroundColor White

if (-not ($ok1 -and $ok2)) {
  Write-Warn "One or more services may still be starting. Use Get-Job; Receive-Job -Name obsidian-apiservices/vault-api for logs."
}

Write-Host ""
Write-Info "Useful commands"
Write-Host "  Get-Job" -ForegroundColor Gray
Write-Host "  Receive-Job -Name obsidian-api -Keep | Select-Object -Last 100" -ForegroundColor Gray
Write-Host "  Receive-Job -Name vault-api    -Keep | Select-Object -Last 100" -ForegroundColor Gray
Write-Host "  Stop-Job obsidian-api, vault-api" -ForegroundColor Gray

