#!/usr/bin/env python3
"""
Script to run LangGraph dev server
"""

import subprocess
import sys
import os
import time

def run_langgraph_dev():
    """Run LangGraph dev server"""
    print("🚀 Starting LangGraph dev server...")
    
    # Set environment variables
    os.environ['LANGSMITH_API_KEY'] = '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'
    os.environ['LANGSMITH_PROJECT'] = 'mcp-obsidian-integration'
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    
    try:
        # Try to run langgraph dev
        print("Attempting to run: langgraph dev --port 8123")
        result = subprocess.run([
            sys.executable, '-m', 'langgraph_cli', 'dev', '--port', '8123'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ LangGraph dev server started successfully!")
        else:
            print("❌ LangGraph dev server failed to start")
            
    except subprocess.TimeoutExpired:
        print("⏰ LangGraph dev server startup timed out")
    except Exception as e:
        print(f"❌ Error running LangGraph dev: {e}")

if __name__ == "__main__":
    run_langgraph_dev()
