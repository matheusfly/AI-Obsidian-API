#!/usr/bin/env python3
"""
Test re-ranking functionality with mock data
"""
import asyncio
import logging
import sys
import os
import time
import statistics
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.search.search_service import SemanticSearchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_mock_data():
    """Create mock data for testing"""
    mock_chunks = [
        {
            "content": "Artificial intelligence and machine learning are transforming the way we process data and make decisions. Deep learning algorithms can identify patterns in large datasets that would be impossible for humans to detect.",
            "path": "ai_ml_basics.md",
            "heading": "Introduction to AI/ML",
            "chunk_index": 0,
            "chunk_token_count": 45,
            "file_type": "dated_note",
            "path_year": "2024",
            "path_month": "01",
            "path_category": "ai",
            "content_tags": ["ai", "machine-learning", "deep-learning"],
            "file_metadata": {
                "tags": ["ai", "machine-learning", "deep-learning"],
                "created": "2024-01-15",
                "modified": "2024-01-20"
            }
        },
        {
            "content": "Vector databases like ChromaDB enable efficient similarity search for embeddings. They use algorithms like HNSW to provide fast approximate nearest neighbor search for high-dimensional vectors.",
            "path": "vector_databases.md", 
            "heading": "Vector Database Fundamentals",
            "chunk_index": 0,
            "chunk_token_count": 38,
            "file_type": "dated_note",
            "path_year": "2024",
            "path_month": "01",
            "path_category": "databases",
            "content_tags": ["vector-database", "embeddings", "similarity-search"],
            "file_metadata": {
                "tags": ["vector-database", "embeddings", "similarity-search"],
                "created": "2024-01-10",
                "modified": "2024-01-18"
            }
        },
        {
            "content": "Cross-encoder models provide more accurate relevance scoring than bi-encoder models for query-document pairs. They process the query and document together, allowing for deeper interaction understanding.",
            "path": "cross_encoders.md",
            "heading": "Cross-Encoder Architecture", 
            "chunk_index": 0,
            "chunk_token_count": 35,
            "file_type": "dated_note",
            "path_year": "2024",
            "path_month": "01",
            "path_category": "nlp",
            "content_tags": ["cross-encoder", "relevance-scoring", "nlp"],
            "file_metadata": {
                "tags": ["cross-encoder", "relevance-scoring", "nlp"],
                "created": "2024-01-12",
                "modified": "2024-01-19"
            }
        },
        {
            "content": "Hybrid search combines semantic vector search with traditional keyword matching to provide comprehensive results. This approach leverages both meaning and exact term matching for better precision.",
            "path": "hybrid_search.md",
            "heading": "Hybrid Search Strategy",
            "chunk_index": 0,
            "chunk_token_count": 33,
            "file_type": "dated_note",
            "path_year": "2024",
            "path_month": "01",
            "path_category": "search",
            "content_tags": ["hybrid-search", "semantic-search", "keyword-matching"],
            "file_metadata": {
                "tags": ["hybrid-search", "semantic-search", "keyword-matching"],
                "created": "2024-01-14",
                "modified": "2024-01-21"
            }
        },
        {
            "content": "Context engineering involves optimizing prompts and context to improve LLM performance. Techniques include prompt templates, few-shot learning, and context-aware retrieval strategies.",
            "path": "context_engineering.md",
            "heading": "Context Engineering Techniques",
            "chunk_index": 0,
            "chunk_token_count": 32,
            "file_type": "dated_note",
            "path_year": "2024",
            "path_month": "01",
            "path_category": "engineering",
            "content_tags": ["context-engineering", "prompt-optimization", "llm"],
            "file_metadata": {
                "tags": ["context-engineering", "prompt-optimization", "llm"],
                "created": "2024-01-16",
                "modified": "2024-01-22"
            }
        },
        {
            "content": "Batch processing optimizes embedding generation by processing multiple texts simultaneously. This reduces computational overhead and improves throughput for large-scale vector operations.",
            "path": "batch_processing.md",
            "heading": "Batch Processing Optimization",
            "chunk_index": 0,
            "chunk_token_count": 30,
            "file_type": "dated_note",
            "path_year": "2024",
            "path_month": "01",
            "path_category": "optimization",
            "content_tags": ["batch-processing", "optimization", "embeddings"],
            "file_metadata": {
                "tags": ["batch-processing", "optimization", "embeddings"],
                "created": "2024-01-11",
                "modified": "2024-01-17"
            }
        },
        {
            "content": "Metadata enrichment enhances search capabilities by extracting and storing additional information about documents. This includes frontmatter parsing, tag extraction, and temporal information.",
            "path": "metadata_enrichment.md",
            "heading": "Metadata Enrichment Strategies",
            "chunk_index": 0,
            "chunk_token_count": 28,
            "file_type": "dated_note",
            "path_year": "2024",
            "path_month": "01",
            "path_category": "metadata",
            "content_tags": ["metadata", "enrichment", "search"],
            "file_metadata": {
                "tags": ["metadata", "enrichment", "search"],
                "created": "2024-01-13",
                "modified": "2024-01-20"
            }
        },
        {
            "content": "Content chunking strategies balance semantic coherence with computational efficiency. Advanced chunking considers document structure, token limits, and overlap requirements for optimal retrieval.",
            "path": "chunking_strategies.md",
            "heading": "Advanced Chunking Techniques",
            "chunk_index": 0,
            "chunk_token_count": 31,
            "file_type": "dated_note",
            "path_year": "2024",
            "path_month": "01",
            "path_category": "processing",
            "content_tags": ["chunking", "content-processing", "retrieval"],
            "file_metadata": {
                "tags": ["chunking", "content-processing", "retrieval"],
                "created": "2024-01-09",
                "modified": "2024-01-16"
            }
        }
    ]
    
    return mock_chunks

async def test_rerank_with_mock_data():
    """Test re-ranking functionality with mock data"""
    logger.info("🚀 Testing Re-Ranking with Mock Data")
    logger.info("=" * 60)
    
    # Initialize services
    chroma_service = ChromaService(
        collection_name="mock_test_collection",
        persist_directory="./test_mock_chroma",
        embedding_model="all-MiniLM-L6-v2",
        optimize_for_large_vault=True
    )
    
    embedding_service = EmbeddingService(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    search_service = SemanticSearchService(
        chroma_service=chroma_service,
        embedding_service=embedding_service
    )
    
    # Create and store mock data
    logger.info("📊 Creating and storing mock data...")
    mock_chunks = create_mock_data()
    mock_texts = [chunk['content'] for chunk in mock_chunks]
    
    # Generate embeddings
    embeddings = embedding_service.batch_generate_embeddings(mock_texts)
    
    # Store in ChromaDB
    chroma_service.store_embeddings(mock_chunks, embeddings)
    
    count = chroma_service.collection.count()
    logger.info(f"✅ Stored {count} mock documents")
    
    # Test queries
    test_queries = [
        "machine learning artificial intelligence",
        "vector database similarity search", 
        "cross encoder relevance scoring",
        "hybrid search semantic keyword",
        "context engineering prompt optimization"
    ]
    
    logger.info("\n🔍 Testing Re-Ranking Performance")
    logger.info("-" * 50)
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n📝 Query {i}: '{query}'")
        
        # Test regular search
        start_time = time.time()
        regular_results = search_service.search_similar(query, n_results=3)
        regular_time = time.time() - start_time
        
        # Test re-ranked search
        start_time = time.time()
        rerank_results = search_service.search_with_rerank(query, n_results=3, rerank_top_k=6)
        rerank_time = time.time() - start_time
        
        # Calculate improvements
        if regular_results and rerank_results:
            regular_scores = [r.get('similarity', 0) for r in regular_results]
            rerank_scores = [r.get('final_score', 0) for r in rerank_results]
            
            avg_regular = statistics.mean(regular_scores)
            avg_rerank = statistics.mean(rerank_scores)
            improvement = ((avg_rerank - avg_regular) / avg_regular * 100) if avg_regular > 0 else 0
            
            time_overhead = ((rerank_time - regular_time) / regular_time * 100) if regular_time > 0 else 0
            
            logger.info(f"  ⏱️  Regular: {regular_time*1000:.1f}ms, Re-rank: {rerank_time*1000:.1f}ms")
            logger.info(f"  📈 Score improvement: {improvement:+.1f}%")
            logger.info(f"  ⚡ Time overhead: {time_overhead:+.1f}%")
            
            # Show top results
            logger.info(f"  🥇 Regular top result: {regular_results[0].get('source_file', 'N/A')} (sim: {regular_results[0].get('similarity', 0):.3f})")
            logger.info(f"  🥇 Re-rank top result: {rerank_results[0].get('source_file', 'N/A')} (final: {rerank_results[0].get('final_score', 0):.3f})")
            
            results.append({
                "query": query,
                "regular_time_ms": regular_time * 1000,
                "rerank_time_ms": rerank_time * 1000,
                "score_improvement_percent": improvement,
                "time_overhead_percent": time_overhead,
                "regular_top_path": regular_results[0].get('source_file', 'N/A'),
                "rerank_top_path": rerank_results[0].get('source_file', 'N/A')
            })
    
    # Calculate overall statistics
    logger.info("\n📊 OVERALL BENCHMARK RESULTS")
    logger.info("=" * 60)
    
    if results:
        avg_improvement = statistics.mean([r["score_improvement_percent"] for r in results])
        avg_time_overhead = statistics.mean([r["time_overhead_percent"] for r in results])
        avg_regular_time = statistics.mean([r["regular_time_ms"] for r in results])
        avg_rerank_time = statistics.mean([r["rerank_time_ms"] for r in results])
        
        logger.info(f"⏱️  Average Regular Search Time: {avg_regular_time:.1f}ms")
        logger.info(f"⏱️  Average Re-rank Search Time: {avg_rerank_time:.1f}ms")
        logger.info(f"📈 Average Score Improvement: {avg_improvement:+.1f}%")
        logger.info(f"⚡ Average Time Overhead: {avg_time_overhead:+.1f}%")
        
        # Recommendations
        logger.info("\n🎯 RECOMMENDATIONS:")
        logger.info("-" * 30)
        
        if avg_improvement > 5:
            logger.info("✅ SIGNIFICANT QUALITY GAIN: Re-ranking provides substantial precision improvements")
        elif avg_improvement > 0:
            logger.info("✅ MODERATE QUALITY GAIN: Re-ranking provides modest precision improvements")
        else:
            logger.info("⚠️  NO QUALITY GAIN: Re-ranking may not be beneficial for this dataset")
        
        if avg_time_overhead < 100:
            logger.info("✅ ACCEPTABLE PERFORMANCE COST: Time overhead is reasonable for production use")
        elif avg_time_overhead < 200:
            logger.info("⚠️  MODERATE PERFORMANCE COST: Consider optimizing re-ranking parameters")
        else:
            logger.info("❌ HIGH PERFORMANCE COST: Re-ranking may be too expensive for production use")
        
        # Show detailed results
        logger.info("\n📋 DETAILED RESULTS:")
        logger.info("-" * 30)
        for result in results:
            logger.info(f"Query: {result['query']}")
            logger.info(f"  Regular: {result['regular_time_ms']:.1f}ms → {result['regular_top_path']}")
            logger.info(f"  Re-rank: {result['rerank_time_ms']:.1f}ms → {result['rerank_top_path']}")
            logger.info(f"  Improvement: {result['score_improvement_percent']:+.1f}%")
            logger.info("")
    
    logger.info("🎉 Re-Ranking Benchmark Complete!")

if __name__ == "__main__":
    asyncio.run(test_rerank_with_mock_data())
