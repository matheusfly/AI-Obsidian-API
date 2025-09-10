# Quick Commands for Obsidian Vault AI System
# Usage: .\quick-commands.ps1 <command> [args]

param(
    [Parameter(Position=0)]
    [string]$Action = "help",
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$ObsidianUrl = "http://localhost:27123"
$VaultUrl = "http://localhost:8080"

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    $colors = @{"Green"="Green";"Red"="Red";"Yellow"="Yellow";"Blue"="Blue";"Cyan"="Cyan"}
    Write-Host $Message -ForegroundColor $colors[$Color]
}

switch ($Action.ToLower()) {
    "help" {
        Write-Status @"
🚀 QUICK COMMANDS:

System Control:
  .\quick-commands.ps1 launch          - Quick launch system
  .\quick-commands.ps1 status          - Show system status
  .\quick-commands.ps1 test            - Run quick test
  .\quick-commands.ps1 stop            - Stop all services

Vault Operations:
  .\quick-commands.ps1 vault-info      - Get vault information
  .\quick-commands.ps1 brain-dump      - List brain dump files
  .\quick-commands.ps1 agents          - Show AGENTS.md
  .\quick-commands.ps1 daily           - Create daily note
  .\quick-commands.ps1 search <query>  - Search vault

File Operations:
  .\quick-commands.ps1 read <file>     - Read file content
  .\quick-commands.ps1 list [folder]   - List files

System Info:
  .\quick-commands.ps1 ports           - Check port usage
  .\quick-commands.ps1 containers      - Show containers
  .\quick-commands.ps1 logs [service]  - Show logs

Dev:
  .\\quick-commands.ps1 motia-dev       - Start Motia dev server (obsidian-api) on port 27123
  .\\quick-commands.ps1 flyde-dev       - Start Flyde dev studio on port 3001
  .\\quick-commands.ps1 dev-all         - Launch Motia & Flyde dev servers

Interactive:
  .\enhanced-cli.ps1 -Interactive      - Start full CLI
"@ "Cyan"
    }
    
    "launch" {
        Write-Status "🚀 Quick launching system..." "Blue"
        docker-compose up -d obsidian-api postgres redis 2>$null
        Start-Sleep -Seconds 10
        
        try {
            $health = Invoke-RestMethod "$ObsidianUrl/health" -TimeoutSec 5
            Write-Status "✅ System launched successfully!" "Green"
        } catch {
            Write-Status "⚠️ Launch completed but services may still be starting" "Yellow"
        }
    }
    
    "status" {
        Write-Status "📊 System Status:" "Blue"
        
        # Test services
        try {
            Invoke-RestMethod "$ObsidianUrl/health" -TimeoutSec 3 | Out-Null
            Write-Status "✅ Obsidian API: HEALTHY" "Green"
        } catch {
            Write-Status "❌ Obsidian API: DOWN" "Red"
        }
        
        try {
            Invoke-RestMethod "$VaultUrl/health" -TimeoutSec 3 | Out-Null
            Write-Status "✅ Vault API: HEALTHY" "Green"
        } catch {
            Write-Status "❌ Vault API: DOWN" "Red"
        }
        
        # Show containers
        Write-Status "`n🐳 Containers:" "Blue"
        docker ps --format "table {{.Names}}\t{{.Status}}" 2>$null
    }
    
    scripts/" {
        Write-Status "🧪 Running quick test..." "Blue"
        
        $tests = @(
            @{Name="Obsidian API"; URL="$ObsidianUrl/health"},
            @{Name="Vault Info"; URL="$ObsidianUrl/vault/info"}
        )
        
        foreach ($test in $tests) {
            try {
                Invoke-RestMethod $test.URL -TimeoutSec 5 | Out-Null
                Write-Status "✅ $($test.Name): PASS" "Green"
            } catch {
                Write-Status "❌ $($test.Name): FAIL" "Red"
            }
        }
    }
    
    "stop" {
        Write-Status "🛑 Stopping all services..." "Yellow"
        docker-compose down 2>$null
        Write-Status "✅ Services stopped" "Green"
    }
    
    "vault-info" {
        try {
            $vault = Invoke-RestMethod "$ObsidianUrl/vault/info" -TimeoutSec 5
            Write-Status "📁 Vault Information:" "Blue"
            Write-Status "   Total Files: $($vault.totalFiles)" "White"
            Write-Status "   Markdown Files: $($vault.markdownFiles)" "White"
            Write-Status "   Path: $($vault.path)" "White"
        } catch {
            Write-Status "❌ Failed to get vault info" "Red"
        }
    }
    
    "brain-dump" {
        try {
            $files = Invoke-RestMethod "$ObsidianUrlscripts/les?path=brain_dump" -TimeoutSec 5
            Write-Status "🧠 Brain Dump Files:" "Blue"
            $files.files | Where-Object {$_.name -like "*.md"} | ForEach-Object {
                Write-Status "   📄 $($_.name)" "White"
            }
        } catch {
            Write-Status "❌ Failed to get brain dump files" "Red"
        }
    }
    
    "agents" {
        try {
            $agents = Invoke-RestMethod "$ObsidianUrlscripts/les/AGENTS.md" -TimeoutSec 5
            Write-Status "🤖 AGENTS.md:" "Blue"
            Write-Status "─" * 50 "Gray"
            Write-Status $agents.content "White"
        } catch {
            Write-Status "❌ Failed to read AGENTS.md" "Red"
        }
    }
    
    "daily" {
        $today = Get-Date -Format "yyyy-MM-dd"
        $content = "# Daily Note - $today`n`n## Goals`n- [ ] `n`n## Notes`n`n## Tasks`n- [ ] `n`n## Reflections`n"
        
        try {
            $body = @{path="daily/$today.md"; content=$content} | ConvertTo-Json
            Invoke-RestMethod "$ObsidianUrlscripts/les" -Method POST -Body $body -ContentType "application/json" | Out-Null
            Write-Status "✅ Daily note created: daily/$today.md" "Green"
        } catch {
            Write-Status "❌ Failed to create daily note" "Red"
        }
    }
    
    "search" {
        if ($Args.Count -eq 0) {
            Write-Status "Usage: search <query>" "Yellow"
        } else {
            $query = $Args -join " "
            try {
                $body = @{query=$query; caseSensitive=$false} | ConvertTo-Json
                $results = Invoke-RestMethod "$ObsidianUrl/vault/search" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
                
                Write-Status "🔍 Search results for '$query':" "Blue"
                foreach ($result in $results.results) {
                    Write-Status "   📄 $($result.path)" "White"
                }
                Write-Status "Total: $($results.total) results" "Gray"
            } catch {
                Write-Status "❌ Search failed" "Red"
            }
        }
    }
    
    "read" {
        if ($Args.Count -eq 0) {
            Write-Status "Usage: read <file>" "Yellow"
        } else {
            $filePath = $Args[0]
            try {
                $file = Invoke-RestMethod "$ObsidianUrlscripts/les/$filePath" -TimeoutSec 5
                Write-Status "📄 $filePath" "Blue"
                Write-Status "─" * 50 "Gray"
                Write-Status $file.content "White"
            } catch {
                Write-Status "❌ Failed to read file: $filePath" "Red"
            }
        }
    }
    
    "list" {
        $folder = if ($Args.Count -gt 0) { $Args[0] } else { "" }
        try {
            $url = "$ObsidianUrlscripts/les"
            if ($folder) { $url += "?path=$folder" }
            
            $files = Invoke-RestMethod $url -TimeoutSec 5
            Write-Status "📂 Files in $(if($folder){$folder}else{'root'}):" "Blue"
            foreach ($file in $files.files) {
                $icon = if ($file.isDirectory) { "📁" } else { "📄" }
                Write-Status "   $icon $($file.name)" "White"
            }
        } catch {
            Write-Status "❌ Failed to list files" "Red"
        }
    }
    
    "ports" {
        Write-Status "🔌 Port Status:" "Blue"
        $ports = @(8080, 27123, 5678, 3000)
        foreach ($port in $ports) {
            $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
            $status = if ($connection) { "✅ IN USE" } else { "⚪ FREE" }
            Write-Status "   Port $port`: $status" "White"
        }
    }
    
    "containers" {
        Write-Status "🐳 Docker Containers:" "Blue"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
    }
    
    logs/" {
        $service = if ($Args.Count -gt 0) { $Args[0] } else { "" }
        if ($service) {
            Write-Status "📋 Logs for ${service}:" "Blue"
            docker-compose logs $service 2>$null
        } else {
            Write-Status "📋 All service logs:" "Blue"
            docker-compose logs 2>$null
        }
    }
    
    "motia-dev" {
Write-Status "🔧 Starting Motia dev server (obsidian-api) on port 27123..." "Blue"
        try {
            $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
            $obsidianApiPath = Join-Path $repoRoot servicesservices/obsidian-api"
            if (-not (Test-Path $obsidianApiPath)) {
                Write-Status "❌ obsidian-api directory not found at: $obsidianApiPath" "Red"
                break
            }
            $port = 27123
            $inUse = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
            if ($inUse) {
                Write-Status "⚠️ Port $port is already in use. The dev server may fail to start." "Yellow"
            }
            Push-Location $obsidianApiPath
            try {
                # Run in current session so logs are visible; press Ctrl+C to stop
                & npx motia dev --port 27123
            } catch {
                Write-Status "❌ Failed to start Motia dev server: $($_.Exception.Message)" "Red"
            } finally {
                Pop-Location
            }
        } catch {
            Write-Status "❌ Unexpected error: $($_.Exception.Message)" "Red"
        }
    }
    
    "flyde-dev" {
        Write-Status "🎨 Starting Flyde dev studio on port 3001..." "Blue"
        try {
            $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
            $flydePath = Join-Path $repoRoot "flyde-project"
            if (-not (Test-Path $flydePath)) {
                Write-Status "❌ flyde-project directory not found at: $flydePath" "Red"
                break
            }
            $port = 3001
            $inUse = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
            if ($inUse) { Write-Status "⚠️ Port $port is already in use." "Yellow" }
            Push-Location $flydePath
            try {
                & npx ts-node src/server.ts
            } catch {
                Write-Status "❌ Failed to start Flyde studio: $($_.Exception.Message)" "Red"
            } finally { Pop-Location }
        } catch { Write-Status "❌ Unexpected error: $($_.Exception.Message)" "Red" }
    }

    "dev-all" {
Write-Status "🚀 Launching Motia and Flyde dev servers..." "Blue"
        Start-Job -ScriptBlock { & powershell -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot/quick-commands.ps1" motia-dev }
        Start-Job -ScriptBlock { & powershell -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot/quick-commands.ps1" flyde-dev }
        Write-Status "⌛ Servers launching in background jobs. Use 'jobs' to list." "Green"
    }
    
    default {
        Write-Status "❌ Unknown command: $Action" "Red"
        Write-Status "💡 Use 'help' to see available commands" "Yellow"
    }
}