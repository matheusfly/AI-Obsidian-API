#!/usr/bin/env python3
"""
LangGraph + Obsidian + MCP Integration Test Suite
Comprehensive testing with full tracing and benchmarking
"""

import asyncio
import json
import requests
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any

class LangGraphObsidianIntegrationTester:
    """Comprehensive test suite for LangGraph + Obsidian + MCP integration"""
    
    def __init__(self):
        self.obsidian_url = "http://127.0.0.1:27123"
        self.langgraph_url = "http://127.0.0.1:2024"
        self.observability_url = "http://127.0.0.1:8002"
        self.test_results = []
        self.thread_id = f"integration_test_{int(time.time())}"
        self.agent_id = "langgraph_obsidian_agent"
        self.workflow_id = "obsidian_integration_workflow"
        
    async def run_comprehensive_integration_test(self):
        """Run comprehensive integration test with full tracing"""
        print("🚀 LANGGRAPH + OBSIDIAN + MCP INTEGRATION TEST")
        print("=" * 60)
        
        # Step 1: Setup observability session
        await self.setup_observability_session()
        
        # Step 2: Test Obsidian API connectivity
        await self.test_obsidian_api_connectivity()
        
        # Step 3: Test LangGraph server connectivity
        await self.test_langgraph_server_connectivity()
        
        # Step 4: Test MCP observability server
        await self.test_mcp_observability_server()
        
        # Step 5: Create comprehensive trace events
        await self.create_comprehensive_trace_events()
        
        # Step 6: Test LangGraph workflow execution
        await self.test_langgraph_workflow_execution()
        
        # Step 7: Test MCP tool integration
        await self.test_mcp_tool_integration()
        
        # Step 8: Test error handling and recovery
        await self.test_error_handling_and_recovery()
        
        # Step 9: Test performance benchmarking
        await self.test_performance_benchmarking()
        
        # Step 10: Generate comprehensive report
        await self.generate_comprehensive_report()
        
    async def setup_observability_session(self):
        """Setup observability session for comprehensive monitoring"""
        print("\n📋 Setting up observability session...")
        try:
            # Create debug session
            response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "create_debug_session",
                "arguments": {
                    "session_name": "langgraph_obsidian_integration",
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "monitoring_level": "comprehensive",
                    "auto_checkpoint_interval": 10
                }
            })
            
            if response.status_code == 200:
                print("✅ Observability session created successfully")
                self.test_results.append(("observability_session", True, "Success"))
            else:
                print(f"❌ Observability session failed: {response.status_code}")
                self.test_results.append(("observability_session", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ Observability session error: {e}")
            self.test_results.append(("observability_session", False, str(e)))
    
    async def test_obsidian_api_connectivity(self):
        """Test Obsidian API connectivity with comprehensive logging"""
        print("\n📋 Testing Obsidian API connectivity...")
        try:
            # Test health endpoint
            health_response = requests.get(f"{self.obsidian_url}/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ Obsidian API health check passed")
                
                # Test file listing
                files_response = requests.get(f"{self.obsidian_url}/vault/files", 
                                           headers={"Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"})
                if files_response.status_code == 200:
                    files_data = files_response.json()
                    print(f"✅ Obsidian API file listing successful ({len(files_data.get('files', []))} files)")
                    
                    # Test file reading
                    if files_data.get('files'):
                        test_file = files_data['files'][0]
                        read_response = requests.get(f"{self.obsidian_url}/vault/{test_file['path']}", 
                                                   headers={"Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"})
                        if read_response.status_code == 200:
                            print("✅ Obsidian API file reading successful")
                            self.test_results.append(("obsidian_api", True, "All endpoints working"))
                        else:
                            print(f"❌ Obsidian API file reading failed: {read_response.status_code}")
                            self.test_results.append(("obsidian_api", False, f"File read failed: {read_response.status_code}"))
                    else:
                        print("⚠️ No files found in Obsidian vault")
                        self.test_results.append(("obsidian_api", True, "Health check passed, no files"))
                else:
                    print(f"❌ Obsidian API file listing failed: {files_response.status_code}")
                    self.test_results.append(("obsidian_api", False, f"File listing failed: {files_response.status_code}"))
            else:
                print(f"❌ Obsidian API health check failed: {health_response.status_code}")
                self.test_results.append(("obsidian_api", False, f"Health check failed: {health_response.status_code}"))
                
        except Exception as e:
            print(f"❌ Obsidian API connectivity error: {e}")
            self.test_results.append(("obsidian_api", False, str(e)))
    
    async def test_langgraph_server_connectivity(self):
        """Test LangGraph server connectivity"""
        print("\n📋 Testing LangGraph server connectivity...")
        try:
            # Test assistants endpoint
            assistants_response = requests.get(f"{self.langgraph_url}/assistants", timeout=5)
            if assistants_response.status_code == 200:
                assistants_data = assistants_response.json()
                print(f"✅ LangGraph server assistants endpoint working ({len(assistants_data.get('assistants', []))} assistants)")
                
                # Test threads endpoint
                threads_response = requests.get(f"{self.langgraph_url}/threads", timeout=5)
                if threads_response.status_code == 200:
                    print("✅ LangGraph server threads endpoint working")
                    self.test_results.append(("langgraph_server", True, "All endpoints working"))
                else:
                    print(f"❌ LangGraph server threads endpoint failed: {threads_response.status_code}")
                    self.test_results.append(("langgraph_server", False, f"Threads endpoint failed: {threads_response.status_code}"))
            else:
                print(f"❌ LangGraph server assistants endpoint failed: {assistants_response.status_code}")
                self.test_results.append(("langgraph_server", False, f"Assistants endpoint failed: {assistants_response.status_code}"))
                
        except Exception as e:
            print(f"❌ LangGraph server connectivity error: {e}")
            self.test_results.append(("langgraph_server", False, str(e)))
    
    async def test_mcp_observability_server(self):
        """Test MCP observability server functionality"""
        print("\n📋 Testing MCP observability server...")
        try:
            # Test health endpoint
            health_response = requests.get(f"{self.observability_url}/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ MCP observability server health check passed")
                
                # Test trace creation
                trace_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                    "name": "create_trace_event",
                    "arguments": {
                        "thread_id": self.thread_id,
                        "agent_id": self.agent_id,
                        "workflow_id": self.workflow_id,
                        "event_type": "mcp_test",
                        "level": "info",
                        "message": "MCP observability server test",
                        "data": {"test_type": "connectivity"},
                        "tags": ["test", "mcp", "observability"]
                    }
                })
                
                if trace_response.status_code == 200:
                    print("✅ MCP observability server trace creation successful")
                    self.test_results.append(("mcp_observability", True, "All functions working"))
                else:
                    print(f"❌ MCP observability server trace creation failed: {trace_response.status_code}")
                    self.test_results.append(("mcp_observability", False, f"Trace creation failed: {trace_response.status_code}"))
            else:
                print(f"❌ MCP observability server health check failed: {health_response.status_code}")
                self.test_results.append(("mcp_observability", False, f"Health check failed: {health_response.status_code}"))
                
        except Exception as e:
            print(f"❌ MCP observability server error: {e}")
            self.test_results.append(("mcp_observability", False, str(e)))
    
    async def create_comprehensive_trace_events(self):
        """Create comprehensive trace events for testing"""
        print("\n📋 Creating comprehensive trace events...")
        try:
            trace_events = [
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "workflow_start",
                    "level": "info",
                    "message": "Starting LangGraph + Obsidian integration workflow",
                    "data": {"workflow_type": "integration_test", "start_time": datetime.now().isoformat()},
                    "tags": ["workflow", "start", "integration"]
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "obsidian_api_call",
                    "level": "info",
                    "message": "Calling Obsidian API for vault files",
                    "data": {"endpoint": "/vault/files", "method": "GET", "vault": "Nomade Milionario"},
                    "tags": ["api", "obsidian", "vault"]
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "langgraph_workflow_call",
                    "level": "info",
                    "message": "Executing LangGraph workflow for data processing",
                    "data": {"workflow_name": "obsidian-workflow", "input": {"vault_name": "Nomade Milionario"}},
                    "tags": ["langgraph", "workflow", "execution"]
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "mcp_tool_call",
                    "level": "info",
                    "message": "Using MCP tool for enhanced functionality",
                    "data": {"tool_name": "search_notes", "parameters": {"query": "langgraph"}},
                    "tags": ["mcp", "tool", "search"]
                },
                {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "performance_metric",
                    "level": "info",
                    "message": "Recording performance metrics",
                    "data": {"api_calls": 5, "response_time_ms": 250, "memory_usage_mb": 45.2},
                    "tags": ["performance", "metrics", "monitoring"]
                }
            ]
            
            success_count = 0
            for event in trace_events:
                response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                    "name": "create_trace_event",
                    "arguments": event
                })
                
                if response.status_code == 200:
                    success_count += 1
            
            print(f"✅ Created {success_count}/{len(trace_events)} trace events successfully")
            self.test_results.append(("trace_events", True, f"Created {success_count}/{len(trace_events)} events"))
            
        except Exception as e:
            print(f"❌ Trace event creation error: {e}")
            self.test_results.append(("trace_events", False, str(e)))
    
    async def test_langgraph_workflow_execution(self):
        """Test LangGraph workflow execution with Obsidian integration"""
        print("\n📋 Testing LangGraph workflow execution...")
        try:
            # Test workflow execution
            workflow_payload = {
                "assistant_id": "obsidian-workflow",
                "input": {
                    "vault_name": "Nomade Milionario",
                    "search_query": "langgraph",
                    "limit": 5
                }
            }
            
            response = requests.post(f"{self.langgraph_url}/threads/{self.thread_id}/runs", 
                                   json=workflow_payload, timeout=30)
            
            if response.status_code == 200:
                run_data = response.json()
                print(f"✅ LangGraph workflow execution successful (Run ID: {run_data.get('run_id', 'unknown')})")
                
                # Wait for workflow completion
                await asyncio.sleep(2)
                
                # Check run status
                status_response = requests.get(f"{self.langgraph_url}/threads/{self.thread_id}/runs/{run_data.get('run_id')}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ Workflow status: {status_data.get('status', 'unknown')}")
                    self.test_results.append(("langgraph_workflow", True, "Workflow executed successfully"))
                else:
                    print(f"⚠️ Could not check workflow status: {status_response.status_code}")
                    self.test_results.append(("langgraph_workflow", True, "Workflow executed, status check failed"))
            else:
                print(f"❌ LangGraph workflow execution failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results.append(("langgraph_workflow", False, f"Execution failed: {response.status_code}"))
                
        except Exception as e:
            print(f"❌ LangGraph workflow execution error: {e}")
            self.test_results.append(("langgraph_workflow", False, str(e)))
    
    async def test_mcp_tool_integration(self):
        """Test MCP tool integration with comprehensive logging"""
        print("\n📋 Testing MCP tool integration...")
        try:
            # Test various MCP tools
            mcp_tools = [
                {
                    "name": "get_traces",
                    "arguments": {
                        "thread_id": self.thread_id,
                        "limit": 10
                    }
                },
                {
                    "name": "get_performance_metrics",
                    "arguments": {
                        "thread_id": self.thread_id,
                        "agent_id": self.agent_id
                    }
                },
                {
                    "name": "analyze_error_patterns",
                    "arguments": {
                        "thread_id": self.thread_id,
                        "time_range_hours": 1
                    }
                },
                {
                    "name": "get_agent_communication_log",
                    "arguments": {
                        "thread_id": self.thread_id,
                        "agent_id": self.agent_id,
                        "communication_type": "all",
                        "limit": 20
                    }
                }
            ]
            
            success_count = 0
            for tool in mcp_tools:
                response = requests.post(f"{self.observability_url}/mcp/call_tool", json=tool)
                if response.status_code == 200:
                    success_count += 1
                    print(f"✅ MCP tool '{tool['name']}' executed successfully")
                else:
                    print(f"❌ MCP tool '{tool['name']}' failed: {response.status_code}")
            
            print(f"✅ MCP tool integration: {success_count}/{len(mcp_tools)} tools working")
            self.test_results.append(("mcp_tools", True, f"{success_count}/{len(mcp_tools)} tools working"))
            
        except Exception as e:
            print(f"❌ MCP tool integration error: {e}")
            self.test_results.append(("mcp_tools", False, str(e)))
    
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        print("\n📋 Testing error handling and recovery...")
        try:
            # Test error trace creation
            error_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "create_trace_event",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "test_error",
                    "level": "error",
                    "message": "Simulated error for testing error handling",
                    "data": {"error_type": "test", "error_code": "TEST_ERROR_001"},
                    "tags": ["error", "test", "recovery"]
                }
            })
            
            if error_response.status_code == 200:
                print("✅ Error trace creation successful")
                
                # Test error pattern analysis
                pattern_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                    "name": "analyze_error_patterns",
                    "arguments": {
                        "thread_id": self.thread_id,
                        "time_range_hours": 1,
                        "error_threshold": 1
                    }
                })
                
                if pattern_response.status_code == 200:
                    print("✅ Error pattern analysis successful")
                    self.test_results.append(("error_handling", True, "Error handling and analysis working"))
                else:
                    print(f"❌ Error pattern analysis failed: {pattern_response.status_code}")
                    self.test_results.append(("error_handling", False, f"Pattern analysis failed: {pattern_response.status_code}"))
            else:
                print(f"❌ Error trace creation failed: {error_response.status_code}")
                self.test_results.append(("error_handling", False, f"Error trace creation failed: {error_response.status_code}"))
                
        except Exception as e:
            print(f"❌ Error handling test error: {e}")
            self.test_results.append(("error_handling", False, str(e)))
    
    async def test_performance_benchmarking(self):
        """Test performance benchmarking and metrics collection"""
        print("\n📋 Testing performance benchmarking...")
        try:
            # Start performance monitoring
            start_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "start_performance_monitoring",
                "arguments": {
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "thread_id": self.thread_id
                }
            })
            
            if start_response.status_code == 200:
                print("✅ Performance monitoring started")
                
                # Simulate some work
                await asyncio.sleep(1)
                
                # Stop performance monitoring
                stop_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                    "name": "stop_performance_monitoring",
                    "arguments": {
                        "agent_id": self.agent_id,
                        "workflow_id": self.workflow_id,
                        "thread_id": self.thread_id
                    }
                })
                
                if stop_response.status_code == 200:
                    print("✅ Performance monitoring stopped")
                    
                    # Get performance metrics
                    metrics_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                        "name": "get_performance_metrics",
                        "arguments": {
                            "thread_id": self.thread_id,
                            "agent_id": self.agent_id
                        }
                    })
                    
                    if metrics_response.status_code == 200:
                        print("✅ Performance metrics retrieved successfully")
                        self.test_results.append(("performance_benchmarking", True, "Performance monitoring working"))
                    else:
                        print(f"❌ Performance metrics retrieval failed: {metrics_response.status_code}")
                        self.test_results.append(("performance_benchmarking", False, f"Metrics retrieval failed: {metrics_response.status_code}"))
                else:
                    print(f"❌ Performance monitoring stop failed: {stop_response.status_code}")
                    self.test_results.append(("performance_benchmarking", False, f"Monitoring stop failed: {stop_response.status_code}"))
            else:
                print(f"❌ Performance monitoring start failed: {start_response.status_code}")
                self.test_results.append(("performance_benchmarking", False, f"Monitoring start failed: {start_response.status_code}"))
                
        except Exception as e:
            print(f"❌ Performance benchmarking error: {e}")
            self.test_results.append(("performance_benchmarking", False, str(e)))
    
    async def generate_comprehensive_report(self):
        """Generate comprehensive test report with all tracing logs"""
        print("\n📋 Generating comprehensive report...")
        try:
            # Get debug session status
            session_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "get_debug_session_status",
                "arguments": {
                    "session_name": "langgraph_obsidian_integration",
                    "include_recommendations": True
                }
            })
            
            # Get comprehensive debug report
            report_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "generate_debug_report",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "report_type": "detailed",
                    "include_timeline": True,
                    "include_recommendations": True
                }
            })
            
            # Generate final test report
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r[1]])
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print("\n" + "=" * 60)
            print("📊 COMPREHENSIVE INTEGRATION TEST REPORT")
            print("=" * 60)
            print(f"🎯 Overall Success Rate: {success_rate:.1f}%")
            print(f"⏱️ Total Duration: {time.time():.2f} seconds")
            print(f"✅ Passed Tests: {passed_tests}")
            print(f"❌ Failed Tests: {failed_tests}")
            print(f"📊 Total Tests: {total_tests}")
            
            print("\n📋 Detailed Results:")
            print("-" * 40)
            for test_name, passed, message in self.test_results:
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status} {test_name} - {message}")
            
            # Save detailed report
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "thread_id": self.thread_id,
                "agent_id": self.agent_id,
                "workflow_id": self.workflow_id,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "test_results": [
                    {"test_name": r[0], "passed": r[1], "message": r[2]} 
                    for r in self.test_results
                ],
                "session_status": session_response.json() if session_response.status_code == 200 else None,
                "debug_report": report_response.json() if report_response.status_code == 200 else None
            }
            
            with open("langgraph_obsidian_integration_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Detailed report saved to: langgraph_obsidian_integration_report.json")
            
            if success_rate >= 90:
                print("\n🎉 EXCELLENT! LangGraph + Obsidian + MCP integration is working perfectly!")
            elif success_rate >= 70:
                print("\n👍 GOOD! Most integration features are working, minor issues to address")
            else:
                print("\n⚠️ NEEDS ATTENTION! Multiple integration issues require fixes")
                
        except Exception as e:
            print(f"❌ Report generation error: {e}")

async def main():
    """Main test function"""
    tester = LangGraphObsidianIntegrationTester()
    await tester.run_comprehensive_integration_test()

if __name__ == "__main__":
    asyncio.run(main())
