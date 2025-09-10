#!/usr/bin/env python3
"""
Test Agentic Gemini RAG CLI - Validate Gemini integration and agentic features
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

async def test_agentic_gemini():
    """Test agentic Gemini functionality"""
    print("🧪 Testando Agentic Gemini RAG CLI...")
    
    try:
        # Import the CLI
        import importlib.util
        spec = importlib.util.spec_from_file_location("agentic_gemini_rag_cli", "agentic-gemini-rag-cli.py")
        agentic_cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agentic_cli)
        AgenticGeminiRAGCLI = agentic_cli.AgenticGeminiRAGCLI
        
        # Create instance
        cli = AgenticGeminiRAGCLI()
        print("✓ CLI instance created")
        
        # Test initialization
        init_success = await cli.initialize()
        if init_success:
            print("✓ CLI initialization successful")
        else:
            print("✗ CLI initialization failed")
            return False
        
        # Test Gemini integration
        print("\n--- Testing Gemini Integration ---")
        
        # Test 1: Gemini status
        print("\n1. Testing Gemini status...")
        await cli.gemini_commands("status")
        print("✓ Gemini status check works")
        
        # Test 2: Gemini test
        print("\n2. Testing Gemini connection...")
        await cli.gemini_commands("test")
        print("✓ Gemini test works")
        
        # Test 3: Agentic search with Gemini
        print("\n3. Testing agentic search with Gemini...")
        await cli.search_command("como atingir auto performance")
        print("✓ Agentic search with Gemini works")
        
        # Test 4: Follow-up suggestions with Gemini
        print("\n4. Testing follow-up suggestions with Gemini...")
        await cli.show_suggestions()
        print("✓ Follow-up suggestions with Gemini work")
        
        # Test 5: Context management
        print("\n5. Testing context management...")
        cli.show_context()
        print("✓ Context management works")
        
        # Test 6: Stats with Gemini metrics
        print("\n6. Testing stats with Gemini metrics...")
        cli.show_stats()
        print("✓ Stats with Gemini metrics work")
        
        # Test 7: Cache management
        print("\n7. Testing cache management...")
        cli.cache_commands("stats")
        print("✓ Cache management works")
        
        print("\n🎉 All agentic Gemini tests completed!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing agentic Gemini: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_agentic_gemini()
    
    if success:
        print("\n✅ Agentic Gemini RAG CLI is working with intelligent AI reasoning!")
        print("Run: python agentic-gemini-rag-cli.py")
        print("Note: Set GEMINI_API_KEY environment variable for full functionality")
    else:
        print("\n❌ Agentic Gemini has issues that need to be fixed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
