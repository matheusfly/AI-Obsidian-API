param([switch]$Interactive = $false)

function Write-Color($msg, $color = "White") { Write-Host $msg -ForegroundColor $color }

function Test-Health($name, $url) {
    try {
        Invoke-RestMethod "$url/health" -TimeoutSec 3 | Out-Null
        Write-Color "✅ $name`: OK" "Green"
        return $true
    } catch {
        Write-Color "❌ $name`: FAIL" "Red"
        return $false
    }
}

function Show-Status {
    Write-Color "`n📊 STATUS:" "Cyan"
    Test-Health "Obsidian API" "http://localhost:27123"
    Test-Health "Vault API" "http://localhost:8080"
    docker ps --format "table {{.Names}}\t{{.Status}}"
}

function Start-CLI {
    Write-Color "🔧 VAULT CLI - Type 'help' for commands" "Green"
    
    while ($true) {
        Write-Host "`nVault> " -NoNewline -ForegroundColor Cyan
        $input = Read-Host
        
        switch ($input.ToLower()) {
            "help" {
                Write-Color @"
Commands:
  status    - Show system status
  launch    - Start core services
  test      - Quick health test
  agents    - Show AGENTS.md
  exit      - Exit CLI
"@ "Yellow"
            }
            "status" { Show-Status }
            "launch" {
                Write-Color "🚀 Starting services..." "Blue"
                docker-compose up -d obsidian-api postgres redis
                Start-Sleep 5
                Show-Status
            }
            scripts/" {
                Write-Color "🧪 Testing..." "Blue"
                Test-Health "Obsidian API" "http://localhost:27123"
            }
            "agents" {
                try {
                    $agents = Invoke-RestMethod "http://localhost:27123scripts/les/AGENTS.md" -TimeoutSec 5
                    Write-Color "🤖 AGENTS.md:" "Blue"
                    Write-Color $agents.content "White"
                } catch {
                    Write-Color "❌ Failed to read AGENTS.md" "Red"
                }
            }
            "exit" { Write-Color "👋 Goodbye!" "Green"; return }
            "" { continue }
            default { Write-Color "❌ Unknown: $input" "Red" }
        }
    }
}

if ($Interactive) { Start-CLI } else { Show-Status }