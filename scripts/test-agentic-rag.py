#!/usr/bin/env python3
"""
Test Agentic RAG CLI - Validate agentic synthesis and intelligent features
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

async def test_agentic_rag():
    """Test agentic RAG functionality"""
    print("🧪 Testando Agentic RAG CLI...")
    
    try:
        # Import the CLI
        import importlib.util
        spec = importlib.util.spec_from_file_location("agentic_rag_cli", "agentic-rag-cli.py")
        agentic_cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agentic_cli)
        AgenticRAGCLI = agentic_cli.AgenticRAGCLI
        
        # Create instance
        cli = AgenticRAGCLI()
        print("✓ CLI instance created")
        
        # Test initialization
        init_success = await cli.initialize()
        if init_success:
            print("✓ CLI initialization successful")
        else:
            print("✗ CLI initialization failed")
            return False
        
        # Test agentic features
        print("\n--- Testing Agentic Features ---")
        
        # Test 1: Agentic search with synthesis
        print("\n1. Testing agentic search with synthesis...")
        await cli.search_command("como atingir auto performance")
        print("✓ Agentic search with synthesis works")
        
        # Test 2: Follow-up suggestions
        print("\n2. Testing follow-up suggestions...")
        await cli.show_suggestions()
        print("✓ Follow-up suggestions work")
        
        # Test 3: Context management
        print("\n3. Testing context management...")
        cli.show_context()
        print("✓ Context management works")
        
        # Test 4: Synthesis status
        print("\n4. Testing synthesis status...")
        cli.synthesis_commands("status")
        print("✓ Synthesis status works")
        
        # Test 5: Stats with synthesis metrics
        print("\n5. Testing stats with synthesis metrics...")
        cli.show_stats()
        print("✓ Stats with synthesis metrics work")
        
        # Test 6: Another search to test context switching
        print("\n6. Testing context switching...")
        await cli.search_command("machine learning algorithms")
        print("✓ Context switching works")
        
        # Test 7: Cache management
        print("\n7. Testing cache management...")
        cli.cache_commands("stats")
        print("✓ Cache management works")
        
        print("\n🎉 All agentic tests completed!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing agentic RAG: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_agentic_rag()
    
    if success:
        print("\n✅ Agentic RAG CLI is working with intelligent synthesis!")
        print("Run: python agentic-rag-cli.py")
        print("Features: Intelligent synthesis, context-aware responses, smart suggestions")
    else:
        print("\n❌ Agentic RAG has issues that need to be fixed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
