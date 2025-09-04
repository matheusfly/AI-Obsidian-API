#!/usr/bin/env python3
"""
Advanced Indexing Service for Obsidian Vault RAG System
Handles complex file processing, multiple chunking strategies, and optimized indexing
"""

import os
import json
import logging
import asyncio
import aiohttp
import aiofiles
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from qdrant_client import QdrantClient
from qdrant_client.http import models
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OBSIDIAN_API_URL = os.getenv('OBSIDIAN_API_URL', 'http://host.docker.internal:27123')
OBSIDIAN_API_KEY = os.getenv('OBSIDIAN_API_KEY', 'b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70')
VECTOR_DB_URL = os.getenv('VECTOR_DB_URL', 'http://qdrant:6333')
EMBEDDING_API_URL = os.getenv('EMBEDDING_API_URL', 'http://embedding-service:8000')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'obsidian_vault_advanced')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
PORT = int(os.getenv('PORT', 8000))

# FastAPI app
app = FastAPI(title="Advanced Indexing Service", version="1.0.0")

# Global clients
qdrant_client = None
embedding_session = None

class IndexingRequest(BaseModel):
    vault_path: Optional[str] = None
    file_patterns: Optional[List[str]] = ["*.md", "*.txt"]
    chunking_strategy: Optional[str] = "markdown_aware"
    force_reindex: Optional[bool] = False
    batch_size: Optional[int] = BATCH_SIZE

class IndexingStatus(BaseModel):
    status: str
    progress: float
    total_files: int
    processed_files: int
    indexed_chunks: int
    errors: List[str]
    start_time: str
    last_update: str

# Global indexing status
indexing_status = {
    "status": "idle",
    "progress": 0.0,
    "total_files": 0,
    "processed_files": 0,
    "indexed_chunks": 0,
    "errors": [],
    "start_time": "",
    "last_update": ""
}

async def initialize_clients():
    """Initialize Qdrant and embedding service clients"""
    global qdrant_client, embedding_session
    
    try:
        # Initialize Qdrant client
        qdrant_client = QdrantClient(url=VECTOR_DB_URL)
        logger.info(f"Connected to Qdrant at {VECTOR_DB_URL}")
        
        # Initialize embedding service session
        embedding_session = aiohttp.ClientSession()
        logger.info(f"Initialized embedding service session for {EMBEDDING_API_URL}")
        
        # Create collection if it doesn't exist
        await create_collection()
        
    except Exception as e:
        logger.error(f"Failed to initialize clients: {str(e)}")
        raise

async def create_collection():
    """Create Qdrant collection with optimized settings"""
    try:
        # Check if collection exists
        collections = qdrant_client.get_collections()
        collection_exists = any(col.name == COLLECTION_NAME for col in collections.collections)
        
        if not collection_exists:
            logger.info(f"Creating collection: {COLLECTION_NAME}")
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=384,  # BGE-small embedding dimension
                    distance=models.Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfig(
                    indexing_threshold=20000,
                    memmap_threshold=10000,
                    vacuum_min_vector_number=1000
                ),
                hnsw_config=models.HnswConfig(
                    m=24,
                    ef_construct=128,
                    ef=128
                ),
                wal_config=models.WalConfig(
                    wal_capacity_mb=1024,
                    wal_segments_after_flush=2
                )
            )
            logger.info(f"Collection {COLLECTION_NAME} created successfully")
        else:
            logger.info(f"Collection {COLLECTION_NAME} already exists")
            
    except Exception as e:
        logger.error(f"Failed to create collection: {str(e)}")
        raise

async def get_all_files_from_vault() -> List[Dict[str, Any]]:
    """Get all files from Obsidian vault via REST API"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
            
            # Get all notes
            async with session.get(f"{OBSIDIAN_API_URL}/notes", headers=headers) as response:
                if response.status == 200:
                    notes = await response.json()
                    logger.info(f"Retrieved {len(notes)} notes from vault")
                    return notes
                else:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"Failed to get notes: {error_text}")
                    
    except Exception as e:
        logger.error(f"Failed to get files from vault: {str(e)}")
        raise

async def get_file_content(file_path: str) -> Optional[str]:
    """Get content of a specific file"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
            params = {"path": file_path}
            
            async with session.get(f"{OBSIDIAN_API_URL}/note", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", "")
                else:
                    logger.warning(f"Failed to get content for {file_path}: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Error getting content for {file_path}: {str(e)}")
        return None

async def generate_embeddings(texts: List[str], chunking_strategy: str = "markdown_aware") -> List[Dict[str, Any]]:
    """Generate embeddings for multiple texts"""
    try:
        async with embedding_session.post(
            f"{EMBEDDING_API_URL}/embed/batch",
            json={
                "texts": texts,
                "chunking_strategy": chunking_strategy,
                "include_metadata": True
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_text = await response.text()
                raise HTTPException(status_code=response.status, detail=f"Embedding failed: {error_text}")
                
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        raise

async def index_file_chunks(file_path: str, content: str, chunking_strategy: str = "markdown_aware") -> int:
    """Index chunks for a single file"""
    try:
        # Generate embeddings for the file content
        embedding_data = await generate_embeddings([content], chunking_strategy)
        
        if not embedding_data.get("embeddings") or not embedding_data.get("chunks"):
            logger.warning(f"No embeddings generated for {file_path}")
            return 0
        
        # Prepare points for Qdrant
        points = []
        for i, (embedding, chunk) in enumerate(zip(embedding_data["embeddings"], embedding_data["chunks"])):
            # Create unique point ID
            point_id = hashlib.md5(f"{file_path}_{i}_{chunk['metadata'].get('chunk_id', '')}".encode()).hexdigest()
            
            # Prepare metadata
            metadata = {
                "file_path": file_path,
                "file_name": Path(file_path).name,
                "chunk_index": i,
                "total_chunks": len(embedding_data["chunks"]),
                "chunking_strategy": chunking_strategy,
                "indexed_at": datetime.now().isoformat(),
                **chunk["metadata"]
            }
            
            # Create point
            point = models.PointStruct(
                id=point_id,
                vector=embedding,
                payload=metadata
            )
            points.append(point)
        
        # Insert points into Qdrant
        if points:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            logger.info(f"Indexed {len(points)} chunks for {file_path}")
            return len(points)
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to index file {file_path}: {str(e)}")
        indexing_status["errors"].append(f"{file_path}: {str(e)}")
        return 0

async def process_files_batch(files: List[Dict[str, Any]], chunking_strategy: str, batch_size: int):
    """Process a batch of files concurrently"""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async def process_single_file(file_info):
        async with semaphore:
            file_path = file_info["path"]
            
            # Get file content
            content = await get_file_content(file_path)
            if not content:
                logger.warning(f"No content retrieved for {file_path}")
                return 0
            
            # Index file chunks
            chunks_indexed = await index_file_chunks(file_path, content, chunking_strategy)
            
            # Update status
            indexing_status["processed_files"] += 1
            indexing_status["indexed_chunks"] += chunks_indexed
            indexing_status["progress"] = (indexing_status["processed_files"] / indexing_status["total_files"]) * 100
            indexing_status["last_update"] = datetime.now().isoformat()
            
            return chunks_indexed
    
    # Process files in batches
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        tasks = [process_single_file(file_info) for file_info in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Small delay between batches to prevent overwhelming the services
        await asyncio.sleep(0.1)

async def full_vault_indexing(request: IndexingRequest):
    """Perform full vault indexing"""
    try:
        # Update status
        indexing_status.update({
            "status": "running",
            "progress": 0.0,
            "total_files": 0,
            "processed_files": 0,
            "indexed_chunks": 0,
            "errors": [],
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat()
        })
        
        # Get all files from vault
        files = await get_all_files_from_vault()
        indexing_status["total_files"] = len(files)
        
        if not files:
            indexing_status["status"] = "completed"
            return
        
        logger.info(f"Starting indexing of {len(files)} files")
        
        # Process files in batches
        await process_files_batch(files, request.chunking_strategy, request.batch_size)
        
        # Mark as completed
        indexing_status["status"] = "completed"
        indexing_status["last_update"] = datetime.now().isoformat()
        
        logger.info(f"Indexing completed. Processed {indexing_status['processed_files']} files, indexed {indexing_status['indexed_chunks']} chunks")
        
    except Exception as e:
        logger.error(f"Indexing failed: {str(e)}")
        indexing_status["status"] = "failed"
        indexing_status["errors"].append(f"Indexing failed: {str(e)}")
        indexing_status["last_update"] = datetime.now().isoformat()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await initialize_clients()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if embedding_session:
        await embedding_session.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "advanced-indexing-service",
        "qdrant_connected": qdrant_client is not None,
        "embedding_service_connected": embedding_session is not None
    }

@app.post("/index")
async def start_indexing(request: IndexingRequest, background_tasks: BackgroundTasks):
    """Start indexing process"""
    if indexing_status["status"] == "running":
        raise HTTPException(status_code=409, detail="Indexing is already in progress")
    
    # Start indexing in background
    background_tasks.add_task(full_vault_indexing, request)
    
    return {
        "message": "Indexing started",
        "request": request.dict(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_indexing_status():
    """Get current indexing status"""
    return indexing_status

@app.get("/stats")
async def get_indexing_stats():
    """Get indexing statistics"""
    try:
        # Get collection info
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        
        return {
            "collection_name": COLLECTION_NAME,
            "total_points": collection_info.points_count,
            "vector_size": collection_info.config.params.vectors.size,
            "distance_metric": collection_info.config.params.vectors.distance,
            "indexing_status": indexing_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.delete("/index")
async def clear_index():
    """Clear the entire index"""
    try:
        qdrant_client.delete_collection(COLLECTION_NAME)
        await create_collection()
        
        return {
            "message": "Index cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {str(e)}")

@app.post("/reindex")
async def reindex_vault(request: IndexingRequest, background_tasks: BackgroundTasks):
    """Clear and reindex the entire vault"""
    if indexing_status["status"] == "running":
        raise HTTPException(status_code=409, detail="Indexing is already in progress")
    
    # Clear index first
    try:
        qdrant_client.delete_collection(COLLECTION_NAME)
        await create_collection()
    except Exception as e:
        logger.error(f"Failed to clear index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {str(e)}")
    
    # Start reindexing
    background_tasks.add_task(full_vault_indexing, request)
    
    return {
        "message": "Reindexing started",
        "request": request.dict(),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info(f"Starting Advanced Indexing Service on port {PORT}")
    logger.info(f"Obsidian API URL: {OBSIDIAN_API_URL}")
    logger.info(f"Vector DB URL: {VECTOR_DB_URL}")
    logger.info(f"Embedding API URL: {EMBEDDING_API_URL}")
    logger.info(f"Collection Name: {COLLECTION_NAME}")
    logger.info(f"Batch Size: {BATCH_SIZE}")
    logger.info(f"Max Concurrent Requests: {MAX_CONCURRENT_REQUESTS}")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
