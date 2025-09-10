#!/usr/bin/env python3
"""
Debug script to investigate why chunking isn't working
"""

import asyncio
import logging
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.hybrid_content_processor import HybridContentProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_chunking():
    """Debug why chunking isn't working"""
    logger.info("🔍 Debugging chunking issue...")
    
    # Initialize components
    filesystem_client = FilesystemVaultClient('D:\\Nomade Milionario')
    content_processor = HybridContentProcessor()
    
    # Get files
    files = await filesystem_client.list_vault_files()
    logger.info(f"Found {len(files)} files")
    
    if not files:
        logger.error("❌ No files found!")
        return
    
    # Try first few files
    for i, file_info in enumerate(files[:3]):
        logger.info(f"\n📄 Testing file {i+1}: {file_info['path']}")
        
        try:
            file_data = await filesystem_client.get_file_content(file_info['path'])
            logger.info(f"File content length: {len(file_data['content'])}")
            logger.info(f"File content preview: {file_data['content'][:200]}...")
            
            # Try chunking
            chunks = content_processor.chunk_content(
                content=file_data['content'],
                file_metadata=file_data,
                path=file_info['path']
            )
            logger.info(f"Chunks created: {len(chunks)}")
            
            if chunks:
                logger.info(f"First chunk preview: {chunks[0]['content'][:100]}...")
                logger.info(f"Chunk metadata: {list(chunks[0].keys())}")
            else:
                logger.warning("⚠️ No chunks created!")
                
        except Exception as e:
            logger.error(f"❌ Error processing file {file_info['path']}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chunking())
