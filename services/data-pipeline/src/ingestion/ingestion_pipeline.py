#!/usr/bin/env python3
"""
Optimized Asynchronous Batch Embedding Pipeline
High-performance ingestion with configurable batch processing and ChromaDB optimization
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import time

# Import our services
from .filesystem_client import FilesystemVaultClient
from ..processing.hybrid_content_processor import HybridContentProcessor
from ..embeddings.embedding_service import EmbeddingService
from ..vector.chroma_service import ChromaService

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """
    Optimized ingestion pipeline with asynchronous batch processing.
    
    Key Features:
    - Configurable batch_size for optimal GPU/CPU utilization
    - Sequential batch processing to prevent memory overflow
    - Enhanced error handling per batch
    - ChromaDB optimization with HNSW parameters
    - Metadata indexing optimization
    """
    
    def __init__(self, 
                 filesystem_client: FilesystemVaultClient,
                 content_processor: HybridContentProcessor,
                 embedding_service: EmbeddingService,
                 chroma_service: ChromaService,
                 batch_size: int = 50):
        """
        Initialize the optimized ingestion pipeline.
        
        Args:
            filesystem_client: FilesystemVaultClient instance
            content_processor: HybridContentProcessor instance
            embedding_service: EmbeddingService instance
            chroma_service: ChromaService instance
            batch_size: Number of chunks per batch (default: 50)
        """
        self.filesystem_client = filesystem_client
        self.content_processor = content_processor
        self.embedding_service = embedding_service
        self.chroma_service = chroma_service
        self.batch_size = batch_size
        
        logger.info(f"Initialized IngestionPipeline with batch_size: {batch_size}")

    async def ingest_all_files(self) -> Dict[str, Any]:
        """
        Optimized ingestion with asynchronous batch processing.
        
        Process Flow:
        1. Gather all chunks from all files
        2. Process chunks in configurable batches
        3. Generate embeddings per batch
        4. Store embeddings per batch
        5. Return comprehensive statistics
        """
        start_time = time.time()
        logger.info("🚀 Starting optimized batch ingestion process")
        
        # Step 1: Gather all files
        logger.info("Step 1: Discovering vault files")
        files = await self.filesystem_client.list_vault_files()
        logger.info(f"Discovered {len(files)} files in vault")
        
        # Step 2: Gather all chunks with enriched metadata
        logger.info("Step 2: Processing files into chunks")
        all_chunks = []
        all_file_metadata = {}
        processed_files = 0
        skipped_files = 0
        
        for file_info in files:
            if file_info.get('type') == 'file' and file_info['path'].endswith('.md'):
                try:
                    # Get file content with enhanced metadata
                    file_data = await self.filesystem_client.get_file_content(file_info['path'])
                    
                    # Process into chunks using hybrid processor
                    chunks = self.content_processor.chunk_content(
                        content=file_data['content'],
                        file_metadata=file_data,
                        path=file_info['path']
                    )
                    
                    # Attach file-level metadata to each chunk
                    for chunk in chunks:
                        chunk['file_metadata'] = {
                            'tags': file_data.get('tags', []),
                            'frontmatter': file_data.get('frontmatter', {}),
                            'modified': file_data.get('file_modified'),
                            'created': file_data.get('file_created'),
                            'size': file_data.get('file_size'),
                            'word_count': file_data.get('file_word_count'),
                            'char_count': file_data.get('file_char_count'),
                            # Enhanced metadata
                            'path_year': file_data.get('path_year'),
                            'path_month': file_data.get('path_month'),
                            'path_day': file_data.get('path_day'),
                            'path_category': file_data.get('path_category'),
                            'path_subcategory': file_data.get('path_subcategory'),
                            'file_type': file_data.get('file_type'),
                            'content_type': file_data.get('content_type'),
                            'content_tags': file_data.get('content_tags', []),
                            'links': file_data.get('links', [])
                        }
                    
                    all_chunks.extend(chunks)
                    all_file_metadata[file_info['path']] = file_data
                    processed_files += 1
                    
                    if processed_files % 100 == 0:
                        logger.info(f"Processed {processed_files} files, {len(all_chunks)} chunks so far")
                        
                except Exception as e:
                    logger.error(f"Skipping file {file_info['path']} due to error: {e}")
                    skipped_files += 1
        
        logger.info(f"Chunk processing complete: {processed_files} files processed, {skipped_files} skipped")
        logger.info(f"Total chunks created: {len(all_chunks)}")
        
        # Step 3: Process chunks in optimized batches
        logger.info(f"Step 3: Processing {len(all_chunks)} chunks in batches of {self.batch_size}")
        
        total_batches = (len(all_chunks) + self.batch_size - 1) // self.batch_size
        successful_batches = 0
        failed_batches = 0
        total_embeddings_stored = 0
        
        for i in range(0, len(all_chunks), self.batch_size):
            batch_number = i // self.batch_size + 1
            batch_chunks = all_chunks[i:i + self.batch_size]
            batch_texts = [chunk['content'] for chunk in batch_chunks]
            
            logger.info(f"Processing batch {batch_number}/{total_batches} ({len(batch_chunks)} chunks)")
            
            try:
                # Generate embeddings for this batch
                batch_start_time = time.time()
                batch_embeddings = self.embedding_service.batch_generate_embeddings(batch_texts)
                embedding_time = time.time() - batch_start_time
                
                # Store embeddings for this batch
                storage_start_time = time.time()
                self.chroma_service.store_embeddings(batch_chunks, batch_embeddings)
                storage_time = time.time() - storage_start_time
                
                total_embeddings_stored += len(batch_embeddings)
                successful_batches += 1
                
                logger.info(f"✅ Batch {batch_number} completed: {len(batch_chunks)} chunks, "
                          f"{embedding_time:.2f}s embedding, {storage_time:.2f}s storage")
                
                # Optional: Small delay to prevent overwhelming the system
                if batch_number % 10 == 0:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"❌ Failed to process batch {batch_number} starting at index {i}: {e}")
                failed_batches += 1
                
                # Optionally continue with next batch or halt
                if failed_batches > 5:  # Stop if too many consecutive failures
                    logger.error("Too many batch failures, stopping ingestion")
                    break
        
        # Step 4: Calculate final statistics
        total_time = time.time() - start_time
        
        stats = {
            "ingestion_summary": {
                "total_files_discovered": len(files),
                "files_processed": processed_files,
                "files_skipped": skipped_files,
                "total_chunks_created": len(all_chunks),
                "total_embeddings_stored": total_embeddings_stored,
                "total_batches": total_batches,
                "successful_batches": successful_batches,
                "failed_batches": failed_batches,
                "batch_size": self.batch_size
            },
            "performance_metrics": {
                "total_ingestion_time": total_time,
                "chunks_per_second": len(all_chunks) / total_time if total_time > 0 else 0,
                "embeddings_per_second": total_embeddings_stored / total_time if total_time > 0 else 0,
                "average_batch_time": total_time / total_batches if total_batches > 0 else 0
            },
            "system_stats": {
                "embedding_cache_stats": self.embedding_service.get_cache_stats(),
                "chroma_stats": self.chroma_service.get_collection_stats(),
                "vault_stats": self.filesystem_client.get_vault_stats()
            }
        }
        
        logger.info(f"🎉 Ingestion complete in {total_time:.2f}s: {total_embeddings_stored} embeddings stored")
        logger.info(f"Performance: {stats['performance_metrics']['chunks_per_second']:.1f} chunks/sec, "
                   f"{stats['performance_metrics']['embeddings_per_second']:.1f} embeddings/sec")
        
        return stats

    async def ingest_files_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Ingest a specific batch of files (useful for incremental updates).
        
        Args:
            file_paths: List of file paths to ingest
            
        Returns:
            Dict with ingestion statistics
        """
        logger.info(f"Processing batch of {len(file_paths)} files")
        
        all_chunks = []
        processed_files = 0
        
        for file_path in file_paths:
            try:
                file_data = await self.filesystem_client.get_file_content(file_path)
                chunks = self.content_processor.chunk_content(
                    content=file_data['content'],
                    file_metadata=file_data,
                    path=file_path
                )
                
                # Attach metadata
                for chunk in chunks:
                    chunk['file_metadata'] = file_data
                
                all_chunks.extend(chunks)
                processed_files += 1
                
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {e}")
        
        # Process chunks in batches
        total_embeddings_stored = 0
        for i in range(0, len(all_chunks), self.batch_size):
            batch_chunks = all_chunks[i:i + self.batch_size]
            batch_texts = [chunk['content'] for chunk in batch_chunks]
            
            try:
                batch_embeddings = self.embedding_service.batch_generate_embeddings(batch_texts)
                self.chroma_service.store_embeddings(batch_chunks, batch_embeddings)
                total_embeddings_stored += len(batch_embeddings)
            except Exception as e:
                logger.error(f"Failed to process batch: {e}")
        
        return {
            "files_processed": processed_files,
            "chunks_created": len(all_chunks),
            "embeddings_stored": total_embeddings_stored
        }

    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get current pipeline configuration."""
        return {
            "batch_size": self.batch_size,
            "embedding_model": self.embedding_service.model_name,
            "max_batch_tokens": self.embedding_service.max_batch_tokens,
            "content_processor_type": "HybridContentProcessor",
            "chroma_collection": self.chroma_service.collection.name
        }

    def optimize_batch_size(self, test_chunks: List[str]) -> int:
        """
        Dynamically optimize batch size based on system performance.
        
        Args:
            test_chunks: Sample chunks to test with
            
        Returns:
            Optimal batch size
        """
        logger.info("Testing different batch sizes for optimization")
        
        test_sizes = [25, 50, 100, 200]
        best_size = self.batch_size
        best_time = float('inf')
        
        for size in test_sizes:
            try:
                start_time = time.time()
                test_batch = test_chunks[:size]
                self.embedding_service.batch_generate_embeddings(test_batch)
                test_time = time.time() - start_time
                
                logger.info(f"Batch size {size}: {test_time:.2f}s for {len(test_batch)} chunks")
                
                if test_time < best_time:
                    best_time = test_time
                    best_size = size
                    
            except Exception as e:
                logger.error(f"Failed to test batch size {size}: {e}")
        
        logger.info(f"Optimal batch size: {best_size} (was {self.batch_size})")
        self.batch_size = best_size
        return best_size
