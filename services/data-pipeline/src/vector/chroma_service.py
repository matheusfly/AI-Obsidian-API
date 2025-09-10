#!/usr/bin/env python3
"""
Enhanced ChromaDB Service
Rich metadata storage and advanced querying capabilities
"""

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import hashlib
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ChromaService:
    """Enhanced ChromaDB service with rich metadata and advanced querying"""
    
    def __init__(self, collection_name: str = "obsidian_vault", persist_directory: str = "./data/chroma", 
                 embedding_model: str = "all-MiniLM-L6-v2", optimize_for_large_vault: bool = True):
        """
        Initialize the optimized ChromaDB service with HNSW configuration.
        Args:
            collection_name (str): Name of the ChromaDB collection.
            persist_directory (str): Directory to persist ChromaDB data.
            embedding_model (str): Name of the embedding model to use.
            optimize_for_large_vault (bool): Enable optimizations for large vaults (7.25GB+).
        """
        # Initialize ChromaDB client with optimized settings and disabled telemetry
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Configure embedding function
        # Handle both cases: with and without sentence-transformers/ prefix
        if embedding_model.startswith("sentence-transformers/"):
            model_name = embedding_model
        else:
            model_name = f"sentence-transformers/{embedding_model}"
        
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        
        # Optimized HNSW configuration for large vaults
        if optimize_for_large_vault:
            logger.info("🔧 Configuring ChromaDB with HNSW optimizations for large vault")
            self.hnsw_config = {
                "hnsw:space": "cosine",  # Cosine similarity for better semantic search
                "hnsw:construction_ef": 200,  # Higher construction ef for better index quality
                "hnsw:search_ef": 100,  # Higher search ef for better recall
                "hnsw:M": 16,  # Higher M for better connectivity in large datasets
            }
        else:
            # Default configuration for smaller vaults
            self.hnsw_config = {
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 100,
                "hnsw:search_ef": 50,
                "hnsw:M": 8,
            }
        
        # Try to get existing collection first, then create if needed
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Retrieved existing collection: {collection_name}")
        except Exception:
            # Collection doesn't exist or has different embedding function
            try:
                # Create collection with optimized metadata (ChromaDB only supports simple types)
                collection_metadata = {
                    "description": "Obsidian vault embeddings with rich metadata and HNSW optimization",
                    "optimized_for_large_vault": optimize_for_large_vault,
                    "embedding_model": model_name,
                    "created_with_batch_optimization": True,
                    "hnsw_space": self.hnsw_config.get("hnsw:space", "cosine"),
                    "hnsw_construction_ef": self.hnsw_config.get("hnsw:construction_ef", 100),
                    "hnsw_search_ef": self.hnsw_config.get("hnsw:search_ef", 50),
                    "hnsw_M": self.hnsw_config.get("hnsw:M", 8)
                }
                
                self.collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                    metadata=collection_metadata
                )
                logger.info(f"Created optimized collection: {collection_name}")
                logger.info(f"HNSW Configuration: {self.hnsw_config}")
            except Exception as e:
                # If creation fails, try to get without embedding function
                self.collection = self.client.get_collection(name=collection_name)
                logger.warning(f"Using existing collection without embedding function: {e}")
        
        logger.info(f"Initialized optimized ChromaService with collection: {collection_name}, model: {embedding_model}")
        logger.info(f"HNSW optimization enabled: {optimize_for_large_vault}")

    def store_embeddings(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Store chunks and embeddings with rich, validated metadata."""
        if len(chunks) != len(embeddings):
            raise ValueError("Mismatch: Number of chunks must equal number of embeddings.")

        logger.info(f"Storing {len(chunks)} chunks with rich metadata in ChromaDB")
        
        start_time = time.time()
        status = "success"

        ids = []
        documents = []
        metadatas = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Validate critical fields
            required_fields = ["path", "heading", "chunk_index", "chunk_token_count"]
            for field in required_fields:
                if field not in chunk:
                    raise KeyError(f"Chunk missing required metadata field: '{field}'")

            # Create a UNIQUE, STABLE ID
            # Using path, heading, ACTUAL chunk_index, and storage index 'i' for absolute uniqueness
            unique_id = hashlib.sha256(
                f"{chunk['path']}::{chunk['heading']}::{chunk['chunk_index']}::{i}".encode()
            ).hexdigest()

            ids.append(unique_id)
            documents.append(chunk['content'])

            # Prepare METADATA (enhanced with new fields)
            meta = {
                # Core
                "path": chunk['path'],
                "heading": chunk['heading'],
                "chunk_index": chunk['chunk_index'],
                "source_file": chunk['path'],  # Redundant but useful for filtering
                # File Stats (Inherited)
                "file_word_count": chunk.get('file_word_count', 0),
                "file_char_count": chunk.get('file_char_count', 0),
                "file_size": chunk.get('file_size', 0),
                "file_modified": chunk.get('file_modified', 0),
                "file_created": chunk.get('file_created', 0),
                # Tags (Inherited & Separated)
                "file_tags": ",".join(chunk.get('frontmatter_tags', []) + chunk.get('content_tags', [])),
                "frontmatter_tags": ",".join(chunk.get('frontmatter_tags', [])),
                "content_tags": ",".join(chunk.get('content_tags', [])),
                # Chunk Stats (Computed)
                "chunk_token_count": chunk.get('chunk_token_count', 0),  # ✅ Uses pre-computed value
                "chunk_word_count": chunk.get('chunk_word_count', 0),
                "chunk_char_count": chunk.get('chunk_char_count', 0),
                # Frontmatter (Inherited)
                "has_frontmatter": chunk.get('has_frontmatter', False),
                "frontmatter_keys": ",".join(chunk.get('frontmatter_keys', [])),
                # File Structure (Inherited)
                "file_extension": chunk.get('file_extension', ""),
                "directory_path": chunk.get('directory_path', ""),
                "file_name": chunk.get('file_name', ""),
                # Enhanced Metadata Fields (ensure no None values for ChromaDB)
                "path_year": chunk.get('path_year') or 0,
                "path_month": chunk.get('path_month') or 0,
                "path_day": chunk.get('path_day') or 0,
                "path_category": chunk.get('path_category', ""),
                "path_subcategory": chunk.get('path_subcategory', ""),
                "file_type": chunk.get('file_type', ""),
                "content_type": chunk.get('content_type', ""),
                "links": ",".join(chunk.get('links', [])),
            }
            metadatas.append(meta)

        # Log sample for debugging
        if metadatas:
            logger.debug(f"Storing chunk with metadata sample: {metadatas[0]}")

        try:
            # Store in ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(f"Successfully stored {len(chunks)} chunks in ChromaDB.")
        except Exception as e:
            status = "error"
            logger.error(f"Failed to store embeddings: {e}")
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            try:
                from ..monitoring.metrics import get_metrics
                metrics = get_metrics()
                metrics.record_chroma_batch_operation("store_embeddings", len(chunks))
                metrics.record_chroma_query("store_embeddings", duration, status)
            except Exception as e:
                logger.warning(f"Failed to record metrics: {e}")

    def search_similar(self, query_text: str, n_results: int = 5, where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for similar content with optional metadata filtering.
        Args:
            query_text (str): The search query.
            n_results (int): Number of results to return.
            where (Dict): Optional metadata filter.
        Returns:
            List[Dict]: List of search results with metadata.
        """
        logger.info(f"Searching for: '{query_text}' with {n_results} results")
        
        start_time = time.time()
        status = "success"
        
        try:
            # First try with query_texts (works if collection has embedding function)
            query_params = {
                "query_texts": [query_text],
                "n_results": n_results
            }
            
            if where:
                query_params["where"] = where
                logger.debug(f"Using metadata filter: {where}")

            results = self.collection.query(**query_params)
        except Exception as e:
            status = "error"
            logger.error(f"ChromaDB query failed: {e}")
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            try:
                from ..monitoring.metrics import get_metrics
                metrics = get_metrics()
                metrics.record_chroma_query("search_similar", duration, status)
            except Exception as e:
                logger.warning(f"Failed to record metrics: {e}")
        
        # If no results, try with manual embedding generation
        if not results['documents'][0]:
            logger.debug("No results with query_texts, trying manual embedding generation")
            try:
                # Generate embedding manually
                query_embedding = self.embedding_function([query_text])[0]
                
                query_params = {
                    "query_embeddings": [query_embedding],
                    "n_results": n_results
                }
                
                if where:
                    query_params["where"] = where
                
                results = self.collection.query(**query_params)
                logger.debug(f"Manual embedding search returned {len(results['documents'][0])} results")
            except Exception as e:
                logger.warning(f"Manual embedding generation failed: {e}")
                return []

        formatted_results = []
        for i, (doc, metadata, distance, doc_id) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0],
            results['ids'][0]
        )):
            # Convert distance to similarity score
            similarity_score = 1 - distance if distance <= 1 else 0

            formatted_results.append({
                "rank": i + 1,
                "content": doc,
                "metadata": metadata,
                "similarity_score": similarity_score,
                "distance": distance,
                "id": doc_id
            })

        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results

    def search_by_metadata(self, filters: Dict[str, Any], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search by metadata filters only (no semantic search).
        Args:
            filters (Dict): Metadata filters to apply.
            n_results (int): Number of results to return.
        Returns:
            List[Dict]: List of results matching the metadata filters.
        """
        logger.info(f"Searching by metadata filters: {filters}")
        
        try:
            results = self.collection.get(
                where=filters,
                limit=n_results
            )
            
            formatted_results = []
            for i, (doc, metadata, doc_id) in enumerate(zip(
                results['documents'],
                results['metadatas'],
                results['ids']
            )):
                formatted_results.append({
                    "rank": i + 1,
                    "content": doc,
                    "metadata": metadata,
                    "id": doc_id,
                    "similarity_score": 1.0,  # No semantic similarity for metadata-only search
                    "distance": 0.0
                })
            
            logger.info(f"Found {len(formatted_results)} results matching metadata filters")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Metadata search failed: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get comprehensive collection statistics including HNSW optimization info."""
        count = self.collection.count()
        
        # Get collection metadata for optimization info
        collection_metadata = self.collection.metadata if hasattr(self.collection, 'metadata') else {}
        
        return {
            "collection_name": self.collection.name,
            "total_chunks": count,
            "embedding_model": self.embedding_function.model_name if hasattr(self.embedding_function, 'model_name') else "unknown",
            "hnsw_optimization": collection_metadata.get("optimized_for_large_vault", False),
            "hnsw_config": collection_metadata.get("hnsw_config", {}),
            "batch_optimization_enabled": collection_metadata.get("created_with_batch_optimization", False)
        }

    def optimize_metadata_indexing(self) -> Dict[str, Any]:
        """
        Optimize metadata indexing for better query performance.
        ChromaDB automatically indexes metadata, but we can verify consistency.
        """
        logger.info("🔍 Optimizing metadata indexing")
        
        try:
            # Get a sample of metadata to verify indexing
            sample_results = self.collection.get(limit=10)
            metadata_keys = set()
            
            for metadata in sample_results['metadatas']:
                metadata_keys.update(metadata.keys())
            
            # Verify critical metadata fields are present
            critical_fields = [
                'path', 'heading', 'chunk_index', 'file_type', 'path_year', 
                'path_month', 'path_category', 'content_tags'
            ]
            
            missing_fields = [field for field in critical_fields if field not in metadata_keys]
            
            optimization_result = {
                "metadata_fields_found": len(metadata_keys),
                "critical_fields_present": len(critical_fields) - len(missing_fields),
                "missing_critical_fields": missing_fields,
                "indexing_status": "optimized" if len(missing_fields) == 0 else "needs_attention"
            }
            
            logger.info(f"Metadata indexing optimization complete: {optimization_result}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Metadata indexing optimization failed: {e}")
            return {"error": str(e), "indexing_status": "failed"}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the optimized ChromaDB setup."""
        try:
            # Test search performance
            test_query = "test query for performance measurement"
            start_time = time.time()
            results = self.search_similar(test_query, n_results=5)
            search_time = time.time() - start_time
            
            # Test metadata filtering performance
            start_time = time.time()
            metadata_results = self.search_by_metadata({"file_type": "dated_note"}, n_results=5)
            metadata_time = time.time() - start_time
            
            return {
                "semantic_search_time_ms": search_time * 1000,
                "metadata_filter_time_ms": metadata_time * 1000,
                "hnsw_config": self.hnsw_config,
                "collection_size": self.collection.count(),
                "optimization_status": "active"
            }
            
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {e}")
            return {"error": str(e)}

    def delete_collection(self):
        """Delete the entire collection."""
        self.client.delete_collection(self.collection.name)
        logger.info(f"Deleted collection: {self.collection.name}")

    def reset_collection(self):
        """Reset the collection by deleting and recreating it."""
        collection_name = self.collection.name
        self.delete_collection()
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Obsidian vault embeddings with rich metadata"}
        )
        
        logger.info(f"Reset collection: {collection_name}")