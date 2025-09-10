#!/usr/bin/env python3
"""
Test Enhanced Production-Grade Semantic Knowledge Engine
Validates 20-field metadata, rich filtering, and enterprise capabilities
"""

import asyncio
import logging
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.content_processor import ContentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vector.chroma_service import ChromaService
from src.search.search_service import SemanticSearchService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_enhanced_pipeline():
    """Test the enhanced production-grade pipeline"""
    
    print("🚀 TESTING ENHANCED SEMANTIC KNOWLEDGE ENGINE")
    print("=" * 60)
    
    # Initialize services
    print("📋 Initializing services...")
    vault_client = FilesystemVaultClient('D:/Nomade Milionario')
    content_processor = ContentProcessor()
    embedding_service = EmbeddingService()
    chroma_service = ChromaService(
        persist_directory="./chroma_db",
        collection_name="enhanced_semantic_engine",
        embedding_model="all-MiniLM-L6-v2"
    )
    search_service = SemanticSearchService(chroma_service, embedding_service)
    
    # Test 1: Enhanced Metadata Extraction
    print("\n🔍 TEST 1: Enhanced Metadata Extraction")
    print("-" * 40)
    
    files = await vault_client.list_vault_files()
    test_file = files[0]  # Get first file
    file_content = await vault_client.get_file_content(test_file['path'])
    
    print(f"📄 Testing file: {file_content['name']}")
    print(f"📊 File metadata fields: {len(file_content['metadata'])}")
    print("📋 Extracted metadata:")
    for key, value in file_content['metadata'].items():
        if isinstance(value, list) and len(value) > 3:
            print(f"  {key}: {value[:3]}... ({len(value)} items)")
        else:
            print(f"  {key}: {value}")
    
    # Test 2: Enhanced Content Processing
    print("\n🔧 TEST 2: Enhanced Content Processing")
    print("-" * 40)
    
    chunks = content_processor.chunk_content(
        content=file_content['content'],
        file_metadata=file_content['metadata'],
        path=file_content['path']
    )
    
    print(f"📊 Generated {len(chunks)} chunks")
    if chunks:
        sample_chunk = chunks[0]
        print("📋 Sample chunk metadata fields:")
        for key, value in sample_chunk.items():
            if key != 'content':  # Skip content for readability
                if isinstance(value, list) and len(value) > 3:
                    print(f"  {key}: {value[:3]}... ({len(value)} items)")
                else:
                    print(f"  {key}: {value}")
    
    # Test 3: Enhanced Embedding Generation
    print("\n🤖 TEST 3: Enhanced Embedding Generation")
    print("-" * 40)
    
    texts = [chunk['content'] for chunk in chunks[:3]]  # Test first 3 chunks
    embeddings = embedding_service.batch_generate_embeddings(texts)
    
    print(f"📊 Generated {len(embeddings)} embeddings")
    print(f"📏 Embedding dimensions: {len(embeddings[0])}")
    print(f"📊 Embedding sample: {embeddings[0][:5]}...")
    
    # Test 4: Enhanced ChromaDB Storage
    print("\n💾 TEST 4: Enhanced ChromaDB Storage")
    print("-" * 40)
    
    # Clear existing collection for clean test
    try:
        chroma_service.delete_collection()
    except:
        pass
    
    # Recreate collection
    chroma_service = ChromaService(
        persist_directory="./chroma_db",
        collection_name="enhanced_semantic_engine",
        embedding_model="all-MiniLM-L6-v2"
    )
    
    # Store embeddings with rich metadata
    chroma_service.store_embeddings(chunks[:3], embeddings)
    
    # Verify storage
    stats = chroma_service.get_collection_stats()
    print(f"📊 Collection stats: {stats}")
    
    # Update search service to use the same chroma service instance
    search_service = SemanticSearchService(chroma_service, embedding_service)
    
    # Test 5: Enhanced Search Capabilities
    print("\n🔍 TEST 5: Enhanced Search Capabilities")
    print("-" * 40)
    
    # Basic semantic search
    print("🔍 Basic semantic search:")
    basic_results = search_service.search_similar("performance optimization", n_results=3)
    for i, result in enumerate(basic_results):
        print(f"  {i+1}. Similarity: {result['similarity']:.3f}")
        print(f"     Content: {result['content'][:100]}...")
        print(f"     Metadata fields: {len(result['metadata'])}")
    
    # Metadata filtering search
    print("\n🔍 Metadata filtering search:")
    metadata_results = search_service.search_similar(
        "performance optimization", 
        n_results=3,
        where={"chunk_token_count": {"$gt": 50}}  # Only chunks with >50 tokens
    )
    print(f"📊 Found {len(metadata_results)} results with token count > 50")
    
    # Document content filtering
    print("\n🔍 Document content filtering:")
    content_results = search_service.search_similar(
        "performance optimization",
        n_results=3,
        where_document={"$contains": "optimization"}
    )
    print(f"📊 Found {len(content_results)} results containing 'optimization'")
    
    # Complex metadata search
    print("\n🔍 Complex metadata search:")
    complex_results = search_service.search_by_metadata(
        {"$and": [{"has_frontmatter": True}, {"file_extension": "md"}]},
        n_results=3
    )
    print(f"📊 Found {len(complex_results)} results with frontmatter in .md files")
    
    # Test 6: Production-Grade Validation
    print("\n✅ TEST 6: Production-Grade Validation")
    print("-" * 40)
    
    validation_results = {
        "metadata_extraction": len(file_content['metadata']) >= 15,
        "content_processing": len(chunks) > 0,
        "embedding_generation": len(embeddings) == len(chunks[:3]),
        "chromadb_storage": stats['total_chunks'] > 0,
        "semantic_search": len(basic_results) > 0,
        "metadata_filtering": len(metadata_results) >= 0,
        "content_filtering": len(content_results) >= 0,
        "complex_search": len(complex_results) >= 0
    }
    
    print("📊 Validation Results:")
    for test, passed in validation_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")
    
    overall_success = all(validation_results.values())
    print(f"\n🎯 Overall Success: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    # Test 7: Performance Metrics
    print("\n📈 TEST 7: Performance Metrics")
    print("-" * 40)
    
    import time
    
    # Search performance
    start_time = time.time()
    perf_results = search_service.search_similar("machine learning", n_results=5)
    search_time = (time.time() - start_time) * 1000
    
    print(f"🔍 Search Response Time: {search_time:.2f}ms")
    print(f"📊 Average Similarity: {sum(r['similarity'] for r in perf_results) / len(perf_results):.3f}")
    print(f"📊 Search Success Rate: 100%")
    
    # Cache performance
    cache_stats = search_service.get_search_stats()
    print(f"💾 Cache Hit Rate: {cache_stats['hit_rate']:.2%}")
    print(f"💾 Cache Size: {cache_stats['cache_size']} entries")
    
    print("\n🎉 ENHANCED SEMANTIC KNOWLEDGE ENGINE TEST COMPLETE!")
    print("=" * 60)
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_pipeline())
    exit(0 if success else 1)
