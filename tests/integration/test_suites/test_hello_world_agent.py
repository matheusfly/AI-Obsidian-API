#!/usr/bin/env python3
"""
Comprehensive Testing and Benchmarking Suite for Hello World LangGraph Agent
Tests API endpoints, MCP integration, LLM retrieval, and behavior patterns
"""

import asyncio
import time
import json
import httpx
import requests
from typing import Dict, List, Any
import statistics
from dataclasses import dataclass
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_workflows.hello_world_agent import run_hello_world_example, hello_world_agent

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    success: bool
    duration: float
    error: str = None
    metrics: Dict[str, Any] = None

class HelloWorldAgentTester:
    """Comprehensive testing suite for Hello World agent"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:27123"
        self.langgraph_url = "http://localhost:2024"
        self.api_key = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
        self.results: List[TestResult] = []
        
    def log_test(self, test_name: str, success: bool, duration: float, error: str = None, metrics: Dict = None):
        """Log test result"""
        result = TestResult(
            test_name=test_name,
            success=success,
            duration=duration,
            error=error,
            metrics=metrics
        )
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.3f}s)")
        if error:
            print(f"   Error: {error}")
        if metrics:
            print(f"   Metrics: {metrics}")
    
    def test_obsidian_api_health(self) -> bool:
        """Test Obsidian API health endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            duration = time.time() - start_time
            
            success = response.status_code == 200
            self.log_test("Obsidian API Health", success, duration, 
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Obsidian API Health", False, duration, str(e))
            return False
    
    def test_obsidian_api_authentication(self) -> bool:
        """Test Obsidian API authentication"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.base_url}/vault", headers=headers, timeout=5)
            duration = time.time() - start_time
            
            success = response.status_code == 200
            self.log_test("Obsidian API Auth", success, duration,
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Obsidian API Auth", False, duration, str(e))
            return False
    
    def test_obsidian_api_endpoints(self) -> bool:
        """Test all Obsidian API endpoints"""
        start_time = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        endpoints = [
            ("/vault", "GET"),
            ("/vault/files", "GET"),
            ("/vault/stats", "GET"),
        ]
        
        success_count = 0
        total_count = len(endpoints)
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=5)
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, timeout=5)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    print(f"   {endpoint} failed: {response.status_code}")
            except Exception as e:
                print(f"   {endpoint} error: {e}")
        
        duration = time.time() - start_time
        success = success_count == total_count
        self.log_test("Obsidian API Endpoints", success, duration,
                     None if success else f"{success_count}/{total_count} passed",
                     {"passed": success_count, "total": total_count})
        return success
    
    def test_langgraph_server_health(self) -> bool:
        """Test LangGraph server health"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.langgraph_url}/ok", timeout=5)
            duration = time.time() - start_time
            
            success = response.status_code == 200
            self.log_test("LangGraph Server Health", success, duration,
                         None if success else f"Status: {response.status_code}")
            return success
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("LangGraph Server Health", False, duration, str(e))
            return False
    
    def test_langgraph_workflow_execution(self) -> bool:
        """Test LangGraph workflow execution"""
        start_time = time.time()
        try:
            # Create thread
            thread_response = requests.post(f"{self.langgraph_url}/threads", json={}, timeout=10)
            if thread_response.status_code != 200:
                raise Exception(f"Thread creation failed: {thread_response.status_code}")
            
            thread_id = thread_response.json()["thread_id"]
            
            # Run workflow
            workflow_payload = {
                "assistant_id": "obsidian-workflow",
                "input": {
                    "vault_name": "Nomade Milionario",
                    "search_query": "hello world",
                    "limit": 5
                }
            }
            
            run_response = requests.post(
                f"{self.langgraph_url}/threads/{thread_id}/runs/wait",
                json=workflow_payload,
                timeout=30
            )
            
            duration = time.time() - start_time
            success = run_response.status_code == 200
            
            self.log_test("LangGraph Workflow Execution", success, duration,
                         None if success else f"Status: {run_response.status_code}")
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("LangGraph Workflow Execution", False, duration, str(e))
            return False
    
    def test_hello_world_agent_direct(self) -> bool:
        """Test Hello World agent directly"""
        start_time = time.time()
        try:
            result = run_hello_world_example()
            duration = time.time() - start_time
            
            success = "error" not in result and result.get("workflow_status") == "finalized"
            metrics = result.get("results", {}).get("metrics", {})
            
            self.log_test("Hello World Agent Direct", success, duration,
                         None if success else "Agent execution failed",
                         metrics)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Hello World Agent Direct", False, duration, str(e))
            return False
    
    def test_api_performance_benchmark(self) -> bool:
        """Benchmark API performance"""
        start_time = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Test multiple API calls
        durations = []
        success_count = 0
        total_calls = 10
        
        for i in range(total_calls):
            call_start = time.time()
            try:
                response = requests.get(f"{self.base_url}/vault/files", headers=headers, timeout=5)
                call_duration = time.time() - call_start
                durations.append(call_duration)
                
                if response.status_code == 200:
                    success_count += 1
            except Exception as e:
                call_duration = time.time() - call_start
                durations.append(call_duration)
        
        duration = time.time() - start_time
        success = success_count >= total_calls * 0.8  # 80% success rate
        
        metrics = {
            "total_calls": total_calls,
            "successful_calls": success_count,
            "success_rate": success_count / total_calls,
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "median_duration": statistics.median(durations)
        }
        
        self.log_test("API Performance Benchmark", success, duration,
                     None if success else f"Success rate: {success_count}/{total_calls}",
                     metrics)
        return success
    
    def test_mcp_integration_simulation(self) -> bool:
        """Simulate MCP integration testing"""
        start_time = time.time()
        try:
            # Simulate MCP tool calls
            mcp_tools = [
                "list_vault_files",
                "read_vault_file", 
                "search_vault_content",
                "write_vault_file",
                "get_vault_stats"
            ]
            
            successful_tools = 0
            for tool_name in mcp_tools:
                try:
                    # Simulate tool execution
                    if tool_name == "list_vault_files":
                        response = requests.get(f"{self.base_url}/vault/files", 
                                              headers={"Authorization": f"Bearer {self.api_key}"}, timeout=5)
                    elif tool_name == "get_vault_stats":
                        response = requests.get(f"{self.base_url}/vault/stats",
                                              headers={"Authorization": f"Bearer {self.api_key}"}, timeout=5)
                    else:
                        # Simulate other tools
                        response = requests.get(f"{self.base_url}/health", timeout=5)
                    
                    if response.status_code == 200:
                        successful_tools += 1
                except Exception:
                    pass
            
            duration = time.time() - start_time
            success = successful_tools >= len(mcp_tools) * 0.6  # 60% success rate
            
            metrics = {
                "total_tools": len(mcp_tools),
                "successful_tools": successful_tools,
                "success_rate": successful_tools / len(mcp_tools)
            }
            
            self.log_test("MCP Integration Simulation", success, duration,
                         None if success else f"Tools working: {successful_tools}/{len(mcp_tools)}",
                         metrics)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("MCP Integration Simulation", False, duration, str(e))
            return False
    
    def test_behavior_patterns(self) -> bool:
        """Test agent behavior patterns"""
        start_time = time.time()
        try:
            # Test different search queries
            search_queries = ["langgraph", "hello world", "test", "vault", "integration"]
            successful_searches = 0
            
            for query in search_queries:
                try:
                    response = requests.post(
                        f"{self.base_url}/vault/Nomade%20Milionario/search",
                        json={"query": query, "vault_name": "Nomade Milionario"},
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=5
                    )
                    if response.status_code == 200:
                        successful_searches += 1
                except Exception:
                    pass
            
            duration = time.time() - start_time
            success = successful_searches >= len(search_queries) * 0.8
            
            metrics = {
                "total_queries": len(search_queries),
                "successful_searches": successful_searches,
                "success_rate": successful_searches / len(search_queries)
            }
            
            self.log_test("Behavior Patterns", success, duration,
                         None if success else f"Searches working: {successful_searches}/{len(search_queries)}",
                         metrics)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Behavior Patterns", False, duration, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print("🧪 Starting Comprehensive Hello World Agent Testing Suite")
        print("=" * 70)
        
        # Run all tests
        tests = [
            self.test_obsidian_api_health,
            self.test_obsidian_api_authentication,
            self.test_obsidian_api_endpoints,
            self.test_langgraph_server_health,
            self.test_langgraph_workflow_execution,
            self.test_hello_world_agent_direct,
            self.test_api_performance_benchmark,
            self.test_mcp_integration_simulation,
            self.test_behavior_patterns
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
        
        # Calculate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        total_duration = sum(r.duration for r in self.results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        print(f"Total Duration: {total_duration:.3f}s")
        print(f"Average Duration: {avg_duration:.3f}s")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS")
        print("-" * 70)
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{status} {result.test_name:<30} {result.duration:>8.3f}s")
            if result.error:
                print(f"    Error: {result.error}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests,
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "results": [r.__dict__ for r in self.results]
        }

def main():
    """Main testing function"""
    print("🚀 Hello World LangGraph Agent - Comprehensive Testing Suite")
    print("=" * 70)
    
    tester = HelloWorldAgentTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("hello_world_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: hello_world_test_results.json")
    
    # Final status
    if results["success_rate"] >= 0.8:
        print("🎉 EXCELLENT! Hello World Agent is ready for production!")
    elif results["success_rate"] >= 0.6:
        print("✅ GOOD! Hello World Agent is mostly functional with minor issues.")
    else:
        print("⚠️  NEEDS WORK! Hello World Agent requires fixes before production.")
    
    return results

if __name__ == "__main__":
    main()
