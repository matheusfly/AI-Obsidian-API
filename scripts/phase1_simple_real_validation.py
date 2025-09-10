#!/usr/bin/env python3
"""
Phase 1 Simple Real Data Validation
Simplified validation using real data-pipeline services
"""

import sys
import time
import json
import os
from pathlib import Path

# Add data-pipeline src to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

def test_phase1_components():
    """Test Phase 1 components with real data"""
    print("🚀 Phase 1 Simple Real Data Validation")
    print("=" * 50)
    
    results = {
        "phase": "1",
        "test_name": "Phase 1 Simple Real Data Validation",
        "components": {},
        "overall_score": 0.0,
        "passed": False
    }
    
    # Test 1: Embedding Service
    print("\n🧪 Test 1: Embedding Service")
    try:
        from embeddings.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService()
        test_text = "This is a test for embedding generation"
        embedding = embedding_service.generate_embedding(test_text)
        
        results["components"]["embedding_service"] = {
            "working": True,
            "dimension": len(embedding),
            "model_name": embedding_service.model_name,
            "multilingual": embedding_service.is_multilingual
        }
        print(f"  ✅ Embedding Service Working (dim: {len(embedding)})")
        
    except Exception as e:
        results["components"]["embedding_service"] = {
            "working": False,
            "error": str(e)
        }
        print(f"  ❌ Embedding Service Failed: {e}")
    
    # Test 2: ChromaDB Service
    print("\n🗄️ Test 2: ChromaDB Service")
    try:
        from vector.chroma_service import ChromaService
        
        vector_db_path = Path(__file__).parent.parent / "data" / "chroma"
        chroma_service = ChromaService(
            collection_name="test_simple_validation",
            persist_directory=str(vector_db_path),
            embedding_model="all-MiniLM-L6-v2"
        )
        
        # Get collection stats
        stats = chroma_service.get_collection_stats()
        
        results["components"]["chromadb_service"] = {
            "working": True,
            "collection_name": chroma_service.collection.name,
            "total_chunks": stats.get("total_chunks", 0),
            "embedding_model": stats.get("embedding_model", "unknown")
        }
        print(f"  ✅ ChromaDB Service Working (chunks: {stats.get('total_chunks', 0)})")
        
    except Exception as e:
        results["components"]["chromadb_service"] = {
            "working": False,
            "error": str(e)
        }
        print(f"  ❌ ChromaDB Service Failed: {e}")
    
    # Test 3: Vault Data Availability
    print("\n📚 Test 3: Vault Data Availability")
    try:
        vault_path = Path(__file__).parent.parent / "data" / "raw" / "vault"
        vault_files = list(vault_path.glob("*.md"))
        
        if vault_files:
            # Read sample content
            sample_content = ""
            for file_path in vault_files[:1]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sample_content = f.read()[:200]
                    break
            
            results["components"]["vault_data"] = {
                "available": True,
                "file_count": len(vault_files),
                "sample_content_length": len(sample_content),
                "sample_files": [f.name for f in vault_files[:3]]
            }
            print(f"  ✅ Vault Data Available ({len(vault_files)} files)")
        else:
            results["components"]["vault_data"] = {
                "available": False,
                "error": "No markdown files found"
            }
            print(f"  ❌ No Vault Data Found")
            
    except Exception as e:
        results["components"]["vault_data"] = {
            "available": False,
            "error": str(e)
        }
        print(f"  ❌ Vault Data Error: {e}")
    
    # Test 4: Cross-Encoder Re-ranking
    print("\n🎯 Test 4: Cross-Encoder Re-ranking")
    try:
        from sentence_transformers import CrossEncoder
        
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        # Test with sample data
        query = "artificial intelligence"
        documents = [
            "Machine learning is a subset of artificial intelligence",
            "Web scraping involves extracting data from websites"
        ]
        
        pairs = [(query, doc) for doc in documents]
        scores = cross_encoder.predict(pairs)
        
        results["components"]["cross_encoder"] = {
            "working": True,
            "model_name": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "test_scores": [float(s) for s in scores],
            "score_range": [float(min(scores)), float(max(scores))]
        }
        print(f"  ✅ Cross-Encoder Working (scores: {[float(s) for s in scores]})")
        
    except Exception as e:
        results["components"]["cross_encoder"] = {
            "working": False,
            "error": str(e)
        }
        print(f"  ❌ Cross-Encoder Failed: {e}")
    
    # Calculate overall score
    working_components = sum(1 for comp in results["components"].values() if comp.get("working", False))
    total_components = len(results["components"])
    results["overall_score"] = working_components / total_components if total_components > 0 else 0
    results["passed"] = results["overall_score"] >= 0.75
    
    print(f"\n🎯 Phase 1 Validation Results")
    print("=" * 40)
    for name, comp in results["components"].items():
        status = "✅" if comp.get("working", False) else "❌"
        print(f"  {name}: {status}")
    
    print(f"\nOverall Score: {results['overall_score']:.2%}")
    print(f"Status: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
    
    return results

if __name__ == "__main__":
    results = test_phase1_components()
    
    # Save results
    with open("phase1_simple_real_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nFinal Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
