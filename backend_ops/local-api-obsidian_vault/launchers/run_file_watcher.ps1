[CmdletBinding()]
param(
    [string]$VaultPath = "",
    [string]$WebhookUrl = "http://localhost:5678/webhookscripts/le-change",
    [string]$ApiKey = "",
    [int]$Port = 8000,
    [string]$Host = "0.0.0.0"
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Err($msg)  { Write-Host "[ERR ] $msg" -ForegroundColor Red }

# Ensure env is prepared
if (-not (Test-Path servicesservicesscripts/le-watcher\.venv\Scripts\Activate.ps1")) {
    Write-Info servicesservicesscripts/le-watcher venv not found, running setup_uv_env.ps1"
    & "scripts/_uv_env.ps1" | Out-Null
}

# Resolve VaultPath
if (-not $VaultPath) {
    if ($env:VAULT_PATH) { $VaultPath = $env:VAULT_PATH }
}
if (-not $VaultPath) {
    Write-Info "No VaultPath provided; defaulting to C:\\ObsidianVault"
    $VaultPath = "C:\\ObsidianVault"
}

# Activate venv
. servicesservicesscripts/le-watcher\.venv\Scripts\Activate.ps1"

# Environment variables for production
$env:PYTHONUNBUFFERED = "1"
$env:ENV = "production"
$env:VAULT_PATH = $VaultPath
$env:WEBHOOK_URL = $WebhookUrl
if ($ApiKey) { $env:API_KEY = $ApiKey }
$env:PORT = "$Port"

Write-Info "Launching File Watcher (uvicorn) on ${Host}:${Port}"
uvicorn file_watcher:app --app-dir servicesservicesscripts/le-watcher" --host $Host --port $Port --log-level info --proxy-headers
