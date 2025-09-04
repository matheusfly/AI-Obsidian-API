# 🚀 Smart Server Manager - Auto-detect, Start & Activate Visual Tools
# Comprehensive logic to check, start, and activate all services with plugins

param(
    [switch]$AutoStart,
    [switch]$CheckOnly,
    [switch]$ActivatePlugins,
    [switch]$FullSystem
)

# Color definitions
$Colors = @{
    Green = "Green"
    Blue = "Blue"
    Yellow = "Yellow"
    Red = "Red"
    Magenta = "Magenta"
    Cyan = "Cyan"
    White = "White"
}

# Service configurations
$Services = @{
    "Flyde" = @{
        Port = 3001
        Path = "flyde-project"
        Command = "npm run dev"
        HealthUrl = "http://localhost:3001/health"
        FlowsUrl = "http://localhost:3001/flows"
        Plugin = "flyde.flyde-vscode"
        Description = "Visual Flow Programming"
    }
    "Motia" = @{
        Port = 3000
        Path = "motia-project"
        Command = "npm run dev"
        HealthUrl = "http://localhost:3000/health"
        APIUrl = "http://localhost:3000/api"
        Plugin = "motia.vscode-extension"
        Description = "Workflow Automation"
    }
    "ObsidianAPI" = @{
        Port = 27123
        Path = servicesservices/obsidian-api"
        Command = "npx motia dev --port 27123"
        HealthUrl = "http://localhost:27123/health"
        WorkbenchUrl = "http://localhost:27123"
        Plugin = "obsidian.obsidian-vscode"
        Description = "Obsidian Integration"
    }
    servicesservices/n8n" = @{
        Port = 5678
        Path = servicesservices/n8n"
        Command = "npx n8n start"
        HealthUrl = "http://localhost:5678/healthz"
        WebUrl = "http://localhost:5678"
        Plugin = servicesservices/n8n.n8n-vscode"
        Description = "Workflow Automation"
    }
    "Ollama" = @{
        Port = 11434
        Path = "ollama"
        Command = "ollama serve"
        HealthUrl = "http://localhost:11434/api/tags"
        WebUrl = "http://localhost:11434"
        Plugin = "ollama.ollama-vscode"
        Description = "AI Model Server"
    }
}

function Show-Banner {
    Write-Host "🚀 Smart Server Manager" -ForegroundColor $Colors.Magenta
    Write-Host "=======================" -ForegroundColor $Colors.Magenta
    Write-Host "Auto-detect, Start & Activate Visual Tools" -ForegroundColor $Colors.White
    Write-Host ""
}

function Test-Port {
    param([int]$Port)
    
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

function Test-ServiceHealth {
    param([string]$Name, [string]$HealthUrl)
    
    try {
        $response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 5
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-Service {
    param([string]$Name, [hashtable]$Config)
    
    Write-Host "🚀 Starting $Name..." -ForegroundColor $Colors.Cyan
    
    if (-not (Test-Path $Config.Path)) {
        Write-Host "  ❌ Path not found: $($Config.Path)" -ForegroundColor $Colors.Red
        return $false
    }
    
    try {
        # Start service in background
        $process = Start-Process -FilePath "powershell" -ArgumentList "-Command", "cd '$($Config.Path)'; $($Config.Command)" -PassThru -WindowStyle Hidden
        
        # Wait for service to start
        $timeout = 30
        $elapsed = 0
        
        while ($elapsed -lt $timeout) {
            Start-Sleep -Seconds 2
            $elapsed += 2
            
            if (Test-Port $Config.Port) {
                Write-Host "  ✅ $Name started successfully on port $($Config.Port)" -ForegroundColor $Colors.Green
                return $true
            }
        }
        
        Write-Host "  ⚠️ $Name started but may not be fully ready" -ForegroundColor $Colors.Yellow
        return $true
        
    } catch {
        Write-Host "  ❌ Failed to start $Name`: $($_.Exception.Message)" -ForegroundColor $Colors.Red
        return $false
    }
}

function Install-VSCodeExtension {
    param([string]$ExtensionId)
    
    try {
        Write-Host "🔌 Installing extension: $ExtensionId" -ForegroundColor $Colors.Cyan
        
        # Try different installation methods
        $methods = @(
            "code --install-extension $ExtensionId",
            "cursor --install-extension $ExtensionId",
            "npx @vscode/vsce install $ExtensionId"
        )
        
        foreach ($method in $methods) {
            try {
                Invoke-Expression $method 2>$null
                Write-Host "  ✅ Extension installed successfully" -ForegroundColor $Colors.Green
                return $true
            } catch {
                continue
            }
        }
        
        Write-Host "  ⚠️ Could not install extension automatically" -ForegroundColor $Colors.Yellow
        Write-Host "  📝 Please install manually: $ExtensionId" -ForegroundColor $Colors.Cyan
        return $false
        
    } catch {
        Write-Host "  ❌ Extension installation failed" -ForegroundColor $Colors.Red
        return $false
    }
}

function Test-VisualTools {
    Write-Host "🎨 Testing Visual Tools Integration..." -ForegroundColor $Colors.Magenta
    Write-Host "=====================================" -ForegroundColor $Colors.Magenta
    
    $results = @{}
    
    foreach ($service in $Services.GetEnumerator()) {
        $name = $service.Key
        $config = $service.Value
        
        Write-Host ""
        Write-Host "🔍 Checking $name ($($config.Description))..." -ForegroundColor $Colors.Cyan
        
        # Check if port is open
        $portOpen = Test-Port $config.Port
        Write-Host "  Port $($config.Port): $(if($portOpen) {'✅ Open'} else {'❌ Closed'})" -ForegroundColor $(if($portOpen) {$Colors.Green} else {$Colors.Red})
        
        if ($portOpen) {
            # Check health endpoint
            $healthy = Test-ServiceHealth $name $config.HealthUrl
            Write-Host "  Health Check: $(if($healthy) {'✅ Healthy'} else {'⚠️ Not responding'})" -ForegroundColor $(if($healthy) {$Colors.Green} else {$Colors.Yellow})
            
            # Test specific endpoints
            if ($config.FlowsUrl) {
                try {
                    $flowsResponse = Invoke-WebRequest -Uri $config.FlowsUrl -UseBasicParsing -TimeoutSec 5
                    Write-Host "  Flows API: ✅ Working" -ForegroundColor $Colors.Green
                } catch {
                    Write-Host "  Flows API: ❌ Not working" -ForegroundColor $Colors.Red
                }
            }
            
            if ($config.APIUrl) {
                try {
                    $apiResponse = Invoke-WebRequest -Uri $config.APIUrl -UseBasicParsing -TimeoutSec 5
                    Write-Host "  API Endpoint: ✅ Working" -ForegroundColor $Colors.Green
                } catch {
                    Write-Host "  API Endpoint: ❌ Not working" -ForegroundColor $Colors.Red
                }
            }
        }
        
        $results[$name] = @{
            PortOpen = $portOpen
            Healthy = $healthy
            Config = $config
        }
    }
    
    return $results
}

function Start-MissingServices {
    param([hashtable]$TestResults)
    
    Write-Host ""
    Write-Host "🚀 Starting Missing Services..." -ForegroundColor $Colors.Magenta
    Write-Host "===============================" -ForegroundColor $Colors.Magenta
    
    foreach ($result in $TestResults.GetEnumerator()) {
        $name = $result.Key
        $data = $result.Value
        
        if (-not $data.PortOpen) {
            Write-Host ""
            $success = Start-Service $name $data.Config
            if ($success) {
                # Update test results
                $TestResults[$name].PortOpen = $true
            }
        } else {
            Write-Host "  ✅ $name is already running" -ForegroundColor $Colors.Green
        }
    }
}

function Activate-VisualPlugins {
    param([hashtable]$TestResults)
    
    Write-Host ""
    Write-Host "🔌 Activating Visual Tool Plugins..." -ForegroundColor $Colors.Magenta
    Write-Host "====================================" -ForegroundColor $Colors.Magenta
    
    foreach ($result in $TestResults.GetEnumerator()) {
        $name = $result.Key
        $data = $result.Value
        
        if ($data.PortOpen -and $data.Config.Plugin) {
            Write-Host ""
            Write-Host "🎨 Activating $name plugin..." -ForegroundColor $Colors.Cyan
            Install-VSCodeExtension $data.Config.Plugin
        }
    }
}

function Show-ServiceStatus {
    param([hashtable]$TestResults)
    
    Write-Host ""
    Write-Host "📊 Service Status Summary" -ForegroundColor $Colors.Magenta
    Write-Host "========================" -ForegroundColor $Colors.Magenta
    
    $totalServices = $TestResults.Count
    $runningServices = ($TestResults.Values | Where-Object { $_.PortOpen }).Count
    $healthyServices = ($TestResults.Values | Where-Object { $_.Healthy }).Count
    
    Write-Host "Total Services: $totalServices" -ForegroundColor $Colors.White
    Write-Host "Running: $runningServices/$totalServices" -ForegroundColor $(if($runningServices -eq $totalServices) {$Colors.Green} else {$Colors.Yellow})
    Write-Host "Healthy: $healthyServices/$totalServices" -ForegroundColor $(if($healthyServices -eq $totalServices) {$Colors.Green} else {$Colors.Yellow})
    
    Write-Host ""
    Write-Host "🎯 Service Details:" -ForegroundColor $Colors.White
    
    foreach ($result in $TestResults.GetEnumerator()) {
        $name = $result.Key
        $data = $result.Value
        $config = $data.Config
        
        $status = if ($data.PortOpen -and $data.Healthy) { "✅ FULLY OPERATIONAL" } 
                 elseif ($data.PortOpen) { "⚠️ RUNNING (Health issues)" }
                 else { "❌ NOT RUNNING" }
        
        $color = if ($data.PortOpen -and $data.Healthy) { $Colors.Green }
                elseif ($data.PortOpen) { $Colors.Yellow }
                else { $Colors.Red }
        
        Write-Host "  $name`: $status" -ForegroundColor $color
        Write-Host "    Port: $($config.Port) | Description: $($config.Description)" -ForegroundColor $Colors.Cyan
        
        if ($data.PortOpen) {
            Write-Host "    🌐 Access: $($config.HealthUrl)" -ForegroundColor $Colors.Blue
        }
    }
}

function Show-QuickAccess {
    Write-Host ""
    Write-Host "🔗 Quick Access URLs" -ForegroundColor $Colors.Magenta
    Write-Host "===================" -ForegroundColor $Colors.Magenta
    
    Write-Host "🎨 Visual Tools:" -ForegroundColor $Colors.White
    Write-Host "  • Flyde Studio: http://localhost:3001" -ForegroundColor $Colors.Cyan
    Write-Host "  • Motia Workbench: http://localhost:3000" -ForegroundColor $Colors.Cyan
    Write-Host "  • Obsidian API: http://localhost:27123" -ForegroundColor $Colors.Cyan
    
    Write-Host ""
    Write-Host "🔧 Backend Services:" -ForegroundColor $Colors.White
    Write-Host "  • n8n Workflows: http://localhost:5678" -ForegroundColor $Colors.Cyan
    Write-Host "  • Ollama AI: http://localhost:11434" -ForegroundColor $Colors.Cyan
    
    Write-Host ""
    Write-Host "📊 Health Checks:" -ForegroundColor $Colors.White
    Write-Host "  • Flyde Health: http://localhost:3001/health" -ForegroundColor $Colors.Cyan
    Write-Host "  • Motia Health: http://localhost:3000/health" -ForegroundColor $Colors.Cyan
    Write-Host "  • Obsidian Health: http://localhost:27123/health" -ForegroundColor $Colors.Cyan
}

# Main execution
Show-Banner

Write-Host "🔍 Testing all services..." -ForegroundColor $Colors.Yellow
$testResults = Test-VisualTools

if ($CheckOnly) {
    Show-ServiceStatus $testResults
    Show-QuickAccess
    exit 0
}

if ($AutoStart -or $FullSystem) {
    Start-MissingServices $testResults
    
    # Wait for services to stabilize
    Write-Host ""
    Write-Host "⏳ Waiting for services to stabilize..." -ForegroundColor $Colors.Yellow
    Start-Sleep -Seconds 5
    
    # Re-test after starting
    Write-Host "🔍 Re-testing services..." -ForegroundColor $Colors.Yellow
    $testResults = Test-VisualTools
}

if ($ActivatePlugins -or $FullSystem) {
    Activate-VisualPlugins $testResults
}

Show-ServiceStatus $testResults
Show-QuickAccess

# Final status
$totalServices = $testResults.Count
$runningServices = ($testResults.Values | Where-Object { $_.PortOpen }).Count
$healthyServices = ($testResults.Values | Where-Object { $_.Healthy }).Count

Write-Host ""
if ($runningServices -eq $totalServices -and $healthyServices -eq $totalServices) {
    Write-Host "🎉 ALL SYSTEMS OPERATIONAL! Ready for visual development!" -ForegroundColor $Colors.Green
} elseif ($runningServices -eq $totalServices) {
    Write-Host "⚠️ All services running, but some have health issues." -ForegroundColor $Colors.Yellow
} else {
    Write-Host "🔧 Some services need attention. Check the status above." -ForegroundColor $Colors.Red
}

Write-Host ""
Write-Host "🚀 Smart Server Manager complete!" -ForegroundColor $Colors.Magenta
