#!/usr/bin/env python3
"""
Test script for Advanced Context-Aware Chunking
Validates the enhanced ContentProcessor with hybrid chunking strategy
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from ingestion.filesystem_client import FilesystemVaultClient
from processing.content_processor import ContentProcessor
from embeddings.embedding_service import EmbeddingService
from vector.chroma_service import ChromaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_advanced_chunking():
    """Test the advanced chunking functionality with real data."""
    
    logger.info("🚀 Testing Advanced Context-Aware Chunking System")
    
    # Initialize components
    vault_path = r"D:\Nomade Milionario"
    filesystem_client = FilesystemVaultClient(vault_path)
    
    # Test with different chunking configurations
    configs = [
        {"max_chunk_size": 256, "chunk_overlap": 64, "name": "Small Chunks"},
        {"max_chunk_size": 512, "chunk_overlap": 128, "name": "Medium Chunks"},
        {"max_chunk_size": 1024, "chunk_overlap": 256, "name": "Large Chunks"}
    ]
    
    for config in configs:
        logger.info(f"\n📊 Testing Configuration: {config['name']}")
        logger.info(f"   Max Chunk Size: {config['max_chunk_size']} tokens")
        logger.info(f"   Chunk Overlap: {config['chunk_overlap']} tokens")
        
        # Initialize processor with current config
        processor = ContentProcessor(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            max_chunk_size=config['max_chunk_size'],
            chunk_overlap=config['chunk_overlap']
        )
        
        # Get a sample file for testing
        try:
            files = await filesystem_client.list_vault_files()
            if not files:
                logger.warning("No files found for testing")
                continue
                
            test_file = files[0]['path']
            logger.info(f"   Testing with file: {test_file}")
            
            # Get file content
            file_data = await filesystem_client.get_file_content(test_file)
            content = file_data['content']
            metadata = file_data['metadata']
            
            logger.info(f"   File size: {len(content)} characters")
            logger.info(f"   File tokens: {processor._count_tokens(content)} tokens")
            
            # Test chunking
            chunks = processor.chunk_content(content, metadata, test_file)
            
            logger.info(f"   Generated {len(chunks)} chunks")
            
            # Analyze chunk quality
            chunk_sizes = [chunk['chunk_token_count'] for chunk in chunks]
            avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
            max_size = max(chunk_sizes) if chunk_sizes else 0
            min_size = min(chunk_sizes) if chunk_sizes else 0
            
            logger.info(f"   Chunk size stats:")
            logger.info(f"     Average: {avg_size:.1f} tokens")
            logger.info(f"     Min: {min_size} tokens")
            logger.info(f"     Max: {max_size} tokens")
            
            # Test sentence boundary detection
            logger.info(f"   Testing sentence boundary detection...")
            test_text = "This is a sentence. This is another sentence! And a third one? Here's a fourth sentence."
            sentences = processor._split_by_sentences(test_text)
            logger.info(f"     Split into {len(sentences)} sentences: {sentences}")
            
            # Test sliding window with overlap
            logger.info(f"   Testing sliding window with overlap...")
            long_text = " ".join(["This is a test sentence."] * 50)  # Create a long text
            window_chunks = list(processor._split_text_by_tokens(long_text))
            logger.info(f"     Split long text into {len(window_chunks)} chunks")
            
            if len(window_chunks) > 1:
                # Check overlap between consecutive chunks
                chunk1_tokens = processor.tokenizer.encode(window_chunks[0], truncation=False, add_special_tokens=False)
                chunk2_tokens = processor.tokenizer.encode(window_chunks[1], truncation=False, add_special_tokens=False)
                
                # Simple overlap check (first few tokens of chunk2 should be in chunk1)
                overlap_found = False
                for i in range(min(10, len(chunk2_tokens))):
                    if chunk2_tokens[i] in chunk1_tokens[-20:]:  # Check last 20 tokens of chunk1
                        overlap_found = True
                        break
                
                logger.info(f"     Overlap detected: {overlap_found}")
            
            # Show sample chunks
            logger.info(f"   Sample chunks:")
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                logger.info(f"     Chunk {i+1}: '{chunk['heading']}' ({chunk['chunk_token_count']} tokens)")
                logger.info(f"       Preview: {chunk['content'][:100]}...")
            
        except Exception as e:
            logger.error(f"   Error testing configuration {config['name']}: {e}")
            continue
    
    logger.info("\n✅ Advanced Chunking Test Completed")

async def test_chunking_with_embeddings():
    """Test chunking with embedding generation and storage."""
    
    logger.info("\n🔗 Testing Chunking with Embedding Generation")
    
    try:
        # Initialize components
        vault_path = r"D:\Nomade Milionario"
        filesystem_client = FilesystemVaultClient(vault_path)
        
        # Use advanced chunking configuration
        processor = ContentProcessor(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            max_chunk_size=512,
            chunk_overlap=128
        )
        
        embedding_service = EmbeddingService(
            model_name='sentence-transformers/all-MiniLM-L6-v2'
        )
        
        chroma_service = ChromaService(
            persist_directory="./test_advanced_chroma_db",
            collection_name="advanced_chunking_test",
            embedding_model="all-MiniLM-L6-v2"
        )
        
        # Get a sample file
        files = await filesystem_client.list_vault_files()
        if not files:
            logger.warning("No files found for embedding test")
            return
            
        test_file = files[0]['path']
        logger.info(f"Processing file: {test_file}")
        
        # Get file content and chunk it
        file_data = await filesystem_client.get_file_content(test_file)
        chunks = processor.chunk_content(file_data['content'], file_data['metadata'], test_file)
        
        logger.info(f"Generated {len(chunks)} chunks with advanced chunking")
        
        # Generate embeddings
        texts = [chunk['content'] for chunk in chunks]
        embeddings = embedding_service.batch_generate_embeddings(texts)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Store in ChromaDB
        chroma_service.store_embeddings(chunks, embeddings)
        
        logger.info("✅ Successfully stored chunks with advanced chunking in ChromaDB")
        
        # Test search
        search_results = chroma_service.search_similar("test query", n_results=3)
        logger.info(f"Search returned {len(search_results)} results")
        
        for i, result in enumerate(search_results):
            logger.info(f"  Result {i+1}: {result['similarity_score']:.3f} similarity")
            logger.info(f"    Heading: {result['metadata']['heading']}")
            logger.info(f"    Tokens: {result['metadata']['chunk_token_count']}")
        
    except Exception as e:
        logger.error(f"Error in embedding test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_advanced_chunking())
    asyncio.run(test_chunking_with_embeddings())
