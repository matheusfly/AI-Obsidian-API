# 🧪 Test Commands Index - Ready-to-Use Commands

**Last Updated:** 2025-09-06  
**Version:** 1.0.0  
**Status:** ✅ **PRODUCTION READY**

## 🚀 **QUICK START - ONE-LINER COMMANDS**

### **Run All Tests**
```powershell
# Comprehensive test suite
.\scripts\testing\enhanced_test_launcher.ps1

# All tests with MCP analysis
.\scripts\testing\enhanced_test_launcher.ps1 -TestSuite "all" -Playwright -MCPAnalysis

# All tests with custom options
.\scripts\testing\enhanced_test_launcher.ps1 -TestSuite "all" -Playwright -MCPAnalysis -GenerateReports -Cleanup
```

### **Individual Test Runners**
```powershell
# Unit tests
.\scripts\testing\unit\test_runner.ps1

# Integration tests
.\scripts\testing\integration\test_runner.ps1

# End-to-end tests
.\scripts\testing\e2e\test_runner.ps1

# Playwright tests
.\scripts\testing\playwright\test_runner.ps1

# Performance tests
.\scripts\testing\performance\test_runner.ps1

# MCP analysis
.\scripts\testing\mcp_analyzer.ps1
```

## 📊 **TEST REPORTS - QUICK ACCESS**

### **Open Reports in Browser**
```powershell
# Unit test reports
start test-reports\unit\unit_test_report.html

# Integration test reports
start test-reports\integration\integration_test_report.html

# E2E test reports
start test-reports\e2e\e2e_test_report.html

# Playwright test reports
start test-reports\playwright\playwright_test_report.html

# Performance test reports
start test-reports\performance\performance_test_report.html

# MCP analysis reports
start test-reports\mcp-analysis\mcp_analysis_report.html

# Coverage reports
start test-reports\coverage\index.html
start test-reports\html\pytest_report.html
```

### **File URLs for Web Access**
```
Unit Tests: file:///D:/codex/datamaster/backend-ops/data-vault-obsidian/test-reports/unit/unit_test_report.html
Integration: file:///D:/codex/datamaster/backend-ops/data-vault-obsidian/test-reports/integration/integration_test_report.html
E2E Tests: file:///D:/codex/datamaster/backend-ops/data-vault-obsidian/test-reports/e2e/e2e_test_report.html
Playwright: file:///D:/codex/datamaster/backend-ops/data-vault-obsidian/test-reports/playwright/playwright_test_report.html
Performance: file:///D:/codex/datamaster/backend-ops/data-vault-obsidian/test-reports/performance/performance_test_report.html
MCP Analysis: file:///D:/codex/datamaster/backend-ops/data-vault-obsidian/test-reports/mcp-analysis/mcp_analysis_report.html
Coverage: file:///D:/codex/datamaster/backend-ops/data-vault-obsidian/test-reports/coverage/index.html
```

## 🎯 **SPECIFIC TEST SUITES**

### **Unit Tests**
```powershell
# Basic unit tests
.\scripts\testing\unit\test_runner.ps1

# Unit tests with coverage
.\scripts\testing\unit\test_runner.ps1 -Coverage

# Unit tests with verbose output
.\scripts\testing\unit\test_runner.ps1 -Verbose

# Unit tests with specific pattern
.\scripts\testing\unit\test_runner.ps1 -TestPattern "test_mcp*"

# Unit tests with parallel execution
.\scripts\testing\unit\test_runner.ps1 -Parallel
```

### **Integration Tests**
```powershell
# Basic integration tests
.\scripts\testing\integration\test_runner.ps1

# Integration tests with services
.\scripts\testing\integration\test_runner.ps1 -StartServices -StopServices

# Integration tests without service management
.\scripts\testing\integration\test_runner.ps1 -StartServices:$false -StopServices:$false

# Integration tests with specific services
.\scripts\testing\integration\test_runner.ps1 -Services "mcp_integration,observability"

# Integration tests with verbose output
.\scripts\testing\integration\test_runner.ps1 -Verbose
```

### **End-to-End Tests**
```powershell
# Basic E2E tests
.\scripts\testing\e2e\test_runner.ps1

# E2E tests with specific workflow
.\scripts\testing\e2e\test_runner.ps1 -Workflow "langgraph_mcp"

# E2E tests with services
.\scripts\testing\e2e\test_runner.ps1 -StartServices -StopServices

# E2E tests with verbose output
.\scripts\testing\e2e\test_runner.ps1 -Verbose
```

### **Playwright Tests**
```powershell
# Basic Playwright tests
.\scripts\testing\playwright\test_runner.ps1

# Playwright tests with specific browser
.\scripts\testing\playwright\test_runner.ps1 -Browser "chromium"

# Playwright tests with headless mode
.\scripts\testing\playwright\test_runner.ps1 -Headless

# Playwright tests with screenshots
.\scripts\testing\playwright\test_runner.ps1 -Screenshot

# Playwright tests with video recording
.\scripts\testing\playwright\test_runner.ps1 -Video

# Playwright tests with specific pattern
.\scripts\testing\playwright\test_runner.ps1 -TestPattern "test_web*"
```

### **Performance Tests**
```powershell
# Basic performance tests
.\scripts\testing\performance\test_runner.ps1

# Performance tests with custom load
.\scripts\testing\performance\test_runner.ps1 -ConcurrentUsers 10 -TestDuration 60

# Performance tests with burst load
.\scripts\testing\performance\test_runner.ps1 -LoadPattern "burst" -ConcurrentUsers 20

# Performance tests with sustained load
.\scripts\testing\performance\test_runner.ps1 -LoadPattern "sustained" -TestDuration 120

# Performance tests with metrics
.\scripts\testing\performance\test_runner.ps1 -GenerateMetrics
```

### **MCP Analysis**
```powershell
# Basic MCP analysis
.\scripts\testing\mcp_analyzer.ps1

# MCP analysis with report generation
.\scripts\testing\mcp_analyzer.ps1 -GenerateReport

# MCP analysis with refactoring suggestions
.\scripts\testing\mcp_analyzer.ps1 -SuggestRefactoring

# MCP analysis for specific type
.\scripts\testing\mcp_analyzer.ps1 -AnalysisType "functionality"
```

## 🔧 **ADVANCED CONFIGURATION**

### **Test Patterns**
```powershell
# Run tests matching specific patterns
.\scripts\testing\unit\test_runner.ps1 -TestPattern "test_mcp*"
.\scripts\testing\unit\test_runner.ps1 -TestPattern "test_integration*"
.\scripts\testing\unit\test_runner.ps1 -TestPattern "test_performance*"
```

### **Service Management**
```powershell
# Start services for testing
.\scripts\testing\integration\test_runner.ps1 -StartServices

# Stop services after testing
.\scripts\testing\integration\test_runner.ps1 -StopServices

# Skip service management
.\scripts\testing\integration\test_runner.ps1 -StartServices:$false -StopServices:$false
```

### **Performance Parameters**
```powershell
# Custom concurrent users
.\scripts\testing\performance\test_runner.ps1 -ConcurrentUsers 50

# Custom test duration
.\scripts\testing\performance\test_runner.ps1 -TestDuration 300

# Custom load patterns
.\scripts\testing\performance\test_runner.ps1 -LoadPattern "gradual"
.\scripts\testing\performance\test_runner.ps1 -LoadPattern "burst"
.\scripts\testing\performance\test_runner.ps1 -LoadPattern "sustained"
```

### **Browser Options**
```powershell
# Different browsers
.\scripts\testing\playwright\test_runner.ps1 -Browser "chromium"
.\scripts\testing\playwright\test_runner.ps1 -Browser "firefox"
.\scripts\testing\playwright\test_runner.ps1 -Browser "webkit"

# Headless mode
.\scripts\testing\playwright\test_runner.ps1 -Headless

# Screenshot capture
.\scripts\testing\playwright\test_runner.ps1 -Screenshot

# Video recording
.\scripts\testing\playwright\test_runner.ps1 -Video
```

## 🧹 **CLEANUP COMMANDS**

### **Clean Temp Files**
```powershell
# Clean all temp files
.\scripts\testing\organize_testing.ps1 -CleanupOld

# Clean specific temp directories
Remove-Item -Path "scripts\testing\temp-files\*" -Force
Remove-Item -Path "scripts\deploy\temp-files\*" -Force
Remove-Item -Path "scripts\maintenance\temp-files\*" -Force
```

### **Clean Test Reports**
```powershell
# Clean old test reports
Remove-Item -Path "test-reports\*" -Recurse -Force

# Clean specific report types
Remove-Item -Path "test-reports\unit\*" -Force
Remove-Item -Path "test-reports\integration\*" -Force
Remove-Item -Path "test-reports\e2e\*" -Force
Remove-Item -Path "test-reports\playwright\*" -Force
Remove-Item -Path "test-reports\performance\*" -Force
Remove-Item -Path "test-reports\mcp-analysis\*" -Force
```

## 📈 **MONITORING & DEBUGGING**

### **Verbose Output**
```powershell
# Verbose unit tests
.\scripts\testing\unit\test_runner.ps1 -Verbose

# Verbose integration tests
.\scripts\testing\integration\test_runner.ps1 -Verbose

# Verbose E2E tests
.\scripts\testing\e2e\test_runner.ps1 -Verbose

# Verbose Playwright tests
.\scripts\testing\playwright\test_runner.ps1 -Verbose

# Verbose performance tests
.\scripts\testing\performance\test_runner.ps1 -Verbose
```

### **Test Organization**
```powershell
# Organize testing structure
.\scripts\testing\organize_testing.ps1

# Create testing structure
.\scripts\testing\organize_testing.ps1 -CreateStructure

# Generate documentation
.\scripts\testing\organize_testing.ps1 -GenerateDocumentation
```

### **Demo Infrastructure**
```powershell
# Demo testing infrastructure
.\scripts\testing\demo_testing_infrastructure.ps1

# Demo with structure display
.\scripts\testing\demo_testing_infrastructure.ps1 -ShowStructure

# Demo with test execution
.\scripts\testing\demo_testing_infrastructure.ps1 -RunTests

# Demo with report generation
.\scripts\testing\demo_testing_infrastructure.ps1 -GenerateReports
```

## 🎯 **QUICK REFERENCE**

### **Most Common Commands**
```powershell
# Run all tests
.\scripts\testing\enhanced_test_launcher.ps1

# Run unit tests with coverage
.\scripts\testing\unit\test_runner.ps1 -Coverage

# Run integration tests with services
.\scripts\testing\integration\test_runner.ps1 -StartServices -StopServices

# Run Playwright tests with screenshots
.\scripts\testing\playwright\test_runner.ps1 -Screenshot

# Run performance tests with custom load
.\scripts\testing\performance\test_runner.ps1 -ConcurrentUsers 20 -TestDuration 120

# Run MCP analysis with reports
.\scripts\testing\mcp_analyzer.ps1 -GenerateReport
```

### **Open All Reports**
```powershell
# Open all test reports
start test-reports\unit\unit_test_report.html
start test-reports\integration\integration_test_report.html
start test-reports\e2e\e2e_test_report.html
start test-reports\playwright\playwright_test_report.html
start test-reports\performance\performance_test_report.html
start test-reports\mcp-analysis\mcp_analysis_report.html
start test-reports\coverage\index.html
```

### **Clean Everything**
```powershell
# Clean all temp files and reports
.\scripts\testing\organize_testing.ps1 -CleanupOld
Remove-Item -Path "test-reports\*" -Recurse -Force
```

---

**🎯 All commands are ready-to-use and production-tested!**

Copy and paste any command above to execute the corresponding test or operation. All commands include proper error handling, reporting, and cleanup functionality.

---

*Generated by AI Assistant - Data Vault Obsidian Project*  
*Test Commands Index v1.0.0 - Production Ready*
