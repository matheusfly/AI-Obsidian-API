#!/usr/bin/env python3
"""
Test Enhanced Metadata Filtering Capabilities
Validates our rich metadata system and advanced filtering capabilities
"""

import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import our services
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.hybrid_content_processor import HybridContentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vector.chroma_service import ChromaService
from src.search.search_service import SemanticSearchService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
VAULT_ROOT_DIR = Path("D:/Nomade Milionario")
CHROMA_DB_DIR = "./test_chroma_db_metadata_filtering"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "metadata_filtering_test"

async def setup_test_environment():
    """Setup clean test environment"""
    if Path(CHROMA_DB_DIR).exists():
        import shutil
        shutil.rmtree(CHROMA_DB_DIR)
        logger.info(f"Cleaned up existing ChromaDB at {CHROMA_DB_DIR}")
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)

async def test_metadata_extraction():
    """Test our current metadata extraction capabilities"""
    logger.info("\n🔍 Testing Metadata Extraction")
    logger.info("=" * 50)
    
    filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
    
    try:
        # Get a sample file
        files = await filesystem_client.list_vault_files()
        if not files:
            logger.warning("No files found for testing")
            return False
            
        test_file = files[0]['path']
        file_data = await filesystem_client.get_file_content(test_file)
        
        logger.info(f"📄 Testing file: {test_file}")
        logger.info(f"   File size: {len(file_data['content'])} chars")
        
        metadata = file_data['metadata']
        logger.info(f"📊 Extracted Metadata:")
        logger.info(f"   File size: {metadata.get('file_size', 0)} bytes")
        logger.info(f"   File modified: {datetime.fromtimestamp(metadata.get('file_modified', 0))}")
        logger.info(f"   File created: {datetime.fromtimestamp(metadata.get('file_created', 0))}")
        logger.info(f"   Has frontmatter: {metadata.get('has_frontmatter', False)}")
        logger.info(f"   Frontmatter tags: {metadata.get('frontmatter_tags', [])}")
        logger.info(f"   Content tags: {metadata.get('content_tags', [])}")
        logger.info(f"   File extension: {metadata.get('file_extension', '')}")
        logger.info(f"   Directory path: {metadata.get('directory_path', '')}")
        
        # Validate we have rich metadata
        required_fields = [
            'file_size', 'file_modified', 'file_created', 'file_word_count',
            'file_char_count', 'file_name', 'file_extension', 'directory_path',
            'frontmatter_tags', 'content_tags', 'has_frontmatter', 'frontmatter_keys'
        ]
        
        missing_fields = [field for field in required_fields if field not in metadata]
        if missing_fields:
            logger.error(f"❌ Missing metadata fields: {missing_fields}")
            return False
        
        logger.info("✅ Metadata extraction test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in metadata extraction test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chromadb_metadata_storage():
    """Test ChromaDB metadata storage with rich metadata"""
    logger.info("\n🗄️ Testing ChromaDB Metadata Storage")
    logger.info("=" * 50)
    
    filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
    content_processor = HybridContentProcessor(model_name=EMBEDDING_MODEL, max_chunk_size=512, chunk_overlap=128)
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    chroma_service = ChromaService(persist_directory=CHROMA_DB_DIR, collection_name=COLLECTION_NAME, embedding_model=EMBEDDING_MODEL)
    
    try:
        # Process a few files
        files = await filesystem_client.list_vault_files()
        test_files = files[:3]  # Test with 3 files
        
        all_chunks = []
        for file_info in test_files:
            file_data = await filesystem_client.get_file_content(file_info['path'])
            chunks = content_processor.chunk_content(
                content=file_data['content'],
                file_metadata=file_data['metadata'],
                path=file_data['path']
            )
            all_chunks.extend(chunks)
        
        logger.info(f"📊 Processed {len(test_files)} files into {len(all_chunks)} chunks")
        
        # Generate embeddings
        chunk_texts = [chunk['content'] for chunk in all_chunks]
        embeddings = embedding_service.batch_generate_embeddings(chunk_texts)
        
        # Store in ChromaDB
        chroma_service.store_embeddings(all_chunks, embeddings)
        
        # Verify storage
        count = chroma_service.collection.count()
        logger.info(f"📈 Total embeddings stored: {count}")
        
        # Test metadata retrieval
        sample_result = chroma_service.collection.get(limit=1, include=['metadatas'])
        if sample_result and sample_result['metadatas']:
            sample_metadata = sample_result['metadatas'][0]
            logger.info(f"📋 Sample stored metadata:")
            for key, value in sample_metadata.items():
                logger.info(f"   {key}: {value}")
        
        logger.info("✅ ChromaDB metadata storage test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in ChromaDB metadata storage test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_basic_filtering():
    """Test basic metadata filtering capabilities"""
    logger.info("\n🔍 Testing Basic Metadata Filtering")
    logger.info("=" * 50)
    
    chroma_service = ChromaService(persist_directory=CHROMA_DB_DIR, collection_name=COLLECTION_NAME, embedding_model=EMBEDDING_MODEL)
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    search_service = SemanticSearchService(chroma_service, embedding_service)
    
    try:
        # Test 1: Filter by file extension
        logger.info("🧪 Test 1: Filter by file extension (md)")
        results = search_service.search_similar(
            query="Python programming",
            n_results=5,
            where={"file_extension": "md"}
        )
        logger.info(f"   Found {len(results)} results for .md files")
        
        # Test 2: Filter by chunk size
        logger.info("🧪 Test 2: Filter by chunk token count (>200)")
        results = search_service.search_similar(
            query="machine learning",
            n_results=5,
            where={"chunk_token_count": {"$gt": 200}}
        )
        logger.info(f"   Found {len(results)} results for chunks >200 tokens")
        
        # Test 3: Filter by frontmatter presence
        logger.info("🧪 Test 3: Filter by frontmatter presence")
        results = search_service.search_similar(
            query="data science",
            n_results=5,
            where={"has_frontmatter": True}
        )
        logger.info(f"   Found {len(results)} results for files with frontmatter")
        
        # Test 4: Complex filter (multiple conditions)
        logger.info("🧪 Test 4: Complex filter (md files with frontmatter)")
        results = search_service.search_similar(
            query="artificial intelligence",
            n_results=5,
            where={"$and": [{"file_extension": "md"}, {"has_frontmatter": True}]}
        )
        logger.info(f"   Found {len(results)} results for complex filter")
        
        logger.info("✅ Basic filtering test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in basic filtering test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_advanced_filtering():
    """Test advanced filtering capabilities"""
    logger.info("\n🚀 Testing Advanced Filtering")
    logger.info("=" * 50)
    
    chroma_service = ChromaService(persist_directory=CHROMA_DB_DIR, collection_name=COLLECTION_NAME, embedding_model=EMBEDDING_MODEL)
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    search_service = SemanticSearchService(chroma_service, embedding_service)
    
    try:
        # Test 1: Date range filtering (last 30 days)
        logger.info("🧪 Test 1: Date range filtering (last 30 days)")
        thirty_days_ago = datetime.now() - timedelta(days=30)
        timestamp_30_days_ago = thirty_days_ago.timestamp()
        
        results = search_service.search_similar(
            query="technology trends",
            n_results=5,
            where={"file_modified": {"$gte": timestamp_30_days_ago}}
        )
        logger.info(f"   Found {len(results)} results from last 30 days")
        
        # Test 2: Tag filtering
        logger.info("🧪 Test 2: Tag filtering")
        results = search_service.search_by_tags(["python", "programming"], n_results=5)
        logger.info(f"   Found {len(results)} results with python/programming tags")
        
        # Test 3: Path pattern filtering
        logger.info("🧪 Test 3: Path pattern filtering")
        results = search_service.search_by_path("2025", n_results=5)
        logger.info(f"   Found {len(results)} results in 2025 files")
        
        # Test 4: Hybrid search with filters
        logger.info("🧪 Test 4: Hybrid search with filters")
        results = search_service.hybrid_search(
            query="AI machine learning",
            n_results=5,
            filters={"file_extension": "md"}
        )
        logger.info(f"   Found {len(results)} results from hybrid search")
        
        logger.info("✅ Advanced filtering test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in advanced filtering test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_complex_query_scenario():
    """Test the complex query scenario: 'What did I write about AI last month?'"""
    logger.info("\n🎯 Testing Complex Query Scenario")
    logger.info("=" * 50)
    logger.info("Query: 'What did I write about AI last month?'")
    
    chroma_service = ChromaService(persist_directory=CHROMA_DB_DIR, collection_name=COLLECTION_NAME, embedding_model=EMBEDDING_MODEL)
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    search_service = SemanticSearchService(chroma_service, embedding_service)
    
    try:
        # Calculate last month timestamp
        now = datetime.now()
        last_month = now.replace(day=1) - timedelta(days=1)
        last_month_start = last_month.replace(day=1)
        timestamp_last_month = last_month_start.timestamp()
        
        logger.info(f"📅 Searching for files modified since: {last_month_start.strftime('%Y-%m-%d')}")
        
        # Approach 1: Semantic search with date filter
        logger.info("🔍 Approach 1: Semantic search with date filter")
        results = search_service.search_similar(
            query="artificial intelligence AI machine learning",
            n_results=10,
            where={"file_modified": {"$gte": timestamp_last_month}}
        )
        
        logger.info(f"   Found {len(results)} semantically relevant results from last month")
        for i, result in enumerate(results[:3]):
            logger.info(f"   {i+1}. Similarity: {result['similarity']:.3f}")
            logger.info(f"      Path: {result['metadata']['path']}")
            logger.info(f"      Preview: {result['preview'][:100]}...")
        
        # Approach 2: Tag-based search with date filter
        logger.info("🏷️ Approach 2: Tag-based search with date filter")
        ai_tags = ["ai", "artificial-intelligence", "machine-learning", "ml", "neural-network"]
        tag_results = []
        
        for tag in ai_tags:
            tag_results.extend(search_service.search_by_tags([tag], n_results=5))
        
        # Filter by date
        recent_tag_results = [
            result for result in tag_results 
            if result['metadata'].get('file_modified', 0) >= timestamp_last_month
        ]
        
        logger.info(f"   Found {len(recent_tag_results)} tag-based results from last month")
        
        # Approach 3: Hybrid approach
        logger.info("🔄 Approach 3: Hybrid search with date filter")
        hybrid_results = search_service.hybrid_search(
            query="AI artificial intelligence machine learning",
            n_results=10,
            filters={"file_modified": {"$gte": timestamp_last_month}}
        )
        
        logger.info(f"   Found {len(hybrid_results)} hybrid results from last month")
        
        # Summary
        total_unique_results = len(set(
            result['id'] for result in results + recent_tag_results + hybrid_results
        ))
        
        logger.info(f"📊 Summary:")
        logger.info(f"   Semantic results: {len(results)}")
        logger.info(f"   Tag results: {len(recent_tag_results)}")
        logger.info(f"   Hybrid results: {len(hybrid_results)}")
        logger.info(f"   Total unique results: {total_unique_results}")
        
        if total_unique_results > 0:
            logger.info("✅ Complex query scenario test passed!")
            return True
        else:
            logger.warning("⚠️ No results found for complex query scenario")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error in complex query scenario test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all metadata filtering tests"""
    logger.info("🚀 Starting Enhanced Metadata Filtering Tests")
    logger.info("=" * 60)
    
    await setup_test_environment()
    
    test_results = []
    
    # Run tests
    test_results.append(await test_metadata_extraction())
    test_results.append(await test_chromadb_metadata_storage())
    test_results.append(await test_basic_filtering())
    test_results.append(await test_advanced_filtering())
    test_results.append(await test_complex_query_scenario())
    
    # Summary
    logger.info("\n📊 TEST SUMMARY")
    logger.info("=" * 60)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    logger.info(f"✅ Passed: {passed_tests}/{total_tests}")
    logger.info(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED! Enhanced metadata filtering is working perfectly!")
    else:
        logger.warning("⚠️ Some tests failed. Check logs for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    asyncio.run(main())
