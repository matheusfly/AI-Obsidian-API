#!/usr/bin/env python3
"""
Simple test to check current system status
"""

import requests
import json

def test_obsidian_api():
    """Test Mock Obsidian API"""
    print("🔍 Testing Mock Obsidian API...")
    try:
        response = requests.get("http://127.0.0.1:27123/health", timeout=3)
        if response.status_code == 200:
            print("✅ Mock Obsidian API: OK")
            return True
        else:
            print(f"❌ Mock Obsidian API: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Mock Obsidian API: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    print("🔍 Testing file operations...")
    try:
        headers = {"Authorization": "Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"}
        
        # List files
        response = requests.get("http://127.0.0.1:27123/vault/files", headers=headers, timeout=3)
        if response.status_code == 200:
            files = response.json()
            print(f"✅ File listing: {len(files.get('files', []))} files found")
        else:
            print("❌ File listing: FAILED")
            return False
        
        # Read a file
        response = requests.get("http://127.0.0.1:27123/vault/file?path=README.md", headers=headers, timeout=3)
        if response.status_code == 200:
            content = response.json()
            print(f"✅ File reading: {len(content.get('content', ''))} characters read")
        else:
            print("❌ File reading: FAILED")
            return False
            
        # Search files
        search_data = {"query": "langgraph", "vault_name": "Nomade Milionario"}
        response = requests.post("http://127.0.0.1:27123/vault/search", headers=headers, json=search_data, timeout=3)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ File search: {len(results.get('results', []))} results found")
        else:
            print("❌ File search: FAILED")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ File operations failed: {e}")
        return False

def test_langgraph_workflow():
    """Test LangGraph workflow"""
    print("🔍 Testing LangGraph workflow...")
    try:
        import subprocess
        result = subprocess.run(["python", "langgraph_workflows/obsidian_workflow.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ LangGraph workflow: SUCCESS")
            if "Workflow completed successfully" in result.stdout:
                print("✅ Workflow completed with success status")
            return True
        else:
            print(f"❌ LangGraph workflow: FAILED - {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ LangGraph workflow test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 SIMPLE SYSTEM STATUS TEST")
    print("=" * 40)
    
    # Test results
    tests = {
        "Obsidian API": test_obsidian_api(),
        "File Operations": test_file_operations(),
        "LangGraph Workflow": test_langgraph_workflow()
    }
    
    # Calculate score
    passed = sum(1 for result in tests.values() if result)
    total = len(tests)
    percentage = (passed / total) * 100
    
    print("\n📊 TEST RESULTS")
    print("=" * 20)
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({percentage:.1f}%)")
    
    if percentage >= 100:
        print("🎉 EXCELLENT! All tests passed!")
        print("✅ First API call SUCCESSFUL!")
        print("🚀 System ready for production!")
    elif percentage >= 66:
        print("✅ GOOD! Most tests passed!")
        print("🔧 Minor issues to resolve")
    else:
        print("⚠️  NEEDS WORK! Several tests failed")
        print("🛠️  Critical issues to fix")
    
    return percentage >= 66

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
