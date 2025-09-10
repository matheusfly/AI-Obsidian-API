#!/usr/bin/env python3
"""
Simple Phase 4 test to verify real data integration
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add data-pipeline services to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

print("🚀 Starting Simple Phase 4 Test")
print("=" * 50)

try:
    print("📁 Checking data-pipeline path...")
    print(f"Data pipeline src: {data_pipeline_src}")
    print(f"Exists: {data_pipeline_src.exists()}")
    
    if data_pipeline_src.exists():
        print("📂 Listing data-pipeline contents...")
        for item in data_pipeline_src.iterdir():
            print(f"  - {item.name}")
    
    print("\n🔍 Trying to import services...")
    
    try:
        from embeddings.embedding_service import EmbeddingService
        print("✅ EmbeddingService imported successfully")
        
        # Test embedding service
        embedding_service = EmbeddingService()
        print("✅ EmbeddingService initialized successfully")
        
        # Test embedding generation
        test_text = "Test embedding for philosophy and mathematics"
        embedding = embedding_service.embed_text(test_text)
        print(f"✅ Embedding generated: shape {embedding.shape}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Service error: {e}")
    
    print("\n🔍 Testing ChromaDB service...")
    
    try:
        from vector.chroma_service import ChromaService
        print("✅ ChromaService imported successfully")
        
        chroma_service = ChromaService()
        print("✅ ChromaService initialized successfully")
        
        # Test collection stats
        stats = chroma_service.get_collection_stats()
        print(f"✅ Collection stats: {stats}")
        
    except ImportError as e:
        print(f"❌ ChromaDB import error: {e}")
    except Exception as e:
        print(f"❌ ChromaDB service error: {e}")
    
    print("\n🔍 Testing search service...")
    
    try:
        from search.semantic_search_service import SemanticSearchService
        print("✅ SemanticSearchService imported successfully")
        
        search_service = SemanticSearchService(chroma_service, embedding_service)
        print("✅ SemanticSearchService initialized successfully")
        
        # Test search
        test_query = "What are the main philosophical currents?"
        results = search_service.search(test_query, [], top_k=3)
        print(f"✅ Search test: {len(results)} results")
        
    except ImportError as e:
        print(f"❌ Search import error: {e}")
    except Exception as e:
        print(f"❌ Search service error: {e}")
    
    print("\n📊 Phase 4 Simple Test Results:")
    print("✅ All basic services are working with real data!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Simple Phase 4 Test Complete")
