# 🔄 Restart All Systems - Complete System Restart & Recovery
# Comprehensive restart of all services with health monitoring

param(
    [switch]$Force,
    [switch]$Clean,
    [switch]$Monitor
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

function Show-Banner {
    Write-Host "🔄 RESTART ALL SYSTEMS" -ForegroundColor $Colors.Magenta
    Write-Host "=====================" -ForegroundColor $Colors.Magenta
    Write-Host "Complete System Restart & Recovery" -ForegroundColor $Colors.White
    Write-Host ""
}

function Stop-AllServices {
    Write-Host "🛑 Stopping All Services..." -ForegroundColor $Colors.Yellow
    Write-Host "============================" -ForegroundColor $Colors.Yellow
    
    # Kill all Node.js processes
    Write-Host "🔍 Finding Node.js processes..." -ForegroundColor $Colors.Cyan
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        Write-Host "  📊 Found $($nodeProcesses.Count) Node.js processes" -ForegroundColor $Colors.White
        foreach ($process in $nodeProcesses) {
            Write-Host "    Killing PID: $($process.Id)" -ForegroundColor $Colors.Yellow
            try {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            } catch {
                Write-Host "    ⚠️ Could not kill PID: $($process.Id)" -ForegroundColor $Colors.Yellow
            }
        }
    } else {
        Write-Host "  ✅ No Node.js processes found" -ForegroundColor $Colors.Green
    }
    
    # Kill any processes on our ports
    $ports = @(3000, 3001, 27123, 5678, 11434)
    foreach ($port in $ports) {
        try {
            $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
            if ($processes) {
                foreach ($process in $processes) {
                    $pid = $process.OwningProcess
                    Write-Host "  🔍 Killing process on port $port (PID: $pid)" -ForegroundColor $Colors.Yellow
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                }
            }
        } catch {
            # Port not in use
        }
    }
    
    Write-Host "  ✅ All services stopped" -ForegroundColor $Colors.Green
}

function Clean-System {
    if ($Clean) {
        Write-Host ""
        Write-Host "🧹 Cleaning System..." -ForegroundColor $Colors.Yellow
        Write-Host "====================" -ForegroundColor $Colors.Yellow
        
        # Clean npm cache
        Write-Host "  🧹 Cleaning npm cache..." -ForegroundColor $Colors.Cyan
        try {
            npm cache clean --force 2>$null
            Write-Host "    ✅ npm cache cleaned" -ForegroundColor $Colors.Green
        } catch {
            Write-Host "    ⚠️ npm cache clean failed" -ForegroundColor $Colors.Yellow
        }
        
        # Clean node_modules if needed
        if ($Force) {
            Write-Host "  🧹 Cleaning node_modules..." -ForegroundColor $Colors.Cyan
            $projects = @("flyde-project", "motia-project", servicesservices/obsidian-api")
            foreach ($project in $projects) {
                if (Test-Path "$project/node_modules") {
                    Write-Host "    Removing $project/node_modules..." -ForegroundColor $Colors.Yellow
                    Remove-Item "$project/node_modules" -Recurse -Force -ErrorAction SilentlyContinue
                }
            }
        }
        
        Write-Host "  ✅ System cleaned" -ForegroundColor $Colors.Green
    }
}

function Start-Services {
    Write-Host ""
    Write-Host "🚀 Starting Services..." -ForegroundColor $Colors.Yellow
    Write-Host "======================" -ForegroundColor $Colors.Yellow
    
    # Start Flyde
    Write-Host "🎨 Starting Flyde Studio..." -ForegroundColor $Colors.Cyan
    try {
        $flydeJob = Start-Job -ScriptBlock {
            Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\flyde-project"
            npm run dev
        } -Name "Flyde"
        Write-Host "  ✅ Flyde job started (ID: $($flydeJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ❌ Failed to start Flyde: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Start Motia
    Write-Host "⚡ Starting Motia Integration..." -ForegroundColor $Colors.Cyan
    try {
        $motiaJob = Start-Job -ScriptBlock {
            Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\motia-project"
            npm run dev
        } -Name "Motia"
        Write-Host "  ✅ Motia job started (ID: $($motiaJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ❌ Failed to start Motia: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Start Obsidian API
    Write-Host "📝 Starting Obsidian API..." -ForegroundColor $Colors.Cyan
    try {
        $obsidianJob = Start-Job -ScriptBlock {
            Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\obsidian-api"
            npx motia dev --port 27123
        } -Name "ObsidianAPI"
        Write-Host "  ✅ Obsidian API job started (ID: $($obsidianJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ❌ Failed to start Obsidian API: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Start Ollama if available
    Write-Host "🤖 Starting Ollama..." -ForegroundColor $Colors.Cyan
    try {
        $ollamaJob = Start-Job -ScriptBlock {
            ollama serve
        } -Name "Ollama"
        Write-Host "  ✅ Ollama job started (ID: $($ollamaJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ⚠️ Ollama not available or already running" -ForegroundColor $Colors.Yellow
    }
    
    # Start n8n if available
    Write-Host "🔗 Starting n8n..." -ForegroundColor $Colors.Cyan
    try {
        $n8nJob = Start-Job -ScriptBlock {
            npx n8n start
        } -Name servicesservices/n8n"
        Write-Host "  ✅ n8n job started (ID: $($n8nJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ⚠️ n8n not available or already running" -ForegroundColor $Colors.Yellow
    }
}

function Wait-ForServices {
    Write-Host ""
    Write-Host "⏳ Waiting for Services to Start..." -ForegroundColor $Colors.Yellow
    Write-Host "===================================" -ForegroundColor $Colors.Yellow
    
    $services = @(
        @{ Name = "Flyde"; Port = 3001; Url = "http://localhost:3001/health" }
        @{ Name = "Motia"; Port = 3000; Url = "http://localhost:3000/health" }
        @{ Name = "ObsidianAPI"; Port = 27123; Url = "http://localhost:27123/health" }
    )
    
    $maxWait = 60 # seconds
    $startTime = Get-Date
    
    foreach ($service in $services) {
        Write-Host ""
        Write-Host "🔍 Waiting for $($service.Name)..." -ForegroundColor $Colors.Cyan
        
        $elapsed = 0
        $ready = $false
        
        while ($elapsed -lt $maxWait -and -not $ready) {
            try {
                $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
                if ($response.StatusCode -eq 200) {
                    $ready = $true
                    Write-Host "  ✅ $($service.Name) is ready!" -ForegroundColor $Colors.Green
                }
            } catch {
                # Service not ready yet
            }
            
            if (-not $ready) {
                Start-Sleep -Seconds 2
                $elapsed += 2
                Write-Host "  ⏳ Still waiting... ($elapsed/$maxWait seconds)" -ForegroundColor $Colors.Yellow
            }
        }
        
        if (-not $ready) {
            Write-Host "  ⚠️ $($service.Name) may not be fully ready" -ForegroundColor $Colors.Yellow
        }
    }
}

function Test-AllServices {
    Write-Host ""
    Write-Host "🧪 Testing All Services..." -ForegroundColor $Colors.Yellow
    Write-Host "=========================" -ForegroundColor $Colors.Yellow
    
    $testResults = @{}
    
    # Test Flyde
    Write-Host ""
    Write-Host "🎨 Testing Flyde..." -ForegroundColor $Colors.Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3001/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Health check: OK" -ForegroundColor $Colors.Green
            $testResults["Flyde"] = $true
        } else {
            Write-Host "  ❌ Health check: Failed" -ForegroundColor $Colors.Red
            $testResults["Flyde"] = $false
        }
    } catch {
        Write-Host "  ❌ Flyde not responding" -ForegroundColor $Colors.Red
        $testResults["Flyde"] = $false
    }
    
    # Test Motia
    Write-Host ""
    Write-Host "⚡ Testing Motia..." -ForegroundColor $Colors.Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Health check: OK" -ForegroundColor $Colors.Green
            $testResults["Motia"] = $true
        } else {
            Write-Host "  ❌ Health check: Failed" -ForegroundColor $Colors.Red
            $testResults["Motia"] = $false
        }
    } catch {
        Write-Host "  ❌ Motia not responding" -ForegroundColor $Colors.Red
        $testResults["Motia"] = $false
    }
    
    # Test Obsidian API
    Write-Host ""
    Write-Host "📝 Testing Obsidian API..." -ForegroundColor $Colors.Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:27123/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Health check: OK" -ForegroundColor $Colors.Green
            $testResults["ObsidianAPI"] = $true
        } else {
            Write-Host "  ❌ Health check: Failed" -ForegroundColor $Colors.Red
            $testResults["ObsidianAPI"] = $false
        }
    } catch {
        Write-Host "  ❌ Obsidian API not responding" -ForegroundColor $Colors.Red
        $testResults["ObsidianAPI"] = $false
    }
    
    return $testResults
}

function Show-FinalStatus {
    param([hashtable]$Results)
    
    Write-Host ""
    Write-Host "📊 FINAL STATUS REPORT" -ForegroundColor $Colors.Magenta
    Write-Host "=====================" -ForegroundColor $Colors.Magenta
    
    $totalServices = $Results.Count
    $runningServices = ($Results.Values | Where-Object { $_ -eq $true }).Count
    $successRate = [Math]::Round(($runningServices / $totalServices) * 100, 1)
    
    Write-Host "Total Services: $totalServices" -ForegroundColor $Colors.White
    Write-Host "Running: $runningServices/$totalServices ($successRate%)" -ForegroundColor $(if($successRate -ge 80) {$Colors.Green} else {$Colors.Yellow})
    
    Write-Host ""
    Write-Host "🎯 Service Details:" -ForegroundColor $Colors.White
    foreach ($result in $Results.GetEnumerator()) {
        $status = if ($result.Value) { "✅ RUNNING" } else { "❌ NOT RUNNING" }
        $color = if ($result.Value) { $Colors.Green } else { $Colors.Red }
        Write-Host "  $($result.Key): $status" -ForegroundColor $color
    }
    
    Write-Host ""
    Write-Host "🔗 Quick Access:" -ForegroundColor $Colors.White
    Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor $Colors.Cyan
    Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor $Colors.Cyan
    Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor $Colors.Cyan
    
    if ($successRate -ge 80) {
        Write-Host ""
        Write-Host "🎉 SYSTEM RESTART SUCCESSFUL!" -ForegroundColor $Colors.Green
        Write-Host "All visual development tools are ready!" -ForegroundColor $Colors.Green
    } else {
        Write-Host ""
        Write-Host "⚠️ SOME SERVICES NEED ATTENTION" -ForegroundColor $Colors.Yellow
        Write-Host scripts/ the status above and restart if needed." -ForegroundColor $Colors.Yellow
    }
}

# Main execution
Show-Banner

Stop-AllServices
Clean-System
Start-Services
Wait-ForServices
$testResults = Test-AllServices
Show-FinalStatus $testResults

Write-Host ""
Write-Host "🔄 System restart complete!" -ForegroundColor $Colors.Magenta
