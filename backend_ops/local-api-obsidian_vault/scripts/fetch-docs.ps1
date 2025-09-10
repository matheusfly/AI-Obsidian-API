param(
  [string]$OutDir = "./docs/integrations"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$urls = @(
  # Motia
  'https://www.motia.dev/docs/getting-started/build-your-first-app',
  'https://www.motia.dev/docs/getting-started/quick-start',
  'https://github.com/MotiaDev/motia?tab=readme-ov-file',
  # Flyde
  'https://flyde.dev/',
  'https://flyde.dev/docs',
  'https://flyde.dev/docs/2-core-concepts',
  'https://flyde.dev/docs/3-built-in-nodes',
  'https://flyde.dev/docs/4-integrate-flows',
  'https://flyde.dev/docs/5-custom-nodes'
)

function New-DirIfMissing([string]$Path) {
  if (-not (Test-Path -Path $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

New-DirIfMissing -Path $OutDir
New-DirIfMissing -Path (Join-Path $OutDir 'motia')
New-DirIfMissing -Path (Join-Path $OutDir 'flyde')

function Get-SafeFileName([string]$url) {
  $uri = [System.Uri]$url
  $path = $uri.AbsolutePath.Trim('/') -replace '[^a-zA-Z0-9-_./]', '_'
  if ([string]::IsNullOrWhiteSpace($path)) { $path = 'index' }
  $file = ($path -replace '/', '_')
  if ($file.Length -gt 150) { $file = $file.Substring(0,150) }
  return "${($uri.Host)}_${file}.html"
}

Write-Host "Fetching docs to $OutDir ..."

foreach ($u in $urls) {
  try {
    $hostName = ([System.Uri]$u).Host
    $subdir = if ($hostName -like '*motia*') { 'motia' } elseif ($hostName -like '*flyde*') { 'flyde' } else { 'motia' }
    $targetDir = Join-Path $OutDir $subdir
    $fileName = Get-SafeFileName $u
    $targetPath = Join-Path $targetDir $fileName

    Write-Host ("- GET {0} -> {1}" -f $u, $targetPath)

    try {
      $resp = Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 60
      $content = $resp.Content
    } catch {
      Write-Warning "Invoke-WebRequest failed, trying curl.exe... ($_ )"
      $content = (& curl.exe -L -s $u)
    }

    Set-Content -Path $targetPath -Value $content -Encoding UTF8
  } catch {
    Write-Warning ("Failed to fetch {0}: {1}" -f $u, $_)
  }
}

Write-Host "Done. Files saved under $OutDir."

