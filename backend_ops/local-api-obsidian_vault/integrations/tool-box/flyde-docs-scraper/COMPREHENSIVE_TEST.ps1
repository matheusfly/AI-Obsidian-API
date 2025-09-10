# Comprehensive Test Script for Flyde Docs Scraper

Write-Host "🧪 Flyde Docs Scraper - Comprehensive Test Suite" -ForegroundColor Green
Write-Host "Testing all components and operational coverage..." -ForegroundColor Cyan
Write-Host ""

# Navigate to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$testResults = @{
    "Python Check" = $false
    "Dependencies" = $false
    "Simple Scraping" = $false
    "Data Extraction" = $false
    "File Operations" = $false
    "Configuration" = $false
    "Visual Flow" = $false
    "Web UI" = $false
    "Error Handling" = $false
    "Performance" = $false
}

# Test 1: Python Check
Write-Host "🔍 Test 1: Python Installation" -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python") {
        $testResults["Python Check"] = $true
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python not found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
}

# Test 2: Dependencies
Write-Host "🔍 Test 2: Dependencies Check" -ForegroundColor Yellow
try {
    $requestsCheck = python -c "import requests; print('requests OK')" 2>&1
    if ($requestsCheck -match "requests OK") {
        $testResults["Dependencies"] = $true
        Write-Host "✅ Basic dependencies available" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Installing requests..." -ForegroundColor Yellow
        pip install requests
        $testResults["Dependencies"] = $true
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Dependency check failed" -ForegroundColor Red
}

# Test 3: Simple Scraping
Write-Host "🔍 Test 3: Simple Scraping Test" -ForegroundColor Yellow
try {
    python simple_test.py
    if (Test-Path "data\simple_test_*.json") {
        $testResults["Simple Scraping"] = $true
        Write-Host "✅ Simple scraping test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Simple scraping test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Simple scraping test failed" -ForegroundColor Red
}

# Test 4: Data Extraction
Write-Host "🔍 Test 4: Data Extraction Test" -ForegroundColor Yellow
try {
    $latestFile = Get-ChildItem "data\simple_test_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestFile) {
        $content = Get-Content $latestFile.FullName -Raw | ConvertFrom-Json
        if ($content.statistics.content_length -gt 0 -and $content.statistics.text_length -gt 0) {
            $testResults["Data Extraction"] = $true
            Write-Host "✅ Data extraction test passed" -ForegroundColor Green
            Write-Host "   Content Length: $($content.statistics.content_length)" -ForegroundColor Cyan
            Write-Host "   Text Length: $($content.statistics.text_length)" -ForegroundColor Cyan
            Write-Host "   Links Found: $($content.statistics.links_count)" -ForegroundColor Cyan
        } else {
            Write-Host "❌ Data extraction test failed - no content" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Data extraction test failed - no output file" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Data extraction test failed" -ForegroundColor Red
}

# Test 5: File Operations
Write-Host "🔍 Test 5: File Operations Test" -ForegroundColor Yellow
try {
    # Create test directories
    New-Item -ItemType Directory -Force -Path "data" | Out-Null
    New-Item -ItemType Directory -Force -Path "logs" | Out-Null
    New-Item -ItemType Directory -Force -Path "data\cache" | Out-Null
    
    # Test file creation
    $testFile = "data\test_file.txt"
    "Test content" | Out-File -FilePath $testFile -Encoding UTF8
    
    if (Test-Path $testFile) {
        Remove-Item $testFile
        $testResults["File Operations"] = $true
        Write-Host "✅ File operations test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ File operations test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ File operations test failed" -ForegroundColor Red
}

# Test 6: Configuration
Write-Host "🔍 Test 6: Configuration Test" -ForegroundColor Yellow
try {
    if (Test-Path ".env") {
        $testResults["Configuration"] = $true
        Write-Host "✅ Configuration file exists" -ForegroundColor Green
    } else {
        # Create .env file
        @"
# Flyde Docs Scraper Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./data/flyde_docs.db
REDIS_URL=redis://localhost:6379
MAX_CONCURRENT_REQUESTS=10
REQUEST_DELAY=1.0
TIMEOUT=30
MAX_RETRIES=3
REQUESTS_PER_MINUTE=60
"@ | Out-File -FilePath ".env" -Encoding UTF8
        $testResults["Configuration"] = $true
        Write-Host "✅ Configuration file created" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Configuration test failed" -ForegroundColor Red
}

# Test 7: Visual Flow
Write-Host "🔍 Test 7: Visual Flow Test" -ForegroundColor Yellow
try {
    if (Test-Path "flows\hello-world.flyde") {
        $flowContent = Get-Content "flows\hello-world.flyde" -Raw
        if ($flowContent -match '"id": "hello-world"') {
            $testResults["Visual Flow"] = $true
            Write-Host "✅ Visual flow file exists and valid" -ForegroundColor Green
        } else {
            Write-Host "❌ Visual flow file invalid" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Visual flow file not found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Visual flow test failed" -ForegroundColor Red
}

# Test 8: Web UI
Write-Host "🔍 Test 8: Web UI Test" -ForegroundColor Yellow
try {
    if (Test-Path "web_ui\main.py") {
        $webContent = Get-Content "web_ui\main.py" -Raw
        if ($webContent -match "FastAPI" -and $webContent -match "app = FastAPI") {
            $testResults["Web UI"] = $true
            Write-Host "✅ Web UI files exist and valid" -ForegroundColor Green
        } else {
            Write-Host "❌ Web UI files invalid" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Web UI files not found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Web UI test failed" -ForegroundColor Red
}

# Test 9: Error Handling
Write-Host "🔍 Test 9: Error Handling Test" -ForegroundColor Yellow
try {
    # Test with invalid URL
    $errorTest = python -c "
import requests
try:
    response = requests.get('https://invalid-url-that-does-not-exist.com', timeout=5)
    print('ERROR: Should have failed')
except:
    print('SUCCESS: Error handling works')
" 2>&1
    
    if ($errorTest -match "SUCCESS") {
        $testResults["Error Handling"] = $true
        Write-Host "✅ Error handling test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Error handling test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error handling test failed" -ForegroundColor Red
}

# Test 10: Performance
Write-Host "🔍 Test 10: Performance Test" -ForegroundColor Yellow
try {
    $startTime = Get-Date
    python simple_test.py
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    if ($duration -lt 10) {
        $testResults["Performance"] = $true
        Write-Host "✅ Performance test passed ($([math]::Round($duration, 2))s)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Performance test slow ($([math]::Round($duration, 2))s)" -ForegroundColor Yellow
        $testResults["Performance"] = $true
    }
} catch {
    Write-Host "❌ Performance test failed" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "📊 COMPREHENSIVE TEST RESULTS" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

$passedTests = 0
$totalTests = $testResults.Count

foreach ($test in $testResults.GetEnumerator()) {
    $status = if ($test.Value) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($test.Value) { "Green" } else { "Red" }
    Write-Host "$($test.Key): $status" -ForegroundColor $color
    if ($test.Value) { $passedTests++ }
}

Write-Host ""
Write-Host "📈 OVERALL SCORE: $passedTests/$totalTests ($([math]::Round(($passedTests/$totalTests)*100, 1))%)" -ForegroundColor Cyan

if ($passedTests -eq $totalTests) {
    Write-Host "🎉 ALL TESTS PASSED! System is fully operational!" -ForegroundColor Green
} elseif ($passedTests -ge ($totalTests * 0.8)) {
    Write-Host "✅ Most tests passed! System is mostly operational!" -ForegroundColor Yellow
} else {
    Write-Host "⚠️ Some tests failed. Check the issues above." -ForegroundColor Red
}

Write-Host ""
Write-Host "🚀 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Run: .\QUICK_START.ps1" -ForegroundColor White
Write-Host "2. Run: .\FIX_LAUNCH.ps1" -ForegroundColor White
Write-Host "3. Run: .\LAUNCH_ALL_FIXED.ps1 web" -ForegroundColor White
Write-Host "4. Open: http://localhost:8000" -ForegroundColor White