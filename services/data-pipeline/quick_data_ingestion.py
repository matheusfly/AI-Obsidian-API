#!/usr/bin/env python3
"""
Quick data ingestion for benchmarking
"""
import asyncio
import logging
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.processing.hybrid_content_processor import HybridContentProcessor
from src.ingestion.filesystem_client import FilesystemVaultClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def quick_ingestion():
    """Quick ingestion of sample data for benchmarking"""
    logger.info("🚀 Starting Quick Data Ingestion for Benchmarking")
    
    # Initialize services
    chroma_service = ChromaService(
        collection_name="test_batch_200",
        persist_directory="./test_chroma_db_optimized",
        embedding_model="all-MiniLM-L6-v2",
        optimize_for_large_vault=True
    )
    
    embedding_service = EmbeddingService(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    content_processor = HybridContentProcessor(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        max_chunk_size=512,
        chunk_overlap=128
    )
    
    filesystem_client = FilesystemVaultClient(vault_path="D:\\Nomade Milionario")
    
    # Get sample files
    files = await filesystem_client.list_vault_files()
    sample_files = [f for f in files if f['path'].endswith('.md')][:5]  # Take first 5 files
    
    logger.info(f"📊 Processing {len(sample_files)} sample files")
    
    all_chunks = []
    for file_info in sample_files:
        try:
            file_data = await filesystem_client.get_file_content(file_info['path'])
            chunks = content_processor.chunk_content(
                content=file_data['content'],
                file_metadata=file_data,
                path=file_info['path']
            )
            all_chunks.extend(chunks)
            logger.info(f"✅ Processed {file_info['path']}: {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"❌ Failed to process {file_info['path']}: {e}")
    
    logger.info(f"📊 Total chunks created: {len(all_chunks)}")
    
    if all_chunks:
        # Generate embeddings in batches
        batch_size = 25
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i + batch_size]
            batch_texts = [chunk['content'] for chunk in batch_chunks]
            
            try:
                batch_embeddings = embedding_service.batch_generate_embeddings(batch_texts)
                chroma_service.store_embeddings(batch_chunks, batch_embeddings)
                logger.info(f"✅ Stored batch {i//batch_size + 1}: {len(batch_chunks)} chunks")
            except Exception as e:
                logger.error(f"❌ Failed to store batch {i//batch_size + 1}: {e}")
        
        # Verify storage
        count = chroma_service.collection.count()
        logger.info(f"🎉 Data ingestion complete! Collection now contains {count} documents")
    else:
        logger.error("❌ No chunks created. Cannot proceed with ingestion.")

if __name__ == "__main__":
    asyncio.run(quick_ingestion())
