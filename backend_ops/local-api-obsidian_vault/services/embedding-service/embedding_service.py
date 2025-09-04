#!/usr/bin/env python3
"""
Advanced Embedding Service for Obsidian Vault RAG System
Supports multiple embedding models and advanced chunking strategies
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import hashlib

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken
import markdown
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-small-en-v1.5')
MAX_CHUNK_SIZE = int(os.getenv('MAX_CHUNK_SIZE', '512'))
OVERLAP_SIZE = int(os.getenv('OVERLAP_SIZE', '50'))
PORT = int(os.getenv('PORT', 8000))

# FastAPI app
app = FastAPI(title="Advanced Embedding Service", version="1.0.0")

# Global model cache
embedding_models = {}

class EmbeddingRequest(BaseModel):
    text: str
    model: Optional[str] = MODEL_NAME
    chunking_strategy: Optional[str] = "markdown_aware"
    include_metadata: Optional[bool] = True

class BatchEmbeddingRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = MODEL_NAME
    chunking_strategy: Optional[str] = "markdown_aware"
    include_metadata: Optional[bool] = True

class ChunkingRequest(BaseModel):
    content: str
    strategy: str = "markdown_aware"
    max_tokens: int = MAX_CHUNK_SIZE
    overlap: int = OVERLAP_SIZE

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    chunks: List[Dict[str, Any]]
    metadata: Dict[str, Any]

def load_embedding_model(model_name: str):
    """Load and cache embedding model"""
    if model_name not in embedding_models:
        logger.info(f"Loading embedding model: {model_name}")
        try:
            embedding_models[model_name] = SentenceTransformer(model_name)
            logger.info(f"Successfully loaded model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
    
    return embedding_models[model_name]

def markdown_aware_chunking(content: str, max_tokens: int = MAX_CHUNK_SIZE, overlap: int = OVERLAP_SIZE) -> List[Dict[str, Any]]:
    """
    Advanced Markdown-aware chunking that preserves structure and context
    """
    chunks = []
    current_chunk = ""
    current_header = ""
    current_section = ""
    in_code_block = False
    code_block_language = ""
    chunk_metadata = {
        "headers": [],
        "links": [],
        "tags": [],
        "code_blocks": [],
        "lists": [],
        "tables": []
    }
    
    # Initialize tokenizer
    encoding = tiktoken.get_encoding("cl100k_base")
    
    lines = content.split('\n')
    line_number = 0
    
    for line in lines:
        line_number += 1
        line_stripped = line.strip()
        
        # Track headers for context preservation
        if line_stripped.startswith('#'):
            header_level = len(line_stripped) - len(line_stripped.lstrip('#'))
            header_text = line_stripped.lstrip('# ').strip()
            current_header = header_text
            chunk_metadata["headers"].append({
                "level": header_level,
                "text": header_text,
                "line": line_number
            })
        
        # Handle code blocks specially
        if line_stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_language = line_stripped[3:].strip()
                chunk_metadata["code_blocks"].append({
                    "language": code_block_language,
                    "start_line": line_number
                })
            else:
                in_code_block = False
                if chunk_metadata["code_blocks"]:
                    chunk_metadata["code_blocks"][-1]["end_line"] = line_number
        
        # Extract links and tags
        if '[[' in line and ']]' in line:
            links = re.findall(r'\[\[([^\]]+)\]\]', line)
            chunk_metadata["links"].extend(links)
        
        if '#' in line:
            tags = re.findall(r'#(\w+)', line)
            chunk_metadata["tags"].extend(tags)
        
        # Handle tables
        if '|' in line and line.count('|') >= 2:
            chunk_metadata["tables"].append(line_number)
        
        # Handle lists
        if line_stripped.startswith(('-', '*', '+')) or re.match(r'^\d+\.', line_stripped):
            chunk_metadata["lists"].append(line_number)
        
        # Check if we need to create a new chunk
        current_chunk_with_line = current_chunk + line + '\n'
        token_count = len(encoding.encode(current_chunk_with_line))
        
        if token_count > max_tokens and not in_code_block:
            # Create chunk with metadata
            if current_chunk.strip():
                chunk_data = {
                    "content": current_chunk.strip(),
                    "metadata": {
                        "header": current_header,
                        "section": current_section,
                        "line_start": line_number - len(current_chunk.split('\n')) + 1,
                        "line_end": line_number - 1,
                        "token_count": len(encoding.encode(current_chunk)),
                        "chunk_id": hashlib.md5(current_chunk.encode()).hexdigest()[:8],
                        **chunk_metadata
                    }
                }
                chunks.append(chunk_data)
            
            # Start new chunk with overlap
            overlap_text = ""
            if overlap > 0 and current_chunk:
                overlap_lines = current_chunk.split('\n')[-overlap:]
                overlap_text = '\n'.join(overlap_lines) + '\n'
            
            current_chunk = overlap_text + line + '\n'
            chunk_metadata = {
                "headers": [h for h in chunk_metadata["headers"] if h["line"] >= line_number - overlap],
                "links": [],
                "tags": [],
                "code_blocks": [],
                "lists": [],
                "tables": []
            }
        else:
            current_chunk = current_chunk_with_line
    
    # Add final chunk
    if current_chunk.strip():
        chunk_data = {
            "content": current_chunk.strip(),
            "metadata": {
                "header": current_header,
                "section": current_section,
                "line_start": line_number - len(current_chunk.split('\n')) + 1,
                "line_end": line_number,
                "token_count": len(encoding.encode(current_chunk)),
                "chunk_id": hashlib.md5(current_chunk.encode()).hexdigest()[:8],
                **chunk_metadata
            }
        }
        chunks.append(chunk_data)
    
    return chunks

def semantic_chunking(content: str, max_tokens: int = MAX_CHUNK_SIZE) -> List[Dict[str, Any]]:
    """
    Semantic chunking based on sentence similarity
    """
    # Split into sentences
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return []
    
    # Load a small model for sentence similarity
    model = load_embedding_model('all-MiniLM-L6-v2')
    sentence_embeddings = model.encode(sentences)
    
    # Calculate similarities between consecutive sentences
    similarities = []
    for i in range(len(sentence_embeddings) - 1):
        sim = cosine_similarity([sentence_embeddings[i]], [sentence_embeddings[i + 1]])[0][0]
        similarities.append(sim)
    
    # Find break points where similarity drops significantly
    break_points = [0]
    threshold = np.mean(similarities) - np.std(similarities)
    
    for i, sim in enumerate(similarities):
        if sim < threshold:
            break_points.append(i + 1)
    
    break_points.append(len(sentences))
    
    # Create chunks
    chunks = []
    encoding = tiktoken.get_encoding("cl100k_base")
    
    for i in range(len(break_points) - 1):
        start = break_points[i]
        end = break_points[i + 1]
        chunk_sentences = sentences[start:end]
        chunk_content = '. '.join(chunk_sentences) + '.'
        
        if len(encoding.encode(chunk_content)) <= max_tokens:
            chunk_data = {
                "content": chunk_content,
                "metadata": {
                    "chunk_type": "semantic",
                    "sentence_start": start,
                    "sentence_end": end,
                    "token_count": len(encoding.encode(chunk_content)),
                    "chunk_id": hashlib.md5(chunk_content.encode()).hexdigest()[:8],
                    "similarity_score": similarities[start:end-1] if start < end-1 else [1.0]
                }
            }
            chunks.append(chunk_data)
    
    return chunks

def hierarchical_chunking(content: str, max_tokens: int = MAX_CHUNK_SIZE) -> List[Dict[str, Any]]:
    """
    Hierarchical chunking that preserves document structure
    """
    chunks = []
    encoding = tiktoken.get_encoding("cl100k_base")
    
    # Parse markdown structure
    md = markdown.Markdown(extensions=['toc', 'tables', 'fenced_code'])
    html = md.convert(content)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract hierarchical structure
    current_section = ""
    current_subsection = ""
    current_chunk = ""
    chunk_metadata = {
        "hierarchy": [],
        "structure": "hierarchical"
    }
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'blockquote']):
        element_text = element.get_text().strip()
        
        if element.name.startswith('h'):
            level = int(element.name[1])
            if level <= 2:
                current_section = element_text
            else:
                current_subsection = element_text
            
            chunk_metadata["hierarchy"].append({
                "level": level,
                "text": element_text,
                "type": "header"
            })
        
        # Check if adding this element would exceed token limit
        test_chunk = current_chunk + element_text + '\n\n'
        if len(encoding.encode(test_chunk)) > max_tokens and current_chunk:
            # Save current chunk
            chunk_data = {
                "content": current_chunk.strip(),
                "metadata": {
                    "section": current_section,
                    "subsection": current_subsection,
                    "token_count": len(encoding.encode(current_chunk)),
                    "chunk_id": hashlib.md5(current_chunk.encode()).hexdigest()[:8],
                    **chunk_metadata
                }
            }
            chunks.append(chunk_data)
            
            # Start new chunk
            current_chunk = element_text + '\n\n'
        else:
            current_chunk = test_chunk
    
    # Add final chunk
    if current_chunk.strip():
        chunk_data = {
            "content": current_chunk.strip(),
            "metadata": {
                "section": current_section,
                "subsection": current_subsection,
                "token_count": len(encoding.encode(current_chunk)),
                "chunk_id": hashlib.md5(current_chunk.encode()).hexdigest()[:8],
                **chunk_metadata
            }
        }
        chunks.append(chunk_data)
    
    return chunks

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": list(embedding_models.keys()),
        "service": "advanced-embedding-service"
    }

@app.post("/chunk")
async def chunk_text(request: ChunkingRequest):
    """Chunk text using specified strategy"""
    try:
        if request.strategy == "markdown_aware":
            chunks = markdown_aware_chunking(request.content, request.max_tokens, request.overlap)
        elif request.strategy == "semantic":
            chunks = semantic_chunking(request.content, request.max_tokens)
        elif request.strategy == "hierarchical":
            chunks = hierarchical_chunking(request.content, request.max_tokens)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown chunking strategy: {request.strategy}")
        
        return {
            "chunks": chunks,
            "total_chunks": len(chunks),
            "strategy": request.strategy,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Chunking error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chunking failed: {str(e)}")

@app.post("/embed")
async def generate_embedding(request: EmbeddingRequest):
    """Generate embedding for a single text"""
    try:
        model = load_embedding_model(request.model)
        
        # Chunk the text if needed
        if request.chunking_strategy:
            if request.chunking_strategy == "markdown_aware":
                chunks = markdown_aware_chunking(request.text)
            elif request.chunking_strategy == "semantic":
                chunks = semantic_chunking(request.text)
            elif request.chunking_strategy == "hierarchical":
                chunks = hierarchical_chunking(request.text)
            else:
                chunks = [{"content": request.text, "metadata": {}}]
        else:
            chunks = [{"content": request.text, "metadata": {}}]
        
        # Generate embeddings for each chunk
        embeddings = []
        for chunk in chunks:
            embedding = model.encode(chunk["content"])
            embeddings.append(embedding.tolist())
        
        return EmbeddingResponse(
            embeddings=embeddings,
            chunks=chunks,
            metadata={
                "model": request.model,
                "chunking_strategy": request.chunking_strategy,
                "total_chunks": len(chunks),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

@app.post("/embed/batch")
async def generate_batch_embeddings(request: BatchEmbeddingRequest):
    """Generate embeddings for multiple texts"""
    try:
        model = load_embedding_model(request.model)
        
        all_embeddings = []
        all_chunks = []
        
        for text in request.texts:
            # Chunk the text
            if request.chunking_strategy:
                if request.chunking_strategy == "markdown_aware":
                    chunks = markdown_aware_chunking(text)
                elif request.chunking_strategy == "semantic":
                    chunks = semantic_chunking(text)
                elif request.chunking_strategy == "hierarchical":
                    chunks = hierarchical_chunking(text)
                else:
                    chunks = [{"content": text, "metadata": {}}]
            else:
                chunks = [{"content": text, "metadata": {}}]
            
            # Generate embeddings for each chunk
            for chunk in chunks:
                embedding = model.encode(chunk["content"])
                all_embeddings.append(embedding.tolist())
                all_chunks.append(chunk)
        
        return EmbeddingResponse(
            embeddings=all_embeddings,
            chunks=all_chunks,
            metadata={
                "model": request.model,
                "chunking_strategy": request.chunking_strategy,
                "total_texts": len(request.texts),
                "total_chunks": len(all_chunks),
                "embedding_dimension": len(all_embeddings[0]) if all_embeddings else 0,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        logger.error(f"Batch embedding error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch embedding failed: {str(e)}")

@app.get("/models")
async def list_models():
    """List available embedding models"""
    return {
        "loaded_models": list(embedding_models.keys()),
        "default_model": MODEL_NAME,
        "available_strategies": ["markdown_aware", "semantic", "hierarchical"],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info(f"Starting Advanced Embedding Service on port {PORT}")
    logger.info(f"Default model: {MODEL_NAME}")
    logger.info(f"Max chunk size: {MAX_CHUNK_SIZE} tokens")
    logger.info(f"Overlap size: {OVERLAP_SIZE} tokens")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)
