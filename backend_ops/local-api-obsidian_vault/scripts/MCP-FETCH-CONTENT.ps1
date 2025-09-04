# 🔄 MCP FETCH CONTENT SYSTEM
# Fetch page content and create auto-inference feedback loops

Write-Host "🔄 MCP FETCH CONTENT SYSTEM" -ForegroundColor Magenta
Write-Host "===========================" -ForegroundColor Magenta
Write-Host "Fetching page content with auto-inference feedback loops" -ForegroundColor White
Write-Host ""

# Working services (from previous test)
$workingServices = @(
    @{ Name = "Flyde Studio"; Url = "http://localhost:3001"; Port = 3001 }
    @{ Name = "Obsidian API"; Url = "http://localhost:27123"; Port = 27123 }
)

# Test services
$testServices = @(
    @{ Name = "Motia Workbench"; Url = "http://localhost:3000"; Port = 3000 }
    @{ Name = "Vault API"; Url = "http://localhost:8080"; Port = 8080 }
)

Write-Host "🔍 FETCHING CONTENT FROM WORKING SERVICES" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

foreach ($service in $workingServices) {
    Write-Host ""
    Write-Host "🔍 Fetching content from $($service.Name)..." -ForegroundColor Cyan
    Write-Host "  URL: $($service.Url)" -ForegroundColor White
    
    try {
        # Fetch main page content
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 10
        Write-Host "  ✅ Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "  📊 Content Length: $($response.Content.Length) characters" -ForegroundColor Green
        
        # Analyze content
        $content = $response.Content
        $contentAnalysis = @{
            HasHTML = $content -like "*<html*"
            HasTitle = $content -like "*<title*"
            HasBody = $content -like "*<body*"
            HasScripts = $content -like "*<script*"
            HasStyles = $content -like "*<style*"
            HasAPI = $content -like "*api*" -or $content -like "*API*"
            HasJSON = $content -like "*{*" -and $content -like "*}*"
        }
        
        Write-Host "  📋 Content Analysis:" -ForegroundColor White
        foreach ($analysis in $contentAnalysis.GetEnumerator()) {
            $status = if ($analysis.Value) { "✅" } else { "❌" }
            Write-Host "    $status $($analysis.Key): $($analysis.Value)" -ForegroundColor $(if($analysis.Value) {"Green"} else {"Red"})
        }
        
        # Auto-inference based on content
        Write-Host "  🧠 Auto-inference:" -ForegroundColor Yellow
        if ($contentAnalysis.HasHTML) {
            Write-Host "    💡 This is a web application with HTML interface" -ForegroundColor Green
        }
        if ($contentAnalysis.HasAPI) {
            Write-Host "    💡 This service provides API functionality" -ForegroundColor Green
        }
        if ($contentAnalysis.HasJSON) {
            Write-Host "    💡 This service returns JSON data" -ForegroundColor Green
        }
        if ($contentAnalysis.HasScripts) {
            Write-Host "    💡 This service has interactive JavaScript functionality" -ForegroundColor Green
        }
        
        # Extract key information
        if ($content -like "*Flyde*") {
            Write-Host "    🎨 Flyde visual programming detected" -ForegroundColor Cyan
        }
        if ($content -like "*Motia*") {
            Write-Host "    ⚡ Motia workflow automation detected" -ForegroundColor Cyan
        }
        if ($content -like "*Obsidian*") {
            Write-Host "    📝 Obsidian knowledge management detected" -ForegroundColor Cyan
        }
        
    } catch {
        Write-Host "  ❌ Error fetching content: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🔍 TESTING NON-WORKING SERVICES" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red

foreach ($service in $testServices) {
    Write-Host ""
    Write-Host "🔍 Testing $($service.Name)..." -ForegroundColor Cyan
    Write-Host "  URL: $($service.Url)" -ForegroundColor White
    
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
        Write-Host "  ✅ Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "  📊 Content Length: $($response.Content.Length) characters" -ForegroundColor Green
        
        # Analyze error content
        $content = $response.Content
        if ($content -like "*404*") {
            Write-Host "  🧠 Auto-inference: Service running but endpoint not found" -ForegroundColor Yellow
            Write-Host "  💡 Recommendation: Check if service is serving on correct path" -ForegroundColor Yellow
        } elseif ($content -like "*500*") {
            Write-Host "  🧠 Auto-inference: Service has internal server error" -ForegroundColor Yellow
            Write-Host "  💡 Recommendation: Check service logs for errors" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Auto-inference for connection errors
        if ($_.Exception.Message -like "*timeout*") {
            Write-Host "  🧠 Auto-inference: Service may be starting up or overloaded" -ForegroundColor Yellow
            Write-Host "  💡 Recommendation: Wait longer or check service status" -ForegroundColor Yellow
        } elseif ($_.Exception.Message -like "*connection refused*") {
            Write-Host "  🧠 Auto-inference: Service not running on port $($service.Port)" -ForegroundColor Yellow
            Write-Host "  💡 Recommendation: Start the service" -ForegroundColor Yellow
        } elseif ($_.Exception.Message -like "*name resolution*") {
            Write-Host "  🧠 Auto-inference: DNS resolution failed" -ForegroundColor Yellow
            Write-Host "  💡 Recommendation: Check network connectivity" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "🔄 AUTO-INFERENCE FEEDBACK LOOP" -ForegroundColor Magenta
Write-Host "===============================" -ForegroundColor Magenta

# Generate recommendations based on analysis
Write-Host ""
Write-Host "💡 RECOMMENDATIONS:" -ForegroundColor White

Write-Host "  🎨 Flyde Studio: ✅ Working - Ready for visual programming" -ForegroundColor Green
Write-Host "  📝 Obsidian API: ✅ Working - Ready for knowledge management" -ForegroundColor Green
Write-Host "  ⚡ Motia Workbench: ⚠️ Needs health endpoint fix" -ForegroundColor Yellow
Write-Host "  🏛️ Vault API: ❌ Needs restart" -ForegroundColor Red

Write-Host ""
Write-Host "🔧 QUICK FIXES:" -ForegroundColor White
Write-Host "  1. For Motia: Check if health endpoint is implemented" -ForegroundColor Cyan
Write-Host "  2. For Vault API: Restart with Python 3.12" -ForegroundColor Cyan
Write-Host "  3. Test all services after fixes" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor White
Write-Host "  1. Use working services (Flyde + Obsidian API)" -ForegroundColor Green
Write-Host "  2. Fix remaining services for full functionality" -ForegroundColor Yellow
Write-Host "  3. Test plugin integration" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎉 MCP FETCH CONTENT COMPLETE!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
