# Enhanced Interactive CLI with Quick Launch and Custom Commands
param(
    [string]$Command = "",
    [string]$BaseUrl = "http://localhost:8080",
    [string]$ObsidianUrl = "http://localhost:27123",
    [switch]$Interactive = $false
)

$script:Config = @{
    BaseUrl = $BaseUrl
    ObsidianUrl = $ObsidianUrl
    Verbose = $false
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    $colors = @{"Red"="Red";"Green"="Green";"Yellow"="Yellow";"Blue"="Blue";"Cyan"="Cyan";"White"="White";"Gray"="Gray"}
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Write-Banner {
    Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔧 ENHANCED VAULT CLI 🔧                                 ║
║                   Advanced System Management                                 ║
║                      Quick Launch & Control                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ "Cyan"
}

function Invoke-QuickLaunch {
    Write-ColorOutput "🚀 Quick launching system..." "Blue"
    
    try {
        # Stop existing services
        Write-ColorOutput "🛑 Stopping existing services..." "Yellow"
        docker-compose down 2>$null
        
        # Start essential services
        Write-ColorOutput "🔨 Starting core services..." "Blue"
        docker-compose up -d obsidian-api postgres redis 2>$null
        
        Start-Sleep -Seconds 10
        
        # Test services
        $obsidianHealth = Test-ServiceHealth "Obsidian API" $script:Config.ObsidianUrl
        
        if ($obsidianHealth) {
            Write-ColorOutput "✅ Core system launched successfully!" "Green"
            Show-QuickStatus
        } else {
            Write-ColorOutput "⚠️ Partial launch - some services may need manual start" "Yellow"
        }
        
    } catch {
        Write-ColorOutput "❌ Launch failed: $($_.Exception.Message)" "Red"
    }
}

function Test-ServiceHealth {
    param([string]$Name, [string]$Url)
    
    try {
        $response = Invoke-RestMethod -Uri "$Url/health" -TimeoutSec 5
        Write-ColorOutput "✅ $Name`: HEALTHY" "Green"
        return $true
    } catch {
        Write-ColorOutput "❌ $Name`: FAILED" "Red"
        return $false
    }
}

function Show-QuickStatus {
    Write-ColorOutput "`n📊 QUICK STATUS:" "Cyan"
    
    # Test core services
    Test-ServiceHealth "Obsidian API" $script:Config.ObsidianUrl
    Test-ServiceHealth "Vault API" $script:Config.BaseUrl
    
    # Show vault info
    try {
        $vault = Invoke-RestMethod -Uri "$($script:Config.ObsidianUrl)/vault/info" -TimeoutSec 5
        Write-ColorOutput "📁 Vault: $($vault.markdownFiles) markdown files" "Blue"
    } catch {
        Write-ColorOutput "📁 Vault: Not accessible" "Red"
    }
    
    # Show containers
    Write-ColorOutput "`n🐳 Containers:" "Blue"
    docker ps --format "table {{.Names}}\t{{.Status}}" 2>$null
}

function Invoke-QuickTest {
    Write-ColorOutput "🧪 Running quick system test..." "Blue"
    
    $tests = @(
        @{Name="Obsidian API Health"; URL="$($script:Config.ObsidianUrl)/health"},
        @{Name="Vault Info"; URL="$($script:Config.ObsidianUrl)/vault/info"},
        @{Name="Brain Dump Files"; URL="$($script:Config.ObsidianUrl)scripts/les?path=brain_dump"}
    )
    
    $passed = 0
    foreach ($test in $tests) {
        try {
            $response = Invoke-RestMethod -Uri $test.URL -TimeoutSec 5
            Write-ColorOutput "✅ $($test.Name): PASS" "Green"
            $passed++
        } catch {
            Write-ColorOutput "❌ $($test.Name): FAIL" "Red"
        }
    }
    
    Write-ColorOutput "`n📊 Test Results: $passed/$($tests.Count) passed" "Cyan"
}

function Get-BrainDumpFiles {
    try {
        $files = Invoke-RestMethod -Uri "$($script:Config.ObsidianUrl)scripts/les?path=brain_dump" -TimeoutSec 5
        Write-ColorOutput "🧠 Brain Dump Files:" "Blue"
        $mdFiles = $files.files | Where-Object {$_.name -like "*.md"}
        foreach ($file in $mdFiles) {
            Write-ColorOutput "   📄 $($file.name)" "White"
        }
        Write-ColorOutput "`nTotal: $($mdFiles.Count) files" "Gray"
    } catch {
        Write-ColorOutput "❌ Failed to get brain dump files" "Red"
    }
}

function Read-AgentsFile {
    try {
        $agents = Invoke-RestMethod -Uri "$($script:Config.ObsidianUrl)scripts/les/AGENTS.md" -TimeoutSec 5
        Write-ColorOutput "🤖 AGENTS.md Content:" "Blue"
        Write-ColorOutput "─" * 50 "Gray"
        Write-ColorOutput $agents.content "White"
        Write-ColorOutput "─" * 50 "Gray"
    } catch {
        Write-ColorOutput "❌ Failed to read AGENTS.md" "Red"
    }
}

function New-DailyNote {
    $today = Get-Date -Format "yyyy-MM-dd"
    $content = @"
# Daily Note - $today

## 🎯 Goals
- [ ] 

## 📝 Notes


## 🔄 Tasks
- [ ] 

## 💭 Reflections


---
Created: $(Get-Date)
Tags: #daily
"@
    
    try {
        $body = @{path="daily/$today.md"; content=$content} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$($script:Config.ObsidianUrl)scripts/les" -Method POST -Body $body -ContentType "application/json"
        Write-ColorOutput "✅ Daily note created: daily/$today.md" "Green"
    } catch {
        Write-ColorOutput "❌ Failed to create daily note: $($_.Exception.Message)" "Red"
    }
}

function Show-SystemMetrics {
    Write-ColorOutput "📊 System Performance:" "Blue"
    
    # Test response times
    $times = @()
    for ($i = 1; $i -le 3; $i++) {
        try {
            $start = Get-Date
            Invoke-RestMethod -Uri "$($script:Config.ObsidianUrl)/health" -TimeoutSec 5 | Out-Null
            $duration = ((Get-Date) - $start).TotalMilliseconds
            $times += $duration
            Write-ColorOutput "   Test $i`: $([math]::Round($duration, 2))ms" "White"
        } catch {
            Write-ColorOutput "   Test $i`: FAILED" "Red"
        }
    }
    
    if ($times.Count -gt 0) {
        $avg = ($times | Measure-Object -Average).Average
        Write-ColorOutput "⚡ Average response: $([math]::Round($avg, 2))ms" "Green"
    }
}

function Start-EnhancedCLI {
    Write-Banner
    Write-ColorOutput "🎮 Enhanced CLI Mode - Type 'help' for all commands" "Green"
    Write-ColorOutput "💡 Quick start: 'launch' | scripts/' | 'status' | 'brain-dump'" "Yellow"
    
    while ($true) {
        try {
            Write-Host "`nVault> " -NoNewline -ForegroundColor "Cyan"
            $input = Read-Host
            if ([string]::IsNullOrWhiteSpace($input)) { continue }
            
            $parts = $input -split '\s+'
            $cmd = $parts[0].ToLower()
            $args = if ($parts.Length -gt 1) { $parts[1..($parts.Length-1)] } else { @() }
        
        switch ($cmd) {
            "help" {
                Write-ColorOutput @"

🚀 ENHANCED CLI COMMANDS:
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🎯 Quick Actions:                                                           │
│   launch                       - Quick launch system                        │
│   test                         - Run quick system test                      │
│   status                       - Show system status                         │
│   brain-dump                   - List brain dump files                      │
│   agents                       - Show AGENTS.md content                     │
│   daily                        - Create today's daily note                  │
│   metrics                      - Show performance metrics                   │
│                                                                             │
│ 🐳 Docker Control:                                                          │
│   start [service]              - Start service(s)                           │
│   stop [service]               - Stop service(s)                            │
│   restart [service]            - Restart service(s)                         │
│   ps                           - Show containers                            │
│   logs [service]               - Show logs                                  │
│                                                                             │
│ 📁 Vault Operations:                                                        │
│   vault-info                   - Get vault information                      │
│   list-files [folder]          - List files in folder                      │
│   read-file <path>             - Read file content                          │
│   search <query>               - Search vault content                       │
│                                                                             │
│ 🔧 System:                                                                  │
│   ports                        - Check port usage                           │
│   env                          - Show environment                           │
│   config <key> <value>         - Set configuration                          │
│   verbose                      - Toggle verbose mode                        │
│                                                                             │
│ 💡 Utilities:                                                               │
│   clear                        - Clear screen                               │
│   history                      - Show command history                       │
│   exit/quit/q                  - Exit CLI                                   │
└─────────────────────────────────────────────────────────────────────────────┘
"@ "Yellow"
            }
            
            "launch" { Invoke-QuickLaunch }
            scripts/" { Invoke-QuickTest }
            "status" { Show-QuickStatus }
            "brain-dump" { Get-BrainDumpFiles }
            "agents" { Read-AgentsFile }
            "daily" { New-DailyNote }
            "metrics" { Show-SystemMetrics }
            
            "start" {
                $service = if ($args.Count -gt 0) { $args[0] } else { "" }
                if ($service) {
                    Write-ColorOutput "🔄 Starting $service..." "Blue"
                    docker-compose up -d $service
                } else {
                    Write-ColorOutput "🔄 Starting all services..." "Blue"
                    docker-compose up -d
                }
            }
            
            "stop" {
                $service = if ($args.Count -gt 0) { $args[0] } else { "" }
                if ($service) {
                    Write-ColorOutput "🛑 Stopping $service..." "Yellow"
                    docker-compose stop $service
                } else {
                    Write-ColorOutput "🛑 Stopping all services..." "Yellow"
                    docker-compose down
                }
            }
            
            scripts/" {
                $service = if ($args.Count -gt 0) { $args[0] } else { "" }
                if ($service) {
                    Write-ColorOutput "🔄 Restarting $service..." "Blue"
                    docker-compose restart $service
                } else {
                    Write-ColorOutput "🔄 Restarting all services..." "Blue"
                    docker-compose restart
                }
            }
            
            "ps" {
                Write-ColorOutput "🐳 Running containers:" "Blue"
                docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            }
            
            logs/" {
                $service = if ($args.Count -gt 0) { $args[0] } else { "" }
                if ($service) {
                    Write-ColorOutput "📋 Logs for $service..." "Blue"
                    docker-compose logs -f $service
                } else {
                    Write-ColorOutput "📋 All logs..." "Blue"
                    docker-compose logs
                }
            }
            
            "vault-info" {
                try {
                    $vault = Invoke-RestMethod -Uri "$($script:Config.ObsidianUrl)/vault/info" -TimeoutSec 5
                    Write-ColorOutput "📁 Vault Information:" "Blue"
                    Write-ColorOutput "   Path: $($vault.path)" "White"
                    Write-ColorOutput "   Total Files: $($vault.totalFiles)" "White"
                    Write-ColorOutput "   Markdown Files: $($vault.markdownFiles)" "White"
                    Write-ColorOutput "   Last Modified: $($vault.lastModified)" "White"
                } catch {
                    Write-ColorOutput "❌ Failed to get vault info" "Red"
                }
            }
            
            "list-files" {
                $folder = if ($args.Count -gt 0) { $args[0] } else { "" }
                try {
                    $url = "$($script:Config.ObsidianUrl)scripts/les"
                    if ($folder) { $url += "?path=$folder" }
                    
                    $files = Invoke-RestMethod -Uri $url -TimeoutSec 5
                    Write-ColorOutput "📂 Files in $(if($folder){$folder}else{'root'}):" "Blue"
                    foreach ($file in $files.files) {
                        $icon = if ($file.isDirectory) { "📁" } else { "📄" }
                        Write-ColorOutput "   $icon $($file.name)" "White"
                    }
                } catch {
                    Write-ColorOutput "❌ Failed to list files" "Red"
                }
            }
            
            "read-file" {
                if ($args.Count -eq 0) {
                    Write-ColorOutput "Usage: read-file <path>" "Yellow"
                } else {
                    $filePath = $args[0]
                    try {
                        $file = Invoke-RestMethod -Uri "$($script:Config.ObsidianUrl)scripts/les/$filePath" -TimeoutSec 5
                        Write-ColorOutput "📄 $filePath" "Blue"
                        Write-ColorOutput "─" * 50 "Gray"
                        Write-ColorOutput $file.content "White"
                        Write-ColorOutput "─" * 50 "Gray"
                        Write-ColorOutput "Size: $($file.size) bytes" "Gray"
                    } catch {
                        Write-ColorOutput "❌ Failed to read file: $filePath" "Red"
                    }
                }
            }
            
            "search" {
                if ($args.Count -eq 0) {
                    Write-ColorOutput "Usage: search <query>" "Yellow"
                } else {
                    $query = $args -join " "
                    try {
                        $body = @{query=$query; caseSensitive=$false} | ConvertTo-Json
                        $results = Invoke-RestMethod -Uri "$($script:Config.ObsidianUrl)/vault/search" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
                        
                        Write-ColorOutput "🔍 Search results for '$query':" "Blue"
                        foreach ($result in $results.results) {
                            Write-ColorOutput "   📄 $($result.path) ($($result.matches) matches)" "White"
                        }
                        Write-ColorOutput "Total: $($results.total) results" "Gray"
                    } catch {
                        Write-ColorOutput "❌ Search failed" "Red"
                    }
                }
            }
            
            "ports" {
                Write-ColorOutput "🔌 Port Status:" "Blue"
                $ports = @(8080, 27123, 5678, 3000, 9090, 5432, 6379)
                foreach ($port in $ports) {
                    $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
                    $status = if ($connection) { "✅ IN USE" } else { "⚪ FREE" }
                    Write-ColorOutput "   Port $port`: $status" "White"
                }
            }
            
            "env" {
                Write-ColorOutput "🔧 Environment:" "Blue"
                Write-ColorOutput "   Base URL: $($script:Config.BaseUrl)" "White"
                Write-ColorOutput "   Obsidian URL: $($script:Config.ObsidianUrl)" "White"
                Write-ColorOutput "   Verbose: $($script:Config.Verbose)" "White"
            }
            
            config/" {
                if ($args.Count -eq 2) {
                    $key = $args[0].ToLower()
                    $value = $args[1]
                    
                    switch ($key) {
                        "baseurl" { 
                            $script:Config.BaseUrl = $value
                            Write-ColorOutput "✅ Base URL updated: $value" "Green"
                        }
                        "obsidianurl" { 
                            $script:Config.ObsidianUrl = $value
                            Write-ColorOutput "✅ Obsidian URL updated: $value" "Green"
                        }
                        default {
                            Write-ColorOutput "❌ Unknown config key: $key" "Red"
                        }
                    }
                } else {
                    Write-ColorOutput "Usage: config <key> <value>" "Yellow"
                    Write-ColorOutput "Keys: baseurl, obsidianurl" "Gray"
                }
            }
            
            "verbose" {
                $script:Config.Verbose = -not $script:Config.Verbose
                Write-ColorOutput "Verbose mode: $(if($script:Config.Verbose){'ON'}else{'OFF'})" "Yellow"
            }
            
            "history" {
                Write-ColorOutput "📜 Command History:" "Blue"
                Get-History | Select-Object -Last 10 | ForEach-Object {
                    Write-ColorOutput "   $($_.Id): $($_.CommandLine)" "White"
                }
            }
            
            "clear" { Clear-Host; Write-Banner }
            
            {$_ -in @("exit", "quit", "q")} {
                Write-ColorOutput "👋 Goodbye!" "Green"
                return
            }
            
            default {
                Write-ColorOutput "❌ Unknown command: $cmd" "Red"
                Write-ColorOutput "💡 Type 'help' for available commands" "Yellow"
            }
        } catch {
            Write-ColorOutput "❌ Error: $($_.Exception.Message)" "Red"
        }
    }
}

# Main execution
if ($Interactive -or $Command -eq "") {
    Start-EnhancedCLI
} else {
    # Execute single command
    switch ($Command.ToLower()) {
        "launch" { Invoke-QuickLaunch }
        scripts/" { Invoke-QuickTest }
        "status" { Show-QuickStatus }
        "brain-dump" { Get-BrainDumpFiles }
        "agents" { Read-AgentsFile }
        "daily" { New-DailyNote }
        "metrics" { Show-SystemMetrics }
        default {
            Write-ColorOutput "❌ Unknown command: $Command" "Red"
            Write-ColorOutput "Available: launch, test, status, brain-dump, agents, daily, metrics" "Yellow"
        }
    }
}