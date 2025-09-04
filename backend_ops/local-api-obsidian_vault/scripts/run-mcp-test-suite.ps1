[CmdletBinding()]
param(
  [string]$VaultApiBase = "http://localhost:8080",
  [switch]$IncludeWebMCP,
  [switch]$IncludeGitHub,
  [switch]$IncludeBrave,
  [switch]$IncludeContext7,
  [switch]$IncludeByterover,
  [switch]$IncludePlaywright,
  [string]$OutDir = logs//mcp-tests",
  [int]$TimeoutSec = 12
)

$ErrorActionPreference = 'Stop'

function New-Stamp { (Get-Date).ToString('yyyyMMdd-HHmmss') }
function Ensure-Dir($p) { if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null } }
function Save-Json($obj, $path) {
  try { $obj | ConvertTo-Json -Depth 6 | Out-File -FilePath $path -Encoding UTF8 } catch { "{}" | Out-File -FilePath $path -Encoding UTF8 }
}
function Save-Text($text, $path) { $text | Out-File -FilePath $path -Encoding UTF8 }

$stamp = New-Stamp
$root = Join-Path -Path (Get-Location) -ChildPath ($OutDir)
$dest = Join-Path $root $stamp
Ensure-Dir $root; Ensure-Dir $dest

Write-Host "[MCP TEST] Output folder: $dest" -ForegroundColor Cyan

# 1) Quick prerequisite check
$prereq = @{
  node = (Get-Command node -ErrorAction SilentlyContinue) -ne $null
  npx  = (Get-Command npx -ErrorAction SilentlyContinue) -ne $null
  uvx  = (Get-Command uvx -ErrorAction SilentlyContinue) -ne $null
}
Save-Json $prereq (Join-Path $dest 'prerequisites.json')
Write-Host "[MCP TEST] Prerequisites => node=$($prereq.node) npx=$($prereq.npx) uvx=$($prereq.uvx)"

# 2) Run existing lightweight MCP server smoke checks (if present)
$quickScript = Join-Path (Split-Path $PSScriptRoot -Parent) 'scriptsscripts/_mcp_servers.ps1'
if (Test-Path $quickScript) {
  Write-Host "[MCP TEST] Running scriptsscripts/_mcp_servers.ps1 -SkipDocker ..." -ForegroundColor Yellow
  try {
    $out = & pwsh -NoProfile -ExecutionPolicy Bypass -File $quickScript -SkipDocker 2>&1
    Save-Text ($out | Out-String) (Join-Path $dest scripts/_mcp_servers.log')
  } catch {
    Save-Text $_.Exception.ToString() (Join-Path $dest scripts/_mcp_servers.error.log')
  }
} else {
  Write-Host "[MCP TEST] Skipping test_mcp_servers.ps1 (not found)" -ForegroundColor DarkGray
}

# 3) Test Vault API HTTP MCP endpoints (if server is up)
function Test-Url($name, $url) {
  try {
    $resp = Invoke-WebRequest -Uri $url -TimeoutSec $TimeoutSec -UseBasicParsing -ErrorAction Stop
    return @{ ok = $true; status = $resp.StatusCode; url = $url }
  } catch {
    return @{ ok = $false; error = $_.Exception.Message; url = $url }
  }
}

Write-Host "[MCP TEST] Checking Vault API: $VaultApiBase" -ForegroundColor Yellow
$health = Test-Url 'vault-health' ("$VaultApiBase/health")
Save-Json $health (Join-Path $dest servicesservices/vault-api.health.json')

if ($health.ok) {
  # List tools
  try {
    $tools = Invoke-RestMethod -Uri ("$VaultApiBase/api/v1/mcp/tools") -TimeoutSec $TimeoutSec
    Save-Json $tools (Join-Path $dest servicesservices/vault-api.tools.json')
    Write-Host ("[MCP TEST] Vault API tools: {0}" -f $tools.total)
  } catch {
    Save-Text $_.Exception.ToString() (Join-Path $dest servicesservices/vault-api.tools.error.log')
  }

  # Call a few tools
  $calls = @(
    @{ name = 'read_file'; body = @{ tool='read_file'; arguments=@{ path='README.md' } } },
    @{ name = 'list_files'; body = @{ tool='list_files'; arguments=@{ path='' } } },
    @{ name = 'search_content'; body = @{ tool='search_content'; arguments=@{ query='TODO' } } }
  )

  foreach ($c in $calls) {
    $fname = servicesservices/vault-api.call.{0}.json" -f $c.name
    try {
      $res = Invoke-RestMethod -Uri ("$VaultApiBase/api/v1/mcp/tools/call") -Method Post -Body ($c.body | ConvertTo-Json) -ContentType 'application/json' -TimeoutSec $TimeoutSec
      Save-Json $res (Join-Path $dest $fname)
    } catch {
      Save-Text $_.Exception.ToString() (Join-Path $dest ($fname + '.error.log'))
    }
  }
} else {
  Write-Host "[MCP TEST] Vault API not reachable; skipping HTTP tool calls" -ForegroundColor DarkYellow
}

# 4) Custom MCP servers quick invocations (only if tools exist)
# We will attempt the repo's custom servers with --test which should exit quickly.
$customServers = @(
  @{ name='graphiti';      path=(Join-Path (Split-Path $PSScriptRoot -Parent) 'graphiti-server\index.js') },
  @{ name='aci';           path=(Join-Path (Split-Path $PSScriptRoot -Parent) servicesservices/aci-server\index.js') },
  @{ name='obsidian-vault';path=(Join-Path (Split-Path $PSScriptRoot -Parent) servicesservices/obsidian-mcp-server\index.js') }
)

foreach ($srv in $customServers) {
  if (Test-Path $srv.path) {
    Write-Host "[MCP TEST] Testing $($srv.name) MCP server --test" -ForegroundColor Yellow
    $log = Join-Path $dest ("custom-" + $srv.name + '.log')
    try {
      # Most of these support a --test switch per existing setup scripts
      $out = & node $srv.path --test 2>&1
      Save-Text ($out | Out-String) $log
    } catch {
      Save-Text $_.Exception.ToString() ($log + '.error.log')
    }
  }
}

# 5) Optional: external MCPs (guarded by flags and env vars)
function Has-Env($name) { return -not [string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($name)) }

if ($IncludeGitHub -and $prereq.npx -and (Has-Env 'GITHUB_PERSONAL_ACCESS_TOKEN')) {
  try {
    $out = & npx -y @modelcontextprotocol/server-github --version 2>&1
    Save-Text ($out | Out-String) (Join-Path $dest 'github.version.log')
  } catch { Save-Text $_.Exception.ToString() (Join-Path $dest 'github.version.error.log') }
}

if ($IncludeBrave -and $prereq.uvx -and (Has-Env 'BRAVE_API_KEY')) {
  try {
    $out = & uvx mcp-server-brave-search --help 2>&1
    Save-Text ($out | Out-String) (Join-Path $dest 'brave.help.log')
  } catch { Save-Text $_.Exception.ToString() (Join-Path $dest 'brave.help.error.log') }
}

if ($IncludeContext7 -and $prereq.uvx -and (Has-Env 'CONTEXT7_API_KEY')) {
  try {
    $out = & uvx mcp-server-context7 --help 2>&1
    Save-Text ($out | Out-String) (Join-Path $dest 'context7.help.log')
  } catch { Save-Text $_.Exception.ToString() (Join-Path $dest 'context7.help.error.log') }
}

if ($IncludeByterover -and (Has-Env 'BYTEROVER_API_KEY')) {
  # External health check already exists in test_mcp_servers.ps1; record env presence only
  Save-Json @{ byterover_key_present = $true } (Join-Path $dest 'byterover.env.json')
}

if ($IncludePlaywright -and $prereq.uvx) {
  try {
    $out = & uvx mcp-server-playwright --help 2>&1
    Save-Text ($out | Out-String) (Join-Path $dest 'playwright.help.log')
  } catch { Save-Text $_.Exception.ToString() (Join-Path $dest 'playwright.help.error.log') }
}

# 6) Summary
$summary = @{
  output_dir = $dest
  vault_api  = $VaultApiBase
  timestamp  = $stamp
}
Save-Json $summary (Join-Path $dest 'SUMMARY.json')

Write-Host "[MCP TEST] Complete. Artifacts in: $dest" -ForegroundColor Green

