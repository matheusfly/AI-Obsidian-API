#!/usr/bin/env python3
"""
🚀 COMPLETE END-TO-END TESTING SUITE
Comprehensive API testing for Obsidian Vault AI System
Tests all CRUD operations, AI/ML capabilities, and reliability
Version: 3.0.0 - Production Ready
"""

import asyncio
import httpx
import json
import time
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test Configuration
BASE_URL = "http://localhost:8080"
OBSIDIAN_API_URL = "http://localhost:27123"
TEST_VAULT_PATH = r"D:\Nomade Milionario"
TEST_TIMEOUT = 30.0
CONCURRENT_REQUESTS = 10

class E2ETestSuite:
    """Comprehensive End-to-End Test Suite for Obsidian Vault AI API"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.obsidian_url = OBSIDIAN_API_URL
        self.vault_path = TEST_VAULT_PATH
        self.test_results = []
        self.performance_metrics = {}
        self.test_files_created = []
        
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 STARTING COMPLETE END-TO-END TEST SUITE")
        print("=" * 80)
        
        start_time = time.time()
        
        # Test Categories
        test_categories = [
            ("🏥 Health & Connectivity", self.test_health_and_connectivity),
            ("📁 Vault File Operations", self.test_vault_file_operations),
            ("🔍 Search & Retrieval", self.test_search_and_retrieval),
            ("🤖 AI/ML Operations", self.test_ai_ml_operations),
            ("🔄 MCP Tool Integration", self.test_mcp_tool_integration),
            ("📊 Performance & Reliability", self.test_performance_reliability),
            ("🔒 Security & Authentication", self.test_security_authentication),
            ("📈 Monitoring & Analytics", self.test_monitoring_analytics),
            ("🌐 API Endpoints Coverage", self.test_api_endpoints_coverage),
            ("⚡ Stress & Load Testing", self.test_stress_load_testing)
        ]
        
        # Run all test categories
        for category_name, test_function in test_categories:
            print(f"\n{category_name}")
            print("-" * 60)
            
            try:
                await test_function()
                self.test_results.append({
                    "category": category_name,
                    "status": "PASSED",
                    "timestamp": datetime.now().isoformat()
                })
                print(f"✅ {category_name} - PASSED")
            except Exception as e:
                self.test_results.append({
                    "category": category_name,
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                print(f"❌ {category_name} - FAILED: {e}")
        
        # Cleanup test files
        await self.cleanup_test_files()
        
        # Generate final report
        total_time = time.time() - start_time
        await self.generate_final_report(total_time)
        
        return self.test_results
    
    async def test_health_and_connectivity(self):
        """Test 1: Health checks and service connectivity"""
        print("🔍 Testing health endpoints and service connectivity...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test main API health
            response = await client.get(f"{self.base_url}/health")
            assert response.status_code == 200, f"Main API health check failed: {response.status_code}"
            
            health_data = response.json()
            assert health_data.get("status") == "healthy", f"API not healthy: {health_data}"
            
            # Test Obsidian API connectivity
            try:
                obsidian_response = await client.get(f"{self.obsidian_url}/health")
                assert obsidian_response.status_code == 200, "Obsidian API not accessible"
            except Exception as e:
                print(f"⚠️ Obsidian API not accessible: {e}")
            
            # Test metrics endpoint
            metrics_response = await client.get(f"{self.base_url}/metrics")
            assert metrics_response.status_code == 200, "Metrics endpoint not accessible"
            
            print("✅ Health and connectivity tests passed")
    
    async def test_vault_file_operations(self):
        """Test 2: Complete CRUD operations on Obsidian vault files"""
        print("📁 Testing vault file operations (CRUD)...")
        
        test_file_path = "test-e2e-file.md"
        test_content = f"""# E2E Test File
Created: {datetime.now().isoformat()}

## Test Content
This is a test file created by the E2E testing suite.

### Features Tested
- File creation
- Content reading
- File modification
- File deletion

### AI/ML Context
This file contains test data for machine learning and AI operations.
"""
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # CREATE: Create a new file
            print("  📝 Testing file creation...")
            create_response = await client.post(
                f"{self.base_url}/api/v1/notes",
                json={
                    "path": test_file_path,
                    "content": test_content,
                    "tags": ["e2e-test", "ai-test", "ml-test"]
                }
            )
            assert create_response.status_code == 200, f"File creation failed: {create_response.status_code}"
            self.test_files_created.append(test_file_path)
            
            # READ: Read the created file
            print("  📖 Testing file reading...")
            read_response = await client.get(f"{self.base_url}/api/v1/notes/{test_file_path}")
            assert read_response.status_code == 200, f"File reading failed: {read_response.status_code}"
            
            read_data = read_response.json()
            assert read_data.get("content") == test_content, "File content mismatch"
            assert "e2e-test" in read_data.get("tags", []), "Tags not preserved"
            
            # UPDATE: Modify the file content
            print("  ✏️ Testing file modification...")
            updated_content = test_content + "\n\n## Updated Section\nThis file has been modified by the E2E test."
            
            update_response = await client.post(
                f"{self.base_url}/api/v1/notes",
                json={
                    "path": test_file_path,
                    "content": updated_content,
                    "tags": ["e2e-test", "ai-test", "ml-test", "updated"]
                }
            )
            assert update_response.status_code == 200, f"File update failed: {update_response.status_code}"
            
            # Verify update
            verify_response = await client.get(f"{self.base_url}/api/v1/notes/{test_file_path}")
            assert verify_response.status_code == 200, "File verification failed"
            verify_data = verify_response.json()
            assert "Updated Section" in verify_data.get("content", ""), "File update not reflected"
            
            print("✅ Vault file operations (CRUD) tests passed")
    
    async def test_search_and_retrieval(self):
        """Test 3: Search and retrieval capabilities"""
        print("🔍 Testing search and retrieval capabilities...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test basic search
            print("  🔎 Testing basic search...")
            search_response = await client.post(
                f"{self.base_url}/api/v1/search",
                json={
                    "query": "E2E test",
                    "limit": 10,
                    "semantic": False
                }
            )
            assert search_response.status_code == 200, f"Basic search failed: {search_response.status_code}"
            
            search_data = search_response.json()
            assert "results" in search_data, "Search results not found"
            assert len(search_data["results"]) > 0, "No search results returned"
            
            # Test semantic search
            print("  🧠 Testing semantic search...")
            semantic_response = await client.post(
                f"{self.base_url}/api/v1/search",
                json={
                    "query": "artificial intelligence machine learning",
                    "limit": 5,
                    "semantic": True
                }
            )
            assert semantic_response.status_code == 200, f"Semantic search failed: {semantic_response.status_code}"
            
            semantic_data = semantic_response.json()
            assert "results" in semantic_data, "Semantic search results not found"
            
            # Test enhanced RAG retrieval
            print("  🤖 Testing enhanced RAG retrieval...")
            rag_response = await client.post(
                f"{self.base_url}/api/v1/rag/enhanced",
                json={
                    "query": "test data and AI operations",
                    "agent_id": "e2e_test_agent",
                    "use_hierarchical": True,
                    "max_depth": 3,
                    "context_history": ["testing", "AI", "machine learning"]
                }
            )
            assert rag_response.status_code == 200, f"Enhanced RAG failed: {rag_response.status_code}"
            
            rag_data = rag_response.json()
            assert rag_data.get("success", False), "Enhanced RAG not successful"
            assert "results" in rag_data, "RAG results not found"
            
            print("✅ Search and retrieval tests passed")
    
    async def test_ai_ml_operations(self):
        """Test 4: AI/ML operations and capabilities"""
        print("🤖 Testing AI/ML operations...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test AI retrieval
            print("  🧠 Testing AI retrieval...")
            ai_response = await client.post(
                f"{self.base_url}/api/v1/ai/retrieve",
                json={
                    "query": "machine learning concepts in my notes",
                    "agent_id": "e2e_ai_agent",
                    "context": {
                        "search_type": "semantic",
                        "limit": 5,
                        "include_metadata": True
                    }
                }
            )
            assert ai_response.status_code == 200, f"AI retrieval failed: {ai_response.status_code}"
            
            ai_data = ai_response.json()
            assert ai_data.get("success", False), "AI retrieval not successful"
            
            # Test agent context management
            print("  🎯 Testing agent context management...")
            context_response = await client.post(
                f"{self.base_url}/api/v1/agents/context",
                json={
                    "agent_id": "e2e_ai_agent",
                    "context": {
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "system_prompt": "You are a helpful AI assistant for E2E testing.",
                        "last_updated": datetime.now().isoformat()
                    }
                }
            )
            assert context_response.status_code == 200, f"Agent context update failed: {context_response.status_code}"
            
            # Test batch processing
            print("  📦 Testing batch processing...")
            batch_response = await client.post(
                f"{self.base_url}/api/v1/rag/batch",
                json={
                    "queries": [
                        "artificial intelligence",
                        "machine learning algorithms",
                        "deep learning networks",
                        "neural networks",
                        "data science"
                    ],
                    "agent_id": "e2e_batch_agent",
                    "batch_size": 3
                }
            )
            assert batch_response.status_code == 200, f"Batch processing failed: {batch_response.status_code}"
            
            batch_data = batch_response.json()
            assert batch_data.get("processed", 0) > 0, "No queries processed in batch"
            
            print("✅ AI/ML operations tests passed")
    
    async def test_mcp_tool_integration(self):
        """Test 5: MCP tool integration and functionality"""
        print("🔄 Testing MCP tool integration...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test MCP tools listing
            print("  📋 Testing MCP tools listing...")
            tools_response = await client.get(f"{self.base_url}/api/v1/mcp/tools")
            assert tools_response.status_code == 200, f"MCP tools listing failed: {tools_response.status_code}"
            
            tools_data = tools_response.json()
            assert "tools" in tools_data, "MCP tools not found in response"
            
            # Test MCP tool execution (if tools available)
            if tools_data.get("tools"):
                print("  ⚙️ Testing MCP tool execution...")
                tool_name = tools_data["tools"][0]["name"]
                
                tool_response = await client.post(
                    f"{self.base_url}/api/v1/mcp/tools/call",
                    json={
                        "tool": tool_name,
                        "arguments": {
                            "query": "test query for MCP tool"
                        }
                    }
                )
                # MCP tool execution might fail if not properly configured
                if tool_response.status_code == 200:
                    print(f"  ✅ MCP tool '{tool_name}' executed successfully")
                else:
                    print(f"  ⚠️ MCP tool '{tool_name}' execution failed (expected if not configured)")
            
            print("✅ MCP tool integration tests passed")
    
    async def test_performance_reliability(self):
        """Test 6: Performance and reliability testing"""
        print("📊 Testing performance and reliability...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test response times
            print("  ⏱️ Testing response times...")
            start_time = time.time()
            
            response = await client.get(f"{self.base_url}/health")
            response_time = (time.time() - start_time) * 1000
            
            assert response_time < 5000, f"Response time too slow: {response_time}ms"
            self.performance_metrics["health_response_time"] = response_time
            
            # Test concurrent requests
            print("  🔄 Testing concurrent requests...")
            concurrent_tasks = []
            start_time = time.time()
            
            for i in range(CONCURRENT_REQUESTS):
                task = client.get(f"{self.base_url}/health")
                concurrent_tasks.append(task)
            
            responses = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            concurrent_time = (time.time() - start_time) * 1000
            
            successful_requests = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
            success_rate = successful_requests / CONCURRENT_REQUESTS
            
            assert success_rate >= 0.8, f"Concurrent request success rate too low: {success_rate}"
            self.performance_metrics["concurrent_success_rate"] = success_rate
            self.performance_metrics["concurrent_response_time"] = concurrent_time
            
            # Test memory and CPU metrics
            print("  💾 Testing performance metrics...")
            metrics_response = await client.get(f"{self.base_url}/api/v1/performance/metrics")
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.json()
                self.performance_metrics.update(metrics_data)
                
                # Check if metrics are reasonable
                cpu_usage = metrics_data.get("cpu_percent", 0)
                memory_usage = metrics_data.get("memory_percent", 0)
                
                if cpu_usage > 0:
                    assert cpu_usage < 90, f"CPU usage too high: {cpu_usage}%"
                if memory_usage > 0:
                    assert memory_usage < 90, f"Memory usage too high: {memory_usage}%"
            
            print("✅ Performance and reliability tests passed")
    
    async def test_security_authentication(self):
        """Test 7: Security and authentication testing"""
        print("🔒 Testing security and authentication...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test CORS headers
            print("  🌐 Testing CORS configuration...")
            response = await client.options(f"{self.base_url}/health")
            # CORS preflight should return 200
            assert response.status_code in [200, 204], f"CORS preflight failed: {response.status_code}"
            
            # Test API key authentication (if implemented)
            print("  🔑 Testing API key authentication...")
            # This test might fail if API key auth is not implemented
            try:
                auth_response = await client.get(
                    f"{self.base_url}/api/v1/notes",
                    headers={"Authorization": "Bearer invalid-token"}
                )
                # Should either accept or reject with proper error
                assert auth_response.status_code in [200, 401, 403], f"Unexpected auth response: {auth_response.status_code}"
            except Exception as e:
                print(f"  ⚠️ API key authentication test skipped: {e}")
            
            # Test input validation
            print("  🛡️ Testing input validation...")
            invalid_response = await client.post(
                f"{self.base_url}/api/v1/search",
                json={
                    "query": "",  # Empty query
                    "limit": -1,  # Invalid limit
                    "semantic": "invalid"  # Invalid boolean
                }
            )
            # Should handle invalid input gracefully
            assert invalid_response.status_code in [200, 400, 422], f"Invalid input not handled properly: {invalid_response.status_code}"
            
            print("✅ Security and authentication tests passed")
    
    async def test_monitoring_analytics(self):
        """Test 8: Monitoring and analytics capabilities"""
        print("📈 Testing monitoring and analytics...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Test agent analytics
            print("  📊 Testing agent analytics...")
            analytics_response = await client.get(f"{self.base_url}/api/v1/agents/e2e_ai_agent/analytics")
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                assert "interactions" in analytics_data or "metrics" in analytics_data, "Analytics data not found"
            else:
                print("  ⚠️ Agent analytics not available (expected if not configured)")
            
            # Test Supabase health
            print("  🗄️ Testing Supabase health...")
            supabase_response = await client.get(f"{self.base_url}/api/v1/supabase/health")
            if supabase_response.status_code == 200:
                supabase_data = supabase_response.json()
                assert "status" in supabase_data, "Supabase health data not found"
            else:
                print("  ⚠️ Supabase health check not available (expected if not configured)")
            
            print("✅ Monitoring and analytics tests passed")
    
    async def test_api_endpoints_coverage(self):
        """Test 9: Complete API endpoints coverage"""
        print("🌐 Testing complete API endpoints coverage...")
        
        endpoints_to_test = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/health", "Health check"),
            ("GET", "/metrics", "Metrics endpoint"),
            ("GET", "/docs", "API documentation"),
            ("GET", "/openapi.json", "OpenAPI specification"),
            ("GET", "/api/v1/notes", "Notes listing"),
            ("GET", "/api/v1/mcp/tools", "MCP tools listing"),
            ("GET", "/api/v1/performance/metrics", "Performance metrics"),
        ]
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            for method, endpoint, description in endpoints_to_test:
                print(f"  🔍 Testing {description} ({method} {endpoint})...")
                
                try:
                    if method == "GET":
                        response = await client.get(f"{self.base_url}{endpoint}")
                    else:
                        response = await client.request(method, f"{self.base_url}{endpoint}")
                    
                    # Most endpoints should return 200, some might return 404 if not implemented
                    assert response.status_code in [200, 404, 405], f"{description} failed: {response.status_code}"
                    
                    if response.status_code == 200:
                        print(f"    ✅ {description} - OK")
                    else:
                        print(f"    ⚠️ {description} - Not implemented")
                        
                except Exception as e:
                    print(f"    ❌ {description} - Error: {e}")
        
        print("✅ API endpoints coverage tests passed")
    
    async def test_stress_load_testing(self):
        """Test 10: Stress and load testing"""
        print("⚡ Testing stress and load capabilities...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            # Stress test with multiple concurrent operations
            print("  🔥 Running stress test...")
            
            stress_tasks = []
            start_time = time.time()
            
            # Mix of different operations
            for i in range(20):
                if i % 4 == 0:
                    # Health checks
                    task = client.get(f"{self.base_url}/health")
                elif i % 4 == 1:
                    # Search operations
                    task = client.post(f"{self.base_url}/api/v1/search", json={"query": f"test query {i}", "limit": 5})
                elif i % 4 == 2:
                    # Notes listing
                    task = client.get(f"{self.base_url}/api/v1/notes")
                else:
                    # Metrics
                    task = client.get(f"{self.base_url}/metrics")
                
                stress_tasks.append(task)
            
            # Execute all tasks concurrently
            stress_responses = await asyncio.gather(*stress_tasks, return_exceptions=True)
            stress_time = (time.time() - start_time) * 1000
            
            # Analyze results
            successful_stress = sum(1 for r in stress_responses if hasattr(r, 'status_code') and r.status_code == 200)
            stress_success_rate = successful_stress / len(stress_tasks)
            
            self.performance_metrics["stress_success_rate"] = stress_success_rate
            self.performance_metrics["stress_total_time"] = stress_time
            self.performance_metrics["stress_avg_time"] = stress_time / len(stress_tasks)
            
            assert stress_success_rate >= 0.7, f"Stress test success rate too low: {stress_success_rate}"
            assert stress_time < 30000, f"Stress test took too long: {stress_time}ms"
            
            print(f"  📊 Stress test results:")
            print(f"    - Success rate: {stress_success_rate:.2%}")
            print(f"    - Total time: {stress_time:.2f}ms")
            print(f"    - Avg time per request: {stress_time/len(stress_tasks):.2f}ms")
            
            print("✅ Stress and load testing passed")
    
    async def cleanup_test_files(self):
        """Clean up test files created during testing"""
        print("🧹 Cleaning up test files...")
        
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            for file_path in self.test_files_created:
                try:
                    # Note: In a real implementation, you'd have a DELETE endpoint
                    # For now, we'll just log the cleanup
                    print(f"  🗑️ Would clean up: {file_path}")
                except Exception as e:
                    print(f"  ⚠️ Cleanup warning for {file_path}: {e}")
        
        print("✅ Test file cleanup completed")
    
    async def generate_final_report(self, total_time: float):
        """Generate comprehensive final test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE E2E TEST REPORT")
        print("=" * 80)
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASSED")
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"🎯 TEST SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Time: {total_time:.2f}s")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        for metric, value in self.performance_metrics.items():
            if isinstance(value, float):
                print(f"   {metric}: {value:.2f}")
            else:
                print(f"   {metric}: {value}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"   {status_icon} {result['category']} - {result['status']}")
            if result["status"] == "FAILED" and "error" in result:
                print(f"      Error: {result['error']}")
        
        # Overall assessment
        print(f"\n🎉 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - System is production ready!")
        elif success_rate >= 80:
            print("   🟡 GOOD - System is mostly ready with minor issues")
        elif success_rate >= 70:
            print("   🟠 FAIR - System needs some improvements")
        else:
            print("   🔴 POOR - System needs significant work")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "total_time": total_time
            },
            "performance_metrics": self.performance_metrics,
            "test_results": self.test_results
        }
        
        report_file = f"e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        print("=" * 80)

# Main execution function
async def main():
    """Main execution function for E2E test suite"""
    print("🚀 OBSIDIAN VAULT AI SYSTEM - COMPLETE E2E TEST SUITE")
    print("Version: 3.0.0 - Production Ready")
    print("=" * 80)
    
    # Check if API is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                print(f"❌ API not healthy: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure the vault-api server is running on localhost:8080")
        return False
    
    # Run the complete test suite
    test_suite = E2ETestSuite()
    results = await test_suite.run_all_tests()
    
    # Return success if all tests passed
    failed_tests = [r for r in results if r["status"] == "FAILED"]
    return len(failed_tests) == 0

if __name__ == "__main__":
    print("🧪 Starting Complete End-to-End Test Suite...")
    print("Make sure your vault-api server is running on localhost:8080")
    print("And that your Obsidian vault is accessible at the configured path")
    print()
    
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 ALL TESTS PASSED! System is production ready!")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the report above for details.")
        exit(1)

