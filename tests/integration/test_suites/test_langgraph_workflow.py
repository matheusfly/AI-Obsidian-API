#!/usr/bin/env python3
"""
Test LangGraph Workflow Integration
Demonstrates complete symbiosis between LangGraph and Obsidian
"""

import requests
import json
import time

def test_langgraph_workflow():
    """Test the LangGraph workflow integration"""
    
    print("🚀 Testing LangGraph Workflow Integration")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing LangGraph Server Health...")
    try:
        response = requests.get("http://localhost:8003/health", timeout=10)
        if response.status_code == 200:
            print("✅ LangGraph Server is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ LangGraph Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LangGraph Server health check error: {str(e)}")
        return False
    
    # Test 2: List workflows
    print("\n2. Testing Workflow List...")
    try:
        response = requests.get("http://localhost:8003/workflows", timeout=10)
        if response.status_code == 200:
            workflows = response.json()
            print("✅ Workflows listed successfully")
            print(f"   Available workflows: {len(workflows.get('workflows', []))}")
            for workflow in workflows.get('workflows', []):
                print(f"   - {workflow['name']}: {workflow['description']}")
        else:
            print(f"❌ Workflow list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Workflow list error: {str(e)}")
    
    # Test 3: Run Obsidian integration workflow
    print("\n3. Testing Obsidian Integration Workflow...")
    try:
        workflow_data = {
            "vault_name": "Nomade Milionario",
            "workflow_type": "integration",
            "parameters": {
                "search_query": "langgraph integration",
                "current_file": "README.md"
            }
        }
        
        response = requests.post(
            "http://localhost:8003/workflows/obsidian-integration",
            json=workflow_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Obsidian Integration Workflow completed")
            print(f"   Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Message: {result.get('message', 'N/A')}")
            
            if result.get('success'):
                results = result.get('results', {})
                print(f"   Files found: {results.get('files_found', 0)}")
                print(f"   Search results: {results.get('search_results', 0)}")
                print(f"   Summary file: {results.get('summary_file', 'N/A')}")
        else:
            print(f"❌ Obsidian Integration Workflow failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Obsidian Integration Workflow error: {str(e)}")
    
    # Test 4: Run search workflow
    print("\n4. Testing Search Workflow...")
    try:
        search_data = {
            "vault_name": "Nomade Milionario",
            "workflow_type": "search",
            "parameters": {
                "query": "langgraph"
            }
        }
        
        response = requests.post(
            "http://localhost:8003/workflows/obsidian-search",
            json=search_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search Workflow completed")
            print(f"   Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Success: {result.get('success', False)}")
            
            if result.get('success'):
                results = result.get('results', {})
                print(f"   Query: {results.get('query', 'N/A')}")
                print(f"   Results count: {results.get('results_count', 0)}")
        else:
            print(f"❌ Search Workflow failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search Workflow error: {str(e)}")
    
    # Test 5: Test file operations workflow
    print("\n5. Testing File Operations Workflow...")
    try:
        file_ops_data = {
            "vault_name": "Nomade Milionario",
            "workflow_type": "file_operations",
            "parameters": {}
        }
        
        response = requests.post(
            "http://localhost:8003/workflows/obsidian-file-operations",
            json=file_ops_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File Operations Workflow completed")
            print(f"   Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Success: {result.get('success', False)}")
            
            if result.get('success'):
                results = result.get('results', {})
                print(f"   Files processed: {results.get('files_processed', 0)}")
                print(f"   Total files: {results.get('total_files', 0)}")
        else:
            print(f"❌ File Operations Workflow failed: {response.status_code}")
    except Exception as e:
        print(f"❌ File Operations Workflow error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 LangGraph Workflow Integration Test Complete!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_langgraph_workflow()
