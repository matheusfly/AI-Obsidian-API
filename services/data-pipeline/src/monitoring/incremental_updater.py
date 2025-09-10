#!/usr/bin/env python3
"""
Incremental Update Service for Single-File Processing
Handles atomic updates to prevent duplicates and maintain consistency
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..ingestion.filesystem_client import FilesystemVaultClient
from ..processing.content_processor import ContentProcessor
from ..embeddings.embedding_service import EmbeddingService
from ..vector.chroma_service import ChromaService

logger = logging.getLogger(__name__)

class IncrementalUpdateService:
    """Service for processing individual file updates with atomic operations"""
    
    def __init__(self, 
                 vault_path: str,
                 chroma_service: ChromaService,
                 embedding_service: EmbeddingService,
                 content_processor: ContentProcessor):
        """
        Initialize the incremental update service.
        Args:
            vault_path (str): Path to the Obsidian vault
            chroma_service (ChromaService): ChromaDB service instance
            embedding_service (EmbeddingService): Embedding service instance
            content_processor (ContentProcessor): Content processor instance
        """
        self.vault_path = vault_path
        self.chroma_service = chroma_service
        self.embedding_service = embedding_service
        self.content_processor = content_processor
        self.filesystem_client = FilesystemVaultClient(vault_path)
        
        logger.info(f"Initialized IncrementalUpdateService for vault: {vault_path}")

    async def process_file_update(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single file update atomically.
        Args:
            file_path (str): Relative path to the file
        Returns:
            Dict[str, Any]: Processing results
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Processing file update: {file_path}")
            
            # Step 1: Delete existing chunks for this file (atomic operation)
            deleted_count = await self._delete_existing_chunks(file_path)
            logger.info(f"Deleted {deleted_count} existing chunks for: {file_path}")
            
            # Step 2: Read and process the updated file
            file_content = await self.filesystem_client.get_file_content(file_path)
            
            # Step 3: Generate chunks
            chunks = self.content_processor.chunk_content(
                content=file_content['content'],
                file_metadata=file_content['metadata'],
                path=file_path
            )
            
            if not chunks:
                logger.warning(f"No chunks generated for file: {file_path}")
                return {
                    "success": True,
                    "file_path": file_path,
                    "chunks_processed": 0,
                    "chunks_deleted": deleted_count,
                    "processing_time_ms": (asyncio.get_event_loop().time() - start_time) * 1000
                }
            
            # Step 4: Generate embeddings
            texts = [chunk['content'] for chunk in chunks]
            embeddings = self.embedding_service.batch_generate_embeddings(texts)
            
            # Step 5: Store new chunks atomically
            self.chroma_service.store_embeddings(chunks, embeddings)
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            logger.info(f"Successfully processed file: {file_path} ({len(chunks)} chunks, {processing_time:.2f}ms)")
            
            return {
                "success": True,
                "file_path": file_path,
                "chunks_processed": len(chunks),
                "chunks_deleted": deleted_count,
                "processing_time_ms": processing_time,
                "file_size": file_content['metadata'].get('file_size', 0),
                "file_word_count": file_content['metadata'].get('file_word_count', 0)
            }
            
        except Exception as e:
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"Error processing file {file_path}: {e}")
            
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e),
                "processing_time_ms": processing_time
            }

    async def process_file_deletion(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file deletion by removing all its chunks.
        Args:
            file_path (str): Relative path to the deleted file
        Returns:
            Dict[str, Any]: Deletion results
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Processing file deletion: {file_path}")
            
            # Delete all chunks for this file
            deleted_count = await self._delete_existing_chunks(file_path)
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            logger.info(f"Successfully deleted {deleted_count} chunks for file: {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "chunks_deleted": deleted_count,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"Error deleting file {file_path}: {e}")
            
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e),
                "processing_time_ms": processing_time
            }

    async def _delete_existing_chunks(self, file_path: str) -> int:
        """
        Delete all existing chunks for a file from ChromaDB.
        Args:
            file_path (str): Relative path to the file
        Returns:
            int: Number of chunks deleted
        """
        try:
            # Query to find all chunks for this file
            results = self.chroma_service.collection.get(
                where={"path": file_path},
                include=['metadatas']
            )
            
            if not results['ids']:
                return 0
                
            # Delete the chunks
            self.chroma_service.collection.delete(ids=results['ids'])
            
            return len(results['ids'])
            
        except Exception as e:
            logger.error(f"Error deleting chunks for {file_path}: {e}")
            return 0

    async def batch_process_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process multiple file updates in batch.
        Args:
            file_paths (List[str]): List of relative file paths
        Returns:
            Dict[str, Any]: Batch processing results
        """
        start_time = asyncio.get_event_loop().time()
        results = []
        
        logger.info(f"Starting batch processing of {len(file_paths)} files")
        
        # Process files concurrently (but limit concurrency to avoid overwhelming the system)
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent file processes
        
        async def process_with_semaphore(file_path: str):
            async with semaphore:
                return await self.process_file_update(file_path)
        
        # Process all files
        tasks = [process_with_semaphore(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
        failed = len(results) - successful
        total_chunks = sum(r.get('chunks_processed', 0) for r in results if isinstance(r, dict))
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        logger.info(f"Batch processing complete: {successful} successful, {failed} failed, {total_chunks} total chunks")
        
        return {
            "success": failed == 0,
            "files_processed": len(file_paths),
            "successful": successful,
            "failed": failed,
            "total_chunks": total_chunks,
            "processing_time_ms": processing_time,
            "results": results
        }

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        try:
            collection_stats = self.chroma_service.get_collection_stats()
            return {
                "collection_name": collection_stats.get('collection_name', 'unknown'),
                "total_chunks": collection_stats.get('total_chunks', 0),
                "embedding_model": collection_stats.get('embedding_model', 'unknown'),
                "vault_path": self.vault_path
            }
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {"error": str(e)}
