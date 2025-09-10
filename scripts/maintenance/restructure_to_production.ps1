# Production Repository Restructuring Script
# This script restructures the repository to production-grade architecture

param(
    [switch]$DryRun = $false,
    [switch]$Detailed = $false,
    [switch]$Backup = $true
)

Write-Host "🏗️ PRODUCTION REPOSITORY RESTRUCTURING" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be moved" -ForegroundColor Yellow
}

# Create backup if requested
if ($Backup -and -not $DryRun) {
    $BackupDir = "backup_restructure_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "`n📦 Creating backup: $BackupDir" -ForegroundColor Yellow
    Copy-Item -Path "." -Destination $BackupDir -Recurse -Exclude "backup_*", "temp", "logs", "__pycache__"
    Write-Host "  ✅ Backup created successfully" -ForegroundColor Green
}

# Define new production structure
$NewStructure = @{
    "src" = @{
        "presentation" = @{
            "api" = @{
                "v1" = @{
                    "auth" = "Authentication endpoints"
                    "obsidian" = "Obsidian integration endpoints"
                    "langgraph" = "LangGraph endpoints"
                    "mcp" = "MCP endpoints"
                }
                "middleware" = "API middleware"
            }
            "web" = @{
                "dashboard" = "Monitoring dashboard"
                "studio" = "LangGraph Studio interface"
                "admin" = "Admin interface"
            }
            "cli" = @{
                "commands" = "CLI commands"
                "utils" = "CLI utilities"
            }
        }
        "application" = @{
            "use_cases" = @{
                "obsidian" = "Obsidian-related use cases"
                "langgraph" = "LangGraph-related use cases"
                "mcp" = "MCP-related use cases"
                "monitoring" = "Monitoring use cases"
            }
            "services" = "Application services"
            "dto" = "Data Transfer Objects"
            "interfaces" = "Service interfaces"
        }
        "domain" = @{
            "entities" = @{
                "obsidian" = "Obsidian entities"
                "langgraph" = "LangGraph entities"
                "mcp" = "MCP entities"
            }
            "value_objects" = "Value objects"
            "repositories" = "Repository interfaces"
            "services" = "Domain services"
        }
        "infrastructure" = @{
            "persistence" = @{
                "repositories" = "Repository implementations"
                "models" = "Database models"
                "migrations" = "Database migrations"
            }
            "external" = @{
                "obsidian" = "Obsidian API client"
                "langgraph" = "LangGraph API client"
                "langsmith" = "LangSmith client"
                "mcp" = "MCP clients"
            }
            "messaging" = "Message queues and events"
            "monitoring" = "Monitoring and observability"
            "config" = "Configuration management"
        }
    }
    "services" = @{
        "obsidian-service" = "Obsidian microservice"
        "langgraph-service" = "LangGraph microservice"
        "mcp-service" = "MCP microservice"
        "monitoring-service" = "Monitoring microservice"
        "api-gateway" = "API Gateway service"
    }
    "apps" = @{
        "web-app" = "Web application"
        "studio-app" = "LangGraph Studio app"
        "dashboard-app" = "Monitoring dashboard app"
        "cli-app" = "CLI application"
    }
    "infrastructure" = @{
        "docker" = @{
            "base" = "Base images"
            "services" = "Service images"
            "apps" = "Application images"
        }
        "kubernetes" = "Kubernetes manifests"
        "terraform" = "Terraform configurations"
        "monitoring" = "Monitoring configurations"
    }
    "tests" = @{
        "unit" = "Unit tests"
        "integration" = "Integration tests"
        "e2e" = "End-to-end tests"
        "performance" = "Performance tests"
        "fixtures" = "Test fixtures"
    }
    "docs" = @{
        "architecture" = "Architecture documentation"
        "api" = "API documentation"
        "deployment" = "Deployment guides"
        "development" = "Development guides"
        "user" = "User documentation"
    }
    "scripts" = @{
        "build" = "Build scripts"
        "deploy" = "Deployment scripts"
        "test" = "Test scripts"
        "maintenance" = "Maintenance scripts"
        "dev" = "Development scripts"
    }
    "tools" = @{
        "linting" = "Linting tools"
        "formatting" = "Code formatting tools"
        "testing" = "Testing tools"
        "monitoring" = "Monitoring tools"
    }
    "data" = @{
        "raw" = "Raw data"
        "processed" = "Processed data"
        "cache" = "Cache data"
        "backups" = "Backup data"
    }
    "logs" = @{
        "application" = "Application logs"
        "system" = "System logs"
        "audit" = "Audit logs"
    }
    "temp" = @{
        "development" = "Development temp files"
        "testing" = "Testing temp files"
        "build" = "Build temp files"
    }
}

# Function to create directory structure
function New-DirectoryStructure {
    param([hashtable]$Structure, [string]$BasePath = ".")
    
    foreach ($item in $Structure.GetEnumerator()) {
        $path = Join-Path $BasePath $item.Key
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
            Write-Host "  ✅ Created: $path" -ForegroundColor Green
        }
        
        if ($item.Value -is [hashtable]) {
            New-DirectoryStructure -Structure $item.Value -BasePath $path
        }
    }
}

# Function to move files to new structure
function Move-FilesToNewStructure {
    param([switch]$DryRun)
    
    $FileMappings = @{
        # API Gateway → src/presentation/api/v1/
        "api_gateway" = "src/presentation/api/v1/obsidian"
        
        # Core Services → src/infrastructure/external/
        "core_services" = "src/infrastructure/external/langgraph"
        
        # MCP Tools → services/mcp-service/src/
        "mcp_tools" = "services/mcp-service/src"
        
        # LangGraph Workflows → src/application/use_cases/langgraph/
        "langgraph_workflows" = "src/application/use_cases/langgraph"
        
        # Monitoring Tools → services/monitoring-service/src/
        "monitoring_tools" = "services/monitoring-service/src"
        
        # Test Suites → tests/
        "test_suites" = "tests/integration"
        "tests" = "tests/unit"
        
        # Documentation → docs/
        "docs" = "docs/architecture"
        "documentation" = "docs/development"
        
        # Deployment → scripts/deploy/
        "deployment" = "scripts/deploy"
        
        # Examples → apps/
        "examples" = "apps/web-app"
        
        # Requirements → root level
        "requirements" = "."
        
        # Data → data/
        "data" = "data/raw"
        "vector_db" = "data/processed"
        "graph_db" = "data/processed"
        "vault" = "data/raw"
        
        # Logs → logs/
        "logs" = "logs/application"
        
        # Temp Files → temp/
        "temp_files" = "temp/development"
        
        # Reports → docs/
        "reports" = "docs/development"
        
        # Utils → src/infrastructure/
        "utils" = "src/infrastructure/config"
        
        # Config → src/infrastructure/config/
        "config" = "src/infrastructure/config"
        
        # Indexer → src/application/services/
        "indexer" = "src/application/services"
        
        # Data Pipeline → src/application/services/
        "data_pipeline" = "src/application/services"
        
        # LangGraph Project → apps/studio-app/
        "langgraph_project" = "apps/studio-app"
        
        # LangGraph Server → services/langgraph-service/src/
        "langgraph_server" = "services/langgraph-service/src"
        
        # Context Cache → data/cache/
        "context-cache" = "data/cache"
        
        # Image → docs/
        "image" = "docs/development"
        
        # Monitoring → infrastructure/monitoring/
        "monitoring" = "infrastructure/monitoring"
        
        # Docker → infrastructure/docker/
        "docker" = "infrastructure/docker"
        
        # Cleanup System → tools/maintenance/
        "cleanup_system" = "tools/maintenance"
    }
    
    $MovedCount = 0
    $FailedCount = 0
    
    foreach ($mapping in $FileMappings.GetEnumerator()) {
        $sourceDir = $mapping.Key
        $targetDir = $mapping.Value
        
        if (Test-Path $sourceDir) {
            try {
                if (-not $DryRun) {
                    if ($targetDir -eq ".") {
                        # Move files from subdirectory to root
                        Get-ChildItem -Path $sourceDir -File | ForEach-Object {
                            Move-Item -Path $_.FullName -Destination "." -Force
                        }
                        Remove-Item -Path $sourceDir -Force
                    } else {
                        # Move entire directory
                        Move-Item -Path $sourceDir -Destination $targetDir -Force
                    }
                    Write-Host "  ✅ Moved: $sourceDir → $targetDir" -ForegroundColor Green
                } else {
                    Write-Host "  🔍 DRY RUN: Would move $sourceDir → $targetDir" -ForegroundColor Yellow
                }
                $MovedCount++
            } catch {
                Write-Host "  ❌ Failed to move $sourceDir`: $($_.Exception.Message)" -ForegroundColor Red
                $FailedCount++
            }
        }
    }
    
    return @{ Moved = $MovedCount; Failed = $FailedCount }
}

# Function to create service structure
function New-ServiceStructure {
    param([string]$ServiceName, [string]$Description)
    
    $ServiceDirs = @(
        "$ServiceName/src",
        "$ServiceName/tests",
        "$ServiceName/docs",
        "$ServiceName/scripts"
    )
    
    foreach ($dir in $ServiceDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "  ✅ Created service structure: $dir" -ForegroundColor Green
        }
    }
    
    # Create service README
    $ReadmeContent = @"
# $ServiceName

$Description

## Structure
- \`src/\` - Source code
- \`tests/\` - Test files
- \`docs/\` - Documentation
- \`scripts/\` - Build and deployment scripts

## Development
\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start service
python src/main.py
\`\`\`
"@
    
    if (-not $DryRun) {
        Set-Content -Path "$ServiceName/README.md" -Value $ReadmeContent
    }
}

# Main execution
Write-Host "`n📁 CREATING NEW PRODUCTION STRUCTURE..." -ForegroundColor Yellow
New-DirectoryStructure -Structure $NewStructure

Write-Host "`n📦 MOVING FILES TO NEW STRUCTURE..." -ForegroundColor Yellow
$MoveResults = Move-FilesToNewStructure -DryRun:$DryRun

Write-Host "`n🏗️ CREATING SERVICE STRUCTURES..." -ForegroundColor Yellow
$Services = @(
    @{ Name = "services/obsidian-service"; Description = "Obsidian vault integration and management" },
    @{ Name = "services/langgraph-service"; Description = "LangGraph workflow execution and management" },
    @{ Name = "services/mcp-service"; Description = "MCP server management and communication" },
    @{ Name = "services/monitoring-service"; Description = "System monitoring and observability" },
    @{ Name = "services/api-gateway"; Description = "Request routing and load balancing" }
)

foreach ($service in $Services) {
    New-ServiceStructure -ServiceName $service.Name -Description $service.Description
}

Write-Host "`n📊 RESTRUCTURING SUMMARY" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host "Directories moved: $($MoveResults.Moved)" -ForegroundColor Green
Write-Host "Directories failed: $($MoveResults.Failed)" -ForegroundColor Red
Write-Host "Services created: $($Services.Count)" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n🔍 DRY RUN COMPLETED - No files were actually moved" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ PRODUCTION RESTRUCTURING COMPLETED!" -ForegroundColor Green
    Write-Host "Repository has been restructured to production-grade architecture" -ForegroundColor Green
}
