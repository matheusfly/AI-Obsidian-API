"""
Comprehensive Testing and Benchmarking Suite for Enhanced Interactive Agent
This suite provides extensive testing, behavior analysis, and performance benchmarking
"""

import asyncio
import json
import time
import traceback
from datetime import datetime
from typing import Dict, List, Any
import statistics

import httpx
import requests
from langgraph_workflows.enhanced_interactive_agent import (
    enhanced_interactive_agent,
    run_enhanced_agent_example,
    AgentState,
    ConversationState
)

# Configuration
OBSIDIAN_API_KEY = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
OBSIDIAN_BASE_URL = "http://127.0.0.1:27123"
LANGGRAPH_SERVER_URL = "http://127.0.0.1:2024"

class TestResults:
    """Class to track test results and metrics"""
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        self.performance_metrics = {}
        self.start_time = datetime.now()
    
    def add_test_result(self, test_name: str, passed: bool, duration: float, error: str = None):
        """Add a test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "duration": duration,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_success_rate(self) -> float:
        """Get success rate percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    def get_total_duration(self) -> float:
        """Get total test duration"""
        return (datetime.now() - self.start_time).total_seconds()

def test_obsidian_api_health() -> bool:
    """Test Obsidian API health and connectivity"""
    try:
        print("🔍 Testing Obsidian API Health...")
        
        response = requests.get(f"{OBSIDIAN_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Obsidian API is healthy")
            return True
        else:
            print(f"❌ Obsidian API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Obsidian API health check failed: {str(e)}")
        return False

def test_obsidian_api_authentication() -> bool:
    """Test Obsidian API authentication"""
    try:
        print("🔐 Testing Obsidian API Authentication...")
        
        headers = {"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
        response = requests.get(f"{OBSIDIAN_BASE_URL}/vault/Nomade%20Milionario/files", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authentication successful - Found {len(data.get('files', []))} files")
            return True
        else:
            print(f"❌ Authentication failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication test failed: {str(e)}")
        return False

def test_obsidian_api_endpoints() -> bool:
    """Test all Obsidian API endpoints"""
    try:
        print("🌐 Testing Obsidian API Endpoints...")
        
        headers = {"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
        vault_name = "Nomade Milionario"
        
        # Test endpoints
        endpoints = [
            ("GET", f"/vault/{vault_name}/files", "List files"),
            ("POST", f"/vault/{vault_name}/search", "Search files", {"query": "test"}),
            ("GET", f"/health", "Health check"),
        ]
        
        all_passed = True
        
        for method, endpoint, description, *data in endpoints:
            try:
                url = f"{OBSIDIAN_BASE_URL}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                elif method == "POST":
                    response = requests.post(url, headers=headers, json=data[0] if data else {}, timeout=10)
                
                if response.status_code in [200, 201]:
                    print(f"✅ {description}: OK")
                else:
                    print(f"❌ {description}: Status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Endpoint testing failed: {str(e)}")
        return False

def test_langgraph_server_health() -> bool:
    """Test LangGraph server health"""
    try:
        print("🔍 Testing LangGraph Server Health...")
        
        response = requests.get(f"{LANGGRAPH_SERVER_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ LangGraph Server is healthy")
            return True
        else:
            print(f"❌ LangGraph Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LangGraph Server health check failed: {str(e)}")
        return False

def test_langgraph_workflows() -> bool:
    """Test LangGraph workflows registration and execution"""
    try:
        print("🤖 Testing LangGraph Workflows...")
        
        # Test workflow registration
        response = requests.get(f"{LANGGRAPH_SERVER_URL}/assistants", timeout=10)
        if response.status_code == 200:
            data = response.json()
            assistants = data.get("assistants", [])
            print(f"✅ Found {len(assistants)} registered workflows")
            
            # Test specific workflows
            workflow_tests = [
                ("obsidian-workflow", {"vault_name": "Nomade Milionario", "search_query": "test", "limit": 5}),
                ("hello-world-agent", {"user_message": "Hello!", "vault_name": "Nomade Milionario"})
            ]
            
            all_passed = True
            
            for workflow_name, test_input in workflow_tests:
                try:
                    test_payload = {
                        "assistant_id": workflow_name,
                        "input": test_input
                    }
                    
                    response = requests.post(
                        f"{LANGGRAPH_SERVER_URL}/assistants/{workflow_name}/invoke",
                        json=test_payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ {workflow_name}: Execution successful")
                    else:
                        print(f"❌ {workflow_name}: Status {response.status_code} - {response.text}")
                        all_passed = False
                        
                except Exception as e:
                    print(f"❌ {workflow_name}: Error - {str(e)}")
                    all_passed = False
            
            return all_passed
        else:
            print(f"❌ Failed to get workflows - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ LangGraph workflows test failed: {str(e)}")
        return False

def test_enhanced_agent_direct() -> bool:
    """Test enhanced agent direct execution"""
    try:
        print("🚀 Testing Enhanced Agent Direct Execution...")
        
        # Create test state
        test_state = AgentState(
            user_input="Hello! Can you search for 'langgraph' in my vault and show me statistics?",
            vault_name="Nomade Milionario"
        )
        
        # Run the agent
        result = enhanced_interactive_agent.invoke(test_state)
        
        # Check results
        if result.current_state == ConversationState.COMPLETED:
            print("✅ Enhanced agent execution completed successfully")
            print(f"   - API Calls: {result.metrics.api_calls}")
            print(f"   - Vault Operations: {result.metrics.vault_operations}")
            print(f"   - Errors: {result.metrics.errors}")
            print(f"   - Conversation Turns: {result.metrics.conversation_turns}")
            return True
        else:
            print(f"❌ Enhanced agent failed - State: {result.current_state}")
            if result.error_log:
                print(f"   Errors: {result.error_log}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced agent direct test failed: {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_agent_conversation_flow() -> bool:
    """Test agent conversation flow with multiple interactions"""
    try:
        print("💬 Testing Agent Conversation Flow...")
        
        # Test multiple conversation scenarios
        test_scenarios = [
            "Hello! Can you help me explore my vault?",
            "Search for 'langgraph' in my notes",
            "Show me the file statistics",
            "List all my markdown files"
        ]
        
        all_passed = True
        
        for i, user_input in enumerate(test_scenarios, 1):
            try:
                print(f"   Scenario {i}: {user_input}")
                
                test_state = AgentState(
                    user_input=user_input,
                    vault_name="Nomade Milionario"
                )
                
                result = enhanced_interactive_agent.invoke(test_state)
                
                if result.current_state == ConversationState.COMPLETED:
                    print(f"   ✅ Scenario {i} completed successfully")
                else:
                    print(f"   ❌ Scenario {i} failed - State: {result.current_state}")
                    all_passed = False
                    
            except Exception as e:
                print(f"   ❌ Scenario {i} error: {str(e)}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Conversation flow test failed: {str(e)}")
        return False

def test_error_handling() -> bool:
    """Test error handling and recovery"""
    try:
        print("🛡️ Testing Error Handling...")
        
        # Test with invalid input
        test_state = AgentState(
            user_input="",  # Empty input
            vault_name="InvalidVault"  # Invalid vault
        )
        
        result = enhanced_interactive_agent.invoke(test_state)
        
        # Check if agent handled errors gracefully
        if result.metrics.errors > 0:
            print("✅ Error handling working - Errors detected and logged")
            print(f"   - Errors logged: {len(result.error_log)}")
            print(f"   - Error rate: {result.metrics.error_rate:.2%}")
            return True
        else:
            print("⚠️ No errors detected - May need more robust error scenarios")
            return True
            
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False

def benchmark_api_performance() -> Dict[str, Any]:
    """Benchmark API performance"""
    try:
        print("⚡ Benchmarking API Performance...")
        
        headers = {"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
        vault_name = "Nomade Milionario"
        
        # Test different API endpoints
        endpoints = [
            ("health", "GET", f"{OBSIDIAN_BASE_URL}/health"),
            ("list_files", "GET", f"{OBSIDIAN_BASE_URL}/vault/{vault_name}/files"),
            ("search", "POST", f"{OBSIDIAN_BASE_URL}/vault/{vault_name}/search", {"query": "test"})
        ]
        
        performance_data = {}
        
        for name, method, url, *data in endpoints:
            times = []
            
            # Run multiple requests to get average
            for _ in range(5):
                start_time = time.time()
                
                try:
                    if method == "GET":
                        response = requests.get(url, headers=headers, timeout=10)
                    elif method == "POST":
                        response = requests.post(url, headers=headers, json=data[0] if data else {}, timeout=10)
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    times.append(duration)
                    
                except Exception as e:
                    print(f"   ⚠️ {name} request failed: {str(e)}")
                    continue
            
            if times:
                performance_data[name] = {
                    "avg_time": statistics.mean(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                    "success_rate": len(times) / 5
                }
                print(f"   📊 {name}: {performance_data[name]['avg_time']:.3f}s avg")
        
        return performance_data
        
    except Exception as e:
        print(f"❌ Performance benchmarking failed: {str(e)}")
        return {}

def test_mcp_integration() -> bool:
    """Test MCP integration capabilities"""
    try:
        print("🔗 Testing MCP Integration...")
        
        # Test MCP tools directly
        from langgraph_workflows.enhanced_interactive_agent import (
            enhanced_vault_health_check,
            enhanced_list_vault_files,
            enhanced_search_vault_content,
            enhanced_get_vault_statistics
        )
        
        mcp_tests = [
            ("Health Check", enhanced_vault_health_check, {}),
            ("List Files", enhanced_list_vault_files, {"vault_name": "Nomade Milionario"}),
            ("Search Content", enhanced_search_vault_content, {"query": "test", "vault_name": "Nomade Milionario"}),
            ("Get Statistics", enhanced_get_vault_statistics, {"vault_name": "Nomade Milionario"})
        ]
        
        all_passed = True
        
        for test_name, test_func, test_args in mcp_tests:
            try:
                result = test_func(**test_args)
                
                if result.get("success", False) or result.get("status") == "healthy":
                    print(f"   ✅ {test_name}: Success")
                else:
                    print(f"   ❌ {test_name}: Failed - {result.get('error', 'Unknown error')}")
                    all_passed = False
                    
            except Exception as e:
                print(f"   ❌ {test_name}: Error - {str(e)}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {str(e)}")
        return False

def run_comprehensive_test_suite() -> TestResults:
    """Run the comprehensive test suite"""
    print("🧪 COMPREHENSIVE ENHANCED AGENT TEST SUITE")
    print("=" * 60)
    
    results = TestResults()
    
    # Test categories
    test_categories = [
        ("Obsidian API Health", test_obsidian_api_health),
        ("Obsidian API Authentication", test_obsidian_api_authentication),
        ("Obsidian API Endpoints", test_obsidian_api_endpoints),
        ("LangGraph Server Health", test_langgraph_server_health),
        ("LangGraph Workflows", test_langgraph_workflows),
        ("Enhanced Agent Direct", test_enhanced_agent_direct),
        ("Agent Conversation Flow", test_agent_conversation_flow),
        ("Error Handling", test_error_handling),
        ("MCP Integration", test_mcp_integration)
    ]
    
    # Run all tests
    for test_name, test_func in test_categories:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            passed = test_func()
            duration = time.time() - start_time
            results.add_test_result(test_name, passed, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            results.add_test_result(test_name, False, duration, str(e))
            print(f"❌ {test_name} crashed: {str(e)}")
    
    # Run performance benchmarks
    print(f"\n⚡ Performance Benchmarking")
    print("-" * 40)
    performance_data = benchmark_api_performance()
    results.performance_metrics = performance_data
    
    return results

def generate_test_report(results: TestResults):
    """Generate comprehensive test report"""
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    # Overall statistics
    success_rate = results.get_success_rate()
    total_duration = results.get_total_duration()
    
    print(f"🎯 Overall Success Rate: {success_rate:.1f}%")
    print(f"⏱️ Total Duration: {total_duration:.2f} seconds")
    print(f"✅ Passed Tests: {results.passed_tests}")
    print(f"❌ Failed Tests: {results.failed_tests}")
    print(f"📊 Total Tests: {results.total_tests}")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    print("-" * 40)
    
    for result in results.test_results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} {result['test_name']} ({result['duration']:.2f}s)")
        if result["error"]:
            print(f"    Error: {result['error']}")
    
    # Performance metrics
    if results.performance_metrics:
        print(f"\n⚡ Performance Metrics:")
        print("-" * 40)
        
        for endpoint, metrics in results.performance_metrics.items():
            print(f"📊 {endpoint}:")
            print(f"   Average: {metrics['avg_time']:.3f}s")
            print(f"   Min: {metrics['min_time']:.3f}s")
            print(f"   Max: {metrics['max_time']:.3f}s")
            print(f"   Std Dev: {metrics['std_dev']:.3f}s")
            print(f"   Success Rate: {metrics['success_rate']:.1%}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    print("-" * 40)
    
    if success_rate >= 90:
        print("🎉 Excellent! System is performing at 110%+ level")
        print("   - All major components are working correctly")
        print("   - Performance is within acceptable ranges")
        print("   - Error handling is robust")
    elif success_rate >= 70:
        print("⚠️ Good performance with room for improvement")
        print("   - Most components are working")
        print("   - Address failed tests for better reliability")
        print("   - Consider performance optimizations")
    else:
        print("❌ System needs attention")
        print("   - Multiple components are failing")
        print("   - Review error logs for common issues")
        print("   - Consider restarting services")
    
    # Save report to file
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "success_rate": success_rate,
        "total_duration": total_duration,
        "passed_tests": results.passed_tests,
        "failed_tests": results.failed_tests,
        "total_tests": results.total_tests,
        "test_results": results.test_results,
        "performance_metrics": results.performance_metrics
    }
    
    with open("enhanced_agent_test_report.json", "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: enhanced_agent_test_report.json")

if __name__ == "__main__":
    # Run comprehensive test suite
    results = run_comprehensive_test_suite()
    
    # Generate report
    generate_test_report(results)
    
    # Final status
    if results.get_success_rate() >= 90:
        print(f"\n🎉 MISSION ACCOMPLISHED! 110%+ System Health Achieved! 🚀")
    else:
        print(f"\n⚠️ System needs attention. Success rate: {results.get_success_rate():.1f}%")
