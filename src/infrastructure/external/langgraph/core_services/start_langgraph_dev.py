#!/usr/bin/env python3
"""
Script to start LangGraph dev server with proper error handling
"""

import subprocess
import sys
import time
import requests
import os

def start_langgraph_dev():
    """Start LangGraph dev server"""
    print("🚀 Starting LangGraph dev server...")
    
    # Change to langgraph_project directory
    os.chdir("langgraph_project")
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, "-m", "langgraph_cli", "dev", 
            "--port", "8123", "--allow-blocking"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("⏳ Waiting for server to start...")
        
        # Wait for server to start
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://127.0.0.1:8123/health", timeout=1)
                if response.status_code == 200:
                    print("✅ LangGraph dev server is running!")
                    print(f"🌐 Server URL: http://127.0.0.1:8123")
                    print(f"🎨 Studio URL: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123")
                    return process
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            print(f"⏳ Still waiting... ({i+1}/30)")
        
        print("❌ Server failed to start within 30 seconds")
        print("📋 Checking server output...")
        
        # Get any output from the process
        stdout, stderr = process.communicate(timeout=5)
        if stdout:
            print("STDOUT:", stdout)
        if stderr:
            print("STDERR:", stderr)
            
        return None
        
    except Exception as e:
        print(f"❌ Error starting LangGraph dev server: {e}")
        return None

if __name__ == "__main__":
    process = start_langgraph_dev()
    if process:
        print("✅ LangGraph dev server started successfully!")
        print("Press Ctrl+C to stop...")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
    else:
        print("❌ Failed to start LangGraph dev server")
        sys.exit(1)
