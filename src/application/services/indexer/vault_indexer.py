import os
import glob
import hashlib
from typing import List, Dict, Any
from vector_db.chroma_client import VectorDatabase

class VaultIndexer:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.vector_db = VectorDatabase()
    
    def chunk_markdown(self, content: str, path: str) -> List[Dict[str, Any]]:
        """Chunk markdown content by headings"""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_heading = "Untitled"
        
        for line in lines:
            if line.startswith('#'):
                # Save previous chunk if it exists
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    chunk_id = f"{path}::{current_heading}"
                    chunks.append({
                        "id": chunk_id,
                        "content": chunk_content,
                        "path": path,
                        "heading": current_heading
                    })
                # Start new chunk with heading
                current_heading = line.lstrip('#').strip()
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk_id = f"{path}::{current_heading}"
            chunks.append({
                "id": chunk_id,
                "content": chunk_content,
                "path": path,
                "heading": current_heading
            })
        
        return chunks
    
    def compute_embedding(self, text: str) -> List[float]:
        """Compute embedding for text (simplified)"""
        # In a real implementation, this would use an actual embedding model
        # For example, OpenAI embeddings or a local model like SentenceTransformers
        # Simplified hash-based "embedding" for demonstration
        hash_bytes = hashlib.md5(text.encode()).digest()
        # Convert bytes to float values in range [0, 100]
        return [b % 100 for b in hash_bytes][:128]
    
    def index_vault(self) -> int:
        """Index all markdown files in the vault"""
        # Find all markdown files
        md_files = glob.glob(os.path.join(self.vault_path, "**/*.md"), recursive=True)
        
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        for file_path in md_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get relative path
                rel_path = os.path.relpath(file_path, self.vault_path)
                
                # Chunk the content
                chunks = self.chunk_markdown(content, rel_path)
                
                # Process each chunk
                for chunk in chunks:
                    # Compute embedding
                    embedding = self.compute_embedding(chunk["content"])
                    
                    # Add to collections
                    documents.append(chunk["content"])
                    embeddings.append(embedding)
                    metadatas.append({
                        "path": chunk["path"],
                        "heading": chunk["heading"]
                    })
                    ids.append(chunk["id"])
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        # Add to vector database
        if documents:
            self.vector_db.add_documents(documents, embeddings, metadatas, ids)
        
        return len(documents)