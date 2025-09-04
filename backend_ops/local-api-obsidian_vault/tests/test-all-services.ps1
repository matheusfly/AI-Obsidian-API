# 🧪 Test All Services Script (PowerShell)
# Comprehensive testing of Flyde, Motia, and backend services

param(
    [switch]$Help,
    [switch]$WebTest,
    [switch]$APITest,
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
    Write-Host "🧪 Comprehensive Service Testing" -ForegroundColor $Colors.Magenta
    Write-Host "=================================" -ForegroundColor $Colors.Magenta
    Write-Host "Testing Flyde, Motia, and backend services" -ForegroundColor $Colors.White
    Write-Host ""
}

function Show-Help {
    Write-Host "Usage: .\test-all-services.ps1 [options]" -ForegroundColor $Colors.Cyan
    Write-Host ""
    Write-Host "Options:" -ForegroundColor $Colors.White
    Write-Host "  -WebTest    Test web interfaces" -ForegroundColor $Colors.Green
    Write-Host "  -APITest    Test API endpoints" -ForegroundColor $Colors.Green
    Write-Host "  -All        Test everything" -ForegroundColor $Colors.Green
    Write-Host "  -Help       Show this help" -ForegroundColor $Colors.Green
    Write-Host ""
}

function Test-Service {
    param([string]$Name, [string]$Url, [string]$Method = "GET", [string]$Body = $null)
    
    try {
        Write-Host "🔍 Testing $Name..." -ForegroundColor $Colors.Cyan
        
        if ($Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        } else {
            $response = Invoke-WebRequest -Uri $Url -Method $Method -ContentType "application/json" -Body $Body -UseBasicParsing -TimeoutSec 10
        }
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $Name`: Healthy (Status: $($response.StatusCode))" -ForegroundColor $Colors.Green
            Write-Host "  📄 Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..." -ForegroundColor $Colors.Cyan
            return $true
        } else {
            Write-Host "  ⚠️ $Name`: Status $($response.StatusCode)" -ForegroundColor $Colors.Yellow
            return $false
        }
    } catch {
        Write-Host "  ❌ $Name`: Failed - $($_.Exception.Message)" -ForegroundColor $Colors.Red
        return $false
    }
}

function Test-WebInterface {
    param([string]$Name, [string]$Url)
    
    try {
        Write-Host "🌐 Testing Web Interface: $Name..." -ForegroundColor $Colors.Cyan
        
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $Name Web Interface: Accessible" -ForegroundColor $Colors.Green
            Write-Host "  📄 Content Type: $($response.Headers.'Content-Type')" -ForegroundColor $Colors.Cyan
            return $true
        } else {
            Write-Host "  ⚠️ $Name Web Interface: Status $($response.StatusCode)" -ForegroundColor $Colors.Yellow
            return $false
        }
    } catch {
        Write-Host "  ❌ $Name Web Interface: Failed - $($_.Exception.Message)" -ForegroundColor $Colors.Red
        return $false
    }
}

function Test-FlydeFlow {
    Write-Host "🎨 Testing Flyde Flow Execution..." -ForegroundColor $Colors.Cyan
    
    try {
        $body = '{"name": "TestUser"}'
        $response = Invoke-WebRequest -Uri "http://localhost:3001/run/hello-world" -Method POST -ContentType "application/json" -Body $body -UseBasicParsing -TimeoutSec 15
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Flyde Flow Execution: Success" -ForegroundColor $Colors.Green
            Write-Host "  📄 Result: $($response.Content)" -ForegroundColor $Colors.Cyan
            return $true
        } else {
            Write-Host "  ⚠️ Flyde Flow Execution: Status $($response.StatusCode)" -ForegroundColor $Colors.Yellow
            return $false
        }
    } catch {
        Write-Host "  ❌ Flyde Flow Execution: Failed - $($_.Exception.Message)" -ForegroundColor $Colors.Red
        return $false
    }
}

function Test-MotiaIntegration {
    Write-Host "⚡ Testing Motia Integration..." -ForegroundColor $Colors.Cyan
    
    try {
        $body = '{"action": "test", "data": {"message": "Hello Motia"}}'
        $response = Invoke-WebRequest -Uri "http://localhost:3000/integrate/obsidian" -Method POST -ContentType "application/json" -Body $body -UseBasicParsing -TimeoutSec 15
        
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Motia Integration: Success" -ForegroundColor $Colors.Green
            Write-Host "  📄 Result: $($response.Content)" -ForegroundColor $Colors.Cyan
            return $true
        } else {
            Write-Host "  ⚠️ Motia Integration: Status $($response.StatusCode)" -ForegroundColor $Colors.Yellow
            return $false
        }
    } catch {
        Write-Host "  ❌ Motia Integration: Failed - $($_.Exception.Message)" -ForegroundColor $Colors.Red
        return $false
    }
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Show-Banner

Write-Host "🚀 Starting Comprehensive Service Tests..." -ForegroundColor $Colors.Yellow
Write-Host "=========================================" -ForegroundColor $Colors.Yellow

$testResults = @{}

# Test API Endpoints
Write-Host ""
Write-Host "🔌 API Endpoint Tests" -ForegroundColor $Colors.Magenta
Write-Host "====================" -ForegroundColor $Colors.Magenta

$testResults.FlydeHealth = Test-Service "Flyde Health" "http://localhost:3001/health"
$testResults.FlydeFlows = Test-Service "Flyde Flows List" "http://localhost:3001/flows"
$testResults.MotiaHealth = Test-Service "Motia Health" "http://localhost:3000/health"
$testResults.MotiaAPI = Test-Service "Motia API" "http://localhost:3000/api"
$testResults.ObsidianHealth = Test-Service "Obsidian Health" "http://localhost:27123/health"

# Test Flow Execution
Write-Host ""
Write-Host "🎨 Flow Execution Tests" -ForegroundColor $Colors.Magenta
Write-Host "=======================" -ForegroundColor $Colors.Magenta

$testResults.FlydeFlow = Test-FlydeFlow
$testResults.MotiaIntegration = Test-MotiaIntegration

# Test Web Interfaces
if ($WebTest -or $All) {
    Write-Host ""
    Write-Host "🌐 Web Interface Tests" -ForegroundColor $Colors.Magenta
    Write-Host "======================" -ForegroundColor $Colors.Magenta
    
    $testResults.FlydeWeb = Test-WebInterface "Flyde" "http://localhost:3001"
    $testResults.MotiaWeb = Test-WebInterface "Motia" "http://localhost:3000"
    $testResults.ObsidianWeb = Test-WebInterface "Obsidian" "http://localhost:27123"
    $testResults.n8nWeb = Test-WebInterface "n8n" "http://localhost:5678"
    $testResults.OllamaWeb = Test-WebInterface "Ollama" "http://localhost:11434"
}

# Test Backend Services
Write-Host ""
Write-Host "🔧 Backend Service Tests" -ForegroundColor $Colors.Magenta
Write-Host "========================" -ForegroundColor $Colors.Magenta

$testResults.n8nHealth = Test-Service "n8n Health" "http://localhost:5678/healthz"
$testResults.OllamaModels = Test-Service "Ollama Models" "http://localhost:11434/api/tags"
$testResults.Prometheus = Test-Service "Prometheus" "http://localhost:9090"
$testResults.Grafana = Test-Service "Grafana" "http://localhost:3000"

# Summary
Write-Host ""
Write-Host "📊 Test Results Summary" -ForegroundColor $Colors.Magenta
Write-Host "=======================" -ForegroundColor $Colors.Magenta

$totalTests = $testResults.Count
$passedTests = ($testResults.Values | Where-Object { $_ -eq $true }).Count
$successRate = [Math]::Round(($passedTests / $totalTests) * 100, 2)

Write-Host "✅ Passed: $passedTests/$totalTests ($successRate%)" -ForegroundColor $Colors.Green
Write-Host "❌ Failed: $($totalTests - $passedTests)" -ForegroundColor $Colors.Red

Write-Host ""
Write-Host "🎯 Service Status:" -ForegroundColor $Colors.White

foreach ($test in $testResults.GetEnumerator()) {
    $status = if ($test.Value) { "✅" } else { "❌" }
    $color = if ($test.Value) { $Colors.Green } else { $Colors.Red }
    Write-Host "  $status $($test.Key)" -ForegroundColor $color
}

Write-Host ""
Write-Host "🔗 Quick Access URLs:" -ForegroundColor $Colors.White
Write-Host "  • Flyde Studio: http://localhost:3001" -ForegroundColor $Colors.Cyan
Write-Host "  • Motia Dev: http://localhost:3000" -ForegroundColor $Colors.Cyan
Write-Host "  • Obsidian API: http://localhost:27123" -ForegroundColor $Colors.Cyan
Write-Host "  • n8n Workflows: http://localhost:5678" -ForegroundColor $Colors.Cyan
Write-Host "  • Ollama AI: http://localhost:11434" -ForegroundColor $Colors.Cyan

if ($successRate -ge 80) {
    Write-Host ""
    Write-Host "🎉 EXCELLENT! Most services are working perfectly!" -ForegroundColor $Colors.Green
} elseif ($successRate -ge 60) {
    Write-Host ""
    Write-Host "⚠️ GOOD! Some services need attention." -ForegroundColor $Colors.Yellow
} else {
    Write-Host ""
    Write-Host "🔧 NEEDS WORK! Several services require fixing." -ForegroundColor $Colors.Red
}

Write-Host ""
Write-Host "🚀 Ready for development!" -ForegroundColor $Colors.Magenta
