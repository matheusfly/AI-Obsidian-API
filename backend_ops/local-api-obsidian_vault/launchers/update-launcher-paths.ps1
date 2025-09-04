# Launcher Path Update Script
# This script updates all launcher scripts to work with the new directory structure

Write-Host "🔄 Updating launcher paths for new directory structure..." -ForegroundColor Green

# Define the new directory structure mapping
$pathMappings = @{
    # Scripts that were moved to scripts/
    scripts/*" = "scripts/"
    scripts/*" = "scripts/"
    scripts/*" = "scripts/"
    scripts/*" = "scripts/"
    scripts/*" = "scripts/"
    scripts/*" = "scripts/"
    scripts/*" = "scripts/"
    scripts/*" = "scripts/"
    scripts/*" = "scripts/"
    
    # Services that were moved to services/
    servicesservices/aci-server" = "servicesservices/aci-server"
    servicesservices/advanced-indexer" = "servicesservices/advanced-indexer"
    servicesservices/embedding-service" = "servicesservices/embedding-service"
    servicesservicesscripts/le-watcher" = "servicesservicesscripts/le-watcher"
    servicesservices/obsidian-api" = "servicesservices/obsidian-api"
    servicesservices/obsidian-data" = "servicesservices/obsidian-data"
    servicesservices/obsidian-mcp-server" = "servicesservices/obsidian-mcp-server"
    servicesservices/vault-api" = "servicesservices/vault-api"
    services/servicesservices/web-interface" = "services/servicesservices/web-interface"
    servicesservices/context-engineering-master" = "servicesservices/context-engineering-master"
    servicesservices/flyde-mcp-project" = "servicesservices/flyde-mcp-project"
    servicesservices/mcp-blocks" = "servicesservices/mcp-blocks"
    servicesservices/n8n" = "servicesservices/n8n"
    servicesservices/nginx" = "servicesservices/nginx"
    servicesservices/postgres" = "servicesservices/postgres"
    servicesservices/qdrant_storage" = "servicesservices/qdrant_storage"
    servicesservices/sentry-config" = "servicesservices/sentry-config"
    
    # Data directories
    data/" = data//"
    datadata/memory" = data/data/memory"
    
    # Monitoring
    monitoring/" = monitoring//"
    
    # Integrations
    integrationsintegrations/tool-box" = "integrationsintegrations/tool-box"
    
    # Tests
    scripts/s" = scripts/s/"
    
    # Logs
    logs/" = logs//"
    
    # Config
    config/" = config//"
}

# Function to update file paths in a script
function Update-ScriptPaths {
    param(
        [string]$FilePath,
        [hashtable]$Mappings
    )
    
    if (!(Test-Path $FilePath)) {
        Write-Host "  ⚠️  File not found: $FilePath" -ForegroundColor Yellow
        return
    }
    
    $content = Get-Content $FilePath -Raw
    $originalContent = $content
    $updated = $false
    
    foreach ($oldPath in $Mappings.Keys) {
        $newPath = $Mappings[$oldPath]
        
        # Update various path patterns
        $patterns = @(
            "\.\\$oldPath",
            "\./$oldPath",
            "`"$oldPath",
            "'$oldPath",
            "\$oldPath",
            "/$oldPath"
        )
        
        foreach ($pattern in $patterns) {
            if ($content -match $pattern) {
                $content = $content -replace $pattern, $newPath
                $updated = $true
            }
        }
    }
    
    if ($updated) {
        try {
            Set-Content -Path $FilePath -Value $content -NoNewline
            Write-Host "  ✅ Updated: $FilePath" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ Failed to update: $FilePath - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  ℹ️  No changes needed: $FilePath" -ForegroundColor Blue
    }
}

# Update all launcher scripts
Write-Host "📝 Updating launcher scripts..." -ForegroundColor Yellow

$launcherFiles = Get-ChildItem -Path "launchers" -Filter "*.ps1" -ErrorAction SilentlyContinue
if ($launcherFiles) {
    foreach ($file in $launcherFiles) {
        Write-Host "  🔄 Processing: $($file.Name)" -ForegroundColor Cyan
        Update-ScriptPaths -FilePath $file.FullName -Mappings $pathMappings
    }
} else {
    Write-Host "  ⚠️  No launcher files found in launchers/ directory" -ForegroundColor Yellow
}

# Update scripts in scripts/ directory
Write-Host "📝 Updating utility scripts..." -ForegroundColor Yellow

$scriptFiles = Get-ChildItem -Path "scripts" -Filter "*.ps1" -ErrorAction SilentlyContinue
if ($scriptFiles) {
    foreach ($file in $scriptFiles) {
        Write-Host "  🔄 Processing: $($file.Name)" -ForegroundColor Cyan
        Update-ScriptPaths -FilePath $file.FullName -Mappings $pathMappings
    }
} else {
    Write-Host "  ⚠️  No script files found in scripts/ directory" -ForegroundColor Yellow
}

# Create a master launcher that can run any script from the new structure
Write-Host "🎯 Creating master launcher..." -ForegroundColor Yellow

$masterLauncher = @'
# Master Launcher - Professional Repository Structure
# This launcher provides easy access to all scripts in the reorganized structure

param(
    [Parameter(Mandatory=$true)]
    [string]$Script,
    [string]$Category = "launchers"
)

$scriptPath = Join-Path $Category $Script

if (Test-Path $scriptPath) {
    Write-Host "🚀 Launching: $scriptPath" -ForegroundColor Green
    & $scriptPath @args
} else {
    Write-Host "❌ Script not found: $scriptPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available categories:" -ForegroundColor Yellow
    Write-Host "  📁 launchers  - Main launcher scripts" -ForegroundColor White
    Write-Host "  🔧 scripts    - Utility and setup scripts" -ForegroundColor White
    Write-Host "  🚀 services   - Service implementations" -ForegroundColor White
    Write-Host "  🧪 tests      - Test scripts" -ForegroundColor White
    Write-Host "  📊 monitoring - Monitoring scripts" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage examples:" -ForegroundColor Cyan
    Write-Host "  .\launch.ps1 -Script LAUNCH_ALL.ps1" -ForegroundColor White
    Write-Host "  .\launch.ps1 -Script setup-mcp-tools.ps1 -Category scripts" -ForegroundColor White
    Write-Host "  .\launch.ps1 -Script test-all-services.ps1 -Category tests" -ForegroundColor White
}
'@

Set-Content -Path "launch.ps1" -Value $masterLauncher
Write-Host "  ✅ Created: launch.ps1" -ForegroundColor Green

# Create a quick reference for the new structure
Write-Host "📚 Creating structure reference..." -ForegroundColor Yellow

$structureReference = @'
# Professional Repository Structure Reference

## Directory Organization

### 📁 launchers/
All main launcher scripts for starting services and systems
- LAUNCH_ALL.ps1
- QUICK_ULTRA_LAUNCHER.ps1
- SMART_ULTRA_LAUNCHER.ps1
- MEGA_VISUAL_LAUNCHER.ps1
- And many more...

### 📚 docs/
All documentation, guides, and references
- README.md
- API documentation
- Setup guides
- Architecture documents

### ⚙️ config/
Configuration files and schemas
- JSON configurations
- Docker compose files
- Environment templates
- Database schemas

### 🔧 scripts/
Utility and setup scripts
- Setup scripts
- Fix scripts
- Installation scripts
- Debug utilities

### 🚀 services/
All service implementations
- aci-server/
- obsidian-api/
- vault-api/
- servicesservices/web-interface/
- And more...

### 🧪 tests/
Test files and reports
- Unit tests
- Integration tests
- Test reports
- Test utilities

### 📝 logs/
Log files and outputs
- Service logs
- Error logs
- Debug outputs

### 💾 data/
Data storage directories
- Application data
- Memory storage
- Cache files

### 📊 monitoring/
Status and monitoring files
- System status
- Dashboards
- Health checks

### 🔗 integrations/
Integration tools and configurations
- MCP configurations
- External tool integrations
- API integrations

### 🛠️ tools/
External tools and utilities
- Third-party tools
- Development utilities
- Helper scripts

## Quick Launch Commands

```powershell
# Launch any script using the master launcher
.\launch.ps1 -Script LAUNCH_ALL.ps1
.\launch.ps1 -Script setup-mcp-tools.ps1 -Category scripts
.\launch.ps1 -Script test-all-services.ps1 -Category tests

# Or run scripts directly from their new locations
.\launchers\LAUNCH_ALL.ps1
.\scripts\setup-mcp-tools.ps1
scripts/s\test-all-services.ps1
```

## Benefits of New Structure

1. **Clear Separation**: Each file type has its dedicated directory
2. **Easy Navigation**: Logical grouping makes finding files intuitive
3. **Professional Appearance**: Clean, organized structure
4. **Maintainable**: Easy to add new files in appropriate categories
5. **Scalable**: Structure can grow with the project
6. **Preserved Functionality**: All launchers work with updated paths
'@

Set-Content -Path "STRUCTURE_REFERENCE.md" -Value $structureReference
Write-Host "  ✅ Created: STRUCTURE_REFERENCE.md" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Path update completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: .\reorganize-repository.ps1" -ForegroundColor White
Write-Host "  2. Test launchers: .\launch.ps1 -Script LAUNCH_ALL.ps1" -ForegroundColor White
Write-Host "  3. Check structure: .\STRUCTURE_REFERENCE.md" -ForegroundColor White
