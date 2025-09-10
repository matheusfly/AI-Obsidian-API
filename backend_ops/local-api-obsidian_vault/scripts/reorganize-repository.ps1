# Professional Repository Reorganization Script
# This script reorganizes the repository into a professional structure
# while preserving all launcher functionality

Write-Host "🚀 Starting Professional Repository Reorganization..." -ForegroundColor Green

# Create the new directory structure
$directories = @(
    "launchers",
    "docs",
    "config", 
    "scripts",
    "services",
    "tests",
    "logs",
    "data",
    "monitoring",
    "integrations",
    "tools"
)

Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ℹ️  Already exists: $dir" -ForegroundColor Blue
    }
}

# File categorization mappings
$fileMappings = @{
    # Launcher scripts (all .ps1 files that contain "launch", "start", "run", "activate")
    "launchers" = @(
        "*launch*", "*start*", "*run*", "*activate*", "*continue*", "*force*",
        "LAUNCH_*", "START-*", "QUICK-*", "SMART_*", "MEGA_*", "ULTRA_*",
        "INTERACTIVE-*", "LIVE-*", "WORKING_*"
    )
    
    # Documentation files
    "docs" = @(
        "*.md", "*.txt", "*GUIDE*", "*REFERENCE*", "*MANUAL*", "*ROADMAP*",
        "*STATUS*", "*SUMMARY*", "*REPORT*", "*CHANGELOG*", "*README*"
    )
    
    # Configuration files
    "config" = @(
        "*.json", "*.yml", "*.yaml", "*.toml", "*.sql", "*.env*", "*config*",
        "pyproject.toml", "poetry.lock", "types.d.ts"
    )
    
    # Setup and utility scripts
    "scripts" = @(
        "setup*", "fix*", "install*", "create*", "restart*", "monitor*",
        "check*", "test*", "debug*", "plugins.ps1", "setup.sh"
    )
    
    # Service implementations
    "services" = @(
        "aci-server", "advanced-indexer", "embedding-service", "file-watcher",
        "obsidian-api", "obsidian-data", "obsidian-mcp-server", "vault-api",
        "web-interface", "context-engineering-master", "flyde-mcp-project",
        "mcp-blocks", "n8n", "nginx", "postgres", "qdrant_storage", "sentry-config"
    )
    
    # Test files
    "tests" = @(
        "test*", "*test*", "tests", "*TEST*", "*integration-test*"
    )
    
    # Log files
    "logs" = @(
        "*.log", "logs", "server_*"
    )
    
    # Data storage
    "data" = @(
        "data", "memory", "obsidian-data"
    )
    
    # Monitoring and status
    "monitoring" = @(
        "monitoring", "*STATUS*", "*DASHBOARD*", "*MINDMAP*"
    )
    
    # Integration tools
    "integrations" = @(
        "tool-box", "tools"
    )
}

Write-Host "📋 Categorizing and moving files..." -ForegroundColor Yellow

# Get all files in root directory
$rootFiles = Get-ChildItem -Path "." -File | Where-Object { $_.Name -notlike "reorganize-repository.ps1" }

foreach ($file in $rootFiles) {
    $moved = $false
    
    foreach ($category in $fileMappings.Keys) {
        foreach ($pattern in $fileMappings[$category]) {
            if ($file.Name -like $pattern) {
                $destination = Join-Path $category $file.Name
                try {
                    Move-Item -Path $file.FullName -Destination $destination -Force
                    Write-Host "  ✅ Moved: $($file.Name) → $category/" -ForegroundColor Green
                    $moved = $true
                    break
                } catch {
                    Write-Host "  ❌ Failed to move: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        }
        if ($moved) { break }
    }
    
    if (-not $moved) {
        Write-Host "  ⚠️  Unmoved: $($file.Name) - needs manual categorization" -ForegroundColor Yellow
    }
}

# Move directories
Write-Host "📁 Moving directories..." -ForegroundColor Yellow

$directoryMappings = @{
    "services" = @("aci-server", "advanced-indexer", "embedding-service", "file-watcher", "obsidian-api", "obsidian-data", "obsidian-mcp-server", "vault-api", "web-interface", "context-engineering-master", "flyde-mcp-project", "mcp-blocks", "n8n", "nginx", "postgres", "qdrant_storage", "sentry-config")
    "data" = @("data", "memory")
    "monitoring" = @("monitoring")
    "integrations" = @("tool-box")
    "tests" = @("tests")
    "logs" = @("logs")
    "config" = @("config")
}

foreach ($category in $directoryMappings.Keys) {
    foreach ($dirName in $directoryMappings[$category]) {
        if (Test-Path $dirName) {
            $destination = Join-Path $category $dirName
            try {
                Move-Item -Path $dirName -Destination $destination -Force
                Write-Host "  ✅ Moved directory: $dirName → $category/" -ForegroundColor Green
            } catch {
                Write-Host "  ❌ Failed to move directory: $dirName - $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}

Write-Host "🎯 Reorganization completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  📁 Launchers: All .ps1 launcher scripts" -ForegroundColor White
Write-Host "  📚 Docs: All documentation and guides" -ForegroundColor White
Write-Host "  ⚙️  Config: Configuration files and schemas" -ForegroundColor White
Write-Host "  🔧 Scripts: Setup and utility scripts" -ForegroundColor White
Write-Host "  🚀 Services: All service implementations" -ForegroundColor White
Write-Host "  🧪 Tests: Test files and reports" -ForegroundColor White
Write-Host "  📝 Logs: Log files and outputs" -ForegroundColor White
Write-Host "  💾 Data: Data storage directories" -ForegroundColor White
Write-Host "  📊 Monitoring: Status and monitoring files" -ForegroundColor White
Write-Host "  🔗 Integrations: Integration tools and configs" -ForegroundColor White
Write-Host "  🛠️  Tools: External tools and utilities" -ForegroundColor White

