# 🔧 FIX PYTHON CONFLICTS - Comprehensive Solution
# Fix Python 3.13 compatibility issues and get all services running

param(
    [switch]$Force,
    [switch]$SkipPython,
    [switch]$UseDocker
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
    Write-Host "🔧 FIXING PYTHON CONFLICTS" -ForegroundColor $Colors.Magenta
    Write-Host "=========================" -ForegroundColor $Colors.Magenta
    Write-Host "Comprehensive Python 3.13 Compatibility Solution" -ForegroundColor $Colors.White
    Write-Host ""
}

function Test-PythonCompatibility {
    Write-Host "🔍 Testing Python Compatibility..." -ForegroundColor $Colors.Yellow
    Write-Host "===================================" -ForegroundColor $Colors.Yellow
    
    $pythonVersion = python --version 2>&1
    Write-Host "Current Python: $pythonVersion" -ForegroundColor $Colors.Cyan
    
    if ($pythonVersion -like "*3.13*") {
        Write-Host "⚠️ Python 3.13 detected - known compatibility issues" -ForegroundColor $Colors.Yellow
        Write-Host "   Issues: setuptools, pkg_resources, ImpImporter" -ForegroundColor $Colors.Yellow
        return $false
    } else {
        Write-Host "✅ Python version should be compatible" -ForegroundColor $Colors.Green
        return $true
    }
}

function Install-Python312 {
    Write-Host ""
    Write-Host "🐍 Installing Python 3.12..." -ForegroundColor $Colors.Yellow
    Write-Host "============================" -ForegroundColor $Colors.Yellow
    
    try {
        # Try winget first
        Write-Host "  🔍 Attempting to install Python 3.12 via winget..." -ForegroundColor $Colors.Cyan
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Python 3.12 installed successfully via winget" -ForegroundColor $Colors.Green
            return $true
        }
    } catch {
        Write-Host "  ⚠️ winget installation failed, trying alternative..." -ForegroundColor $Colors.Yellow
    }
    
    # Alternative: Download and install manually
    Write-Host "  🔍 Downloading Python 3.12 manually..." -ForegroundColor $Colors.Cyan
    $pythonUrl = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
    $installerPath = "$env:TEMP\python-3.12.7-amd64.exe"
    
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
        Write-Host "  📥 Downloaded Python 3.12 installer" -ForegroundColor $Colors.Green
        
        # Install silently
        Start-Process -FilePath $installerPath -ArgumentList "/quiet", scripts/AllUsers=1", "PrependPath=1" -Wait
        Write-Host "  ✅ Python 3.12 installed successfully" -ForegroundColor $Colors.Green
        
        # Clean up
        Remove-Item $installerPath -Force
        return $true
    } catch {
        Write-Host "  ❌ Failed to install Python 3.12" -ForegroundColor $Colors.Red
        return $false
    }
}

function Fix-PythonDependencies {
    Write-Host ""
    Write-Host "🔧 Fixing Python Dependencies..." -ForegroundColor $Colors.Yellow
    Write-Host "=================================" -ForegroundColor $Colors.Yellow
    
    # Try to find Python 3.12
    $python312Paths = @(
        "C:\Python312\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe"
    )
    
    $python312 = $null
    foreach ($path in $python312Paths) {
        if (Test-Path $path) {
            $python312 = $path
            Write-Host "  ✅ Found Python 3.12 at: $path" -ForegroundColor $Colors.Green
            break
        }
    }
    
    if (-not $python312) {
        Write-Host "  ❌ Python 3.12 not found" -ForegroundColor $Colors.Red
        return $false
    }
    
    # Update pip and setuptools in Python 3.12
    Write-Host "  🔧 Updating pip and setuptools..." -ForegroundColor $Colors.Cyan
    try {
        & $python312 -m pip install --upgrade pip setuptools wheel
        Write-Host "  ✅ Dependencies updated successfully" -ForegroundColor $Colors.Green
        return $true
    } catch {
        Write-Host "  ❌ Failed to update dependencies" -ForegroundColor $Colors.Red
        return $false
    }
}

function Create-PythonWrapper {
    Write-Host ""
    Write-Host "📝 Creating Python Wrapper..." -ForegroundColor $Colors.Yellow
    Write-Host "=============================" -ForegroundColor $Colors.Yellow
    
    # Find Python 3.12
    $python312Paths = @(
        "C:\Python312\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe"
    )
    
    $python312 = $null
    foreach ($path in $python312Paths) {
        if (Test-Path $path) {
            $python312 = $path
            break
        }
    }
    
    if (-not $python312) {
        Write-Host "  ❌ Python 3.12 not found" -ForegroundColor $Colors.Red
        return $false
    }
    
    # Create a wrapper script
    $wrapperContent = @"
# Python 3.12 Wrapper for Vault API
# This ensures Vault API uses Python 3.12 instead of 3.13

`$python312 = "$python312"

if (Test-Path `$python312) {
    & `$python312 `$args
} else {
    Write-Host "Python 3.12 not found at: `$python312" -ForegroundColor Red
    exit 1
}
"@
    
    $wrapperPath = "python312.ps1"
    $wrapperContent | Out-File -FilePath $wrapperPath -Encoding UTF8
    
    Write-Host "  ✅ Created Python 3.12 wrapper: $wrapperPath" -ForegroundColor $Colors.Green
    return $true
}

function Fix-VaultAPI {
    Write-Host ""
    Write-Host "🔧 Fixing Vault API..." -ForegroundColor $Colors.Yellow
    Write-Host "======================" -ForegroundColor $Colors.Yellow
    
    if (-not (Test-Path servicesservices/vault-api")) {
        Write-Host "  ❌ vault-api directory not found" -ForegroundColor $Colors.Red
        return $false
    }
    
    # Find Python 3.12
    $python312Paths = @(
        "C:\Python312\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe"
    )
    
    $python312 = $null
    foreach ($path in $python312Paths) {
        if (Test-Path $path) {
            $python312 = $path
            break
        }
    }
    
    if (-not $python312) {
        Write-Host "  ❌ Python 3.12 not found" -ForegroundColor $Colors.Red
        return $false
    }
    
    # Install dependencies with Python 3.12
    Write-Host "  🔧 Installing dependencies with Python 3.12..." -ForegroundColor $Colors.Cyan
    try {
        Set-Location vault-api
        
        # Upgrade pip and setuptools first
        & $python312 -m pip install --upgrade pip setuptools wheel --quiet
        
        # Install requirements
        & $python312 -m pip install -r requirements.txt --quiet
        
        Set-Location ..
        Write-Host "  ✅ Vault API dependencies installed successfully" -ForegroundColor $Colors.Green
        return $true
    } catch {
        Set-Location ..
        Write-Host "  ❌ Failed to install Vault API dependencies" -ForegroundColor $Colors.Red
        return $false
    }
}

function Start-ServicesWithPython312 {
    Write-Host ""
    Write-Host "🚀 Starting Services with Python 3.12..." -ForegroundColor $Colors.Yellow
    Write-Host "=========================================" -ForegroundColor $Colors.Yellow
    
    # Find Python 3.12
    $python312Paths = @(
        "C:\Python312\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe"
    )
    
    $python312 = $null
    foreach ($path in $python312Paths) {
        if (Test-Path $path) {
            $python312 = $path
            break
        }
    }
    
    if (-not $python312) {
        Write-Host "  ❌ Python 3.12 not found" -ForegroundColor $Colors.Red
        return $false
    }
    
    # Kill existing processes
    Write-Host "  🛑 Stopping existing processes..." -ForegroundColor $Colors.Cyan
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
    
    # Start Vault API with Python 3.12
    Write-Host "  🚀 Starting Vault API with Python 3.12..." -ForegroundColor $Colors.Cyan
    try {
        $vaultJob = Start-Job -ScriptBlock {
            Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\vault-api"
            & "C:\Python312\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
        } -Name "VaultAPI"
        Write-Host "  ✅ Vault API started (Job ID: $($vaultJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ❌ Failed to start Vault API: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Start other services
    Write-Host "  🚀 Starting other services..." -ForegroundColor $Colors.Cyan
    
    # Start Flyde
    try {
        $flydeJob = Start-Job -ScriptBlock {
            Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\flyde-project"
            npm run dev
        } -Name "Flyde"
        Write-Host "  ✅ Flyde started (Job ID: $($flydeJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ❌ Failed to start Flyde: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Start Motia
    try {
        $motiaJob = Start-Job -ScriptBlock {
            Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\motia-project"
            npm run dev
        } -Name "Motia"
        Write-Host "  ✅ Motia started (Job ID: $($motiaJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ❌ Failed to start Motia: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    # Start Obsidian API
    try {
        $obsidianJob = Start-Job -ScriptBlock {
            Set-Location "D:\codex\master_code\backend_ops\local-api-obsidian_vault\obsidian-api"
            npx motia dev --port 27123
        } -Name "ObsidianAPI"
        Write-Host "  ✅ Obsidian API started (Job ID: $($obsidianJob.Id))" -ForegroundColor $Colors.Green
    } catch {
        Write-Host "  ❌ Failed to start Obsidian API: $($_.Exception.Message)" -ForegroundColor $Colors.Red
    }
    
    return $true
}

function Test-AllServices {
    Write-Host ""
    Write-Host "🧪 Testing All Services..." -ForegroundColor $Colors.Yellow
    Write-Host "=========================" -ForegroundColor $Colors.Yellow
    
    Start-Sleep -Seconds 10  # Wait for services to start
    
    $services = @(
        @{ Name = "Vault API"; Port = 8080; Url = "http://localhost:8080/health" }
        @{ Name = "Flyde"; Port = 3001; Url = "http://localhost:3001/health" }
        @{ Name = "Motia"; Port = 3000; Url = "http://localhost:3000/health" }
        @{ Name = "Obsidian API"; Port = 27123; Url = "http://localhost:27123/health" }
    )
    
    $results = @{}
    
    foreach ($service in $services) {
        Write-Host ""
        Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor $Colors.Cyan
        
        try {
            $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✅ $($service.Name): HEALTHY" -ForegroundColor $Colors.Green
                $results[$service.Name] = $true
            } else {
                Write-Host "  ⚠️ $($service.Name): Status $($response.StatusCode)" -ForegroundColor $Colors.Yellow
                $results[$service.Name] = $false
            }
        } catch {
            Write-Host "  ❌ $($service.Name): NOT RESPONDING" -ForegroundColor $Colors.Red
            $results[$service.Name] = $false
        }
    }
    
    return $results
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
    Write-Host "  🏛️ Vault API: http://localhost:8080" -ForegroundColor $Colors.Cyan
    Write-Host "  🎨 Flyde Studio: http://localhost:3001" -ForegroundColor $Colors.Cyan
    Write-Host "  ⚡ Motia Workbench: http://localhost:3000" -ForegroundColor $Colors.Cyan
    Write-Host "  📝 Obsidian API: http://localhost:27123" -ForegroundColor $Colors.Cyan
    
    if ($successRate -ge 80) {
        Write-Host ""
        Write-Host "🎉 PYTHON CONFLICTS RESOLVED!" -ForegroundColor $Colors.Green
        Write-Host "All services are running with Python 3.12!" -ForegroundColor $Colors.Green
    } else {
        Write-Host ""
        Write-Host "⚠️ SOME SERVICES NEED ATTENTION" -ForegroundColor $Colors.Yellow
        Write-Host scripts/ the status above and restart if needed." -ForegroundColor $Colors.Yellow
    }
}

# Main execution
Show-Banner

if (-not $SkipPython) {
    $compatible = Test-PythonCompatibility
    
    if (-not $compatible) {
        Write-Host ""
        Write-Host "🔧 Python 3.13 compatibility issues detected" -ForegroundColor $Colors.Yellow
        Write-Host scripts/ing Python 3.12 to resolve conflicts..." -ForegroundColor $Colors.Yellow
        
        $installed = Install-Python312
        if ($installed) {
            Fix-PythonDependencies
            Create-PythonWrapper
        } else {
            Write-Host "❌ Failed to install Python 3.12" -ForegroundColor $Colors.Red
            Write-Host "Please install Python 3.12 manually and run this script again" -ForegroundColor $Colors.Yellow
            exit 1
        }
    }
}

Fix-VaultAPI
Start-ServicesWithPython312
$testResults = Test-AllServices
Show-FinalStatus $testResults

Write-Host ""
Write-Host "🔧 Python conflicts resolution complete!" -ForegroundColor $Colors.Magenta
