"""
Configuration management for Data Pipeline Service
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Obsidian API Configuration
    obsidian_api_key: str = Field(..., env="OBSIDIAN_API_KEY")
    obsidian_host: str = Field(default="127.0.0.1", env="OBSIDIAN_HOST")
    obsidian_port: int = Field(default=27123, env="OBSIDIAN_PORT")
    obsidian_vault_path: str = Field(default="/vault", env="OBSIDIAN_VAULT_PATH")
    
    # Gemini API Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model_name: str = Field(default="gemini-pro", env="GEMINI_MODEL_NAME")
    
    # ChromaDB Configuration
    chroma_url: str = Field(default="http://chroma:8000", env="CHROMA_URL")
    chroma_collection_name: str = Field(default="obsidian_vault", env="CHROMA_COLLECTION_NAME")
    chroma_persist_directory: str = Field(default="./data/chroma", env="CHROMA_PERSIST_DIRECTORY")
    
    # Embedding Configuration
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    embedding_batch_size: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    embedding_cache_size: int = Field(default=10000, env="EMBEDDING_CACHE_SIZE")
    
    # Processing Configuration
    chunk_size: int = Field(default=512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    max_document_size: int = Field(default=10485760, env="MAX_DOCUMENT_SIZE")  # 10MB
    processing_batch_size: int = Field(default=100, env="PROCESSING_BATCH_SIZE")
    
    # Search Configuration
    default_search_results: int = Field(default=5, env="DEFAULT_SEARCH_RESULTS")
    max_search_results: int = Field(default=20, env="MAX_SEARCH_RESULTS")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    
    # Caching Configuration
    cache_ttl_embeddings: int = Field(default=3600, env="CACHE_TTL_EMBEDDINGS")  # 1 hour
    cache_ttl_search: int = Field(default=1800, env="CACHE_TTL_SEARCH")  # 30 minutes
    cache_ttl_content: int = Field(default=7200, env="CACHE_TTL_CONTENT")  # 2 hours
    
    # Monitoring Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # Service Configuration
    service_name: str = Field(default="data-pipeline", env="SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    service_port: int = Field(default=8003, env="SERVICE_PORT")
    service_host: str = Field(default="0.0.0.0", env="SERVICE_HOST")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
