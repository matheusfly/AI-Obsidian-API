# Quick Launch Script - Start System and Make First API Call
param(
    [switch]$SkipDocker = $false,
    [switch]$TestOnly = $false
)

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    $colors = @{"Green"="Green";"Red"="Red";"Yellow"="Yellow";"Blue"="Blue";"Cyan"="Cyan"}
    Write-Host $Message -ForegroundColor $colors[$Color]
}

function Test-ServiceHealth {
    param([string]$Name, [string]$URL)
    try {
        $response = Invoke-RestMethod -Uri $URL -TimeoutSec 5
        Write-Status "✅ $Name is healthy" "Green"
        return $true
    } catch {
        Write-Status "❌ $Name is not responding" "Red"
        return $false
    }
}

Write-Status "🚀 OBSIDIAN VAULT AI - QUICK LAUNCH" "Cyan"
Write-Status "=" * 50 "Blue"

if (-not $SkipDocker) {
    Write-Status "🐳 Starting Docker services..." "Blue"
    docker-compose up -d --build
    
    Write-Status "⏳ Waiting for services to start..." "Yellow"
    Start-Sleep -Seconds 20
}

Write-Status "🔍 Testing service health..." "Blue"

$services = @(
    @{Name="Vault API"; URL="http://localhost:8080/health"},
    @{Name="Obsidian API"; URL="http://localhost:27123/health"}
)

$healthyServices = 0
foreach ($service in $services) {
    if (Test-ServiceHealth $service.Name $service.URL) {
        $healthyServices++
    }
}

if ($healthyServices -eq 0) {
    Write-Status "❌ No services are responding. Starting minimal setup..." "Red"
    
    # Start just the essential services
    Write-Status "🔧 Starting core services only..." "Yellow"
    docker-compose up -d vault-api obsidian-api postgres redis
    Start-Sleep -Seconds 15
}

Write-Status "`n🎯 MAKING FIRST API CALLS..." "Cyan"
Write-Status "=" * 50 "Blue"

# Test 1: Vault API Health
Write-Status "📡 Testing Vault API..." "Blue"
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8080/health"
    Write-Status "✅ Vault API Response: $($health.status)" "Green"
} catch {
    Write-Status "❌ Vault API failed: $($_.Exception.Message)" "Red"
}

# Test 2: Obsidian API Health  
Write-Status "📡 Testing Obsidian API..." "Blue"
try {
    $health = Invoke-RestMethod -Uri "http://localhost:27123/health"
    Write-Status "✅ Obsidian API Response: $($health.status)" "Green"
} catch {
    Write-Status "❌ Obsidian API failed: $($_.Exception.Message)" "Red"
}

# Test 3: Vault Info
Write-Status "📂 Getting vault information..." "Blue"
try {
    $vaultInfo = Invoke-RestMethod -Uri "http://localhost:27123/vault/info"
    Write-Status "✅ Vault Path: $($vaultInfo.path)" "Green"
    Write-Status "✅ Total Files: $($vaultInfo.totalFiles)" "Green"
    Write-Status "✅ Markdown Files: $($vaultInfo.markdownFiles)" "Green"
} catch {
    Write-Status "❌ Vault info failed: $($_.Exception.Message)" "Red"
}

# Test 4: List Files in brain_dump
Write-Status "📋 Listing files in brain_dump folder..." "Blue"
try {
    $files = Invoke-RestMethod -Uri "http://localhost:27123scripts/les?path=brain_dump"
    $mdFiles = $files.files | Where-Object { $_.name -like "*.md" }
    Write-Status "✅ Found $($mdFiles.Count) markdown files in brain_dump" "Green"
    
    if ($mdFiles.Count -gt 0) {
        Write-Status "📄 Sample files:" "Blue"
        $mdFiles | Select-Object -First 3 | ForEach-Object {
            Write-Status "   • $($_.name)" "White"
        }
    }
} catch {
    Write-Status "❌ File listing failed: $($_.Exception.Message)" "Red"
}

# Test 5: Read a specific file (AGENTS.md)
Write-Status "📖 Reading AGENTS.md file..." "Blue"
try {
    $agentsFile = Invoke-RestMethod -Uri "http://localhost:27123scripts/les/AGENTS.md"
    $contentPreview = $agentsFile.content.Substring(0, [Math]::Min(200, $agentsFile.content.Length))
    Write-Status "✅ AGENTS.md loaded successfully" "Green"
    Write-Status "📝 Content preview: $contentPreview..." "White"
    Write-Status "📊 File size: $($agentsFile.size) bytes" "Blue"
} catch {
    Write-Status "❌ AGENTS.md read failed: $($_.Exception.Message)" "Red"
}

# Test 6: MCP Tools (if vault-api is running)
Write-Status "🛠️ Testing MCP Tools..." "Blue"
try {
    $tools = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools"
    Write-Status "✅ MCP Tools available: $($tools.total)" "Green"
    
    if ($tools.tools.Count -gt 0) {
        Write-Status "🔧 Available tools:" "Blue"
        $tools.tools | Select-Object -First 5 | ForEach-Object {
            Write-Status "   • $($_.name): $($_.description)" "White"
        }
    }
} catch {
    Write-Status "❌ MCP Tools failed: $($_.Exception.Message)" "Red"
}

# Test 7: MCP Tool Call - List Files
Write-Status "🔧 Testing MCP Tool Call..." "Blue"
try {
    $toolCall = @{
        tool = "list_files"
        arguments = @{
            path = "brain_dump"
            pattern = "*.md"
        }
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/mcp/tools/call" -Method POST -Body $toolCall -ContentType "application/json"
    
    if ($result.success) {
        Write-Status "✅ MCP Tool call successful" "Green"
        Write-Status "📋 Files found: $($result.result.Count)" "Blue"
    } else {
        Write-Status "❌ MCP Tool call failed: $($result.error)" "Red"
    }
} catch {
    Write-Status "❌ MCP Tool call error: $($_.Exception.Message)" "Red"
}

Write-Status "`n🎉 FIRST API CALLS COMPLETE!" "Cyan"
Write-Status "=" * 50 "Blue"

Write-Status "🌐 Your system is ready! Access points:" "Green"
Write-Status "   • Vault API: http://localhost:8080" "White"
Write-Status "   • API Docs: http://localhost:8080/docs" "White"
Write-Status "   • Obsidian API: http://localhost:27123" "White"

Write-Status "`n🧪 Next steps:" "Yellow"
Write-Status "   • Test interactive CLI: .\scripts\vault-cli.ps1 -Interactive" "White"
Write-Status "   • Run full tests: scripts/s\run-all-tests.ps1" "White"
Write-Status "   • Check logs: docker-compose logs -f" "White"