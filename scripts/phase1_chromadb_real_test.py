#!/usr/bin/env python3
"""
Phase 1.2: Real ChromaDB Service Validation
Tests ChromaDB service with real vault data
"""

import sys
import time
import json
from pathlib import Path

# Add data-pipeline src to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

def test_chromadb_service_with_real_data():
    """Test ChromaDB service using real vault data"""
    print("🗄️ Phase 1.2: Real ChromaDB Service Test")
    print("=" * 60)
    
    try:
        from vector.chroma_service import ChromaService
        from embeddings.embedding_service import EmbeddingService
        
        # Initialize services
        vector_db_path = Path(__file__).parent.parent / "data" / "chroma"
        vault_path = Path(__file__).parent.parent / "data" / "raw" / "vault"
        
        chroma_service = ChromaService(
            collection_name="test_phase1_chromadb_validation",
            persist_directory=str(vector_db_path),
            embedding_model="all-MiniLM-L6-v2",
            optimize_for_large_vault=True
        )
        
        embedding_service = EmbeddingService()
        
        print(f"📚 Collection: {chroma_service.collection.name}")
        print(f"🗄️ Persist Directory: {vector_db_path}")
        
        # Test 1: Collection Statistics
        print("\n📊 Test 1: Collection Statistics")
        try:
            stats = chroma_service.get_collection_stats()
            print(f"  Total Chunks: {stats['total_chunks']}")
            print(f"  Embedding Model: {stats['embedding_model']}")
            print(f"  HNSW Optimization: {stats['hnsw_optimization']}")
            print(f"  Batch Optimization: {stats['batch_optimization_enabled']}")
            collection_stats_working = True
        except Exception as e:
            print(f"  ❌ Collection stats failed: {e}")
            collection_stats_working = False
            stats = {}
        
        # Test 2: Real Data Preparation
        print("\n📝 Test 2: Real Data Preparation")
        vault_files = list(vault_path.glob("*.md"))
        
        if not vault_files:
            print("  ❌ No vault files found")
            return {"error": "No vault files", "passed": False}
        
        print(f"  Found {len(vault_files)} vault files")
        
        # Prepare test chunks
        test_chunks = []
        test_embeddings = []
        
        for i, file_path in enumerate(vault_files[:3]):  # Test with first 3 files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create test chunk
                chunk = {
                    "path": str(file_path),
                    "heading": f"Test Section {i+1}",
                    "chunk_index": 0,
                    "content": content[:1000],  # Limit content for testing
                    "chunk_token_count": len(content.split()),
                    "chunk_word_count": len(content.split()),
                    "chunk_char_count": len(content),
                    "file_word_count": len(content.split()),
                    "file_char_count": len(content),
                    "file_size": file_path.stat().st_size,
                    "file_modified": file_path.stat().st_mtime,
                    "file_created": file_path.stat().st_ctime,
                    "frontmatter_tags": [],
                    "content_tags": [],
                    "has_frontmatter": False,
                    "frontmatter_keys": [],
                    "file_extension": file_path.suffix,
                    "directory_path": str(file_path.parent),
                    "file_name": file_path.name,
                    "path_year": 2024,
                    "path_month": 1,
                    "path_day": 1,
                    "path_category": "test",
                    "path_subcategory": "validation",
                    "file_type": "markdown",
                    "content_type": "documentation",
                    "links": []
                }
                
                # Generate embedding
                embedding = embedding_service.generate_embedding(chunk["content"])
                
                test_chunks.append(chunk)
                test_embeddings.append(embedding)
                
                print(f"  ✅ Prepared chunk from {file_path.name}")
                
            except Exception as e:
                print(f"  ⚠️ Could not process {file_path}: {e}")
        
        if not test_chunks:
            print("  ❌ No chunks prepared")
            return {"error": "No chunks prepared", "passed": False}
        
        print(f"  Prepared {len(test_chunks)} chunks for testing")
        
        # Test 3: Store Embeddings
        print("\n💾 Test 3: Store Embeddings")
        try:
            chroma_service.store_embeddings(test_chunks, test_embeddings)
            print(f"  ✅ Successfully stored {len(test_chunks)} chunks")
            store_success = True
        except Exception as e:
            print(f"  ❌ Store embeddings failed: {e}")
            store_success = False
        
        # Test 4: Semantic Search
        print("\n🔍 Test 4: Semantic Search")
        search_results = []
        test_queries = [
            "artificial intelligence",
            "machine learning algorithms",
            "vector database"
        ]
        
        for query in test_queries:
            try:
                results = chroma_service.search_similar(query, n_results=3)
                search_results.append({
                    "query": query,
                    "results_count": len(results),
                    "success": True
                })
                print(f"  ✅ Query '{query}': {len(results)} results")
            except Exception as e:
                search_results.append({
                    "query": query,
                    "results_count": 0,
                    "success": False,
                    "error": str(e)
                })
                print(f"  ❌ Query '{query}' failed: {e}")
        
        # Test 5: Metadata Search
        print("\n🏷️ Test 5: Metadata Search")
        metadata_results = []
        metadata_filters = [
            {"file_type": "markdown"},
            {"path_category": "test"},
            {"content_type": "documentation"}
        ]
        
        for filter_dict in metadata_filters:
            try:
                results = chroma_service.search_by_metadata(filter_dict, n_results=3)
                metadata_results.append({
                    "filter": filter_dict,
                    "results_count": len(results),
                    "success": True
                })
                print(f"  ✅ Filter {filter_dict}: {len(results)} results")
            except Exception as e:
                metadata_results.append({
                    "filter": filter_dict,
                    "results_count": 0,
                    "success": False,
                    "error": str(e)
                })
                print(f"  ❌ Filter {filter_dict} failed: {e}")
        
        # Calculate success rates
        search_success_rate = sum(1 for r in search_results if r["success"]) / len(search_results) if search_results else 0
        metadata_success_rate = sum(1 for r in metadata_results if r["success"]) / len(metadata_results) if metadata_results else 0
        
        # Quality Assessment
        quality_checks = {
            "collection_stats": collection_stats_working,
            "data_preparation": len(test_chunks) > 0,
            "store_embeddings": store_success,
            "semantic_search": search_success_rate >= 0.5,
            "metadata_search": metadata_success_rate >= 0.5
        }
        
        passed_checks = sum(quality_checks.values())
        total_checks = len(quality_checks)
        quality_score = passed_checks / total_checks
        
        print(f"\n📊 Quality Assessment")
        print(f"  Collection Stats: {'✅' if quality_checks['collection_stats'] else '❌'}")
        print(f"  Data Preparation: {'✅' if quality_checks['data_preparation'] else '❌'}")
        print(f"  Store Embeddings: {'✅' if quality_checks['store_embeddings'] else '❌'}")
        print(f"  Semantic Search: {'✅' if quality_checks['semantic_search'] else '❌'}")
        print(f"  Metadata Search: {'✅' if quality_checks['metadata_search'] else '❌'}")
        print(f"  Quality Score: {quality_score:.2%}")
        
        results = {
            "test_name": "Phase 1.2 Real ChromaDB Service Test",
            "passed": quality_score >= 0.8,
            "quality_score": quality_score,
            "collection_name": chroma_service.collection.name,
            "persist_directory": str(vector_db_path),
            "files_processed": len(vault_files),
            "chunks_prepared": len(test_chunks),
            "collection_stats": stats,
            "store_success": store_success,
            "search_success_rate": search_success_rate,
            "metadata_success_rate": metadata_success_rate,
            "quality_checks": quality_checks,
            "search_results": search_results,
            "metadata_results": metadata_results
        }
        
        print(f"\n🎯 Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "passed": False}

if __name__ == "__main__":
    results = test_chromadb_service_with_real_data()
    
    # Save results
    with open("phase1_chromadb_real_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nFinal Result: {'✅ PASS' if results.get('passed', False) else '❌ FAIL'}")
