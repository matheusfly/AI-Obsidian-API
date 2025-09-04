#!/usr/bin/env pwsh
# Interactive Debugging Suite for Motia and Flyde Integrations

param(
    [string]$Component = "all",
    [switch]$Verbose,
    [switch]$Fix
)

Write-Host "🔧 Interactive Integration Debugger" -ForegroundColor Cyan
Write-Host "Component: $Component" -ForegroundColor Yellow

function Test-NodeModules {
    param([string]$ProjectPath)
    
    $nodeModulesPath = Join-Path $ProjectPath "node_modules"
    if (-not (Test-Path $nodeModulesPath)) {
        Write-Host "❌ Missing node_modules in $ProjectPath" -ForegroundColor Red
        if ($Fix) {
            Write-Host "🔧 Installing dependencies..." -ForegroundColor Yellow
            Set-Location $ProjectPath
            npm install
            Set-Location ..
        }
        return $false
    }
    return $true
}

function Test-MotiaIntegration {
    Write-Host "`n🧪 Testing Motia Integration..." -ForegroundColor Cyan
    
    # Check project structure
    $motiaPath = "motia-project"
    if (-not (Test-Path $motiaPath)) {
        Write-Host "❌ Motia project not found" -ForegroundColor Red
        return $false
    }
    
    # Check dependencies
    if (-not (Test-NodeModules $motiaPath)) {
        return $false
    }
    
    # Test Motia state
    $stateFile = ".motia/motia.state.json"
    if (Test-Path $stateFile) {
        $state = Get-Content $stateFile | ConvertFrom-Json
        Write-Host "✅ Motia state file exists" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "State: $($state | ConvertTo-Json -Compress)" -ForegroundColor Gray
        }
    }
    
    # Test Motia server
    try {
        Set-Location $motiaPath
        Write-Host "🚀 Testing Motia server startup..." -ForegroundColor Yellow
        
        $process = Start-Process -FilePath "npm" -ArgumentList "run", scripts/" -PassThru -NoNewWindow -Wait
        if ($process.ExitCode -eq 0) {
            Write-Host "✅ Motia integration test passed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Motia test failed with exit code $($process.ExitCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Motia test error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    } finally {
        Set-Location ..
    }
}

function Test-FlydeIntegration {
    Write-Host "`n🧪 Testing Flyde Integration..." -ForegroundColor Cyan
    
    # Check project structure
    $flydePath = "flyde-project"
    if (-not (Test-Path $flydePath)) {
        Write-Host "❌ Flyde project not found" -ForegroundColor Red
        return $false
    }
    
    # Check dependencies
    if (-not (Test-NodeModules $flydePath)) {
        return $false
    }
    
    # Check Flyde flows
    $flowsPath = Join-Path $flydePath "flows"
    if (Test-Path $flowsPath) {
        $flows = Get-ChildItem $flowsPath -Filter "*.flyde"
        Write-Host "✅ Found $($flows.Count) Flyde flows" -ForegroundColor Green
        if ($Verbose) {
            $flows | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
        }
    }
    
    # Test Flyde server
    try {
        Set-Location $flydePath
        Write-Host "🚀 Testing Flyde server startup..." -ForegroundColor Yellow
        
        $process = Start-Process -FilePath "npm" -ArgumentList "run", scripts/" -PassThru -NoNewWindow -Wait
        if ($process.ExitCode -eq 0) {
            Write-Host "✅ Flyde integration test passed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Flyde test failed with exit code $($process.ExitCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Flyde test error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    } finally {
        Set-Location ..
    }
}

function Test-DockerIntegration {
    Write-Host "`n🐳 Testing Docker Integration..." -ForegroundColor Cyan
    
    # Check Docker availability
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker available: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker not available" -ForegroundColor Red
        return $false
    }
    
    # Check Docker Compose files
    $composeFiles = @(
        "docker-compose.yml",
        "docker-compose.enhanced-rag.yml"
    )
    
    foreach ($file in $composeFiles) {
        if (Test-Path $file) {
            Write-Host "✅ Found $file" -ForegroundColor Green
            
            # Validate compose file
            try {
                docker-compose -f $file config > $null 2>&1
                Write-Host "✅ $file is valid" -ForegroundColor Green
            } catch {
                Write-Host "❌ $file has syntax errors" -ForegroundColor Red
                if ($Fix) {
                    Write-Host "🔧 Attempting to fix $file..." -ForegroundColor Yellow
                    # Add fix logic here
                }
            }
        } else {
            Write-Host "❌ Missing $file" -ForegroundColor Red
        }
    }
    
    return $true
}

function Test-APIEndpoints {
    Write-Host "`n🌐 Testing API Endpoints..." -ForegroundColor Cyan
    
    $endpoints = @(
        @{ url = "http://localhost:8080/health"; name = "Vault API Health" },
        @{ url = "http://localhost:27123/health"; name = "Obsidian API Health" },
        @{ url = "http://localhost:6333/collections"; name = "Qdrant Collections" },
        @{ url = "http://localhost:3000/health"; name = "Embedding Server" }
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-RestMethod -Uri $endpoint.url -Method GET -TimeoutSec 5
            Write-Host "✅ $($endpoint.name): OK" -ForegroundColor Green
            if ($Verbose) {
                Write-Host "  Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
            }
        } catch {
            Write-Host "❌ $($endpoint.name): Failed" -ForegroundColor Red
            if ($Verbose) {
                Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
            }
        }
    }
}

function Fix-CommonIssues {
    Write-Host "`n🔧 Fixing Common Issues..." -ForegroundColor Cyan
    
    # Fix 1: Install missing dependencies
    Write-Host scripts/ing missing dependencies..." -ForegroundColor Yellow
    
    $projects = @("motia-project", "flyde-project", servicesservices/obsidian-api")
    foreach ($project in $projects) {
        if (Test-Path $project) {
            Set-Location $project
            npm install --silent
            Set-Location ..
            Write-Host "✅ Dependencies installed for $project" -ForegroundColor Green
        }
    }
    
    # Fix 2: Create missing directories
    $requiredDirs = @(logs/", ".motia/streams", servicesservices/qdrant_storage")
    foreach ($dir in $requiredDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✅ Created directory: $dir" -ForegroundColor Green
        }
    }
    
    # Fix 3: Set proper permissions
    if ($IsLinux -or $IsMacOS) {
        chmod +x scripts/*.ps1 2>/dev/null
        chmod +x scripts/*.sh 2>/dev/null
        Write-Host "✅ Set execute permissions on scripts" -ForegroundColor Green
    }
}

function Show-QuickLaunchCommands {
    Write-Host "`n🚀 Quick Launch Commands:" -ForegroundColor Cyan
    Write-Host "  ./scripts/quick-start.ps1           # Start all services" -ForegroundColor White
    Write-Host "  ./scriptsscripts/-enhanced-rag.ps1    # Setup enhanced RAG" -ForegroundColor White
    Write-Host "  ./motia-quick-setup.ps1             # Setup Motia" -ForegroundColor White
    Write-Host "  ./flyde-quick-setup.ps1             # Setup Flyde" -ForegroundColor White
    Write-Host "  docker-compose up -d                # Start Docker services" -ForegroundColor White
    Write-Host "  python test-enhanced-rag.py         # Run comprehensive tests" -ForegroundColor White
}

# Main execution
switch ($Component.ToLower()) {
    "motia" { 
        $result = Test-MotiaIntegration
        if (-not $result -and $Fix) { Fix-CommonIssues }
    }
    "flyde" { 
        $result = Test-FlydeIntegration
        if (-not $result -and $Fix) { Fix-CommonIssues }
    }
    "docker" { 
        $result = Test-DockerIntegration
        if (-not $result -and $Fix) { Fix-CommonIssues }
    }
    "api" { 
        Test-APIEndpoints
    }
    "all" {
        Write-Host "🔍 Running Complete Integration Test Suite..." -ForegroundColor Cyan
        
        $results = @{
            "Motia" = Test-MotiaIntegration
            "Flyde" = Test-FlydeIntegration
            "Docker" = Test-DockerIntegration
        }
        
        Test-APIEndpoints
        
        # Summary
        Write-Host "`n📊 Test Results Summary:" -ForegroundColor Cyan
        foreach ($test in $results.GetEnumerator()) {
            $status = if ($test.Value) { "✅ PASS" } else { "❌ FAIL" }
            $color = if ($test.Value) { "Green" } else { "Red" }
            Write-Host "  $($test.Key): $status" -ForegroundColor $color
        }
        
        if ($Fix -and ($results.Values -contains $false)) {
            Fix-CommonIssues
        }
    }
}

Show-QuickLaunchCommands

Write-Host "`n✅ Debugging complete!" -ForegroundColor Green