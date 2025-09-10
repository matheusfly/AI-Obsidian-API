#!/usr/bin/env python3
"""
Enhanced Filesystem-First Pipeline
Complete pipeline integrating all enhanced components for robust vault ingestion
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import os

# Import our enhanced components
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.content_processor import ContentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vector.chroma_service import ChromaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedFilesystemPipeline:
    """Complete enhanced filesystem-first pipeline"""
    
    def __init__(self, 
                 vault_path: str = r"D:\Nomade Milionario",
                 gemini_api_key: Optional[str] = None,
                 embedding_model: str = "all-MiniLM-L6-v2",
                 max_chunk_size: int = 512,
                 chunk_overlap: int = 64):
        """
        Initialize the enhanced pipeline.
        Args:
            vault_path (str): Path to the Obsidian vault.
            gemini_api_key (str): Gemini API key for LLM integration.
            embedding_model (str): Embedding model to use.
            max_chunk_size (int): Maximum tokens per chunk.
            chunk_overlap (int): Token overlap between chunks.
        """
        # Initialize components
        self.filesystem_client = FilesystemVaultClient(vault_path)
        self.content_processor = ContentProcessor(
            model_name=f"sentence-transformers/{embedding_model}",
            max_chunk_size=max_chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedding_service = EmbeddingService(
            model_name=f"sentence-transformers/{embedding_model}"
        )
        self.chroma_service = ChromaService(
            collection_name="enhanced_obsidian_vault",
            embedding_model=embedding_model
        )
        
        # Initialize Gemini
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini LLM initialized")
        else:
            self.gemini_model = None
            logger.warning("Gemini API key not provided - LLM features disabled")
        
        logger.info(f"Enhanced pipeline initialized with vault: {vault_path}")

    async def ingest_vault(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Ingest the entire vault with enhanced processing.
        Args:
            limit (int): Optional limit on number of files to process.
        Returns:
            Dict: Ingestion statistics and results.
        """
        logger.info("Starting enhanced vault ingestion")
        
        # Step 1: Discover files
        logger.info("Step 1: Discovering vault files")
        all_files = await self.filesystem_client.list_vault_files()
        
        if limit:
            files_to_process = all_files[:limit]
            logger.info(f"Processing limited set of {len(files_to_process)} files")
        else:
            files_to_process = all_files
            logger.info(f"Processing all {len(files_to_process)} files")
        
        # Step 2: Read file contents
        logger.info("Step 2: Reading file contents")
        file_paths = [f["path"] for f in files_to_process]
        file_contents = await self.filesystem_client.get_multiple_files(file_paths)
        
        # Step 3: Process content into chunks
        logger.info("Step 3: Processing content into intelligent chunks")
        all_chunks = self.content_processor.process_multiple_files(file_contents)
        
        # Step 4: Generate embeddings
        logger.info("Step 4: Generating embeddings")
        chunk_texts = [chunk["content"] for chunk in all_chunks]
        embeddings = self.embedding_service.batch_generate_embeddings(chunk_texts)
        
        # Step 5: Store in ChromaDB
        logger.info("Step 5: Storing embeddings in ChromaDB")
        self.chroma_service.store_embeddings(all_chunks, embeddings)
        
        # Return statistics
        stats = {
            "files_discovered": len(all_files),
            "files_processed": len(file_contents),
            "chunks_created": len(all_chunks),
            "embeddings_generated": len(embeddings),
            "vault_stats": self.filesystem_client.get_vault_stats(),
            "embedding_cache_stats": self.embedding_service.get_cache_stats(),
            "chroma_stats": self.chroma_service.get_collection_stats()
        }
        
        logger.info(f"Ingestion complete: {stats}")
        return stats

    async def query_with_llm(self, query_text: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Query the vault using LLM with enhanced context.
        Args:
            query_text (str): The user's query.
            n_results (int): Number of relevant chunks to retrieve.
        Returns:
            Dict: Query results with LLM response.
        """
        if not self.gemini_model:
            raise ValueError("Gemini LLM not initialized - provide API key")
        
        logger.info(f"Processing LLM query: '{query_text}'")
        
        # Step 1: Search for relevant chunks
        search_results = self.chroma_service.search_similar(query_text, n_results=n_results)
        
        # Step 2: Prepare context
        context_parts = []
        for result in search_results:
            context_parts.append(f"**File: {result['metadata']['path']}**\n**Heading: {result['metadata']['heading']}**\n**Similarity: {result['similarity_score']:.3f}**\n\n{result['content']}\n")
        
        context = "\n".join(context_parts)
        
        # Step 3: Generate LLM response
        prompt = f"""Based on the following context from an Obsidian vault, please answer the user's question comprehensively and accurately.

Context:
{context}

User Question: {query_text}

Please provide a detailed answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so."""

        try:
            response = self.gemini_model.generate_content(prompt)
            llm_response = response.text
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            llm_response = f"Error generating response: {str(e)}"
        
        # Return comprehensive results
        result = {
            "query": query_text,
            "search_results": search_results,
            "context_chunks_used": len(search_results),
            "llm_response": llm_response,
            "average_similarity": sum(r["similarity_score"] for r in search_results) / len(search_results) if search_results else 0
        }
        
        logger.info(f"LLM query completed with {len(search_results)} context chunks")
        return result

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics."""
        return {
            "filesystem_stats": self.filesystem_client.get_vault_stats(),
            "embedding_stats": self.embedding_service.get_cache_stats(),
            "chroma_stats": self.chroma_service.get_collection_stats(),
            "content_processor_config": {
                "model_name": self.content_processor.model_name,
                "max_chunk_size": self.content_processor.max_chunk_size,
                "chunk_overlap": self.content_processor.chunk_overlap
            }
        }

async def main():
    """Test the enhanced pipeline"""
    # Get Gemini API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    # Initialize pipeline
    pipeline = EnhancedFilesystemPipeline(
        vault_path=r"D:\Nomade Milionario",
        gemini_api_key=gemini_api_key,
        embedding_model="all-MiniLM-L6-v2",
        max_chunk_size=512,
        chunk_overlap=64
    )
    
    try:
        # Test ingestion with limited files
        logger.info("Testing enhanced pipeline with limited ingestion")
        stats = await pipeline.ingest_vault(limit=10)
        
        print("\n" + "="*60)
        print("ENHANCED PIPELINE INGESTION RESULTS")
        print("="*60)
        print(f"Files discovered: {stats['files_discovered']}")
        print(f"Files processed: {stats['files_processed']}")
        print(f"Chunks created: {stats['chunks_created']}")
        print(f"Embeddings generated: {stats['embeddings_generated']}")
        print(f"Vault size: {stats['vault_stats']['total_size_mb']} MB")
        
        # Test search
        logger.info("Testing enhanced search")
        search_results = pipeline.chroma_service.search_similar("performance optimization", n_results=3)
        
        print("\n" + "="*60)
        print("ENHANCED SEARCH RESULTS")
        print("="*60)
        for result in search_results:
            print(f"📁 File: {result['metadata']['path']}")
            print(f"📊 Similarity: {result['similarity_score']:.3f}")
            print(f"📏 Distance: {result['distance']:.3f}")
            print(f"🏷️ Heading: {result['metadata']['heading']}")
            print(f"📝 Content: {result['content'][:200]}...")
            print("-" * 40)
        
        # Test LLM integration if API key is available
        if gemini_api_key:
            logger.info("Testing LLM integration")
            llm_result = await pipeline.query_with_llm("What are the key performance optimization strategies?", n_results=3)
            
            print("\n" + "="*60)
            print("LLM QUERY RESULTS")
            print("="*60)
            print(f"Query: {llm_result['query']}")
            print(f"Context chunks used: {llm_result['context_chunks_used']}")
            print(f"Average similarity: {llm_result['average_similarity']:.3f}")
            print(f"LLM Response: {llm_result['llm_response']}")
        else:
            logger.warning("Skipping LLM test - no API key provided")
        
        # Final stats
        final_stats = pipeline.get_pipeline_stats()
        print("\n" + "="*60)
        print("FINAL PIPELINE STATISTICS")
        print("="*60)
        print(f"Total files in vault: {final_stats['filesystem_stats']['total_files']}")
        print(f"Total vault size: {final_stats['filesystem_stats']['total_size_mb']} MB")
        print(f"Chunks in ChromaDB: {final_stats['chroma_stats']['total_chunks']}")
        print(f"Embedding cache size: {final_stats['embedding_stats']['cache_size']}")
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
