#!/usr/bin/env python3
"""
Debug Metadata Storage
Check what metadata is actually stored in ChromaDB
"""

import asyncio
import logging
from pathlib import Path

from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.hybrid_content_processor import HybridContentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vector.chroma_service import ChromaService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
VAULT_ROOT_DIR = Path("D:/Nomade Milionario")
CHROMA_DB_DIR = "./debug_chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

async def debug_metadata():
    """Debug what metadata is actually stored."""
    logger.info("🔍 Debugging Metadata Storage")
    
    # Clean up
    if Path(CHROMA_DB_DIR).exists():
        import shutil
        shutil.rmtree(CHROMA_DB_DIR)
    
    # Initialize services
    filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
    content_processor = HybridContentProcessor(max_chunk_size=256, chunk_overlap=64)
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    chroma_service = ChromaService(persist_directory=CHROMA_DB_DIR, collection_name="debug_test", embedding_model=EMBEDDING_MODEL)
    
    # Process one file
    files = await filesystem_client.list_vault_files()
    test_file = files[0]['path']
    
    logger.info(f"📄 Processing file: {test_file}")
    
    # Get file data
    file_data = await filesystem_client.get_file_content(test_file)
    logger.info(f"📊 File metadata keys: {list(file_data['metadata'].keys())}")
    logger.info(f"📊 Enhanced metadata:")
    for key in ['path_year', 'path_month', 'file_type', 'content_type']:
        logger.info(f"   {key}: {file_data['metadata'].get(key, 'NOT_FOUND')}")
    
    # Process into chunks
    chunks = content_processor.chunk_content(
        content=file_data['content'],
        file_metadata=file_data['metadata'],
        path=test_file
    )
    
    logger.info(f"📊 Chunk metadata keys: {list(chunks[0].keys())}")
    logger.info(f"📊 First chunk enhanced metadata:")
    for key in ['path_year', 'path_month', 'file_type', 'content_type']:
        logger.info(f"   {key}: {chunks[0].get(key, 'NOT_FOUND')}")
    
    # Generate embeddings and store
    chunk_texts = [chunk['content'] for chunk in chunks[:3]]  # Just first 3 chunks
    embeddings = embedding_service.batch_generate_embeddings(chunk_texts)
    chroma_service.store_embeddings(chunks[:3], embeddings)
    
    # Check what's actually in ChromaDB
    logger.info("🔍 Checking ChromaDB metadata...")
    results = chroma_service.collection.get(limit=1)
    
    if results['metadatas']:
        stored_metadata = results['metadatas'][0]
        logger.info(f"📊 Stored metadata keys: {list(stored_metadata.keys())}")
        logger.info(f"📊 Stored enhanced metadata:")
        for key in ['path_year', 'path_month', 'file_type', 'content_type']:
            logger.info(f"   {key}: {stored_metadata.get(key, 'NOT_FOUND')}")
        
        # Test filtering
        logger.info("🧪 Testing filters...")
        
        # Test file_type filter
        file_type_results = chroma_service.collection.get(
            where={"file_type": stored_metadata.get('file_type', '')},
            limit=1
        )
        logger.info(f"   file_type filter: {len(file_type_results['metadatas'])} results")
        
        # Test path_year filter
        year_results = chroma_service.collection.get(
            where={"path_year": stored_metadata.get('path_year', 0)},
            limit=1
        )
        logger.info(f"   path_year filter: {len(year_results['metadatas'])} results")
    
    logger.info("✅ Debug complete!")

if __name__ == "__main__":
    asyncio.run(debug_metadata())
