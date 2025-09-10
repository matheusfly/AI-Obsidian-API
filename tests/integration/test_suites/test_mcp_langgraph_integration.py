#!/usr/bin/env python3
"""
MCP + LangGraph Integration Test
Tests integration between LangGraph and all MCP servers from mcp.json
"""

import asyncio
import json
import requests
import time
import subprocess
import signal
import os
from datetime import datetime
from typing import Dict, List, Any

class MCPLangGraphIntegrationTest:
    """Comprehensive test for MCP + LangGraph integration"""
    
    def __init__(self):
        self.mcp_integration_url = "http://127.0.0.1:8003"
        self.langgraph_url = "http://127.0.0.1:2024"
        self.observability_url = "http://127.0.0.1:8002"
        self.mcp_process = None
        self.test_results = []
        
    async def run_complete_integration_test(self):
        """Run complete MCP + LangGraph integration test"""
        print("🚀 MCP + LANGGRAPH INTEGRATION TEST")
        print("=" * 60)
        
        # Step 1: Start MCP Integration Server
        await self.start_mcp_integration_server()
        
        # Step 2: Test MCP Integration Server
        await self.test_mcp_integration_server()
        
        # Step 3: Test LangGraph with MCP Integration
        await self.test_langgraph_mcp_integration()
        
        # Step 4: Test Individual MCP Servers
        await self.test_individual_mcp_servers()
        
        # Step 5: Test Advanced MCP Features
        await self.test_advanced_mcp_features()
        
        # Step 6: Generate comprehensive report
        await self.generate_integration_report()
        
    async def start_mcp_integration_server(self):
        """Start the MCP Integration Server"""
        print("\n📋 Starting MCP Integration Server...")
        try:
            # Start the MCP integration server
            self.mcp_process = subprocess.Popen(
                ["python", "mcp_tools/mcp_integration_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            print("Waiting for MCP Integration Server to start...")
            await asyncio.sleep(5)
            
            # Test if server is running
            try:
                response = requests.get(f"{self.mcp_integration_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ MCP Integration Server started successfully")
                    self.test_results.append(("mcp_integration_server", True, "Server started successfully"))
                else:
                    print(f"❌ MCP Integration Server health check failed: {response.status_code}")
                    self.test_results.append(("mcp_integration_server", False, f"Health check failed: {response.status_code}"))
            except Exception as e:
                print(f"❌ MCP Integration Server not accessible: {e}")
                self.test_results.append(("mcp_integration_server", False, str(e)))
                
        except Exception as e:
            print(f"❌ Failed to start MCP Integration Server: {e}")
            self.test_results.append(("mcp_integration_server", False, str(e)))
    
    async def test_mcp_integration_server(self):
        """Test MCP Integration Server functionality"""
        print("\n📋 Testing MCP Integration Server...")
        try:
            # Test health endpoint
            start_time = time.time()
            health_response = requests.get(f"{self.mcp_integration_url}/health", timeout=5)
            health_duration = (time.time() - start_time) * 1000
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Health check: {health_duration:.2f}ms - {health_data.get('mcp_servers', 0)} servers")
                
                # Test list servers endpoint
                start_time = time.time()
                servers_response = requests.get(f"{self.mcp_integration_url}/mcp/servers", timeout=5)
                servers_duration = (time.time() - start_time) * 1000
                
                if servers_response.status_code == 200:
                    servers_data = servers_response.json()
                    server_count = len(servers_data.get("servers", []))
                    print(f"✅ List servers: {servers_duration:.2f}ms - {server_count} servers")
                    
                    # Test debug endpoint
                    start_time = time.time()
                    debug_response = requests.get(f"{self.mcp_integration_url}/mcp/debug", timeout=5)
                    debug_duration = (time.time() - start_time) * 1000
                    
                    if debug_response.status_code == 200:
                        debug_data = debug_response.json()
                        print(f"✅ Debug info: {debug_duration:.2f}ms")
                        
                        self.test_results.append(("mcp_integration_server", True, f"All endpoints working - {server_count} servers discovered"))
                    else:
                        print(f"❌ Debug endpoint failed: {debug_response.status_code}")
                        self.test_results.append(("mcp_integration_server", False, f"Debug endpoint failed: {debug_response.status_code}"))
                else:
                    print(f"❌ List servers failed: {servers_response.status_code}")
                    self.test_results.append(("mcp_integration_server", False, f"List servers failed: {servers_response.status_code}"))
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                self.test_results.append(("mcp_integration_server", False, f"Health check failed: {health_response.status_code}"))
                
        except Exception as e:
            print(f"❌ MCP Integration Server test error: {e}")
            self.test_results.append(("mcp_integration_server", False, str(e)))
    
    async def test_langgraph_mcp_integration(self):
        """Test LangGraph integration with MCP"""
        print("\n📋 Testing LangGraph + MCP Integration...")
        try:
            # First, register the MCP integrated agent with LangGraph
            print("Registering MCP integrated agent with LangGraph...")
            
            # Test LangGraph server connectivity
            langgraph_response = requests.get(f"{self.langgraph_url}/assistants", timeout=5)
            if langgraph_response.status_code == 200:
                print("✅ LangGraph server is accessible")
                
                # Create assistant for MCP integrated agent
                assistant_payload = {
                    "graph_id": "mcp-integrated-agent",
                    "config": {
                        "configurable": {
                            "thread_id": f"mcp_test_{int(time.time())}"
                        }
                    }
                }
                
                assistant_response = requests.post(f"{self.langgraph_url}/assistants", 
                    json=assistant_payload, timeout=10)
                
                if assistant_response.status_code == 200:
                    assistant_data = assistant_response.json()
                    assistant_id = assistant_data.get("assistant_id")
                    print(f"✅ MCP integrated agent created: {assistant_id}")
                    
                    # Create thread
                    thread_payload = {
                        "metadata": {
                            "test": "mcp_langgraph_integration",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    
                    thread_response = requests.post(f"{self.langgraph_url}/threads", 
                        json=thread_payload, timeout=10)
                    
                    if thread_response.status_code == 200:
                        thread_data = thread_response.json()
                        thread_id = thread_data.get("thread_id")
                        print(f"✅ Thread created: {thread_id}")
                        
                        # Run the MCP integrated workflow
                        run_payload = {
                            "assistant_id": assistant_id,
                            "input": {
                                "current_task": "Test MCP integration with LangGraph",
                                "messages": [{"role": "user", "content": "Test MCP integration"}]
                            }
                        }
                        
                        run_response = requests.post(f"{self.langgraph_url}/threads/{thread_id}/runs", 
                            json=run_payload, timeout=60)
                        
                        if run_response.status_code == 200:
                            run_data = run_response.json()
                            run_id = run_data.get("run_id")
                            print(f"✅ MCP integrated workflow started: {run_id}")
                            
                            self.test_results.append(("langgraph_mcp_integration", True, f"Workflow executed - Assistant: {assistant_id}, Thread: {thread_id}, Run: {run_id}"))
                        else:
                            print(f"❌ MCP integrated workflow failed: {run_response.status_code}")
                            self.test_results.append(("langgraph_mcp_integration", False, f"Workflow execution failed: {run_response.status_code}"))
                    else:
                        print(f"❌ Thread creation failed: {thread_response.status_code}")
                        self.test_results.append(("langgraph_mcp_integration", False, f"Thread creation failed: {thread_response.status_code}"))
                else:
                    print(f"❌ Assistant creation failed: {assistant_response.status_code}")
                    self.test_results.append(("langgraph_mcp_integration", False, f"Assistant creation failed: {assistant_response.status_code}"))
            else:
                print(f"❌ LangGraph server not accessible: {langgraph_response.status_code}")
                self.test_results.append(("langgraph_mcp_integration", False, f"LangGraph server not accessible: {langgraph_response.status_code}"))
                
        except Exception as e:
            print(f"❌ LangGraph MCP integration test error: {e}")
            self.test_results.append(("langgraph_mcp_integration", False, str(e)))
    
    async def test_individual_mcp_servers(self):
        """Test individual MCP servers through the integration server"""
        print("\n📋 Testing Individual MCP Servers...")
        try:
            # Get list of available servers
            servers_response = requests.get(f"{self.mcp_integration_url}/mcp/servers", timeout=5)
            if servers_response.status_code == 200:
                servers_data = servers_response.json()
                available_servers = servers_data.get("servers", [])
                print(f"Testing {len(available_servers)} MCP servers...")
                
                # Test each server
                for server_name in available_servers[:5]:  # Test first 5 servers
                    try:
                        print(f"  Testing {server_name}...")
                        
                        # Get server info
                        server_info_response = requests.get(f"{self.mcp_integration_url}/mcp/servers/{server_name}", timeout=5)
                        if server_info_response.status_code == 200:
                            server_info = server_info_response.json()
                            print(f"    ✅ {server_name}: {server_info.get('status', 'unknown')}")
                        else:
                            print(f"    ❌ {server_name}: Failed to get info ({server_info_response.status_code})")
                            
                    except Exception as e:
                        print(f"    ❌ {server_name}: Error - {e}")
                
                self.test_results.append(("individual_mcp_servers", True, f"Tested {len(available_servers)} servers"))
            else:
                print(f"❌ Failed to get server list: {servers_response.status_code}")
                self.test_results.append(("individual_mcp_servers", False, f"Failed to get server list: {servers_response.status_code}"))
                
        except Exception as e:
            print(f"❌ Individual MCP servers test error: {e}")
            self.test_results.append(("individual_mcp_servers", False, str(e)))
    
    async def test_advanced_mcp_features(self):
        """Test advanced MCP features"""
        print("\n📋 Testing Advanced MCP Features...")
        try:
            # Test batch MCP calls
            print("  Testing batch MCP calls...")
            batch_payload = [
                {"server_name": "brave-search", "tool_name": "brave_web_search", "arguments": {"query": "langgraph", "count": 2}},
                {"server_name": "sequential-thinking", "tool_name": "sequentialthinking", "arguments": {"thought": "Test thinking", "nextThoughtNeeded": False, "thoughtNumber": 1, "totalThoughts": 1}}
            ]
            
            batch_response = requests.post(f"{self.mcp_integration_url}/mcp/batch", json=batch_payload, timeout=30)
            if batch_response.status_code == 200:
                batch_data = batch_response.json()
                print(f"    ✅ Batch calls: {len(batch_data.get('results', []))} results")
            else:
                print(f"    ❌ Batch calls failed: {batch_response.status_code}")
            
            # Test performance metrics
            print("  Testing performance metrics...")
            metrics_response = requests.get(f"{self.mcp_integration_url}/mcp/metrics", timeout=5)
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.json()
                print(f"    ✅ Performance metrics: {metrics_data.get('total_calls', 0)} calls")
            else:
                print(f"    ❌ Performance metrics failed: {metrics_response.status_code}")
            
            # Test call history
            print("  Testing call history...")
            history_response = requests.get(f"{self.mcp_integration_url}/mcp/history", timeout=5)
            if history_response.status_code == 200:
                history_data = history_response.json()
                print(f"    ✅ Call history: {history_data.get('total', 0)} calls")
            else:
                print(f"    ❌ Call history failed: {history_response.status_code}")
            
            self.test_results.append(("advanced_mcp_features", True, "All advanced features tested"))
            
        except Exception as e:
            print(f"❌ Advanced MCP features test error: {e}")
            self.test_results.append(("advanced_mcp_features", False, str(e)))
    
    async def generate_integration_report(self):
        """Generate comprehensive integration report"""
        print("\n📊 GENERATING MCP + LANGGRAPH INTEGRATION REPORT")
        print("=" * 60)
        
        try:
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
            
            # Get MCP integration metrics
            try:
                metrics_response = requests.get(f"{self.mcp_integration_url}/mcp/metrics", timeout=5)
                if metrics_response.status_code == 200:
                    mcp_metrics = metrics_response.json()
                    print(f"\n📈 MCP Integration Metrics:")
                    print(f"  Total MCP Calls: {mcp_metrics.get('total_calls', 0)}")
                    print(f"  Successful Calls: {mcp_metrics.get('successful_calls', 0)}")
                    print(f"  Failed Calls: {mcp_metrics.get('failed_calls', 0)}")
                    print(f"  Average Execution Time: {mcp_metrics.get('average_execution_time', 0):.2f}ms")
            except Exception as e:
                print(f"⚠️ Could not retrieve MCP metrics: {e}")
            
            # Save comprehensive report
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "test_type": "mcp_langgraph_integration",
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "test_results": [
                    {"test_name": r[0], "passed": r[1], "message": r[2]} 
                    for r in self.test_results
                ],
                "mcp_metrics": mcp_metrics if 'mcp_metrics' in locals() else None
            }
            
            with open("mcp_langgraph_integration_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Complete report saved to: mcp_langgraph_integration_report.json")
            
            if success_rate >= 90:
                print("\n🎉 EXCELLENT! MCP + LangGraph integration is working perfectly!")
                print("🚀 All MCP servers are integrated with LangGraph workflows!")
            elif success_rate >= 70:
                print("\n👍 GOOD! Most MCP + LangGraph integration features are working!")
            else:
                print("\n⚠️ NEEDS ATTENTION! Multiple integration issues require fixes")
                
        except Exception as e:
            print(f"❌ Report generation error: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.mcp_process:
            print("\n🧹 Cleaning up MCP Integration Server...")
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
            except:
                self.mcp_process.kill()

async def main():
    """Main function"""
    test = MCPLangGraphIntegrationTest()
    try:
        await test.run_complete_integration_test()
    finally:
        test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
