#!/usr/bin/env python3
"""
Startup Sync Service for Initial Vault Synchronization
Compares filesystem state with ChromaDB to catch changes while service was down
"""

import asyncio
import logging
from typing import Dict, Any, List, Set, Tuple
from pathlib import Path
from datetime import datetime

from ..ingestion.filesystem_client import FilesystemVaultClient
from ..vector.chroma_service import ChromaService

logger = logging.getLogger(__name__)

class StartupSyncService:
    """Service for synchronizing vault state on startup"""
    
    def __init__(self, 
                 vault_path: str,
                 chroma_service: ChromaService):
        """
        Initialize the startup sync service.
        Args:
            vault_path (str): Path to the Obsidian vault
            chroma_service (ChromaService): ChromaDB service instance
        """
        self.vault_path = vault_path
        self.chroma_service = chroma_service
        self.filesystem_client = FilesystemVaultClient(vault_path)
        
        logger.info(f"Initialized StartupSyncService for vault: {vault_path}")

    async def perform_startup_sync(self) -> Dict[str, Any]:
        """
        Perform complete startup synchronization.
        Returns:
            Dict[str, Any]: Sync results
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("Starting vault synchronization...")
            
            # Step 1: Get filesystem state
            filesystem_files = await self._get_filesystem_state()
            logger.info(f"Found {len(filesystem_files)} files in filesystem")
            
            # Step 2: Get ChromaDB state
            chromadb_files = await self._get_chromadb_state()
            logger.info(f"Found {len(chromadb_files)} files in ChromaDB")
            
            # Step 3: Compare states and identify differences
            sync_plan = self._create_sync_plan(filesystem_files, chromadb_files)
            
            # Step 4: Execute sync plan
            sync_results = await self._execute_sync_plan(sync_plan)
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            logger.info(f"Startup sync complete: {processing_time:.2f}ms")
            
            return {
                "success": True,
                "processing_time_ms": processing_time,
                "filesystem_files": len(filesystem_files),
                "chromadb_files": len(chromadb_files),
                "sync_plan": sync_plan,
                "sync_results": sync_results
            }
            
        except Exception as e:
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"Error during startup sync: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "processing_time_ms": processing_time
            }

    async def _get_filesystem_state(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of filesystem."""
        try:
            files = await self.filesystem_client.list_vault_files()
            
            filesystem_state = {}
            for file_info in files:
                # Get file metadata
                file_content = await self.filesystem_client.get_file_content(file_info['path'])
                filesystem_state[file_info['path']] = {
                    'path': file_info['path'],
                    'name': file_info['name'],
                    'size': file_content['metadata'].get('file_size', 0),
                    'modified': file_content['metadata'].get('file_modified', 0),
                    'created': file_content['metadata'].get('file_created', 0),
                    'word_count': file_content['metadata'].get('file_word_count', 0),
                    'char_count': file_content['metadata'].get('file_char_count', 0)
                }
            
            return filesystem_state
            
        except Exception as e:
            logger.error(f"Error getting filesystem state: {e}")
            return {}

    async def _get_chromadb_state(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of ChromaDB."""
        try:
            # Get all chunks and group by file path
            results = self.chroma_service.collection.get(
                include=['metadatas']
            )
            
            if not results['metadatas']:
                return {}
            
            chromadb_state = {}
            for metadata in results['metadatas']:
                file_path = metadata.get('path', '')
                if not file_path:
                    continue
                    
                if file_path not in chromadb_state:
                    chromadb_state[file_path] = {
                        'path': file_path,
                        'chunk_count': 0,
                        'file_size': metadata.get('file_size', 0),
                        'file_modified': metadata.get('file_modified', 0),
                        'file_created': metadata.get('file_created', 0),
                        'file_word_count': metadata.get('file_word_count', 0),
                        'file_char_count': metadata.get('file_char_count', 0)
                    }
                
                chromadb_state[file_path]['chunk_count'] += 1
            
            return chromadb_state
            
        except Exception as e:
            logger.error(f"Error getting ChromaDB state: {e}")
            return {}

    def _create_sync_plan(self, 
                         filesystem_files: Dict[str, Dict[str, Any]], 
                         chromadb_files: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create a plan for synchronizing filesystem and ChromaDB."""
        
        filesystem_paths = set(filesystem_files.keys())
        chromadb_paths = set(chromadb_files.keys())
        
        # Files that exist in filesystem but not in ChromaDB (new files)
        new_files = filesystem_paths - chromadb_paths
        
        # Files that exist in ChromaDB but not in filesystem (deleted files)
        deleted_files = chromadb_paths - filesystem_paths
        
        # Files that exist in both but may have changed
        common_files = filesystem_paths & chromadb_paths
        modified_files = []
        
        for file_path in common_files:
            fs_file = filesystem_files[file_path]
            db_file = chromadb_files[file_path]
            
            # Check if file has been modified
            if (fs_file.get('file_modified', 0) != db_file.get('file_modified', 0) or
                fs_file.get('file_size', 0) != db_file.get('file_size', 0) or
                fs_file.get('file_word_count', 0) != db_file.get('file_word_count', 0)):
                modified_files.append(file_path)
        
        sync_plan = {
            'new_files': list(new_files),
            'deleted_files': list(deleted_files),
            'modified_files': modified_files,
            'unchanged_files': list(common_files - set(modified_files)),
            'total_actions': len(new_files) + len(deleted_files) + len(modified_files)
        }
        
        logger.info(f"Sync plan created: {len(new_files)} new, {len(deleted_files)} deleted, {len(modified_files)} modified")
        
        return sync_plan

    async def _execute_sync_plan(self, sync_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the synchronization plan."""
        results = {
            'new_files_processed': 0,
            'deleted_files_processed': 0,
            'modified_files_processed': 0,
            'errors': []
        }
        
        # Process new files
        for file_path in sync_plan['new_files']:
            try:
                # This would typically call the incremental update service
                # For now, we'll just log the action
                logger.info(f"New file detected: {file_path}")
                results['new_files_processed'] += 1
            except Exception as e:
                logger.error(f"Error processing new file {file_path}: {e}")
                results['errors'].append(f"New file {file_path}: {e}")
        
        # Process deleted files
        for file_path in sync_plan['deleted_files']:
            try:
                # Delete chunks for this file
                deleted_count = await self._delete_file_chunks(file_path)
                logger.info(f"Deleted {deleted_count} chunks for deleted file: {file_path}")
                results['deleted_files_processed'] += 1
            except Exception as e:
                logger.error(f"Error processing deleted file {file_path}: {e}")
                results['errors'].append(f"Deleted file {file_path}: {e}")
        
        # Process modified files
        for file_path in sync_plan['modified_files']:
            try:
                # This would typically call the incremental update service
                # For now, we'll just log the action
                logger.info(f"Modified file detected: {file_path}")
                results['modified_files_processed'] += 1
            except Exception as e:
                logger.error(f"Error processing modified file {file_path}: {e}")
                results['errors'].append(f"Modified file {file_path}: {e}")
        
        return results

    async def _delete_file_chunks(self, file_path: str) -> int:
        """Delete all chunks for a file."""
        try:
            results = self.chroma_service.collection.get(
                where={"path": file_path},
                include=['metadatas']
            )
            
            if not results['ids']:
                return 0
                
            self.chroma_service.collection.delete(ids=results['ids'])
            return len(results['ids'])
            
        except Exception as e:
            logger.error(f"Error deleting chunks for {file_path}: {e}")
            return 0

    def get_sync_summary(self) -> Dict[str, Any]:
        """Get a summary of the last sync operation."""
        try:
            collection_stats = self.chroma_service.get_collection_stats()
            return {
                "collection_name": collection_stats.get('collection_name', 'unknown'),
                "total_chunks": collection_stats.get('total_chunks', 0),
                "embedding_model": collection_stats.get('embedding_model', 'unknown'),
                "vault_path": self.vault_path,
                "last_sync": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting sync summary: {e}")
            return {"error": str(e)}
