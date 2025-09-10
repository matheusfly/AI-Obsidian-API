#!/usr/bin/env python3
"""
Vault Monitor Service - Main Orchestrator
Coordinates file watching, incremental updates, and startup synchronization
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any, Optional
from pathlib import Path

from .file_watcher import DebouncedFileWatcher
from .incremental_updater import IncrementalUpdateService
from .startup_sync import StartupSyncService
from ..ingestion.filesystem_client import FilesystemVaultClient
from ..processing.content_processor import ContentProcessor
from ..embeddings.embedding_service import EmbeddingService
from ..vector.chroma_service import ChromaService

logger = logging.getLogger(__name__)

class VaultMonitorService:
    """Main service for monitoring and maintaining vault synchronization"""
    
    def __init__(self, 
                 vault_path: str,
                 chroma_db_path: str = "./chroma_db",
                 collection_name: str = "enhanced_semantic_engine",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 debounce_delay: float = 2.0):
        """
        Initialize the vault monitor service.
        Args:
            vault_path (str): Path to the Obsidian vault
            chroma_db_path (str): Path to ChromaDB storage
            collection_name (str): ChromaDB collection name
            embedding_model (str): Embedding model name
            debounce_delay (float): File watcher debounce delay
        """
        self.vault_path = vault_path
        self.is_running = False
        self.startup_complete = False
        
        # Initialize core services
        self.filesystem_client = FilesystemVaultClient(vault_path)
        self.content_processor = ContentProcessor(embedding_model)
        self.embedding_service = EmbeddingService(embedding_model)
        self.chroma_service = ChromaService(
            persist_directory=chroma_db_path,
            collection_name=collection_name,
            embedding_model=embedding_model
        )
        
        # Initialize monitoring services
        self.file_watcher = DebouncedFileWatcher(vault_path, debounce_delay)
        self.incremental_updater = IncrementalUpdateService(
            vault_path, self.chroma_service, self.embedding_service, self.content_processor
        )
        self.startup_sync = StartupSyncService(vault_path, self.chroma_service)
        
        # Set up file watcher callbacks
        self.file_watcher.on_file_modified = self._handle_file_modified
        self.file_watcher.on_file_created = self._handle_file_created
        self.file_watcher.on_file_deleted = self._handle_file_deleted
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "files_deleted": 0,
            "total_chunks_processed": 0,
            "total_processing_time_ms": 0,
            "errors": 0,
            "startup_time_ms": 0
        }
        
        logger.info(f"Initialized VaultMonitorService for vault: {vault_path}")

    async def start(self) -> Dict[str, Any]:
        """Start the vault monitoring service."""
        if self.is_running:
            logger.warning("Vault monitor is already running")
            return {"success": False, "error": "Already running"}
        
        try:
            logger.info("Starting vault monitoring service...")
            start_time = asyncio.get_event_loop().time()
            
            # Step 1: Perform startup synchronization
            logger.info("Performing startup synchronization...")
            sync_result = await self.startup_sync.perform_startup_sync()
            
            if not sync_result.get('success', False):
                logger.error(f"Startup sync failed: {sync_result.get('error', 'Unknown error')}")
                return {"success": False, "error": f"Startup sync failed: {sync_result.get('error')}"}
            
            # Step 2: Start file watcher
            logger.info("Starting file watcher...")
            self.file_watcher.start()
            
            # Step 3: Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            self.is_running = True
            self.startup_complete = True
            
            startup_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self.stats["startup_time_ms"] = startup_time
            
            logger.info(f"Vault monitoring service started successfully ({startup_time:.2f}ms)")
            
            return {
                "success": True,
                "startup_time_ms": startup_time,
                "sync_result": sync_result,
                "file_watcher_status": self.file_watcher.get_status()
            }
            
        except Exception as e:
            logger.error(f"Error starting vault monitor: {e}")
            return {"success": False, "error": str(e)}

    async def stop(self):
        """Stop the vault monitoring service."""
        if not self.is_running:
            return
            
        logger.info("Stopping vault monitoring service...")
        
        # Stop file watcher
        self.file_watcher.stop()
        
        # Wait for any pending processing to complete
        await self.file_watcher.wait_for_quiet_period(timeout=10.0)
        
        self.is_running = False
        logger.info("Vault monitoring service stopped")

    async def _handle_file_modified(self, file_path: str):
        """Handle file modification events."""
        try:
            result = await self.incremental_updater.process_file_update(file_path)
            
            if result.get('success', False):
                self.stats["files_processed"] += 1
                self.stats["total_chunks_processed"] += result.get('chunks_processed', 0)
                self.stats["total_processing_time_ms"] += result.get('processing_time_ms', 0)
                logger.info(f"Successfully processed modified file: {file_path}")
            else:
                self.stats["errors"] += 1
                logger.error(f"Failed to process modified file {file_path}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error handling file modification {file_path}: {e}")

    async def _handle_file_created(self, file_path: str):
        """Handle file creation events."""
        try:
            result = await self.incremental_updater.process_file_update(file_path)
            
            if result.get('success', False):
                self.stats["files_processed"] += 1
                self.stats["total_chunks_processed"] += result.get('chunks_processed', 0)
                self.stats["total_processing_time_ms"] += result.get('processing_time_ms', 0)
                logger.info(f"Successfully processed created file: {file_path}")
            else:
                self.stats["errors"] += 1
                logger.error(f"Failed to process created file {file_path}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error handling file creation {file_path}: {e}")

    async def _handle_file_deleted(self, file_path: str):
        """Handle file deletion events."""
        try:
            result = await self.incremental_updater.process_file_deletion(file_path)
            
            if result.get('success', False):
                self.stats["files_deleted"] += 1
                self.stats["total_processing_time_ms"] += result.get('processing_time_ms', 0)
                logger.info(f"Successfully processed deleted file: {file_path}")
            else:
                self.stats["errors"] += 1
                logger.error(f"Failed to process deleted file {file_path}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error handling file deletion {file_path}: {e}")

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.stop())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the vault monitor."""
        try:
            file_watcher_status = self.file_watcher.get_status()
            processing_stats = self.incremental_updater.get_processing_stats()
            sync_summary = self.startup_sync.get_sync_summary()
            
            return {
                "is_running": self.is_running,
                "startup_complete": self.startup_complete,
                "vault_path": self.vault_path,
                "file_watcher": file_watcher_status,
                "processing_stats": processing_stats,
                "sync_summary": sync_summary,
                "monitor_stats": self.stats.copy()
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {"error": str(e)}

    async def force_sync_file(self, file_path: str) -> Dict[str, Any]:
        """Force synchronization of a specific file."""
        try:
            logger.info(f"Force syncing file: {file_path}")
            result = await self.incremental_updater.process_file_update(file_path)
            
            if result.get('success', False):
                logger.info(f"Successfully force synced file: {file_path}")
            else:
                logger.error(f"Failed to force sync file {file_path}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error force syncing file {file_path}: {e}")
            return {"success": False, "error": str(e)}

    async def batch_sync_files(self, file_paths: list) -> Dict[str, Any]:
        """Batch synchronize multiple files."""
        try:
            logger.info(f"Batch syncing {len(file_paths)} files")
            result = await self.incremental_updater.batch_process_files(file_paths)
            
            if result.get('success', False):
                logger.info(f"Successfully batch synced {result.get('successful', 0)} files")
            else:
                logger.error(f"Batch sync had {result.get('failed', 0)} failures")
            
            return result
            
        except Exception as e:
            logger.error(f"Error batch syncing files: {e}")
            return {"success": False, "error": str(e)}

    async def run_forever(self):
        """Run the vault monitor indefinitely."""
        if not self.is_running:
            await self.start()
        
        try:
            logger.info("Vault monitor running... Press Ctrl+C to stop")
            while self.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            await self.stop()
