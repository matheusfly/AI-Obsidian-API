# Obsidian Vault AI CLI - Advanced Operations Tool
# Interactive command-line interface for vault operations and MCP tool calling

param(
    [string]$Command = "",
    [string]$Path = "",
    [string]$Content = "",
    [string]$Query = "",
    [string]$Tool = "",
    [hashtable]$Arguments = @{},
    [string]$ApiKey = "",
    [string]$BaseUrl = "http://localhost:8080",
    [switch]$Interactive = $false,
    [switch]$Verbose = $false
)

# Configuration
$script:Config = @{
    BaseUrl = $BaseUrl
    ApiKey = $ApiKey
    Verbose = $Verbose
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    $colors = @{
        Red = "Red"; Green = "Green"; Yellow = "Yellow"; Blue = "Blue"
        Cyan = "Cyan"; Magenta = "Magenta"; White = "White"; Gray = "Gray"
    }
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Write-Banner {
    Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔧 OBSIDIAN VAULT AI CLI 🔧                              ║
║                     Advanced Operations Tool                                ║
║                         MCP Tool Interface                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@ -Color "Cyan"
}

function Invoke-VaultAPI {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = @{},
        [hashtable]$Headers = @{}
    )
    
    $uri = "$($script:Config.BaseUrl)$Endpoint"
    $requestHeaders = @{
        "Content-Type" = "application/json"
    }
    
    if ($script:Config.ApiKey) {
        $requestHeaders["Authorization"] = "Bearer $($script:Config.ApiKey)"
    }
    
    foreach ($key in $Headers.Keys) {
        $requestHeaders[$key] = $Headers[$key]
    }
    
    try {
        $params = @{
            Uri = $uri
            Method = $Method
            Headers = $requestHeaders
            TimeoutSec = 30
        }
        
        if ($Body.Count -gt 0 -and $Method -ne "GET") {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        if ($script:Config.Verbose) {
            Write-ColorOutput "🔗 $Method $uri" -Color "Gray"
            if ($Body.Count -gt 0) {
                Write-ColorOutput "📤 Body: $($params.Body)" -Color "Gray"
            }
        }
        
        $response = Invoke-RestMethod @params
        
        if ($script:Config.Verbose) {
            Write-ColorOutput "📥 Response: $($response | ConvertTo-Json -Depth 3)" -Color "Gray"
        }
        
        return $response
    }
    catch {
        Write-ColorOutput "❌ API Error: $($_.Exception.Message)" -Color "Red"
        if ($_.Exception.Response) {
            Write-ColorOutput "   Status: $($_.Exception.Response.StatusCode)" -Color "Red"
        }
        return $null
    }
}

function Get-VaultHealth {
    Write-ColorOutput "🔍 Checking vault health..." -Color "Blue"
    
    $health = Invoke-VaultAPI -Endpoint "/health"
    if ($health) {
        Write-ColorOutput "✅ Vault Status: $($health.status)" -Color "Green"
        Write-ColorOutput "📊 Services:" -Color "Blue"
        
        foreach ($service in $health.services.PSObject.Properties) {
            $status = $service.Value
            $color = if ($status -eq "healthy" -or $status -eq "up") { "Green" } else { "Red" }
            Write-ColorOutput "   $($service.Name): $status" -Color $color
        }
        
        if ($health.mcp_tools) {
            Write-ColorOutput "🛠️  MCP Tools: $($health.mcp_tools.available) available" -Color "Cyan"
        }
        
        if ($health.vault) {
            Write-ColorOutput "📁 Vault Path: $($health.vault.path)" -Color "Blue"
            if ($health.vault.note_count) {
                Write-ColorOutput "📝 Notes: $($health.vault.note_count)" -Color "Blue"
            }
        }
    }
}

function Get-MCPTools {
    Write-ColorOutput "🛠️  Fetching MCP tools..." -Color "Blue"
    
    $tools = Invoke-VaultAPI -Endpoint "/api/v1/mcp/tools"
    if ($tools -and $tools.tools) {
        Write-ColorOutput "📋 Available MCP Tools ($($tools.total)):" -Color "Cyan"
        Write-Host ""
        
        foreach ($tool in $tools.tools) {
            Write-ColorOutput "🔧 $($tool.name)" -Color "Yellow"
            Write-ColorOutput "   $($tool.description)" -Color "White"
            
            if ($script:Config.Verbose -and $tool.parameters) {
                Write-ColorOutput "   Parameters:" -Color "Gray"
                if ($tool.parameters.properties) {
                    foreach ($param in $tool.parameters.properties.PSObject.Properties) {
                        $required = if ($tool.parameters.required -contains $param.Name) { " (required)" } else { "" }
                        Write-ColorOutput "     • $($param.Name): $($param.Value.type)$required" -Color "Gray"
                        if ($param.Value.description) {
                            Write-ColorOutput "       $($param.Value.description)" -Color "Gray"
                        }
                    }
                }
            }
            Write-Host ""
        }
    }
}

function Invoke-MCPTool {
    param(
        [string]$ToolName,
        [hashtable]$ToolArguments
    )
    
    Write-ColorOutput "🔧 Calling MCP tool: $ToolName" -Color "Blue"
    
    $body = @{
        tool = $ToolName
        arguments = $ToolArguments
    }
    
    $result = Invoke-VaultAPI -Endpoint "/api/v1/mcp/tools/call" -Method "POST" -Body $body
    
    if ($result) {
        if ($result.success) {
            Write-ColorOutput "✅ Tool executed successfully" -Color "Green"
            Write-ColorOutput "📤 Result:" -Color "Cyan"
            Write-ColorOutput ($result.result | ConvertTo-Json -Depth 5) -Color "White"
        } else {
            Write-ColorOutput "❌ Tool execution failed: $($result.error)" -Color "Red"
        }
    }
}

function Get-Notes {
    param(
        [string]$Folder = "",
        [int]$Limit = 20
    )
    
    $endpoint = "/api/v1/notes?limit=$Limit"
    if ($Folder) {
        $endpoint += "&folder=$Folder"
    }
    
    Write-ColorOutput "📝 Fetching notes..." -Color "Blue"
    
    $notes = Invoke-VaultAPI -Endpoint $endpoint
    if ($notes -and $notes.notes) {
        Write-ColorOutput "📋 Notes ($($notes.total) total):" -Color "Cyan"
        
        foreach ($note in $notes.notes) {
            Write-ColorOutput "📄 $note" -Color "White"
        }
    }
}

function Search-Notes {
    param(
        [string]$SearchQuery,
        [switch]$Semantic = $false,
        [int]$Limit = 10
    )
    
    Write-ColorOutput "🔍 Searching notes for: '$SearchQuery'" -Color "Blue"
    
    $body = @{
        query = $SearchQuery
        semantic = $Semantic.IsPresent
        limit = $Limit
    }
    
    $results = Invoke-VaultAPI -Endpoint "/api/v1/search" -Method "POST" -Body $body
    
    if ($results -and $results.results) {
        Write-ColorOutput "🎯 Search Results ($($results.results.Count)):" -Color "Cyan"
        
        foreach ($result in $results.results) {
            Write-ColorOutput "📄 $($result.path)" -Color "Yellow"
            if ($result.score) {
                Write-ColorOutput "   Score: $($result.score)" -Color "Gray"
            }
            if ($result.snippet) {
                Write-ColorOutput "   Snippet: $($result.snippet)" -Color "White"
            }
            Write-Host ""
        }
    } else {
        Write-ColorOutput "❌ No results found" -Color "Yellow"
    }
}

function New-Note {
    param(
        [string]$NotePath,
        [string]$NoteContent,
        [string[]]$Tags = @()
    )
    
    Write-ColorOutput "📝 Creating note: $NotePath" -Color "Blue"
    
    $body = @{
        path = $NotePath
        content = $NoteContent
        tags = $Tags
    }
    
    $result = Invoke-VaultAPI -Endpoint "/api/v1/notes" -Method "POST" -Body $body
    
    if ($result) {
        Write-ColorOutput "✅ Note created successfully" -Color "Green"
        Write-ColorOutput "📄 Path: $($result.path)" -Color "Cyan"
        if ($result.operation_id) {
            Write-ColorOutput "🔄 Operation ID: $($result.operation_id)" -Color "Gray"
        }
    }
}

function Get-Workflows {
    Write-ColorOutput "🔄 Fetching workflows..." -Color "Blue"
    
    $workflows = Invoke-VaultAPI -Endpoint "/api/v1/workflows"
    
    if ($workflows -and $workflows.workflows) {
        Write-ColorOutput "📋 Available Workflows:" -Color "Cyan"
        
        foreach ($workflow in $workflows.workflows) {
            $status = if ($workflow.active) { "✅ Active" } else { "⏸️  Inactive" }
            $color = if ($workflow.active) { "Green" } else { "Yellow" }
            Write-ColorOutput "🔄 $($workflow.name) ($($workflow.id)) - $status" -Color $color
        }
    }
}

function Start-InteractiveCLI {
    Write-Banner
    Write-ColorOutput "🎮 Interactive CLI Mode - Type 'help' for commands" -Color "Green"
    Write-ColorOutput "💡 Tip: Use config/' to set API key and base URL" -Color "Yellow"
    
    while ($true) {
        Write-Host "`nVault-CLI> " -NoNewline -ForegroundColor "Cyan"
        $input = Read-Host
        $parts = $input -split '\s+', 0, 'SimpleMatch'
        $cmd = $parts[0].ToLower()
        $args = $parts[1..($parts.Length-1)]
        
        switch ($cmd) {
            "help" {
                Write-ColorOutput @"

📋 Available Commands:
┌─────────────────────────────────────────────────────────────────────────────┐
│ System:                                                                     │
│   health                     - Check vault health                          │
│   config [key] [value]       - Set configuration (apikey, baseurl)         │
│   verbose                    - Toggle verbose mode                          │
│                                                                             │
│ Notes:                                                                      │
│   notes [folder] [limit]     - List notes                                  │
│   search <query> [semantic]  - Search notes                                │
│   create <path> <content>    - Create new note                             │
│   read <path>                - Read note content                           │
│                                                                             │
│ MCP Tools:                                                                  │
│   tools                      - List available MCP tools                    │
│   call <tool> [args...]      - Call MCP tool                               │
│                                                                             │
│ Workflows:                                                                  │
│   workflows                  - List workflows                              │
│                                                                             │
│ Examples:                                                                   │
│   search "machine learning"  - Search for ML content                       │
│   call read_file path=note.md - Read a file using MCP                      │
│   create daily/today.md "# Today" - Create daily note                      │
│                                                                             │
│ Utilities:                                                                  │
│   clear                      - Clear screen                                │
│   exit/quit                  - Exit CLI                                    │
└─────────────────────────────────────────────────────────────────────────────┘
"@ -Color "Yellow"
            }
            
            "health" { Get-VaultHealth }
            "tools" { Get-MCPTools }
            "workflows" { Get-Workflows }
            "verbose" { 
                $script:Config.Verbose = -not $script:Config.Verbose
                Write-ColorOutput "Verbose mode: $(if($script:Config.Verbose){'ON'}else{'OFF'})" -Color "Yellow"
            }
            
            config/" {
                if ($args.Count -eq 0) {
                    Write-ColorOutput "Current Configuration:" -Color "Cyan"
                    Write-ColorOutput "  Base URL: $($script:Config.BaseUrl)" -Color "White"
                    Write-ColorOutput "  API Key: $(if($script:Config.ApiKey){'Set'}else{'Not set'})" -Color "White"
                    Write-ColorOutput "  Verbose: $($script:Config.Verbose)" -Color "White"
                } elseif ($args.Count -eq 2) {
                    $key = $args[0].ToLower()
                    $value = $args[1]
                    
                    switch ($key) {
                        "apikey" { 
                            $script:Config.ApiKey = $value
                            Write-ColorOutput "✅ API Key updated" -Color "Green"
                        }
                        "baseurl" { 
                            $script:Config.BaseUrl = $value
                            Write-ColorOutput "✅ Base URL updated to: $value" -Color "Green"
                        }
                        default {
                            Write-ColorOutput "❌ Unknown config key: $key" -Color "Red"
                            Write-ColorOutput "Available keys: apikey, baseurl" -Color "Yellow"
                        }
                    }
                } else {
                    Write-ColorOutput "Usage: config [key] [value]" -Color "Yellow"
                }
            }
            
            "notes" {
                $folder = if ($args.Count -gt 0) { $args[0] } else { "" }
                $limit = if ($args.Count -gt 1) { [int]$args[1] } else { 20 }
                Get-Notes -Folder $folder -Limit $limit
            }
            
            "search" {
                if ($args.Count -eq 0) {
                    Write-ColorOutput "Usage: search <query> [semantic]" -Color "Yellow"
                } else {
                    $query = $args[0]
                    $semantic = ($args.Count -gt 1 -and $args[1] -eq "semantic")
                    Search-Notes -SearchQuery $query -Semantic:$semantic
                }
            }
            
            scripts/" {
                if ($args.Count -lt 2) {
                    Write-ColorOutput "Usage: create <path> <content> [tags...]" -Color "Yellow"
                } else {
                    $path = $args[0]
                    $content = $args[1]
                    $tags = if ($args.Count -gt 2) { $args[2..($args.Length-1)] } else { @() }
                    New-Note -NotePath $path -NoteContent $content -Tags $tags
                }
            }
            
            "read" {
                if ($args.Count -eq 0) {
                    Write-ColorOutput "Usage: read <path>" -Color "Yellow"
                } else {
                    $path = $args[0]
                    $note = Invoke-VaultAPI -Endpoint "/api/v1/notes/$path"
                    if ($note) {
                        Write-ColorOutput "📄 $($note.path)" -Color "Cyan"
                        Write-ColorOutput "─────────────────────────────────────" -Color "Gray"
                        Write-ColorOutput $note.content -Color "White"
                        Write-ColorOutput "─────────────────────────────────────" -Color "Gray"
                        if ($note.retrieved_at) {
                            Write-ColorOutput "Retrieved: $($note.retrieved_at)" -Color "Gray"
                        }
                    }
                }
            }
            
            "call" {
                if ($args.Count -eq 0) {
                    Write-ColorOutput "Usage: call <tool> [key=value...]" -Color "Yellow"
                } else {
                    $toolName = $args[0]
                    $toolArgs = @{}
                    
                    for ($i = 1; $i -lt $args.Count; $i++) {
                        if ($args[$i] -match '^(\w+)=(.+)$') {
                            $toolArgs[$matches[1]] = $matches[2]
                        }
                    }
                    
                    Invoke-MCPTool -ToolName $toolName -ToolArguments $toolArgs
                }
            }
            
            "clear" { Clear-Host; Write-Banner }
            
            {$_ -in @("exit", "quit", "q")} {
                Write-ColorOutput "👋 Goodbye!" -Color "Green"
                return
            }
            
            "" { continue }
            
            default {
                Write-ColorOutput "❌ Unknown command: $cmd" -Color "Red"
                Write-ColorOutput "💡 Type 'help' for available commands" -Color "Yellow"
            }
        }
    }
}

# Main execution
try {
    if ($Interactive -or $Command -eq "") {
        Start-InteractiveCLI
        exit 0
    }
    
    # Non-interactive command execution
    switch ($Command.ToLower()) {
        "health" { Get-VaultHealth }
        "tools" { Get-MCPTools }
        "notes" { Get-Notes -Folder $Path }
        "search" { 
            if (-not $Query) {
                Write-ColorOutput "❌ Query parameter required for search" -Color "Red"
                exit 1
            }
            Search-Notes -SearchQuery $Query 
        }
        scripts/" {
            if (-not $Path -or -not $Content) {
                Write-ColorOutput "❌ Path and Content parameters required for create" -Color "Red"
                exit 1
            }
            New-Note -NotePath $Path -NoteContent $Content
        }
        "call" {
            if (-not $Tool) {
                Write-ColorOutput "❌ Tool parameter required for call" -Color "Red"
                exit 1
            }
            Invoke-MCPTool -ToolName $Tool -ToolArguments $Arguments
        }
        "workflows" { Get-Workflows }
        default {
            Write-ColorOutput "❌ Unknown command: $Command" -Color "Red"
            Write-ColorOutput "Available commands: health, tools, notes, search, create, call, workflows" -Color "Yellow"
            exit 1
        }
    }
    
} catch {
    Write-ColorOutput "❌ CLI execution failed: $($_.Exception.Message)" -Color "Red"
    exit 1
}