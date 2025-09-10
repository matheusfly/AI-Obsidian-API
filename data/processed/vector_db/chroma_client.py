import chromadb
from chromadb.config import Settings
from api_gateway.config import settings
from typing import List, Dict, Any, Optional

class VectorDatabase:
    def __init__(self):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.chroma_persist_directory
        ))
        self.collection = self.client.get_or_create_collection("obsidian_notes")
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], 
                     metadatas: List[Dict[str, Any]], ids: List[str]):
        """Add documents to the vector database"""
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, query_embeddings: Optional[List[List[float]]] = None,
              query_texts: Optional[List[str]] = None,
              n_results: int = 10,
              where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query the vector database"""
        return self.collection.query(
            query_embeddings=query_embeddings,
            query_texts=query_texts,
            n_results=n_results,
            where=where
        )
    
    def delete(self, ids: List[str]):
        """Delete documents from the vector database"""
        self.collection.delete(ids=ids)