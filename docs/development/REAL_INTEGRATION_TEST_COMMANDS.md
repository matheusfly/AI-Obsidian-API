# 🧪 REAL INTEGRATION TEST COMMANDS - QUICK REFERENCE

**Version:** 1.0.0  
**Last Updated:** 2025-09-06  
**Status:** ✅ **ACTIVE PRODUCTION COMMANDS**

---

## 🚀 **QUICK START COMMANDS**

### **Run All Real Integration Tests**
```powershell
# Run complete real integration test suite
.\scripts\testing\real_mcp_integration_test.ps1

# Run with debug mode
.\scripts\testing\real_mcp_integration_test.ps1 -Debug

# Run with verbose output
.\scripts\testing\real_mcp_integration_test.ps1 -Verbose
```

### **Run Individual Test Types**
```powershell
# Test only MCP functionality
.\scripts\testing\real_mcp_integration_test.ps1 -TestType "mcp"

# Test only LangGraph functionality
.\scripts\testing\real_mcp_integration_test.ps1 -TestType "langgraph"

# Test only service integration
.\scripts\testing\real_mcp_integration_test.ps1 -TestType "integration"

# Test only performance
.\scripts\testing\real_mcp_integration_test.ps1 -TestType "performance"
```

---

## 🎭 **PLAYWRIGHT TEST COMMANDS**

### **Run Playwright Tests (Fixed)**
```powershell
# Run Playwright tests with timeout fixes
.\scripts\testing\playwright\test_runner.ps1

# Run with specific browser
.\scripts\testing\playwright\test_runner.ps1 -Browser "chromium"

# Run with headless mode
.\scripts\testing\playwright\test_runner.ps1 -Headless

# Run with screenshots
.\scripts\testing\playwright\test_runner.ps1 -Screenshot

# Run with video recording
.\scripts\testing\playwright\test_runner.ps1 -Video
```

### **Run MCP Playwright Integration**
```powershell
# Run MCP Playwright integration tests
.\scripts\testing\mcp_playwright_integration.ps1

# Run with debug mode
.\scripts\testing\mcp_playwright_integration.ps1 -Debug

# Run with verbose output
.\scripts\testing\mcp_playwright_integration.ps1 -Verbose
```

---

## 🔧 **MCP INTEGRATION COMMANDS**

### **Test MCP Tool Execution**
```powershell
# Test MCP tools directly
Invoke-RestMethod -Uri "http://127.0.0.1:8001/mcp/tools" -Method GET

# Execute MCP tool
$toolData = @{ tool = "test_tool"; parameters = @{ test = "value" } } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8001/mcp/tools/execute" -Method POST -Body $toolData -ContentType "application/json"

# Access MCP resources
Invoke-RestMethod -Uri "http://127.0.0.1:8001/mcp/resources" -Method GET
```

### **Test MCP Health**
```powershell
# Check MCP service health
Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -Method GET

# Check MCP service status
Invoke-RestMethod -Uri "http://127.0.0.1:8001/status" -Method GET
```

---

## 🎭 **LANGGRAPH INTEGRATION COMMANDS**

### **Test LangGraph Workflow Execution**
```powershell
# Execute LangGraph workflow
$workflowData = @{ workflow = "test_workflow"; input = @{ message = "Hello" } } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:2024/workflows/execute" -Method POST -Body $workflowData -ContentType "application/json"

# Get workflow status
Invoke-RestMethod -Uri "http://127.0.0.1:2024/workflows/status" -Method GET

# List available workflows
Invoke-RestMethod -Uri "http://127.0.0.1:2024/workflows" -Method GET
```

### **Test LangGraph Health**
```powershell
# Check LangGraph Studio health
Invoke-RestMethod -Uri "http://127.0.0.1:2024/health" -Method GET

# Check LangGraph Studio status
Invoke-RestMethod -Uri "http://127.0.0.1:2024/status" -Method GET
```

---

## 🔗 **SERVICE INTEGRATION COMMANDS**

### **Test Service-to-Service Communication**
```powershell
# Test MCP to LangGraph integration
$integrationData = @{ source = "mcp"; target = "langgraph"; data = @{ message = "test" } } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8001/integrate/langgraph" -Method POST -Body $integrationData -ContentType "application/json"

# Test data flow validation
$dataFlowTest = @{ test_type = "data_flow"; steps = @("mcp_input", "processing", "langgraph_execution", "output") } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8001/test/data-flow" -Method POST -Body $dataFlowTest -ContentType "application/json"
```

### **Test All Service Health**
```powershell
# Check all services health
$services = @("http://127.0.0.1:8001/health", "http://127.0.0.1:8002/health", "http://127.0.0.1:8003/health", "http://127.0.0.1:2024/health")
foreach ($service in $services) { try { $response = Invoke-RestMethod -Uri $service -Method GET; Write-Host "$service : $($response.status)" } catch { Write-Host "$service : ERROR" } }
```

---

## ⚡ **PERFORMANCE TEST COMMANDS**

### **Test Response Times**
```powershell
# Test MCP response time
$startTime = Get-Date; Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -Method GET; $endTime = Get-Date; Write-Host "MCP Response Time: $(($endTime - $startTime).TotalMilliseconds)ms"

# Test LangGraph response time
$startTime = Get-Date; Invoke-RestMethod -Uri "http://127.0.0.1:2024/health" -Method GET; $endTime = Get-Date; Write-Host "LangGraph Response Time: $(($endTime - $startTime).TotalMilliseconds)ms"

# Test Observability response time
$startTime = Get-Date; Invoke-RestMethod -Uri "http://127.0.0.1:8002/health" -Method GET; $endTime = Get-Date; Write-Host "Observability Response Time: $(($endTime - $startTime).TotalMilliseconds)ms"
```

### **Test Concurrent Requests**
```powershell
# Test concurrent MCP requests
$jobs = @(); for ($i = 0; $i -lt 5; $i++) { $jobs += Start-Job -ScriptBlock { Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -Method GET } }; $jobs | Wait-Job | Receive-Job; $jobs | Remove-Job
```

---

## 📊 **REPORTING COMMANDS**

### **Open Test Reports**
```powershell
# Open real integration report
start test-reports/real_integration_test_report.html

# Open Playwright HTML report
start test-reports/playwright/playwright-results/index.html

# Open MCP Playwright report
start test-reports/mcp-playwright-integration/mcp_playwright_report.html

# Open coverage report
start test-reports/coverage/index.html
```

### **Generate All Reports**
```powershell
# Run all tests and generate reports
.\scripts\testing\real_mcp_integration_test.ps1; .\scripts\testing\playwright\test_runner.ps1; .\scripts\testing\mcp_playwright_integration.ps1
```

---

## 🧹 **CLEANUP COMMANDS**

### **Clean Test Artifacts**
```powershell
# Clean Playwright test artifacts
Remove-Item -Path "test-reports/playwright/playwright-results" -Recurse -Force -ErrorAction SilentlyContinue

# Clean MCP test artifacts
Remove-Item -Path "test-reports/mcp-playwright-integration" -Recurse -Force -ErrorAction SilentlyContinue

# Clean all test reports
Remove-Item -Path "test-reports" -Recurse -Force -ErrorAction SilentlyContinue
```

### **Reset Test Environment**
```powershell
# Reset all test environments
.\scripts\testing\real_mcp_integration_test.ps1; .\scripts\testing\playwright\test_runner.ps1; .\scripts\testing\mcp_playwright_integration.ps1; Write-Host "All tests completed and reports generated!"
```

---

## 🎯 **QUICK DEBUGGING COMMANDS**

### **Debug MCP Issues**
```powershell
# Check MCP service logs
Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*mcp*" }

# Check MCP port usage
netstat -an | findstr "8001"

# Test MCP connectivity
Test-NetConnection -ComputerName "127.0.0.1" -Port 8001
```

### **Debug LangGraph Issues**
```powershell
# Check LangGraph service logs
Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*langgraph*" }

# Check LangGraph port usage
netstat -an | findstr "2024"

# Test LangGraph connectivity
Test-NetConnection -ComputerName "127.0.0.1" -Port 2024
```

---

## 🚀 **ONE-LINER MASTER COMMANDS**

### **Complete Test Suite**
```powershell
# Run everything and generate all reports
.\scripts\testing\real_mcp_integration_test.ps1; .\scripts\testing\playwright\test_runner.ps1; .\scripts\testing\mcp_playwright_integration.ps1; Write-Host "🎉 ALL TESTS COMPLETED! Check test-reports/ folder for results."
```

### **Quick Health Check**
```powershell
# Quick health check of all services
$services = @("http://127.0.0.1:8001/health", "http://127.0.0.1:8002/health", "http://127.0.0.1:8003/health", "http://127.0.0.1:2024/health"); foreach ($service in $services) { try { $response = Invoke-RestMethod -Uri $service -Method GET; Write-Host "✅ $service : $($response.status)" -ForegroundColor Green } catch { Write-Host "❌ $service : ERROR" -ForegroundColor Red } }
```

### **Open All Reports**
```powershell
# Open all test reports in browser
start test-reports/real_integration_test_report.html; start test-reports/playwright/playwright-results/index.html; start test-reports/mcp-playwright-integration/mcp_playwright_report.html; start test-reports/coverage/index.html
```

---

## 📋 **COMMAND CATEGORIES**

| **Category** | **Purpose** | **Key Commands** |
|-------------|-------------|------------------|
| **Real Integration** | Test actual functionality | `.\scripts\testing\real_mcp_integration_test.ps1` |
| **Playwright** | Test web interfaces | `.\scripts\testing\playwright\test_runner.ps1` |
| **MCP Integration** | Test MCP functionality | `.\scripts\testing\mcp_playwright_integration.ps1` |
| **Health Checks** | Verify service status | `Invoke-RestMethod -Uri "http://127.0.0.1:8001/health"` |
| **Performance** | Test response times | Response time measurement commands |
| **Reporting** | Generate and view reports | `start test-reports/...` |
| **Debugging** | Troubleshoot issues | Debug commands above |
| **Cleanup** | Clean test artifacts | Cleanup commands above |

---

## 🎯 **SUCCESS METRICS**

- **Real Integration Tests**: Test actual functionality, not just docs
- **Playwright Tests**: Test web interfaces with proper timeouts
- **MCP Integration**: Test tool execution and resource access
- **Service Integration**: Test service-to-service communication
- **Performance Tests**: Test actual response times and metrics
- **Reporting**: Generate comprehensive HTML reports
- **Debugging**: Provide tools for troubleshooting

---

**REAL INTEGRATION TESTING COMPLETE!** 🎉

*Generated by AI Assistant - Data Vault Obsidian Project*  
*Real Integration Test Commands v1.0.0 - Production-Grade Testing*
