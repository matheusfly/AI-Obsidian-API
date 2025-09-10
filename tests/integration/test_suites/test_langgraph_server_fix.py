#!/usr/bin/env python3
"""
LangGraph Server Fix and Test
Focused on getting LangGraph server working properly
"""

import requests
import json
import time
import subprocess
import os
import signal
import sys
from datetime import datetime

class LangGraphServerFixer:
    """Fix and test LangGraph server functionality"""
    
    def __init__(self):
        self.langgraph_url = "http://127.0.0.1:2024"
        self.observability_url = "http://127.0.0.1:8002"
        self.langgraph_process = None
        
    def check_langgraph_server_status(self):
        """Check if LangGraph server is running and accessible"""
        print("🔍 Checking LangGraph server status...")
        try:
            # Test basic connectivity
            response = requests.get(f"{self.langgraph_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ LangGraph server is running and healthy")
                return True
            else:
                print(f"❌ LangGraph server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ LangGraph server is not accessible")
            return False
        except Exception as e:
            print(f"❌ Error checking LangGraph server: {e}")
            return False
    
    def check_langgraph_endpoints(self):
        """Check all available LangGraph endpoints"""
        print("\n🔍 Checking LangGraph endpoints...")
        endpoints = [
            ("/health", "GET"),
            ("/assistants", "GET"),
            ("/threads", "GET"),
            ("/runs", "GET"),
            ("/", "GET")
        ]
        
        results = {}
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.langgraph_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.langgraph_url}{endpoint}", timeout=5)
                
                results[endpoint] = {
                    "status_code": response.status_code,
                    "method": method,
                    "accessible": True,
                    "response_preview": response.text[:200] if response.text else "No content"
                }
                print(f"  {method} {endpoint}: {response.status_code}")
                
            except Exception as e:
                results[endpoint] = {
                    "status_code": None,
                    "method": method,
                    "accessible": False,
                    "error": str(e)
                }
                print(f"  {method} {endpoint}: ERROR - {e}")
        
        return results
    
    def start_langgraph_server(self):
        """Start LangGraph server using langgraph dev command"""
        print("\n🚀 Starting LangGraph server...")
        try:
            # Check if langgraph is available
            result = subprocess.run(["langgraph", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ LangGraph CLI found: {result.stdout.strip()}")
            else:
                print("❌ LangGraph CLI not found, trying alternative path...")
                # Try alternative path
                alt_path = r"C:\Users\mathe\AppData\Local\Programs\Python\Python313\Scripts\langgraph.exe"
                if os.path.exists(alt_path):
                    print(f"✅ Found LangGraph at: {alt_path}")
                    # Update PATH or use full path
                    os.environ["PATH"] = os.path.dirname(alt_path) + ";" + os.environ["PATH"]
                else:
                    print("❌ LangGraph CLI not found in expected locations")
                    return False
            
            # Start langgraph dev server
            print("Starting langgraph dev server...")
            self.langgraph_process = subprocess.Popen(
                ["langgraph", "dev", "--host", "127.0.0.1", "--port", "2024"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for server to start
            print("Waiting for server to start...")
            time.sleep(10)
            
            # Check if server is now accessible
            if self.check_langgraph_server_status():
                print("✅ LangGraph server started successfully")
                return True
            else:
                print("❌ LangGraph server failed to start properly")
                return False
                
        except Exception as e:
            print(f"❌ Error starting LangGraph server: {e}")
            return False
    
    def test_langgraph_workflows(self):
        """Test LangGraph workflow execution"""
        print("\n🧪 Testing LangGraph workflows...")
        try:
            # First, check if assistants are available
            assistants_response = requests.get(f"{self.langgraph_url}/assistants", timeout=10)
            print(f"Assistants endpoint: {assistants_response.status_code}")
            
            if assistants_response.status_code == 200:
                assistants_data = assistants_response.json()
                print(f"Available assistants: {assistants_data}")
                
                # Try to create a thread
                thread_response = requests.post(f"{self.langgraph_url}/threads", 
                    json={"metadata": {"test": "langgraph_fix"}}, timeout=10)
                print(f"Thread creation: {thread_response.status_code}")
                
                if thread_response.status_code == 200:
                    thread_data = thread_response.json()
                    thread_id = thread_data.get("thread_id")
                    print(f"Created thread: {thread_id}")
                    
                    # Try to run a workflow
                    if assistants_data and len(assistants_data) > 0:
                        assistant_id = assistants_data[0].get("assistant_id")
                        print(f"Using assistant: {assistant_id}")
                        
                        run_payload = {
                            "assistant_id": assistant_id,
                            "input": {
                                "vault_name": "Nomade Milionario",
                                "search_query": "test",
                                "limit": 3
                            }
                        }
                        
                        run_response = requests.post(f"{self.langgraph_url}/threads/{thread_id}/runs", 
                            json=run_payload, timeout=30)
                        print(f"Workflow execution: {run_response.status_code}")
                        
                        if run_response.status_code == 200:
                            run_data = run_response.json()
                            print(f"Workflow started: {run_data}")
                            return True
                        else:
                            print(f"Workflow execution failed: {run_response.text}")
                            return False
                    else:
                        print("No assistants available")
                        return False
                else:
                    print(f"Thread creation failed: {thread_response.text}")
                    return False
            else:
                print(f"Assistants endpoint failed: {assistants_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing LangGraph workflows: {e}")
            return False
    
    def fix_langgraph_configuration(self):
        """Fix LangGraph configuration issues"""
        print("\n🔧 Fixing LangGraph configuration...")
        try:
            # Check langgraph.json
            if os.path.exists("langgraph.json"):
                with open("langgraph.json", "r") as f:
                    config = json.load(f)
                print("Current langgraph.json configuration:")
                print(json.dumps(config, indent=2))
                
                # Ensure proper configuration
                if "graphs" not in config:
                    config["graphs"] = {}
                
                # Add missing configurations
                if "env" not in config:
                    config["env"] = ".env"
                
                if "python_version" not in config:
                    config["python_version"] = "3.11"
                
                # Save updated configuration
                with open("langgraph.json", "w") as f:
                    json.dump(config, f, indent=2)
                print("✅ Updated langgraph.json configuration")
            else:
                print("❌ langgraph.json not found")
                return False
            
            # Check .env file
            if os.path.exists(".env"):
                print("✅ .env file exists")
            else:
                print("⚠️ .env file not found, creating basic one...")
                with open(".env", "w") as f:
                    f.write("LANGCHAIN_API_KEY=your_api_key_here\n")
                    f.write("LANGCHAIN_TRACING_V2=true\n")
                    f.write("LANGCHAIN_PROJECT=langgraph-obsidian\n")
                print("✅ Created basic .env file")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fixing configuration: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive LangGraph server test and fix"""
        print("🚀 LANGGRAPH SERVER FIX AND TEST")
        print("=" * 50)
        
        # Step 1: Check current status
        if self.check_langgraph_server_status():
            print("✅ LangGraph server is already running")
        else:
            print("❌ LangGraph server is not running, attempting to start...")
            
            # Step 2: Fix configuration
            if not self.fix_langgraph_configuration():
                print("❌ Configuration fix failed")
                return False
            
            # Step 3: Start server
            if not self.start_langgraph_server():
                print("❌ Failed to start LangGraph server")
                return False
        
        # Step 4: Check endpoints
        endpoint_results = self.check_langgraph_endpoints()
        
        # Step 5: Test workflows
        workflow_success = self.test_langgraph_workflows()
        
        # Step 6: Generate report
        print("\n📊 LANGGRAPH SERVER TEST REPORT")
        print("=" * 40)
        
        accessible_endpoints = len([r for r in endpoint_results.values() if r["accessible"]])
        total_endpoints = len(endpoint_results)
        
        print(f"Endpoints accessible: {accessible_endpoints}/{total_endpoints}")
        print(f"Workflow execution: {'✅ SUCCESS' if workflow_success else '❌ FAILED'}")
        
        if accessible_endpoints >= total_endpoints * 0.8 and workflow_success:
            print("\n🎉 LangGraph server is working perfectly!")
            return True
        elif accessible_endpoints >= total_endpoints * 0.5:
            print("\n👍 LangGraph server is partially working!")
            return True
        else:
            print("\n⚠️ LangGraph server needs more work!")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.langgraph_process:
            print("\n🧹 Cleaning up LangGraph process...")
            try:
                self.langgraph_process.terminate()
                self.langgraph_process.wait(timeout=5)
            except:
                self.langgraph_process.kill()

def main():
    """Main function"""
    fixer = LangGraphServerFixer()
    try:
        success = fixer.run_comprehensive_test()
        return 0 if success else 1
    finally:
        fixer.cleanup()

if __name__ == "__main__":
    sys.exit(main())
