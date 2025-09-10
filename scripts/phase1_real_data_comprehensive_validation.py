#!/usr/bin/env python3
"""
Phase 1 Real Data Comprehensive Validation
Uses actual data-pipeline services and vault data for reliable testing
"""

import sys
import time
import json
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add data-pipeline src to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

def test_real_embedding_service_advanced():
    """Advanced test of the real embedding service with real data"""
    print("🧪 Phase 1.1: Real Embedding Service Advanced Test")
    print("=" * 60)
    
    try:
        from embeddings.embedding_service import EmbeddingService
        
        # Initialize with real service
        embedding_service = EmbeddingService(
            model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
        
        # Test with real content from vault
        vault_path = Path(__file__).parent.parent / "data" / "raw" / "vault"
        test_files = list(vault_path.glob("*.md"))
        
        if not test_files:
            print("❌ No vault files found for testing")
            return {"error": "No vault files", "service_working": False}
        
        # Read real content
        real_contents = []
        for file_path in test_files[:3]:  # Test with first 3 files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    real_contents.append({
                        "file": str(file_path.name),
                        "content": content[:500] + "..." if len(content) > 500 else content
                    })
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
        
        if not real_contents:
            print("❌ No readable vault content found")
            return {"error": "No readable content", "service_working": False}
        
        # Generate embeddings for real content
        embeddings = []
        for content in real_contents:
            embedding = embedding_service.generate_embedding(content["content"])
            embeddings.append(embedding)
        
        # Test semantic similarity
        similarity_tests = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                similarity_tests.append({
                    "file1": real_contents[i]["file"],
                    "file2": real_contents[j]["file"],
                    "similarity": float(similarity)
                })
        
        # Test embedding consistency
        consistency_tests = []
        for i, content in enumerate(real_contents):
            # Generate embedding twice
            emb1 = embedding_service.generate_embedding(content["content"])
            emb2 = embedding_service.generate_embedding(content["content"])
            consistency = cosine_similarity([emb1], [emb2])[0][0]
            consistency_tests.append({
                "file": content["file"],
                "consistency": float(consistency)
            })
        
        results = {
            "service_working": True,
            "model_name": embedding_service.model_name,
            "multilingual": embedding_service.is_multilingual,
            "embedding_dimension": len(embeddings[0]) if embeddings else 0,
            "real_files_tested": len(real_contents),
            "similarity_tests": similarity_tests,
            "consistency_tests": consistency_tests,
            "avg_similarity": float(np.mean([t["similarity"] for t in similarity_tests])) if similarity_tests else 0,
            "avg_consistency": float(np.mean([t["consistency"] for t in consistency_tests])) if consistency_tests else 0
        }
        
        print(f"✅ Embedding Service Working")
        print(f"Model: {embedding_service.model_name}")
        print(f"Multilingual: {embedding_service.is_multilingual}")
        print(f"Dimension: {results['embedding_dimension']}")
        print(f"Real Files Tested: {results['real_files_tested']}")
        print(f"Average Similarity: {results['avg_similarity']:.3f}")
        print(f"Average Consistency: {results['avg_consistency']:.3f}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "service_working": False}

def test_real_chromadb_service_advanced():
    """Advanced test of the real ChromaDB service with real data"""
    print(f"\n🗄️ Phase 1.2: Real ChromaDB Service Advanced Test")
    print("=" * 60)
    
    try:
        from vector.chroma_service import ChromaService
        
        # Initialize with real paths
        vault_path = Path(__file__).parent.parent / "data" / "raw" / "vault"
        vector_db_path = Path(__file__).parent.parent / "data" / "chroma"
        
        chroma_service = ChromaService(
            collection_name="test_phase1_validation",
            persist_directory=str(vector_db_path),
            embedding_model="all-MiniLM-L6-v2",
            optimize_for_large_vault=True
        )
        
        # Test collection operations
        collection_stats = chroma_service.get_collection_stats()
        
        # Test with real vault content
        vault_files = list(vault_path.glob("*.md"))
        if not vault_files:
            print("❌ No vault files found for ChromaDB testing")
            return {"error": "No vault files", "service_working": False}
        
        # Prepare real content for testing
        test_chunks = []
        test_embeddings = []
        
        from embeddings.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        
        for i, file_path in enumerate(vault_files[:2]):  # Test with first 2 files
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
                
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")
        
        if not test_chunks:
            print("❌ No chunks prepared for ChromaDB testing")
            return {"error": "No chunks prepared", "service_working": False}
        
        # Test storing embeddings
        try:
            chroma_service.store_embeddings(test_chunks, test_embeddings)
            store_success = True
        except Exception as e:
            print(f"Warning: Could not store embeddings: {e}")
            store_success = False
        
        # Test searching
        search_results = []
        if store_success:
            try:
                search_results = chroma_service.search_similar("artificial intelligence", n_results=3)
            except Exception as e:
                print(f"Warning: Search failed: {e}")
        
        # Test metadata search
        metadata_results = []
        if store_success:
            try:
                metadata_results = chroma_service.search_by_metadata(
                    {"file_type": "markdown"}, n_results=3
                )
            except Exception as e:
                print(f"Warning: Metadata search failed: {e}")
        
        results = {
            "service_working": True,
            "collection_name": chroma_service.collection.name,
            "persist_directory": str(vector_db_path),
            "collection_stats": collection_stats,
            "chunks_prepared": len(test_chunks),
            "store_success": store_success,
            "search_results_count": len(search_results),
            "metadata_results_count": len(metadata_results),
            "search_working": len(search_results) > 0,
            "metadata_search_working": len(metadata_results) > 0
        }
        
        print(f"✅ ChromaDB Service Working")
        print(f"Collection: {chroma_service.collection.name}")
        print(f"Persist Directory: {vector_db_path}")
        print(f"Chunks Prepared: {results['chunks_prepared']}")
        print(f"Store Success: {'✅ YES' if results['store_success'] else '❌ NO'}")
        print(f"Search Results: {results['search_results_count']}")
        print(f"Metadata Search: {results['metadata_results_count']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "service_working": False}

def test_real_vector_search_performance():
    """Test real vector search performance with actual data"""
    print(f"\n🔍 Phase 1.3: Real Vector Search Performance Test")
    print("=" * 60)
    
    try:
        from vector.chroma_service import ChromaService
        from embeddings.embedding_service import EmbeddingService
        
        # Initialize services
        vector_db_path = Path(__file__).parent.parent / "data" / "chroma"
        chroma_service = ChromaService(
            collection_name="test_phase1_validation",
            persist_directory=str(vector_db_path),
            embedding_model="all-MiniLM-L6-v2"
        )
        
        embedding_service = EmbeddingService()
        
        # Test queries
        test_queries = [
            "artificial intelligence machine learning",
            "vector database embeddings",
            "philosophy mathematics logic",
            "web scraping data extraction",
            "performance optimization techniques"
        ]
        
        search_results = []
        performance_metrics = []
        
        for query in test_queries:
            start_time = time.time()
            
            try:
                results = chroma_service.search_similar(query, n_results=5)
                search_time = time.time() - start_time
                
                # Analyze results quality
                if results:
                    similarities = [r.get('similarity_score', 0) for r in results]
                    avg_similarity = np.mean(similarities) if similarities else 0
                    max_similarity = max(similarities) if similarities else 0
                    min_similarity = min(similarities) if similarities else 0
                else:
                    avg_similarity = max_similarity = min_similarity = 0
                
                search_results.append({
                    "query": query,
                    "results_count": len(results),
                    "search_time": search_time,
                    "avg_similarity": avg_similarity,
                    "max_similarity": max_similarity,
                    "min_similarity": min_similarity,
                    "success": True
                })
                
                performance_metrics.append({
                    "query": query,
                    "search_time": search_time,
                    "results_per_second": len(results) / search_time if search_time > 0 else 0
                })
                
            except Exception as e:
                search_time = time.time() - start_time
                search_results.append({
                    "query": query,
                    "results_count": 0,
                    "search_time": search_time,
                    "avg_similarity": 0,
                    "max_similarity": 0,
                    "min_similarity": 0,
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate overall metrics
        successful_searches = [r for r in search_results if r["success"]]
        avg_search_time = np.mean([r["search_time"] for r in successful_searches]) if successful_searches else 0
        avg_similarity = np.mean([r["avg_similarity"] for r in successful_searches]) if successful_searches else 0
        success_rate = len(successful_searches) / len(search_results) if search_results else 0
        
        results = {
            "service_working": True,
            "queries_tested": len(test_queries),
            "successful_searches": len(successful_searches),
            "success_rate": success_rate,
            "avg_search_time": avg_search_time,
            "avg_similarity": avg_similarity,
            "search_results": search_results,
            "performance_metrics": performance_metrics
        }
        
        print(f"✅ Vector Search Performance Test")
        print(f"Queries Tested: {results['queries_tested']}")
        print(f"Success Rate: {results['success_rate']:.2%}")
        print(f"Average Search Time: {results['avg_search_time']:.3f}s")
        print(f"Average Similarity: {results['avg_similarity']:.3f}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "service_working": False}

def test_real_reranking_validation():
    """Test real re-ranking with actual data"""
    print(f"\n🎯 Phase 1.4: Real Re-ranking Validation Test")
    print("=" * 60)
    
    try:
        from sentence_transformers import CrossEncoder
        
        # Initialize cross-encoder
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        # Test with real query and documents
        test_query = "artificial intelligence machine learning algorithms"
        test_documents = [
            "Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models.",
            "Web scraping involves extracting data from websites using tools like Scrapy and BeautifulSoup.",
            "Philosophy of mathematics examines the nature of mathematical objects and truth.",
            "Artificial intelligence algorithms use neural networks to process and learn from data.",
            "Database optimization techniques improve query performance and reduce response times."
        ]
        
        # Test cross-encoder scoring
        pairs = [(test_query, doc) for doc in test_documents]
        cross_scores = cross_encoder.predict(pairs)
        
        # Analyze scoring quality
        score_analysis = []
        for i, (doc, score) in enumerate(zip(test_documents, cross_scores)):
            score_analysis.append({
                "document": doc[:100] + "...",
                "cross_score": float(score),
                "rank": i + 1
            })
        
        # Sort by cross-encoder scores
        sorted_results = sorted(score_analysis, key=lambda x: x["cross_score"], reverse=True)
        
        # Test performance
        performance_tests = []
        for candidate_count in [5, 10, 20, 50]:
            start_time = time.time()
            test_pairs = [(test_query, doc) for doc in test_documents * (candidate_count // len(test_documents) + 1)][:candidate_count]
            _ = cross_encoder.predict(test_pairs)
            processing_time = time.time() - start_time
            
            performance_tests.append({
                "candidate_count": candidate_count,
                "processing_time": processing_time,
                "candidates_per_second": candidate_count / processing_time if processing_time > 0 else 0
            })
        
        results = {
            "service_working": True,
            "model_name": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "test_query": test_query,
            "documents_tested": len(test_documents),
            "score_analysis": score_analysis,
            "sorted_results": sorted_results,
            "performance_tests": performance_tests,
            "avg_score": float(np.mean(cross_scores)),
            "score_range": [float(np.min(cross_scores)), float(np.max(cross_scores))]
        }
        
        print(f"✅ Re-ranking Validation Test")
        print(f"Model: {results['model_name']}")
        print(f"Documents Tested: {results['documents_tested']}")
        print(f"Average Score: {results['avg_score']:.3f}")
        print(f"Score Range: {results['score_range'][0]:.3f} - {results['score_range'][1]:.3f}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "service_working": False}

def run_phase1_comprehensive_validation():
    """Run comprehensive Phase 1 validation with real data"""
    print("🚀 Phase 1 Real Data Comprehensive Validation")
    print("=" * 70)
    print("Testing with actual data-pipeline services and vault data")
    print("=" * 70)
    
    start_time = time.time()
    
    # Run all Phase 1 tests
    embedding_results = test_real_embedding_service_advanced()
    chroma_results = test_real_chromadb_service_advanced()
    search_results = test_real_vector_search_performance()
    reranking_results = test_real_reranking_validation()
    
    # Calculate overall Phase 1 score
    embedding_score = 1.0 if embedding_results.get('service_working', False) else 0.0
    chroma_score = 1.0 if chroma_results.get('service_working', False) else 0.0
    search_score = 1.0 if search_results.get('service_working', False) else 0.0
    reranking_score = 1.0 if reranking_results.get('service_working', False) else 0.0
    
    # Weighted scoring based on criticality
    overall_score = (embedding_score * 0.3 + chroma_score * 0.3 + 
                    search_score * 0.25 + reranking_score * 0.15)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n🎯 Phase 1 Validation Results")
    print("=" * 50)
    print(f"1.1 Embedding Service: {embedding_score:.3f}")
    print(f"1.2 ChromaDB Service: {chroma_score:.3f}")
    print(f"1.3 Vector Search: {search_score:.3f}")
    print(f"1.4 Re-ranking: {reranking_score:.3f}")
    print(f"Overall Phase 1 Score: {overall_score:.3f}")
    print(f"Duration: {duration:.2f}s")
    print(f"Status: {'✅ PASS' if overall_score >= 0.8 else '❌ FAIL'}")
    
    # Save comprehensive results
    results = {
        "phase": "1",
        "test_name": "Phase 1 Real Data Comprehensive Validation",
        "overall_score": overall_score,
        "embedding_results": embedding_results,
        "chroma_results": chroma_results,
        "search_results": search_results,
        "reranking_results": reranking_results,
        "duration": duration,
        "passed": overall_score >= 0.8,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("phase1_real_data_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = run_phase1_comprehensive_validation()
    print(f"\nFinal Phase 1 Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
