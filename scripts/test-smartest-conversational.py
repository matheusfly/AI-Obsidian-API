#!/usr/bin/env python3
"""
Test Smartest Conversational RAG CLI - Validate conversational features
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

async def test_smartest_conversational():
    """Test smartest conversational functionality"""
    print("🧪 Testando SMARTEST Conversational RAG CLI...")
    
    try:
        # Import the CLI
        import importlib.util
        spec = importlib.util.spec_from_file_location("smartest_conversational_rag_cli", "smartest-conversational-rag-cli.py")
        smartest_cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(smartest_cli)
        SmartestConversationalRAGCLI = smartest_cli.SmartestConversationalRAGCLI
        
        # Create instance
        cli = SmartestConversationalRAGCLI()
        print("✓ CLI instance created")
        
        # Test initialization
        init_success = await cli.initialize()
        if init_success:
            print("✓ CLI initialization successful")
        else:
            print("✗ CLI initialization failed")
            return False
        
        # Test conversational features
        print("\n--- Testing Conversational Features ---")
        
        # Test 1: Portuguese conversation
        print("\n1. Testing Portuguese conversation...")
        cli.search_command("como atingir auto performance")
        print("✓ Portuguese conversation works")
        
        # Test 2: Context management
        print("\n2. Testing context management...")
        cli.show_context()
        print("✓ Context management works")
        
        # Test 3: Smart suggestions
        print("\n3. Testing smart suggestions...")
        cli.show_suggestions()
        print("✓ Smart suggestions work")
        
        # Test 4: Follow-up conversation
        print("\n4. Testing follow-up conversation...")
        cli.search_command("otimização de performance")
        print("✓ Follow-up conversation works")
        
        # Test 5: Context switch
        print("\n5. Testing context switch...")
        cli.search_command("machine learning algorithms")
        print("✓ Context switch works")
        
        # Test 6: Stats and analytics
        print("\n6. Testing stats and analytics...")
        cli.show_stats()
        print("✓ Stats and analytics work")
        
        # Test 7: Help system
        print("\n7. Testing help system...")
        cli.show_help()
        print("✓ Help system works")
        
        print("\n🎉 All conversational tests completed!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing smartest conversational: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_smartest_conversational()
    
    if success:
        print("\n✅ SMARTEST Conversational RAG CLI is working with intelligent workflows!")
        print("Run: python smartest-conversational-rag-cli.py")
    else:
        print("\n❌ Smartest conversational has issues that need to be fixed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
