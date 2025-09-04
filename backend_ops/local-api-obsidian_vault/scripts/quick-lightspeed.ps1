param(
  [switch]$SkipDocker
)

# Wrapper for ultra-fast startup of core stack
$script = Join-Path $PSScriptRoot 'quick-start.ps1'
& $script -LightSpeed:$true -SkipDocker:$SkipDocker

