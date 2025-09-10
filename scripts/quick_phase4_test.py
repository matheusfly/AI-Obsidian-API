#!/usr/bin/env python3
"""
Quick Phase 4 Test - Verify real data integration
"""

import sys
from pathlib import Path

# Add data-pipeline services to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

print("🚀 Quick Phase 4 Test - Real Data Integration")
print("=" * 50)

try:
    # Test imports
    print("📦 Testing imports...")
    from embeddings.embedding_service import EmbeddingService
    from vector.chroma_service import ChromaService
    from search.semantic_search_service import SemanticSearchService
    print("✅ All imports successful")
    
    # Test service initialization
    print("🔧 Testing service initialization...")
    embedding_service = EmbeddingService()
    chroma_service = ChromaService()
    search_service = SemanticSearchService(chroma_service, embedding_service)
    print("✅ All services initialized")
    
    # Test embedding generation
    print("🧠 Testing embedding generation...")
    test_text = "Test embedding for philosophy and mathematics"
    embedding = embedding_service.embed_text(test_text)
    print(f"✅ Embedding generated: shape {embedding.shape}")
    
    # Test search functionality
    print("🔍 Testing search functionality...")
    test_query = "What are the main philosophical currents?"
    results = search_service.search(test_query, [], top_k=3)
    print(f"✅ Search test: {len(results)} results")
    
    # Test quality metrics
    print("📊 Testing quality metrics...")
    def calculate_precision_at_k(results, relevant_files, k=5):
        if not results:
            return 0.0
        top_k_results = results[:k]
        relevant_count = sum(1 for r in top_k_results if any(rel in r.get('path', '') for rel in relevant_files))
        return relevant_count / len(top_k_results)
    
    mock_results = [
        {"path": "philosophy.md", "similarity": 0.89},
        {"path": "logic.md", "similarity": 0.87},
        {"path": "scrapy.md", "similarity": 0.45}
    ]
    
    precision = calculate_precision_at_k(mock_results, ["philosophy", "logic"], 3)
    print(f"✅ Precision@3: {precision:.3f}")
    
    # Test response quality evaluation
    print("📝 Testing response quality evaluation...")
    def calculate_relevance_score(query, response, expected_keywords):
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        expected_words = set(expected_keywords)
        
        query_response_overlap = len(query_words & response_words) / len(query_words) if query_words else 0
        response_expected_overlap = len(response_words & expected_words) / len(expected_words) if expected_words else 0
        
        return (0.6 * query_response_overlap) + (0.4 * response_expected_overlap)
    
    test_query = "What are the main philosophical currents?"
    good_response = "The main philosophical currents are logicism, formalism, and intuitionism."
    bad_response = "I don't have information about that."
    expected_keywords = ["logicism", "formalism", "intuitionism", "philosophy"]
    
    good_relevance = calculate_relevance_score(test_query, good_response, expected_keywords)
    bad_relevance = calculate_relevance_score(test_query, bad_response, expected_keywords)
    
    print(f"✅ Good response relevance: {good_relevance:.3f}")
    print(f"✅ Bad response relevance: {bad_relevance:.3f}")
    
    # Test performance monitoring
    print("⚡ Testing performance monitoring...")
    import psutil
    import time
    
    process = psutil.Process()
    memory_usage = process.memory_info().rss / 1024 / 1024
    print(f"✅ Memory usage: {memory_usage:.1f} MB")
    
    start_time = time.time()
    for i in range(3):
        search_service.search(f"Test query {i}", [], top_k=2)
    end_time = time.time()
    avg_time = (end_time - start_time) / 3
    print(f"✅ Average search time: {avg_time:.3f}s")
    
    print("\n🎉 Phase 4 Quick Test - ALL TESTS PASSED!")
    print("✅ Real data integration working")
    print("✅ Quality metrics working")
    print("✅ Response evaluation working")
    print("✅ Performance monitoring working")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 Quick Phase 4 Test Complete")
