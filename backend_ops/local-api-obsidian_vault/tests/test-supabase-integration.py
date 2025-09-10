#!/usr/bin/env python3
"""Test Supabase Integration for AI Agent Retrieval"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8080"

async def test_supabase_integration():
    """Test all Supabase-related endpoints"""
    
    print("🧪 Testing Supabase Integration...")
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Supabase Health Check
        print("\n1️⃣ Testing Supabase Health...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/supabase/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        # Test 2: Update Agent Context
        print("\n2️⃣ Testing Agent Context Update...")
        try:
            context_data = {
                "agent_id": "test_agent_001",
                "context": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "system_prompt": "You are a helpful AI assistant for Obsidian vault management.",
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/agents/context",
                json=context_data
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"❌ Context update failed: {e}")
        
        # Test 3: AI Enhanced Retrieval
        print("\n3️⃣ Testing AI Enhanced Retrieval...")
        try:
            retrieval_data = {
                "query": "machine learning concepts in my notes",
                "agent_id": "test_agent_001",
                "context": {
                    "search_type": "semantic",
                    "limit": 5,
                    "include_metadata": True
                }
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/ai/retrieve",
                json=retrieval_data
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"❌ AI retrieval failed: {e}")
        
        # Test 4: Agent Analytics
        print("\n4️⃣ Testing Agent Analytics...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/agents/test_agent_001/analytics?days=7")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"❌ Analytics failed: {e}")
        
        # Test 5: Cached Retrieval (run same query again)
        print("\n5️⃣ Testing Cached Retrieval...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/ai/retrieve",
                json=retrieval_data  # Same query as before
            )
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Source: {result.get('source', 'unknown')}")
            print(f"Response: {result}")
        except Exception as e:
            print(f"❌ Cached retrieval failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Supabase Integration Tests...")
    print("Make sure your vault-api server is running on localhost:8080")
    print("And that Supabase is properly configured in .env")
    
    asyncio.run(test_supabase_integration())
    
    print("\n✅ Tests completed!")
    print("\n📋 Integration Summary:")
    print("- Agent context storage and retrieval")
    print("- Query result caching with Supabase")
    print("- Interaction logging for analytics")
    print("- Health monitoring for Supabase connection")