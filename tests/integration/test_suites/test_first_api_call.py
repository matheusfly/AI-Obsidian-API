#!/usr/bin/env python3
"""
Test script for first successful LangGraph -> Obsidian API call
This script simulates the Obsidian API if it's not available and tests the integration
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
LANGGRAPH_SERVER_URL = "http://localhost:2024"
OBSIDIAN_API_URL = "http://127.0.0.1:27123"
OBSIDIAN_API_KEY = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
VAULT_NAME = "Nomade Milionario"

def test_obsidian_api():
    """Test if Obsidian API is responding"""
    print("🔍 Testing Obsidian Local REST API...")
    try:
        response = requests.get(
            f"{OBSIDIAN_API_URL}/vault",
            headers={"Authorization": f"Bearer {OBSIDIAN_API_KEY}"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Obsidian API is responding")
            return True
        else:
            print(f"⚠️  Obsidian API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Obsidian API not responding: {e}")
        return False

def simulate_obsidian_api():
    """Simulate Obsidian API responses for testing"""
    print("🔧 Simulating Obsidian API responses...")
    
    # Mock responses
    mock_responses = {
        "/vault": {
            "vaults": [{"name": VAULT_NAME, "path": f"D:\\{VAULT_NAME}"}]
        },
        "/vault/files": {
            "files": [
                {"path": "README.md", "name": "README.md", "type": "file"},
                {"path": "test_note.md", "name": "test_note.md", "type": "file"}
            ]
        },
        "/vault/file": {
            "content": "# Test Note\nThis is a test note created by LangGraph.\n\n## Content\n- Item 1\n- Item 2\n- Item 3",
            "path": "test_note.md"
        }
    }
    
    return mock_responses

def test_langgraph_server():
    """Test if LangGraph server is responding"""
    print("🔍 Testing LangGraph Server...")
    try:
        response = requests.get(f"{LANGGRAPH_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ LangGraph Server is responding")
            return True
        else:
            print(f"⚠️  LangGraph Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ LangGraph Server not responding: {e}")
        return False

def test_langgraph_workflows():
    """Test LangGraph workflows"""
    print("🔍 Testing LangGraph Workflows...")
    try:
        response = requests.get(f"{LANGGRAPH_SERVER_URL}/graphs", timeout=5)
        if response.status_code == 200:
            workflows = response.json()
            print(f"✅ Found {len(workflows.get('graphs', []))} workflows")
            for workflow in workflows.get('graphs', []):
                print(f"   - {workflow.get('graph_id', 'Unknown')}")
            return True
        else:
            print(f"⚠️  LangGraph Workflows returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ LangGraph Workflows not responding: {e}")
        return False

def test_first_api_call():
    """Test the first successful API call from LangGraph to Obsidian"""
    print("🚀 Testing First LangGraph -> Obsidian API Call...")
    
    # Test payload
    payload = {
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "Search for notes about 'test' in the vault"
                }
            ],
            "vault_name": VAULT_NAME
        }
    }
    
    try:
        # Try to invoke the obsidian-workflow
        response = requests.post(
            f"{LANGGRAPH_SERVER_URL}/graphs/obsidian-workflow/run",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: First API call completed!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"⚠️  API call returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        return False

def test_workflow_with_mock_data():
    """Test workflow with mock Obsidian data"""
    print("🔧 Testing Workflow with Mock Data...")
    
    # Create a mock workflow that doesn't depend on Obsidian API
    mock_payload = {
        "input": {
            "messages": [
                {
                    "role": "user", 
                    "content": "Create a test note about LangGraph integration"
                }
            ],
            "vault_name": VAULT_NAME,
            "mock_mode": True
        }
    }
    
    try:
        response = requests.post(
            f"{LANGGRAPH_SERVER_URL}/graphs/obsidian-workflow/run",
            json=mock_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Mock workflow completed!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"⚠️  Mock workflow returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Mock workflow failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 FIRST API CALL TEST SUITE")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"LangGraph Server: {LANGGRAPH_SERVER_URL}")
    print(f"Obsidian API: {OBSIDIAN_API_URL}")
    print(f"Vault: {VAULT_NAME}")
    print("=" * 50)
    
    # Wait for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(5)
    
    # Test results
    results = {
        "obsidian_api": False,
        "langgraph_server": False,
        "langgraph_workflows": False,
        "first_api_call": False,
        "mock_workflow": False
    }
    
    # Run tests
    results["obsidian_api"] = test_obsidian_api()
    results["langgraph_server"] = test_langgraph_server()
    
    if results["langgraph_server"]:
        results["langgraph_workflows"] = test_langgraph_workflows()
        
        if results["obsidian_api"]:
            results["first_api_call"] = test_first_api_call()
        else:
            print("⚠️  Obsidian API not available, testing with mock data...")
            results["mock_workflow"] = test_workflow_with_mock_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT! System ready for production!")
    elif success_rate >= 60:
        print("✅ GOOD! Minor issues to resolve")
    else:
        print("⚠️  NEEDS WORK! Critical issues to fix")
    
    # Recommendations
    print("\n🔧 RECOMMENDATIONS:")
    if not results["obsidian_api"]:
        print("1. Start Obsidian and enable Local REST API plugin")
        print("2. Check if port 27123 is available")
    if not results["langgraph_server"]:
        print("3. Start LangGraph dev server: langgraph dev")
    if not results["first_api_call"] and not results["mock_workflow"]:
        print("4. Check LangGraph workflow configuration")
        print("5. Verify workflow compilation")
    
    print("\n🏁 Test completed!")
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
