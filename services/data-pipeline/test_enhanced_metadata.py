#!/usr/bin/env python3
"""
Test Enhanced Metadata Extraction
Validates improved tag extraction and path pattern extraction
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

# Import our services
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.hybrid_content_processor import HybridContentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vector.chroma_service import ChromaService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
VAULT_ROOT_DIR = Path("D:/Nomade Milionario")
CHROMA_DB_DIR = "./test_chroma_db_enhanced_metadata"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

async def setup_test_environment():
    """Ensures a clean ChromaDB for testing."""
    if Path(CHROMA_DB_DIR).exists():
        import shutil
        shutil.rmtree(CHROMA_DB_DIR)
        logger.info(f"Cleaned up existing ChromaDB at {CHROMA_DB_DIR}")
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)

async def test_enhanced_tag_extraction():
    """Test the enhanced tag extraction system."""
    logger.info("\n🏷️ Testing Enhanced Tag Extraction")
    logger.info("=" * 50)
    
    filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
    
    try:
        # Get sample files
        files = await filesystem_client.list_vault_files()
        if not files:
            logger.warning("No files found for testing")
            return
        
        # Test with first few files
        test_files = files[:3]
        
        for file_info in test_files:
            file_path = file_info['path']
            file_data = await filesystem_client.get_file_content(file_path)
            metadata = file_data['metadata']
            
            logger.info(f"\n📄 File: {file_path}")
            logger.info(f"   Content tags: {metadata.get('content_tags', [])}")
            logger.info(f"   Frontmatter tags: {metadata.get('frontmatter_tags', [])}")
            logger.info(f"   Links: {metadata.get('links', [])}")
            
            # Check if we're getting semantic tags instead of numeric IDs
            content_tags = metadata.get('content_tags', [])
            numeric_tags = [tag for tag in content_tags if tag.isdigit()]
            semantic_tags = [tag for tag in content_tags if not tag.isdigit()]
            
            logger.info(f"   Semantic tags: {semantic_tags}")
            logger.info(f"   Numeric tags (should be fewer): {numeric_tags}")
            
            if len(semantic_tags) > len(numeric_tags):
                logger.info("   ✅ Enhanced tag extraction working!")
            else:
                logger.info("   ⚠️ Still getting mostly numeric tags")
    
    except Exception as e:
        logger.error(f"Error testing tag extraction: {e}")
        import traceback
        traceback.print_exc()

async def test_path_pattern_extraction():
    """Test the path pattern extraction system."""
    logger.info("\n📁 Testing Path Pattern Extraction")
    logger.info("=" * 50)
    
    filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
    
    try:
        # Get sample files
        files = await filesystem_client.list_vault_files()
        if not files:
            logger.warning("No files found for testing")
            return
        
        # Test with first few files
        test_files = files[:5]
        
        for file_info in test_files:
            file_path = file_info['path']
            file_data = await filesystem_client.get_file_content(file_path)
            metadata = file_data['metadata']
            
            logger.info(f"\n📄 File: {file_path}")
            logger.info(f"   Path year: {metadata.get('path_year', 'N/A')}")
            logger.info(f"   Path month: {metadata.get('path_month', 'N/A')}")
            logger.info(f"   Path category: {metadata.get('path_category', 'N/A')}")
            logger.info(f"   File type: {metadata.get('file_type', 'N/A')}")
            logger.info(f"   Content type: {metadata.get('content_type', 'N/A')}")
            
            # Validate extracted patterns
            if metadata.get('path_year'):
                logger.info("   ✅ Year extraction working!")
            if metadata.get('file_type'):
                logger.info("   ✅ File type detection working!")
    
    except Exception as e:
        logger.error(f"Error testing path pattern extraction: {e}")
        import traceback
        traceback.print_exc()

async def test_enhanced_filtering():
    """Test filtering with enhanced metadata."""
    logger.info("\n🔍 Testing Enhanced Filtering")
    logger.info("=" * 50)
    
    await setup_test_environment()
    
    filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
    content_processor = HybridContentProcessor(max_chunk_size=256, chunk_overlap=64)
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    chroma_service = ChromaService(persist_directory=CHROMA_DB_DIR, collection_name="enhanced_metadata_test", embedding_model=EMBEDDING_MODEL)
    
    try:
        # Process a few files
        files = await filesystem_client.list_vault_files()
        test_files = files[:3]
        
        all_chunks = []
        for file_info in test_files:
            file_path = file_info['path']
            file_data = await filesystem_client.get_file_content(file_path)
            
            chunks = content_processor.chunk_content(
                content=file_data['content'],
                file_metadata=file_data['metadata'],
                path=file_path
            )
            all_chunks.extend(chunks)
        
        # Generate embeddings and store
        chunk_texts = [chunk['content'] for chunk in all_chunks]
        embeddings = embedding_service.batch_generate_embeddings(chunk_texts)
        chroma_service.store_embeddings(all_chunks, embeddings)
        
        logger.info(f"📈 Stored {len(all_chunks)} chunks with enhanced metadata")
        
        # Test enhanced filtering
        logger.info("\n🧪 Testing Enhanced Filters:")
        
        # Test 1: Filter by file type
        results = chroma_service.search_by_metadata({"file_type": "dated_note"}, n_results=3)
        logger.info(f"   Dated notes: {len(results)} results")
        
        # Test 2: Filter by year
        results = chroma_service.search_by_metadata({"path_year": 2025}, n_results=3)
        logger.info(f"   2025 files: {len(results)} results")
        
        # Test 3: Filter by content type
        results = chroma_service.search_by_metadata({"content_type": "note"}, n_results=3)
        logger.info(f"   Note files: {len(results)} results")
        
        # Test 4: Complex filter (2025 + dated_note)
        results = chroma_service.search_by_metadata({
            "path_year": 2025,
            "file_type": "dated_note"
        }, n_results=3)
        logger.info(f"   2025 dated notes: {len(results)} results")
        
        # Test 5: Semantic search with enhanced metadata filter
        results = chroma_service.search_similar(
            "artificial intelligence machine learning",
            n_results=3,
            where={"path_year": 2025}
        )
        logger.info(f"   AI content from 2025: {len(results)} results")
        
        logger.info("✅ Enhanced filtering test completed!")
    
    except Exception as e:
        logger.error(f"Error testing enhanced filtering: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all enhanced metadata tests."""
    logger.info("🚀 Testing Enhanced Metadata Extraction System")
    logger.info("=" * 60)
    
    # Test enhanced tag extraction
    await test_enhanced_tag_extraction()
    
    # Test path pattern extraction
    await test_path_pattern_extraction()
    
    # Test enhanced filtering
    await test_enhanced_filtering()
    
    logger.info("\n🎉 All Enhanced Metadata Tests Completed!")

if __name__ == "__main__":
    asyncio.run(main())
