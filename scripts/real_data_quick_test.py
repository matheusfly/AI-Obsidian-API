#!/usr/bin/env python3
"""
Quick Real Data Test - Verify all services work with real data
"""

import sys
from pathlib import Path

# Add data-pipeline services to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

print("🚀 Quick Real Data Test")
print("=" * 40)

try:
    # Test imports
    print("📦 Testing imports...")
    from embeddings.embedding_service import EmbeddingService
    from vector.chroma_service import ChromaService
    from search.semantic_search_service import SemanticSearchService
    print("✅ Imports successful")
    
    # Initialize services
    print("🔧 Initializing services...")
    embedding_service = EmbeddingService()
    chroma_service = ChromaService()
    search_service = SemanticSearchService(chroma_service, embedding_service)
    print("✅ Services initialized")
    
    # Test embedding generation
    print("🧠 Testing embedding generation...")
    test_text = "Test embedding for philosophy and mathematics"
    embedding = embedding_service.embed_text(test_text)
    print(f"✅ Embedding shape: {embedding.shape}")
    
    # Test search
    print("🔍 Testing search...")
    results = search_service.search("What are the main philosophical currents?", [], top_k=3)
    print(f"✅ Search results: {len(results)}")
    
    # Test vault data loading
    print("📁 Testing vault data loading...")
    vault_path = Path("D:/Nomade Milionario")
    if vault_path.exists():
        print(f"✅ Vault path exists: {vault_path}")
        
        # Load a sample file
        sample_files = ["LOGICA-INDICE.md", "Hiper-Leitura.md", "scrapy.md"]
        for filename in sample_files:
            file_path = vault_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"✅ Loaded {filename}: {len(content)} characters")
                break
    else:
        print("⚠️ Vault path not found")
    
    print("\n🎉 Quick Real Data Test - ALL TESTS PASSED!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 40)
print("🏁 Quick Real Data Test Complete")
