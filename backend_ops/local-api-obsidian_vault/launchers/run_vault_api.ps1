[CmdletBinding()]
param(
    [string]$VaultPath = "",
    [string]$ObsidianApiUrl = "http://localhost:27123",
    [string]$ObsidianApiKey = "",
    [string]$N8nApiUrl = "http://localhost:5678",
    [int]$Port = 8080,
    [string]$Host = "0.0.0.0"
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Err($msg)  { Write-Host "[ERR ] $msg" -ForegroundColor Red }

# Ensure env is prepared
if (-not (Test-Path servicesservices/vault-api\.venv\Scripts\Activate.ps1")) {
    Write-Info servicesservices/vault-api venv not found, running setup_uv_env.ps1"
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
. servicesservices/vault-api\.venv\Scripts\Activate.ps1"

# Environment variables for production
$env:PYTHONUNBUFFERED = "1"
$env:ENV = "production"
$env:VAULT_PATH = $VaultPath
$env:OBSIDIAN_API_URL = $ObsidianApiUrl
if ($ObsidianApiKey) { $env:OBSIDIAN_API_KEY = $ObsidianApiKey }
$env:N8N_API_URL = $N8nApiUrl

Write-Info ("Launching Vault API (uvicorn) on {0}:{1}" -f $Host, $Port)
uvicorn main:app --app-dir servicesservices/vault-api" --host $Host --port $Port --workers 1 --log-level info --proxy-headers
