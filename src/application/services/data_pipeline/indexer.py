"""
Data Pipeline for Obsidian Vault Indexing
Implements hybrid retrieval with vector and graph databases
"""
import asyncio
import os
import hashlib
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import networkx as nx
import structlog

from config.environment import config

logger = structlog.get_logger()

class ObsidianVaultIndexer:
    """Indexes Obsidian vault content for hybrid retrieval"""
    
    def __init__(self, vault_path: str, vector_db_path: str, graph_db_path: str):
        self.vault_path = Path(vault_path)
        self.vector_db_path = vector_db_path
        self.graph_db_path = graph_db_path
        
        # Initialize vector database
        self.chroma_client = chromadb.PersistentClient(
            path=vector_db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="obsidian_notes",
            metadata={"description": "Obsidian vault notes and chunks"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize graph database
        self.graph = nx.DiGraph()
        self.init_graph_db()
    
    def init_graph_db(self):
        """Initialize SQLite graph database"""
        conn = sqlite3.connect(self.graph_db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                path TEXT,
                heading TEXT,
                content_hash TEXT,
                last_modified TIMESTAMP,
                node_type TEXT DEFAULT 'note'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                target_id TEXT,
                edge_type TEXT,
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES nodes (id),
                FOREIGN KEY (target_id) REFERENCES nodes (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_metadata (
                node_id TEXT,
                key TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES nodes (id),
                PRIMARY KEY (node_id, key)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown content"""
        if not content.startswith('---'):
            return {}
        
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}
            
            frontmatter_text = parts[1].strip()
            # Simple YAML parsing (in production, use PyYAML)
            frontmatter = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"\'')
            
            return frontmatter
        except Exception as e:
            logger.warning("frontmatter_extraction_error", error=str(e))
            return {}
    
    def extract_links(self, content: str) -> List[str]:
        """Extract Obsidian-style links from content"""
        import re
        
        # Extract [[link]] patterns
        link_pattern = r'\[\[([^\]]+)\]\]'
        links = re.findall(link_pattern, content)
        
        # Extract #tag patterns
        tag_pattern = r'#([a-zA-Z0-9_-]+)'
        tags = re.findall(tag_pattern, content)
        
        return links + [f"#{tag}" for tag in tags]
    
    def chunk_content(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Chunk content by headings and size"""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_heading = "Untitled"
        chunk_size = 0
        max_chunk_size = 1000  # tokens
        
        for line in lines:
            if line.startswith('#'):
                # Save previous chunk if it exists
                if current_chunk and chunk_size > 0:
                    chunk_content = '\n'.join(current_chunk)
                    chunk_id = f"{path}::{current_heading}::{hashlib.md5(chunk_content.encode()).hexdigest()[:8]}"
                    
                    chunks.append({
                        "id": chunk_id,
                        "content": chunk_content,
                        "path": path,
                        "heading": current_heading,
                        "chunk_size": chunk_size
                    })
                
                # Start new chunk
                current_heading = line.lstrip('#').strip()
                current_chunk = [line]
                chunk_size = len(line.split())
            else:
                current_chunk.append(line)
                chunk_size += len(line.split())
                
                # Split if chunk gets too large
                if chunk_size > max_chunk_size and current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    chunk_id = f"{path}::{current_heading}::{hashlib.md5(chunk_content.encode()).hexdigest()[:8]}"
                    
                    chunks.append({
                        "id": chunk_id,
                        "content": chunk_content,
                        "path": path,
                        "heading": current_heading,
                        "chunk_size": chunk_size
                    })
                    
                    current_chunk = []
                    chunk_size = 0
        
        # Add final chunk
        if current_chunk and chunk_size > 0:
            chunk_content = '\n'.join(current_chunk)
            chunk_id = f"{path}::{current_heading}::{hashlib.md5(chunk_content.encode()).hexdigest()[:8]}"
            
            chunks.append({
                "id": chunk_id,
                "content": chunk_content,
                "path": path,
                "heading": current_heading,
                "chunk_size": chunk_size
            })
        
        return chunks
    
    async def index_file(self, file_path: Path) -> Dict[str, Any]:
        """Index a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get relative path
            rel_path = str(file_path.relative_to(self.vault_path))
            
            # Extract metadata
            frontmatter = self.extract_frontmatter(content)
            links = self.extract_links(content)
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Create node for graph database
            node_id = f"note::{rel_path}"
            
            # Store in graph database
            conn = sqlite3.connect(self.graph_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO nodes (id, path, heading, content_hash, last_modified, node_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                node_id,
                rel_path,
                frontmatter.get('title', 'Untitled'),
                content_hash,
                datetime.now().isoformat(),
                'note'
            ))
            
            # Store metadata
            for key, value in frontmatter.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO node_metadata (node_id, key, value)
                    VALUES (?, ?, ?)
                """, (node_id, key, str(value)))
            
            conn.commit()
            conn.close()
            
            # Chunk content for vector database
            chunks = self.chunk_content(content, rel_path)
            
            # Process chunks
            documents = []
            embeddings = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                # Generate embedding
                embedding = self.embedding_model.encode(chunk["content"]).tolist()
                
                documents.append(chunk["content"])
                embeddings.append(embedding)
                metadatas.append({
                    "path": chunk["path"],
                    "heading": chunk["heading"],
                    "chunk_id": chunk["id"],
                    "chunk_size": chunk["chunk_size"],
                    "frontmatter": json.dumps(frontmatter),
                    "links": json.dumps(links)
                })
                ids.append(chunk["id"])
            
            # Add to vector database
            if documents:
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            
            # Update graph with links
            self.update_graph_links(node_id, links)
            
            logger.info(
                "file_indexed",
                path=rel_path,
                chunks=len(chunks),
                links=len(links),
                content_length=len(content)
            )
            
            return {
                "path": rel_path,
                "chunks": len(chunks),
                "links": len(links),
                "content_length": len(content),
                "frontmatter_keys": list(frontmatter.keys())
            }
            
        except Exception as e:
            logger.error("file_indexing_error", path=str(file_path), error=str(e))
            return {"path": str(file_path), "error": str(e)}
    
    def update_graph_links(self, source_node_id: str, links: List[str]):
        """Update graph database with link relationships"""
        conn = sqlite3.connect(self.graph_db_path)
        cursor = conn.cursor()
        
        for link in links:
            # Clean link (remove # for tags)
            clean_link = link.lstrip('#')
            
            # Try to find target node
            cursor.execute("""
                SELECT id FROM nodes 
                WHERE path LIKE ? OR heading LIKE ?
            """, (f"%{clean_link}%", f"%{clean_link}%"))
            
            target_nodes = cursor.fetchall()
            
            for (target_id,) in target_nodes:
                if target_id != source_node_id:
                    edge_id = f"{source_node_id}->{target_id}"
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO edges (id, source_id, target_id, edge_type, weight)
                        VALUES (?, ?, ?, ?, ?)
                    """, (edge_id, source_node_id, target_id, "link", 1.0))
        
        conn.commit()
        conn.close()
    
    async def index_vault(self) -> Dict[str, Any]:
        """Index entire vault"""
        logger.info("starting_vault_indexing", vault_path=str(self.vault_path))
        
        # Find all markdown files
        md_files = list(self.vault_path.rglob("*.md"))
        
        results = {
            "total_files": len(md_files),
            "indexed_files": 0,
            "errors": 0,
            "total_chunks": 0,
            "total_links": 0
        }
        
        for file_path in md_files:
            result = await self.index_file(file_path)
            
            if "error" in result:
                results["errors"] += 1
            else:
                results["indexed_files"] += 1
                results["total_chunks"] += result.get("chunks", 0)
                results["total_links"] += result.get("links", 0)
        
        # Update collection metadata
        self.collection.modify(
            metadata={"last_indexed": datetime.now().isoformat()}
        )
        
        logger.info("vault_indexing_completed", **results)
        return results
    
    def search_vector(self, query: str, n_results: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filters
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error("vector_search_error", query=query, error=str(e))
            return []
    
    def search_graph(self, node_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Search using graph relationships"""
        try:
            conn = sqlite3.connect(self.graph_db_path)
            cursor = conn.cursor()
            
            # Find connected nodes
            cursor.execute("""
                WITH RECURSIVE connected_nodes AS (
                    SELECT target_id as node_id, 1 as depth
                    FROM edges 
                    WHERE source_id = ?
                    
                    UNION ALL
                    
                    SELECT e.target_id, cn.depth + 1
                    FROM edges e
                    JOIN connected_nodes cn ON e.source_id = cn.node_id
                    WHERE cn.depth < ?
                )
                SELECT DISTINCT n.id, n.path, n.heading, n.node_type
                FROM connected_nodes cn
                JOIN nodes n ON cn.node_id = n.id
                ORDER BY cn.depth, n.heading
            """, (node_id, max_depth))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "path": row[1],
                    "heading": row[2],
                    "node_type": row[3]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error("graph_search_error", node_id=node_id, error=str(e))
            return []
    
    def hybrid_search(self, query: str, n_results: int = 10, graph_depth: int = 2) -> Dict[str, Any]:
        """Perform hybrid search combining vector and graph methods"""
        # Vector search
        vector_results = self.search_vector(query, n_results)
        
        # Graph search (if we have a specific node)
        graph_results = []
        if vector_results:
            # Use the top vector result for graph expansion
            top_result = vector_results[0]
            top_node_id = top_result['metadata'].get('chunk_id', '').split('::')[0]
            if top_node_id:
                graph_results = self.search_graph(top_node_id, graph_depth)
        
        # Combine and rank results
        combined_results = {
            "vector_results": vector_results,
            "graph_results": graph_results,
            "query": query,
            "total_vector_results": len(vector_results),
            "total_graph_results": len(graph_results)
        }
        
        return combined_results

async def main():
    """Main function for running the indexer"""
    indexer = ObsidianVaultIndexer(
        vault_path=config.OBSIDIAN_VAULT_PATH,
        vector_db_path=config.VECTOR_DB_PATH,
        graph_db_path=config.GRAPH_DB_PATH
    )
    
    # Index the vault
    results = await indexer.index_vault()
    
    print("Indexing Results:")
    print(json.dumps(results, indent=2))
    
    # Example search
    search_results = indexer.hybrid_search("daily notes", n_results=5)
    print("\nSearch Results:")
    print(json.dumps(search_results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
