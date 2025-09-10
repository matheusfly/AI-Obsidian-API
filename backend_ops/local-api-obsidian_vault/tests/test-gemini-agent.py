#!/usr/bin/env python3
"""
Test script for first AI agent call with Gemini Flash Thinking API
Advanced RAG Q&A system integration
"""

import requests
import json
import time
from datetime import datetime

# Configuration
GEMINI_API_KEY = "$env:GOOGLE_API_KEY"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp:generateContent"
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/advanced-rag"
OBSIDIAN_API_URL = "http://localhost:27123"
OBSIDIAN_API_KEY = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

def test_obsidian_api():
    """Test Obsidian API connectivity"""
    print("🔍 Testing Obsidian API connectivity...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{OBSIDIAN_API_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Obsidian API is healthy")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Timestamp: {health_data.get('timestamp', 'unknown')}")
        else:
            print(f"❌ Obsidian API health check failed: {response.status_code}")
            return False
            
        # Test vault info
        headers = {"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
        response = requests.get(f"{OBSIDIAN_API_URL}/vault/info", headers=headers, timeout=10)
        if response.status_code == 200:
            vault_info = response.json()
            print("✅ Vault access successful")
            print(f"   Total files: {vault_info.get('totalFiles', 'unknown')}")
            print(f"   Markdown files: {vault_info.get('markdownFiles', 'unknown')}")
            print(f"   Last modified: {vault_info.get('lastModified', 'unknown')}")
        else:
            print(f"❌ Vault access failed: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Obsidian API test failed: {str(e)}")
        return False

def test_gemini_flash_direct():
    """Test Gemini Flash API directly"""
    print("\n🤖 Testing Gemini Flash API directly...")
    
    try:
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": """You are an advanced AI agent specialized in RAG (Retrieval-Augmented Generation) for Obsidian vaults. 

**TEST QUERY:** What are the best practices for implementing RAG systems in personal knowledge management?

**INSTRUCTIONS:**
1. Provide a comprehensive answer about RAG best practices
2. Include specific technical recommendations
3. Mention key considerations for Obsidian vaults
4. Suggest implementation strategies

Please provide your response now."""
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
                "responseMimeType": "text/plain"
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ Gemini Flash API call successful")
            data = response.json()
            
            if data.get("candidates") and data["candidates"][0].get("content"):
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"\n📝 Gemini Flash Response:")
                print("=" * 80)
                print(answer)
                print("=" * 80)
                
                # Show usage info if available
                if "usageMetadata" in data:
                    usage = data["usageMetadata"]
                    print(f"\n📊 Usage Statistics:")
                    print(f"   Prompt tokens: {usage.get('promptTokenCount', 'N/A')}")
                    print(f"   Response tokens: {usage.get('candidatesTokenCount', 'N/A')}")
                    print(f"   Total tokens: {usage.get('totalTokenCount', 'N/A')}")
                
                return True
            else:
                print("❌ No valid response from Gemini Flash")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"❌ Gemini Flash API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini Flash test failed: {str(e)}")
        return False

def test_n8n_webhook():
    """Test n8n webhook for advanced RAG"""
    print("\n🔄 Testing n8n Advanced RAG Webhook...")
    
    try:
        payload = {
            "question": "What are the best practices for implementing RAG systems in personal knowledge management?",
            "context": "technical",
            "searchType": "hybrid"
        }
        
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            print("✅ n8n webhook call successful")
            data = response.json()
            
            print(f"\n📝 Advanced RAG Response:")
            print("=" * 80)
            print(data.get("answer", "No answer provided"))
            print("=" * 80)
            
            # Show metadata
            if "metadata" in data:
                metadata = data["metadata"]
                print(f"\n📊 Response Metadata:")
                print(f"   Query: {metadata.get('query', 'N/A')}")
                print(f"   Total sources: {metadata.get('totalSources', 'N/A')}")
                print(f"   Citations used: {metadata.get('citationsUsed', 'N/A')}")
                print(f"   Model: {metadata.get('model', 'N/A')}")
                print(f"   Search method: {metadata.get('searchMethod', 'N/A')}")
                print(f"   Quality: {metadata.get('quality', 'N/A')}")
            
            # Show sources
            if "sources" in data and data["sources"]:
                print(f"\n📚 Sources Used:")
                for i, source in enumerate(data["sources"][:3], 1):
                    print(f"   {i}. {source.get('title', 'Unknown')} (Relevance: {source.get('relevance', 'N/A')}%)")
                    print(f"      Path: {source.get('path', 'N/A')}")
                    print(f"      Preview: {source.get('preview', 'N/A')[:100]}...")
            
            return True
        else:
            print(f"❌ n8n webhook call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ n8n webhook test failed: {str(e)}")
        return False

def test_advanced_rag_workflow():
    """Test the complete advanced RAG workflow"""
    print("\n🚀 Testing Complete Advanced RAG Workflow...")
    
    test_questions = [
        "How do I optimize vector embeddings for better semantic search in Obsidian notes?",
        "What are the best practices for maintaining and updating a personal knowledge base with RAG systems?",
        "How can I troubleshoot common issues when integrating Docker with Obsidian for RAG systems?",
        "What are some advanced features of LangGraph in Obsidian that can enhance my workflow?",
        "How do I set up Docker for Obsidian to work seamlessly with RAG systems?"
    ]
    
    successful_tests = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📋 Test {i}/{len(test_questions)}: {question[:60]}...")
        
        try:
            payload = {
                "question": question,
                "context": "technical",
                "searchType": "hybrid"
            }
            
            start_time = time.time()
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=60)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                
                print(f"✅ Test {i} successful ({end_time - start_time:.2f}s)")
                print(f"   Answer length: {len(answer)} characters")
                print(f"   Sources used: {data.get('metadata', {}).get('totalSources', 0)}")
                print(f"   Quality: {data.get('quality', 'unknown')}")
                
                # Show first part of answer
                if answer:
                    preview = answer[:200] + "..." if len(answer) > 200 else answer
                    print(f"   Preview: {preview}")
                
                successful_tests += 1
            else:
                print(f"❌ Test {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test {i} error: {str(e)}")
        
        # Small delay between tests
        time.sleep(2)
    
    print(f"\n📊 Advanced RAG Workflow Test Results:")
    print(f"   Successful tests: {successful_tests}/{len(test_questions)}")
    print(f"   Success rate: {(successful_tests/len(test_questions)*100):.1f}%")
    
    return successful_tests == len(test_questions)

def main():
    """Main test function"""
    print("🎯 OBSIDIAN VAULT AI SYSTEM - ADVANCED RAG TESTING")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Gemini API Key: {GEMINI_API_KEY[:20]}...")
    print(f"Obsidian API: {OBSIDIAN_API_URL}")
    print(f"n8n Webhook: {N8N_WEBHOOK_URL}")
    print("=" * 80)
    
    # Test sequence
    tests = [
        ("Obsidian API", test_obsidian_api),
        ("Gemini Flash Direct", test_gemini_flash_direct),
        ("n8n Webhook", test_n8n_webhook),
        ("Advanced RAG Workflow", test_advanced_rag_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your Advanced RAG system is ready!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please check the issues above.")
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
