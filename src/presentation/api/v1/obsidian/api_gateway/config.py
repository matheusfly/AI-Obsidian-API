from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Obsidian API configuration
    obsidian_api_base: str = "http://localhost:27123"
    obsidian_api_key: Optional[str] = None
    obsidian_vault_path: str = "/vault"
    
    # LangChain configuration
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    
    # Vector database configuration
    chroma_persist_directory: str = "/data/vector"
    
    # Graph database configuration
    graph_db_path: str = "/data/graph.db"
    
    class Config:
        env_file = ".env"

settings = Settings()