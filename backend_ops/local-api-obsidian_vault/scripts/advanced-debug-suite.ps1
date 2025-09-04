# 🔧 Advanced Debug Suite - Comprehensive System Analysis
# Deep debugging, performance testing, and integration validation

param(
    [switch]$FullDebug,
    [switch]$PerformanceTest,
    [switch]$IntegrationTest,
    [switch]$FixIssues,
    [switch]$All
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
    Write-Host "🔧 ADVANCED DEBUG SUITE" -ForegroundColor $Colors.Magenta
    Write-Host "=======================" -ForegroundColor $Colors.Magenta
    Write-Host "Comprehensive System Analysis & Debugging" -ForegroundColor $Colors.White
    Write-Host ""
}

function Test-ServiceDeep {
    param([string]$Name, [string]$Url, [string]$ExpectedResponse)
    
    Write-Host "🔍 Deep testing $Name..." -ForegroundColor $Colors.Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        $statusCode = $response.StatusCode
        $content = $response.Content
        $responseTime = $response.Headers.'X-Response-Time'
        
        Write-Host "  ✅ Status: $statusCode" -ForegroundColor $Colors.Green
        Write-Host "  📊 Response Time: $responseTime" -ForegroundColor $Colors.White
        Write-Host "  📄 Content Length: $($content.Length) chars" -ForegroundColor $Colors.White
        
        if ($ExpectedResponse -and $content -like "*$ExpectedResponse*") {
            Write-Host "  ✅ Expected content found" -ForegroundColor $Colors.Green
            return $true
        } else {
            Write-Host "  ⚠️ Unexpected content" -ForegroundColor $Colors.Yellow
            Write-Host "  📄 Content preview: $($content.Substring(0, [Math]::Min(100, $content.Length)))..." -ForegroundColor $Colors.White
            return $false
        }
        
    } catch {
        Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor $Colors.Red
        return $false
    }
}

function Test-APIEndpoints {
    Write-Host "🌐 Testing API Endpoints..." -ForegroundColor $Colors.Magenta
    Write-Host "============================" -ForegroundColor $Colors.Magenta
    
    $endpoints = @(
        @{
            Name = "Flyde Health"
            Url = "http://localhost:3001/health"
            Expected = "healthy"
        },
        @{
            Name = "Flyde Flows"
            Url = "http://localhost:3001/flows"
            Expected = "flows"
        },
        @{
            Name = "Motia Health"
            Url = "http://localhost:3000/health"
            Expected = "healthy"
        },
        @{
            Name = "Motia API"
            Url = "http://localhost:3000/api"
            Expected = "message"
        },
        @{
            Name = "Obsidian Health"
            Url = "http://localhost:27123/health"
            Expected = "html"
        }
    )
    
    $results = @{}
    
    foreach ($endpoint in $endpoints) {
        Write-Host ""
        $success = Test-ServiceDeep $endpoint.Name $endpoint.Url $endpoint.Expected
        $results[$endpoint.Name] = $success
    }
    
    return $results
}

function Test-Performance {
    Write-Host ""
    Write-Host "⚡ Performance Testing..." -ForegroundColor $Colors.Magenta
    Write-Host "=========================" -ForegroundColor $Colors.Magenta
    
    $testUrls = @(
        "http://localhost:3001/health",
        "http://localhost:3000/health",
        "http://localhost:27123/health"
    )
    
    foreach ($url in $testUrls) {
        Write-Host ""
        Write-Host "🔥 Stress testing $url..." -ForegroundColor $Colors.Cyan
        
        $successCount = 0
        $totalRequests = 10
        $responseTimes = @()
        
        for ($i = 1; $i -le $totalRequests; $i++) {
            try {
                $startTime = Get-Date
                $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
                $endTime = Get-Date
                $responseTime = ($endTime - $startTime).TotalMilliseconds
                
                if ($response.StatusCode -eq 200) {
                    $successCount++
                }
                
                $responseTimes += $responseTime
                Write-Host "  Request $i`: $([Math]::Round($responseTime, 2))ms" -ForegroundColor $Colors.White
                
            } catch {
                Write-Host "  Request $i`: FAILED" -ForegroundColor $Colors.Red
            }
        }
        
        $successRate = ($successCount / $totalRequests) * 100
        $avgResponseTime = ($responseTimes | Measure-Object -Average).Average
        $maxResponseTime = ($responseTimes | Measure-Object -Maximum).Maximum
        $minResponseTime = ($responseTimes | Measure-Object -Minimum).Minimum
        
        Write-Host ""
        Write-Host "  📊 Results for $url`:" -ForegroundColor $Colors.White
        Write-Host "    Success Rate: $([Math]::Round($successRate, 1))%" -ForegroundColor $(if($successRate -ge 90) {$Colors.Green} else {$Colors.Yellow})
        Write-Host "    Avg Response: $([Math]::Round($avgResponseTime, 2))ms" -ForegroundColor $Colors.White
        Write-Host "    Min Response: $([Math]::Round($minResponseTime, 2))ms" -ForegroundColor $Colors.Green
        Write-Host "    Max Response: $([Math]::Round($maxResponseTime, 2))ms" -ForegroundColor $Colors.Yellow
    }
}

function Test-Integration {
    Write-Host ""
    Write-Host "🔗 Integration Testing..." -ForegroundColor $Colors.Magenta
    Write-Host "=========================" -ForegroundColor $Colors.Magenta
    
    # Test Flyde flow execution
    Write-Host ""
    Write-Host "🎨 Testing Flyde Flow Execution..." -ForegroundColor $Colors.Cyan
    
    try {
        $flowData = @{
            input = "Hello from integration test"
            timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "http://localhost:3001/run/hello-world" -Method POST -Body $flowData -ContentType "application/json" -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Flyde flow execution successful" -ForegroundColor $Colors.Green
            $result = $response.Content | ConvertFrom-Json
            Write-Host "  📄 Result: $($result.result)" -ForegroundColor $Colors.White
        } else {
            Write-Host "  ❌ Flyde flow execution failed" -ForegroundColor $Colors.Red
        }
    } catch {
        Write-Host "  ❌ Flyde integration error: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Test Motia API integration
    Write-Host ""
    Write-Host "⚡ Testing Motia API Integration..." -ForegroundColor $Colors.Cyan
    
    try {
        $motiaData = @{
            action = scripts/"
            data = @{
                message = "Integration test"
                timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
            }
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "http://localhost:3000/integrate/obsidian" -Method POST -Body $motiaData -ContentType "application/json" -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Motia API integration successful" -ForegroundColor $Colors.Green
            $result = $response.Content | ConvertFrom-Json
            Write-Host "  📄 Result: $($result.result.action)" -ForegroundColor $Colors.White
        } else {
            Write-Host "  ❌ Motia API integration failed" -ForegroundColor $Colors.Red
        }
    } catch {
        Write-Host "  ❌ Motia integration error: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
}

function Fix-CommonIssues {
    Write-Host ""
    Write-Host "🔧 Fixing Common Issues..." -ForegroundColor $Colors.Magenta
    Write-Host "=========================" -ForegroundColor $Colors.Magenta
    
    # Check for port conflicts
    Write-Host ""
    Write-Host "🔍 Checking for port conflicts..." -ForegroundColor $Colors.Cyan
    
    $ports = @(3000, 3001, 27123, 5678, 11434)
    foreach ($port in $ports) {
        try {
            $connection = New-Object System.Net.Sockets.TcpClient
            $connection.Connect("localhost", $port)
            $connection.Close()
            Write-Host "  ✅ Port $port`: Available" -ForegroundColor $Colors.Green
        } catch {
            Write-Host "  ❌ Port $port`: In use or blocked" -ForegroundColor $Colors.Red
        }
    }
    
    # Check Node.js processes
    Write-Host ""
    Write-Host "🔍 Checking Node.js processes..." -ForegroundColor $Colors.Cyan
    
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        Write-Host "  📊 Found $($nodeProcesses.Count) Node.js processes" -ForegroundColor $Colors.White
        foreach ($process in $nodeProcesses) {
            Write-Host "    PID: $($process.Id) | CPU: $([Math]::Round($process.CPU, 2))s" -ForegroundColor $Colors.White
        }
    } else {
        Write-Host "  ⚠️ No Node.js processes found" -ForegroundColor $Colors.Yellow
    }
    
    # Check disk space
    Write-Host ""
    Write-Host "🔍 Checking disk space..." -ForegroundColor $Colors.Cyan
    
    $drive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freeSpaceGB = [Math]::Round($drive.FreeSpace / 1GB, 2)
    $totalSpaceGB = [Math]::Round($drive.Size / 1GB, 2)
    $usedPercent = [Math]::Round((($drive.Size - $drive.FreeSpace) / $drive.Size) * 100, 1)
    
    Write-Host "  💾 Free Space: $freeSpaceGB GB / $totalSpaceGB GB ($usedPercent% used)" -ForegroundColor $(if($freeSpaceGB -gt 5) {$Colors.Green} else {$Colors.Yellow})
    
    # Check memory usage
    Write-Host ""
    Write-Host "🔍 Checking memory usage..." -ForegroundColor $Colors.Cyan
    
    $memory = Get-WmiObject -Class Win32_OperatingSystem
    $totalMemoryGB = [Math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
    $freeMemoryGB = [Math]::Round($memory.FreePhysicalMemory / 1MB, 2)
    $usedPercent = [Math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 1)
    
    Write-Host "  🧠 Memory: $freeMemoryGB GB free / $totalMemoryGB GB total ($usedPercent% used)" -ForegroundColor $(if($freeMemoryGB -gt 2) {$Colors.Green} else {$Colors.Yellow})
}

function Show-SystemReport {
    Write-Host ""
    Write-Host "📊 SYSTEM REPORT" -ForegroundColor $Colors.Magenta
    Write-Host "===============" -ForegroundColor $Colors.Magenta
    
    # Get system info
    $os = Get-WmiObject -Class Win32_OperatingSystem
    $computer = Get-WmiObject -Class Win32_ComputerSystem
    
    Write-Host "🖥️ System Information:" -ForegroundColor $Colors.White
    Write-Host "  OS: $($os.Caption) $($os.Version)" -ForegroundColor $Colors.Cyan
    Write-Host "  Architecture: $($os.OSArchitecture)" -ForegroundColor $Colors.Cyan
    Write-Host "  Computer: $($computer.Name)" -ForegroundColor $Colors.Cyan
    Write-Host "  User: $($env:USERNAME)" -ForegroundColor $Colors.Cyan
    
    # Get PowerShell version
    Write-Host ""
    Write-Host "🔧 Development Environment:" -ForegroundColor $Colors.White
    Write-Host "  PowerShell: $($PSVersionTable.PSVersion)" -ForegroundColor $Colors.Cyan
    Write-Host "  .NET: $($PSVersionTable.CLRVersion)" -ForegroundColor $Colors.Cyan
    
    # Check Node.js version
    try {
        $nodeVersion = node --version
        Write-Host "  Node.js: $nodeVersion" -ForegroundColor $Colors.Cyan
    } catch {
        Write-Host "  Node.js: Not found" -ForegroundColor $Colors.Red
    }
    
    # Check npm version
    try {
        $npmVersion = npm --version
        Write-Host "  npm: $npmVersion" -ForegroundColor $Colors.Cyan
    } catch {
        Write-Host "  npm: Not found" -ForegroundColor $Colors.Red
    }
}

# Main execution
Show-Banner

if ($All -or $FullDebug) {
    Write-Host "🔍 Running Full Debug Analysis..." -ForegroundColor $Colors.Yellow
    $apiResults = Test-APIEndpoints
    Test-Performance
    Test-Integration
    Fix-CommonIssues
    Show-SystemReport
} elseif ($PerformanceTest) {
    Test-Performance
} elseif ($IntegrationTest) {
    Test-Integration
} elseif ($FixIssues) {
    Fix-CommonIssues
} else {
    $apiResults = Test-APIEndpoints
}

Write-Host ""
Write-Host "🎯 DEBUG ANALYSIS COMPLETE!" -ForegroundColor $Colors.Green
Write-Host "===========================" -ForegroundColor $Colors.Green

if ($apiResults) {
    $successCount = ($apiResults.Values | Where-Object { $_ -eq $true }).Count
    $totalCount = $apiResults.Count
    $successRate = [Math]::Round(($successCount / $totalCount) * 100, 1)
    
    Write-Host "API Success Rate: $successRate% ($successCount/$totalCount)" -ForegroundColor $(if($successRate -ge 80) {$Colors.Green} else {$Colors.Yellow})
}

Write-Host ""
Write-Host "🚀 System ready for advanced development!" -ForegroundColor $Colors.Magenta
