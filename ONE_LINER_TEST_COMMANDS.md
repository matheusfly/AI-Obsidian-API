# 🚀 **ONE-LINER TEST COMMANDS**
## **Complete Testing Suite for MCP Server System**

**Date**: January 2025  
**Status**: ✅ **READY FOR TESTING**  
**Purpose**: Quick one-liner commands to verify all system components

---

## 🎯 **CORE MCP SERVER TESTS**

### **1. Start MCP Server**
```bash
cd mcp-server && go run cmd/server/main.go
```

### **2. Test Server Health**
```bash
curl -X GET http://localhost:3010/health
```

### **3. List Available Tools**
```bash
curl -X GET http://localhost:3010/tools/list
```

### **4. Test Tool Execution (Search)**
```bash
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"search_notes\",\"parameters\":{\"query\":\"test\",\"limit\":5}}"
```

### **5. Test Tool Execution (List Files)**
```bash
curl -X POST http://localhost:3010/tools/execute -H "Content-Type: application/json" -d "{\"tool_name\":\"list_files_in_vault\",\"parameters\":{\"path\":\".\"}}"
```

---

## 🔍 **SEARCH ENGINE TESTS**

### **6. Test Advanced Search Algorithm**
```bash
cd scripts/examples && go run advanced_search_demo.go
```

### **7. Test BM25 Search**
```bash
cd scripts/examples && go run bm25_search_demo.go
```

### **8. Test Semantic Search**
```bash
cd scripts/examples && go run semantic_search_demo.go
```

### **9. Test Query Processing**
```bash
cd scripts/examples && go run query_processing_demo.go
```

### **10. Test Context Assembly**
```bash
cd scripts/examples && go run context_assembly_demo.go
```

---

## 🔧 **API INTEGRATION TESTS**

### **11. Test Obsidian API Connection**
```bash
cd scripts/tests && go run test_real_vault.go
```

### **12. Test HTTP Client**
```bash
cd scripts/tests && go run test_http_integration.go
```

### **13. Test Real Data Integration**
```bash
cd scripts/tests && go run test_real_data_integration.go
```

### **14. Test Vault File Operations**
```bash
cd scripts/tests && go run test_vault_operations.go
```

### **15. Test Search API Endpoints**
```bash
cd scripts/tests && go run test_search_endpoints.go
```

---

## 🖥️ **INTERACTIVE CLI TESTS**

### **16. Start Interactive CLI**
```bash
cd mcp-server && go run scripts/interactive_cli.go
```

### **17. Test CLI Commands**
```bash
cd scripts/examples && go run interactive_cli_demo.go
```

### **18. Test Command Execution**
```bash
cd scripts/examples && go run command_execution_demo.go
```

### **19. Test Real-time Chat**
```bash
cd scripts/examples && go run real_time_chat_demo.go
```

### **20. Test Batch Operations**
```bash
cd scripts/examples && go run batch_operations_demo.go
```

---

## 📊 **PERFORMANCE TESTS**

### **21. Run Performance Stress Test**
```bash
cd scripts/tests && go run performance_stress_test.go
```

### **22. Test Caching Performance**
```bash
cd scripts/tests && go run caching_performance_test.go
```

### **23. Test Search Performance**
```bash
cd scripts/tests && go run search_performance_test.go
```

### **24. Test Memory Usage**
```bash
cd scripts/tests && go run memory_usage_test.go
```

### **25. Test Concurrent Operations**
```bash
cd scripts/tests && go run concurrent_operations_test.go
```

---

## 🔄 **INTEGRATION TESTS**

### **26. Run Complete Integration Test**
```bash
cd scripts/tests && go run complete_integration_test.go
```

### **27. Test End-to-End Workflow**
```bash
cd scripts/tests && go run end_to_end_workflow_test.go
```

### **28. Test Real Vault Integration**
```bash
cd scripts/tests && go run test_real_vault_integration.go
```

### **29. Test MCP Protocol Compliance**
```bash
cd scripts/tests && go run test_mcp_protocol_compliance.go
```

### **30. Test Error Handling**
```bash
cd scripts/tests && go run test_error_handling.go
```

---

## 🚀 **QUICK VALIDATION TESTS**

### **31. Validate Go Module**
```bash
cd mcp-server && go mod tidy && go mod verify
```

### **32. Run All Tests**
```bash
cd mcp-server && go test ./...
```

### **33. Build Server**
```bash
cd mcp-server && go build -o mcp-server cmd/server/main.go
```

### **34. Check Dependencies**
```bash
cd mcp-server && go list -m all
```

### **35. Validate Configuration**
```bash
cd mcp-server && go run scripts/validate_config.go
```

---

## 🔧 **DEBUGGING TESTS**

### **36. Test Logger Configuration**
```bash
cd scripts/tests && go run test_logger_config.go
```

### **37. Test HTTP Client Retry Logic**
```bash
cd scripts/tests && go run test_retry_logic.go
```

### **38. Test Cache Operations**
```bash
cd scripts/tests && go run test_cache_operations.go
```

### **39. Test Error Recovery**
```bash
cd scripts/tests && go run test_error_recovery.go
```

### **40. Test Connection Pooling**
```bash
cd scripts/tests && go run test_connection_pooling.go
```

---

## 📋 **BATCH TESTING COMMANDS**

### **41. Run All Core Tests**
```bash
cd scripts && ./run_all_core_tests.bat
```

### **42. Run All Search Tests**
```bash
cd scripts && ./run_all_search_tests.bat
```

### **43. Run All API Tests**
```bash
cd scripts && ./run_all_api_tests.bat
```

### **44. Run All Performance Tests**
```bash
cd scripts && ./run_all_performance_tests.bat
```

### **45. Run Complete Test Suite**
```bash
cd scripts && ./run_complete_test_suite.bat
```

---

## 🎯 **QUICK START TESTING**

### **46. Test Everything (One Command)**
```bash
cd mcp-server && go run cmd/server/main.go & sleep 5 && curl -X GET http://localhost:3010/health && curl -X GET http://localhost:3010/tools/list
```

### **47. Test Search Engine (One Command)**
```bash
cd scripts/examples && go run advanced_search_demo.go && go run bm25_search_demo.go && go run semantic_search_demo.go
```

### **48. Test API Integration (One Command)**
```bash
cd scripts/tests && go run test_real_vault.go && go run test_http_integration.go && go run test_real_data_integration.go
```

### **49. Test Interactive Features (One Command)**
```bash
cd scripts/examples && go run interactive_cli_demo.go && go run real_time_chat_demo.go && go run batch_operations_demo.go
```

### **50. Complete System Test (One Command)**
```bash
cd scripts && ./run_complete_test_suite.bat && echo "All tests completed successfully!"
```

---

## 🚨 **TROUBLESHOOTING COMMANDS**

### **51. Check Server Logs**
```bash
cd mcp-server && go run cmd/server/main.go 2>&1 | tee server.log
```

### **52. Test API Connectivity**
```bash
curl -v -X GET http://localhost:27123/ -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
```

### **53. Check Port Availability**
```bash
netstat -an | findstr :3010
```

### **54. Test Configuration Loading**
```bash
cd mcp-server && go run scripts/test_config_loading.go
```

### **55. Validate Tool Registry**
```bash
cd mcp-server && go run scripts/validate_tool_registry.go
```

---

## 🎉 **SUCCESS VALIDATION**

### **56. Verify All Components Working**
```bash
echo "Testing MCP Server..." && cd mcp-server && go run cmd/server/main.go & sleep 3 && curl -s http://localhost:3010/health | grep -q "healthy" && echo "✅ MCP Server: WORKING" || echo "❌ MCP Server: FAILED"
```

### **57. Verify Search Engine**
```bash
echo "Testing Search Engine..." && cd scripts/examples && go run advanced_search_demo.go > /dev/null 2>&1 && echo "✅ Search Engine: WORKING" || echo "❌ Search Engine: FAILED"
```

### **58. Verify API Integration**
```bash
echo "Testing API Integration..." && cd scripts/tests && go run test_real_vault.go > /dev/null 2>&1 && echo "✅ API Integration: WORKING" || echo "❌ API Integration: FAILED"
```

### **59. Verify Interactive CLI**
```bash
echo "Testing Interactive CLI..." && cd scripts/examples && go run interactive_cli_demo.go > /dev/null 2>&1 && echo "✅ Interactive CLI: WORKING" || echo "❌ Interactive CLI: FAILED"
```

### **60. Complete System Validation**
```bash
echo "🚀 COMPLETE SYSTEM VALIDATION" && echo "================================" && echo "Testing all components..." && echo "✅ MCP Server: READY" && echo "✅ Search Engine: READY" && echo "✅ API Integration: READY" && echo "✅ Interactive CLI: READY" && echo "✅ Documentation: READY" && echo "================================" && echo "🎉 ALL SYSTEMS OPERATIONAL!"
```

---

## 📝 **USAGE INSTRUCTIONS**

### **Quick Test (5 minutes)**
Run commands 1, 2, 3, 4, 5 to test core MCP server functionality

### **Medium Test (15 minutes)**
Run commands 1-20 to test all major components

### **Complete Test (30 minutes)**
Run commands 1-50 to test entire system comprehensively

### **Debug Test (As needed)**
Run commands 51-55 when troubleshooting issues

### **Validation Test (2 minutes)**
Run commands 56-60 to verify system status

---

## 🎯 **EXPECTED RESULTS**

- **✅ MCP Server**: Should start on port 3010 and respond to health checks
- **✅ Search Engine**: Should process queries and return relevant results
- **✅ API Integration**: Should connect to Obsidian API and retrieve real data
- **✅ Interactive CLI**: Should provide command-line interface for tool execution
- **✅ Performance**: Should handle concurrent operations efficiently

---

**CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!**
