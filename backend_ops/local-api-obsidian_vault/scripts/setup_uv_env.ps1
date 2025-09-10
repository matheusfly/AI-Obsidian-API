[CmdletBinding()]
param(
    [string]$PythonVersion = "3.13",
    [switch]$ForceLock
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERR ] $msg" -ForegroundColor Red }

Write-Info scripts/ing uv availability..."
try {
    $uvVersion = (uv --version)
    Write-Ok "uv present: $uvVersion"
} catch {
    Write-Err "uv is not installed. Please install with: irm https://astral.sh/uvscripts/.ps1 | iex"
    exit 1
}

# Helper to create venv if missing
function Ensure-Venv {
    param(
        [string]$VenvPath,
        [string]$PythonVersion
    )
    if (-not (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
        Write-Info scripts/ing venv at $VenvPath (Python $PythonVersion)"
        uv venv --python $PythonVersion $VenvPath
        Write-Ok scripts/d venv: $VenvPath"
    } else {
        Write-Info "Using existing venv: $VenvPath"
    }
}

# Root project (pyproject.toml)
if (Test-Path "pyproject.toml") {
    Write-Info "Setting up root environment from pyproject.toml"

    Ensure-Venv -VenvPath ".venv" -PythonVersion $PythonVersion
    . ".\.venv\Scripts\Activate.ps1"

    if ($ForceLock -or -not (Test-Path "uv.lock")) {
        Write-Info "Generating uv.lock"
        uv lock
        Write-Ok "uv.lock created"
    } else {
        Write-Info "uv.lock already exists (use -ForceLock to refresh)"
    }

    Write-Info "Syncing dependencies (frozen)"
    uv sync --frozen
    Write-Ok "Root environment ready"

    if (Get-Command -Name deactivate -ErrorAction SilentlyContinue) { deactivate }
} else {
    Write-Warn "pyproject.toml not found at repo root; skipping root env"
}

# vault-api component
if (Test-Path servicesservices/vault-api\requirements.txt") {
    Write-Info "Setting up vault-api environment from requirements.txt"

    Ensure-Venv -VenvPath servicesservices/vault-api\.venv" -PythonVersion $PythonVersion
    . servicesservices/vault-api\.venv\Scripts\Activate.ps1"

    uv pip sync servicesservices/vault-api\requirements.txt"
    Write-Ok servicesservices/vault-api environment ready"

    if (Get-Command -Name deactivate -ErrorAction SilentlyContinue) { deactivate }
} else {
    Write-Info servicesservices/vault-api/requirements.txt not found; skipping vault-api env"
}

# file-watcher component
if (Test-Path servicesservicesscripts/le-watcher\requirements.txt") {
    Write-Info "Setting up file-watcher environment from requirements.txt"

    Ensure-Venv -VenvPath servicesservicesscripts/le-watcher\.venv" -PythonVersion $PythonVersion
    . servicesservicesscripts/le-watcher\.venv\Scripts\Activate.ps1"

    uv pip sync servicesservicesscripts/le-watcher\requirements.txt"
    Write-Ok servicesservicesscripts/le-watcher environment ready"

    if (Get-Command -Name deactivate -ErrorAction SilentlyContinue) { deactivate }
} else {
    Write-Info servicesservicesscripts/le-watcher/requirements.txt not found; skipping file-watcher env"
}

Write-Ok "All environments prepared."

