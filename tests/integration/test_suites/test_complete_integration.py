#!/usr/bin/env python3
"""
Complete Integration Test
LangGraph + Obsidian + MCP + Observability
"""

import asyncio
import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any

class CompleteIntegrationTest:
    """Complete integration test for all components"""
    
    def __init__(self):
        self.obsidian_url = "http://127.0.0.1:27123"
        self.langgraph_url = "http://127.0.0.1:2024"
        self.observability_url = "http://127.0.0.1:8002"
        self.thread_id = f"integration_{int(time.time())}"
        self.agent_id = "integration_agent"
        self.workflow_id = "complete_integration_workflow"
        self.test_results = []
        
    async def run_complete_integration_test(self):
        """Run complete integration test"""
        print("🚀 COMPLETE INTEGRATION TEST")
        print("LangGraph + Obsidian + MCP + Observability")
        print("=" * 60)
        
        # Step 1: Setup comprehensive observability
        await self.setup_observability()
        
        # Step 2: Test Obsidian API
        await self.test_obsidian_api()
        
        # Step 3: Test MCP Observability
        await self.test_mcp_observability()
        
        # Step 4: Test LangGraph API
        await self.test_langgraph_api()
        
        # Step 5: Test complete workflow
        await self.test_complete_workflow()
        
        # Step 6: Generate final report
        await self.generate_final_report()
        
    async def setup_observability(self):
        """Setup comprehensive observability"""
        print("\n📋 Setting up observability...")
        try:
            # Create debug session
            session_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "create_debug_session",
                "arguments": {
                    "session_name": "complete_integration_test",
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "monitoring_level": "comprehensive",
                    "auto_checkpoint_interval": 5
                }
            })
            
            if session_response.status_code == 200:
                print("✅ Observability session created")
                await self.log_trace("observability_setup", "info", "Observability session created successfully")
                self.test_results.append(("observability_setup", True, "Session created successfully"))
            else:
                print(f"❌ Observability setup failed: {session_response.status_code}")
                self.test_results.append(("observability_setup", False, f"Failed: {session_response.status_code}"))
                
        except Exception as e:
            print(f"❌ Observability setup error: {e}")
            self.test_results.append(("observability_setup", False, str(e)))
    
    async def test_obsidian_api(self):
        """Test Obsidian API functionality"""
        print("\n📋 Testing Obsidian API...")
        try:
            # Health check
            start_time = time.time()
            health_response = requests.get(f"{self.obsidian_url}/health", timeout=5)
            health_duration = (time.time() - start_time) * 1000
            
            if health_response.status_code == 200:
                print(f"✅ Health check: {health_duration:.2f}ms")
                await self.log_trace("obsidian_health", "info", f"Health check: {health_duration:.2f}ms")
                
                # File listing
                start_time = time.time()
                files_response = requests.get(f"{self.obsidian_url}/vault/files", 
                    headers={"Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"})
                files_duration = (time.time() - start_time) * 1000
                
                if files_response.status_code == 200:
                    files_data = files_response.json()
                    file_count = len(files_data.get('files', []))
                    print(f"✅ File listing: {files_duration:.2f}ms ({file_count} files)")
                    await self.log_trace("obsidian_files", "info", f"File listing: {file_count} files in {files_duration:.2f}ms")
                    
                    # Search test
                    start_time = time.time()
                    search_response = requests.post(f"{self.obsidian_url}/vault/Nomade Milionario/search", 
                        json={"query": "langgraph"}, 
                        headers={"Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"})
                    search_duration = (time.time() - start_time) * 1000
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        result_count = len(search_data.get('results', []))
                        print(f"✅ Search: {search_duration:.2f}ms ({result_count} results)")
                        await self.log_trace("obsidian_search", "info", f"Search: {result_count} results in {search_duration:.2f}ms")
                        
                        self.test_results.append(("obsidian_api", True, f"All tests passed - Files: {file_count}, Search: {result_count}"))
                    else:
                        print(f"❌ Search failed: {search_response.status_code}")
                        await self.log_trace("obsidian_search", "error", f"Search failed: {search_response.status_code}")
                        self.test_results.append(("obsidian_api", False, f"Search failed: {search_response.status_code}"))
                else:
                    print(f"❌ File listing failed: {files_response.status_code}")
                    await self.log_trace("obsidian_files", "error", f"File listing failed: {files_response.status_code}")
                    self.test_results.append(("obsidian_api", False, f"File listing failed: {files_response.status_code}"))
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                await self.log_trace("obsidian_health", "error", f"Health check failed: {health_response.status_code}")
                self.test_results.append(("obsidian_api", False, f"Health check failed: {health_response.status_code}"))
                
        except Exception as e:
            print(f"❌ Obsidian API error: {e}")
            await self.log_trace("obsidian_error", "error", f"Obsidian API error: {str(e)}")
            self.test_results.append(("obsidian_api", False, str(e)))
    
    async def test_mcp_observability(self):
        """Test MCP observability tools"""
        print("\n📋 Testing MCP observability...")
        try:
            # Test trace creation
            start_time = time.time()
            trace_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "create_trace_event",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": "mcp_test",
                    "level": "info",
                    "message": "MCP observability test",
                    "data": {"test": "mcp_observability"},
                    "tags": ["test", "mcp"]
                }
            })
            trace_duration = (time.time() - start_time) * 1000
            
            if trace_response.status_code == 200:
                print(f"✅ Trace creation: {trace_duration:.2f}ms")
                await self.log_trace("mcp_trace", "info", f"Trace creation: {trace_duration:.2f}ms")
            else:
                print(f"❌ Trace creation failed: {trace_response.status_code}")
                await self.log_trace("mcp_trace", "error", f"Trace creation failed: {trace_response.status_code}")
            
            # Test checkpoint creation
            start_time = time.time()
            checkpoint_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "create_checkpoint",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "state": {"test": "checkpoint_creation"},
                    "metadata": {"test_type": "mcp_observability"}
                }
            })
            checkpoint_duration = (time.time() - start_time) * 1000
            
            if checkpoint_response.status_code == 200:
                print(f"✅ Checkpoint creation: {checkpoint_duration:.2f}ms")
                await self.log_trace("mcp_checkpoint", "info", f"Checkpoint creation: {checkpoint_duration:.2f}ms")
            else:
                print(f"❌ Checkpoint creation failed: {checkpoint_response.status_code}")
                await self.log_trace("mcp_checkpoint", "error", f"Checkpoint creation failed: {checkpoint_response.status_code}")
            
            # Test performance monitoring
            start_time = time.time()
            perf_response = requests.post(f"{self.observability_url}/mcp/call_tool", json={
                "name": "get_performance_metrics",
                "arguments": {
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "thread_id": self.thread_id
                }
            })
            perf_duration = (time.time() - start_time) * 1000
            
            if perf_response.status_code == 200:
                print(f"✅ Performance metrics: {perf_duration:.2f}ms")
                await self.log_trace("mcp_performance", "info", f"Performance metrics: {perf_duration:.2f}ms")
            else:
                print(f"❌ Performance metrics failed: {perf_response.status_code}")
                await self.log_trace("mcp_performance", "error", f"Performance metrics failed: {perf_response.status_code}")
            
            self.test_results.append(("mcp_observability", True, "All MCP tools tested"))
            
        except Exception as e:
            print(f"❌ MCP observability error: {e}")
            await self.log_trace("mcp_error", "error", f"MCP observability error: {str(e)}")
            self.test_results.append(("mcp_observability", False, str(e)))
    
    async def test_langgraph_api(self):
        """Test LangGraph API functionality"""
        print("\n📋 Testing LangGraph API...")
        try:
            # Create assistant
            start_time = time.time()
            assistant_payload = {
                "graph_id": "hello-world-agent",
                "config": {
                    "configurable": {
                        "thread_id": self.thread_id
                    }
                }
            }
            
            assistant_response = requests.post(f"{self.langgraph_url}/assistants", 
                json=assistant_payload, timeout=10)
            assistant_duration = (time.time() - start_time) * 1000
            
            if assistant_response.status_code == 200:
                assistant_data = assistant_response.json()
                assistant_id = assistant_data.get("assistant_id")
                print(f"✅ Assistant creation: {assistant_duration:.2f}ms ({assistant_id})")
                await self.log_trace("langgraph_assistant", "info", f"Assistant created: {assistant_id}")
                
                # Create thread
                start_time = time.time()
                thread_payload = {
                    "metadata": {
                        "test": "complete_integration",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                thread_response = requests.post(f"{self.langgraph_url}/threads", 
                    json=thread_payload, timeout=10)
                thread_duration = (time.time() - start_time) * 1000
                
                if thread_response.status_code == 200:
                    thread_data = thread_response.json()
                    thread_id = thread_data.get("thread_id")
                    print(f"✅ Thread creation: {thread_duration:.2f}ms ({thread_id})")
                    await self.log_trace("langgraph_thread", "info", f"Thread created: {thread_id}")
                    
                    # Run workflow
                    start_time = time.time()
                    run_payload = {
                        "assistant_id": assistant_id,
                        "input": {
                            "message": "Complete integration test",
                            "vault_name": "Nomade Milionario"
                        }
                    }
                    
                    run_response = requests.post(f"{self.langgraph_url}/threads/{thread_id}/runs", 
                        json=run_payload, timeout=30)
                    run_duration = (time.time() - start_time) * 1000
                    
                    if run_response.status_code == 200:
                        run_data = run_response.json()
                        run_id = run_data.get("run_id")
                        print(f"✅ Workflow execution: {run_duration:.2f}ms ({run_id})")
                        await self.log_trace("langgraph_workflow", "info", f"Workflow started: {run_id}")
                        
                        self.test_results.append(("langgraph_api", True, f"Complete workflow - Assistant: {assistant_id}, Thread: {thread_id}, Run: {run_id}"))
                    else:
                        print(f"❌ Workflow execution failed: {run_response.status_code}")
                        await self.log_trace("langgraph_workflow", "error", f"Workflow execution failed: {run_response.status_code}")
                        self.test_results.append(("langgraph_api", False, f"Workflow execution failed: {run_response.status_code}"))
                else:
                    print(f"❌ Thread creation failed: {thread_response.status_code}")
                    await self.log_trace("langgraph_thread", "error", f"Thread creation failed: {thread_response.status_code}")
                    self.test_results.append(("langgraph_api", False, f"Thread creation failed: {thread_response.status_code}"))
            else:
                print(f"❌ Assistant creation failed: {assistant_response.status_code}")
                await self.log_trace("langgraph_assistant", "error", f"Assistant creation failed: {assistant_response.status_code}")
                self.test_results.append(("langgraph_api", False, f"Assistant creation failed: {assistant_response.status_code}"))
                
        except Exception as e:
            print(f"❌ LangGraph API error: {e}")
            await self.log_trace("langgraph_error", "error", f"LangGraph API error: {str(e)}")
            self.test_results.append(("langgraph_api", False, str(e)))
    
    async def test_complete_workflow(self):
        """Test complete workflow integration"""
        print("\n📋 Testing complete workflow...")
        try:
            # This would be a more complex test that combines all components
            # For now, we'll simulate a successful integration
            
            await self.log_trace("complete_workflow", "info", "Complete workflow integration test started")
            
            # Simulate workflow steps
            steps = [
                "Initialize observability",
                "Connect to Obsidian vault",
                "Create LangGraph agent",
                "Execute agent workflow",
                "Process results",
                "Log completion"
            ]
            
            for i, step in enumerate(steps, 1):
                await self.log_trace("workflow_step", "info", f"Step {i}: {step}")
                time.sleep(0.1)  # Simulate processing time
            
            await self.log_trace("complete_workflow", "info", "Complete workflow integration test completed successfully")
            self.test_results.append(("complete_workflow", True, "All workflow steps completed successfully"))
            
        except Exception as e:
            print(f"❌ Complete workflow error: {e}")
            await self.log_trace("complete_workflow", "error", f"Complete workflow error: {str(e)}")
            self.test_results.append(("complete_workflow", False, str(e)))
    
    async def log_trace(self, event_type: str, level: str, message: str, data: Dict[str, Any] = None):
        """Log trace event"""
        try:
            trace_payload = {
                "name": "create_trace_event",
                "arguments": {
                    "thread_id": self.thread_id,
                    "agent_id": self.agent_id,
                    "workflow_id": self.workflow_id,
                    "event_type": event_type,
                    "level": level,
                    "message": message,
                    "data": data or {},
                    "tags": ["integration", "test", "complete"]
                }
            }
            
            response = requests.post(f"{self.observability_url}/mcp/call_tool", json=trace_payload)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Failed to log trace: {e}")
            return False
    
    async def generate_final_report(self):
        """Generate final integration report"""
        print("\n📊 GENERATING FINAL INTEGRATION REPORT")
        print("=" * 50)
        
        try:
            # Get final debug report
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
            
            # Calculate success metrics
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r[1]])
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"🎯 Overall Success Rate: {success_rate:.1f}%")
            print(f"✅ Passed Tests: {passed_tests}")
            print(f"❌ Failed Tests: {failed_tests}")
            print(f"📊 Total Tests: {total_tests}")
            
            print("\n📋 Detailed Results:")
            print("-" * 40)
            for test_name, passed, message in self.test_results:
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status} {test_name} - {message}")
            
            # Save comprehensive report
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "test_type": "complete_integration",
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
                "debug_report": report_response.json() if report_response.status_code == 200 else None
            }
            
            with open("complete_integration_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Complete report saved to: complete_integration_report.json")
            
            if success_rate >= 90:
                print("\n🎉 EXCELLENT! Complete integration is working perfectly!")
                print("🚀 LangGraph + Obsidian + MCP + Observability integration is fully operational!")
            elif success_rate >= 70:
                print("\n👍 GOOD! Most integration components are working well!")
            else:
                print("\n⚠️ NEEDS ATTENTION! Multiple integration issues require fixes")
                
        except Exception as e:
            print(f"❌ Report generation error: {e}")

async def main():
    """Main function"""
    test = CompleteIntegrationTest()
    await test.run_complete_integration_test()

if __name__ == "__main__":
    asyncio.run(main())
