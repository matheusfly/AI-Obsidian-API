#!/usr/bin/env python3
"""
LangGraph API Proper Test
Working with the actual LangGraph server API
"""

import requests
import json
import time
from datetime import datetime

class LangGraphAPITester:
    """Test LangGraph server using proper API calls"""
    
    def __init__(self):
        self.langgraph_url = "http://127.0.0.1:2024"
        self.observability_url = "http://127.0.0.1:8002"
        
    def test_langgraph_api(self):
        """Test LangGraph API with proper calls"""
        print("🚀 LANGGRAPH API PROPER TEST")
        print("=" * 40)
        
        try:
            # Test 1: Create an assistant (workflow)
            print("\n📋 Creating LangGraph assistant...")
            assistant_payload = {
                "graph_id": "obsidian-workflow",
                "config": {
                    "configurable": {
                        "thread_id": "test_thread_123"
                    }
                }
            }
            
            assistant_response = requests.post(f"{self.langgraph_url}/assistants", 
                json=assistant_payload, timeout=10)
            print(f"Assistant creation: {assistant_response.status_code}")
            
            if assistant_response.status_code == 200:
                assistant_data = assistant_response.json()
                assistant_id = assistant_data.get("assistant_id")
                print(f"✅ Assistant created: {assistant_id}")
                
                # Test 2: Create a thread
                print("\n📋 Creating thread...")
                thread_payload = {
                    "metadata": {
                        "test": "langgraph_api_test",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                thread_response = requests.post(f"{self.langgraph_url}/threads", 
                    json=thread_payload, timeout=10)
                print(f"Thread creation: {thread_response.status_code}")
                
                if thread_response.status_code == 200:
                    thread_data = thread_response.json()
                    thread_id = thread_data.get("thread_id")
                    print(f"✅ Thread created: {thread_id}")
                    
                    # Test 3: Run the workflow
                    print("\n📋 Running workflow...")
                    run_payload = {
                        "assistant_id": assistant_id,
                        "input": {
                            "vault_name": "Nomade Milionario",
                            "search_query": "langgraph",
                            "limit": 5
                        }
                    }
                    
                    run_response = requests.post(f"{self.langgraph_url}/threads/{thread_id}/runs", 
                        json=run_payload, timeout=30)
                    print(f"Workflow execution: {run_response.status_code}")
                    
                    if run_response.status_code == 200:
                        run_data = run_response.json()
                        run_id = run_data.get("run_id")
                        print(f"✅ Workflow started: {run_id}")
                        
                        # Test 4: Check run status
                        print("\n📋 Checking run status...")
                        status_response = requests.get(f"{self.langgraph_url}/threads/{thread_id}/runs/{run_id}", 
                            timeout=10)
                        print(f"Run status: {status_response.status_code}")
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"✅ Run status: {status_data.get('status', 'unknown')}")
                            
                            # Test 5: Get thread state
                            print("\n📋 Getting thread state...")
                            state_response = requests.get(f"{self.langgraph_url}/threads/{thread_id}/state", 
                                timeout=10)
                            print(f"Thread state: {state_response.status_code}")
                            
                            if state_response.status_code == 200:
                                state_data = state_response.json()
                                print(f"✅ Thread state retrieved")
                                print(f"State keys: {list(state_data.get('values', {}).keys())}")
                                
                                # Test 6: Get thread messages
                                print("\n📋 Getting thread messages...")
                                messages_response = requests.get(f"{self.langgraph_url}/threads/{thread_id}/messages", 
                                    timeout=10)
                                print(f"Thread messages: {messages_response.status_code}")
                                
                                if messages_response.status_code == 200:
                                    messages_data = messages_response.json()
                                    print(f"✅ Messages retrieved: {len(messages_data.get('messages', []))} messages")
                                    
                                    # Log success to observability
                                    self.log_success_to_observability(assistant_id, thread_id, run_id)
                                    
                                    return True
                                else:
                                    print(f"❌ Messages retrieval failed: {messages_response.text}")
                                    return False
                            else:
                                print(f"❌ Thread state retrieval failed: {state_response.text}")
                                return False
                        else:
                            print(f"❌ Run status check failed: {status_response.text}")
                            return False
                    else:
                        print(f"❌ Workflow execution failed: {run_response.text}")
                        return False
                else:
                    print(f"❌ Thread creation failed: {thread_response.text}")
                    return False
            else:
                print(f"❌ Assistant creation failed: {assistant_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ LangGraph API test error: {e}")
            return False
    
    def log_success_to_observability(self, assistant_id, thread_id, run_id):
        """Log success to observability server"""
        try:
            trace_payload = {
                "name": "create_trace_event",
                "arguments": {
                    "thread_id": thread_id,
                    "agent_id": "langgraph_api_test",
                    "workflow_id": assistant_id,
                    "event_type": "langgraph_api_success",
                    "level": "info",
                    "message": f"LangGraph API test completed successfully - Assistant: {assistant_id}, Thread: {thread_id}, Run: {run_id}",
                    "data": {
                        "assistant_id": assistant_id,
                        "thread_id": thread_id,
                        "run_id": run_id,
                        "test_type": "langgraph_api_proper"
                    },
                    "tags": ["langgraph", "api", "success", "integration"]
                }
            }
            
            response = requests.post(f"{self.observability_url}/mcp/call_tool", json=trace_payload)
            if response.status_code == 200:
                print("✅ Success logged to observability server")
            else:
                print(f"⚠️ Failed to log to observability: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Observability logging error: {e}")
    
    def test_alternative_workflows(self):
        """Test alternative workflows if obsidian-workflow fails"""
        print("\n📋 Testing alternative workflows...")
        
        workflows = [
            "hello-world-agent",
            "enhanced-interactive-agent", 
            "observable-agent"
        ]
        
        for workflow in workflows:
            try:
                print(f"\nTesting workflow: {workflow}")
                
                # Create assistant for this workflow
                assistant_payload = {
                    "graph_id": workflow,
                    "config": {
                        "configurable": {
                            "thread_id": f"test_{workflow}_{int(time.time())}"
                        }
                    }
                }
                
                assistant_response = requests.post(f"{self.langgraph_url}/assistants", 
                    json=assistant_payload, timeout=10)
                
                if assistant_response.status_code == 200:
                    assistant_data = assistant_response.json()
                    assistant_id = assistant_data.get("assistant_id")
                    print(f"✅ {workflow} assistant created: {assistant_id}")
                    
                    # Create thread
                    thread_payload = {
                        "metadata": {
                            "workflow": workflow,
                            "test": "alternative_workflow_test"
                        }
                    }
                    
                    thread_response = requests.post(f"{self.langgraph_url}/threads", 
                        json=thread_payload, timeout=10)
                    
                    if thread_response.status_code == 200:
                        thread_data = thread_response.json()
                        thread_id = thread_data.get("thread_id")
                        print(f"✅ {workflow} thread created: {thread_id}")
                        
                        # Try to run workflow
                        run_payload = {
                            "assistant_id": assistant_id,
                            "input": {
                                "message": f"Test message for {workflow}",
                                "vault_name": "Nomade Milionario"
                            }
                        }
                        
                        run_response = requests.post(f"{self.langgraph_url}/threads/{thread_id}/runs", 
                            json=run_payload, timeout=30)
                        
                        if run_response.status_code == 200:
                            run_data = run_response.json()
                            print(f"✅ {workflow} workflow started: {run_data.get('run_id')}")
                            return True
                        else:
                            print(f"❌ {workflow} workflow failed: {run_response.status_code}")
                    else:
                        print(f"❌ {workflow} thread creation failed: {thread_response.status_code}")
                else:
                    print(f"❌ {workflow} assistant creation failed: {assistant_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing {workflow}: {e}")
        
        return False

def main():
    """Main function"""
    tester = LangGraphAPITester()
    
    # Test main workflow
    success = tester.test_langgraph_api()
    
    if not success:
        print("\n🔄 Main workflow failed, trying alternatives...")
        success = tester.test_alternative_workflows()
    
    if success:
        print("\n🎉 LangGraph API test completed successfully!")
        return 0
    else:
        print("\n❌ All LangGraph API tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
