"""
Environment configuration for LangGraph + Obsidian Vault Integration
"""
import os
from typing import Optional

class EnvironmentConfig:
    """Centralized environment configuration"""
    
    # Obsidian Local REST API Configuration
    OBSIDIAN_API_KEY: str = os.getenv("OBSIDIAN_API_KEY", "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")
    OBSIDIAN_HOST: str = os.getenv("OBSIDIAN_HOST", "127.0.0.1")
    OBSIDIAN_PORT: int = int(os.getenv("OBSIDIAN_PORT", "27123"))
    OBSIDIAN_PROTOCOL: str = os.getenv("OBSIDIAN_PROTOCOL", "http")
    OBSIDIAN_VERIFY_SSL: bool = os.getenv("OBSIDIAN_VERIFY_SSL", "false").lower() == "true"
    OBSIDIAN_TIMEOUT: int = int(os.getenv("OBSIDIAN_TIMEOUT", "10"))
    
    # LangSmith Configuration
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "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")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "obsidian-agents")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "$env:OPENAI_API_KEY")
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "$env:GOOGLE_API_KEY")
    
    # LangGraph Configuration
    LANGGRAPH_HOST: str = os.getenv("LANGGRAPH_HOST", "0.0.0.0")
    LANGGRAPH_PORT: int = int(os.getenv("LANGGRAPH_PORT", "2024"))
    LANGGRAPH_STUDIO_PORT: int = int(os.getenv("LANGGRAPH_STUDIO_PORT", "2025"))
    LANGGRAPH_STUDIO_HOST: str = os.getenv("LANGGRAPH_STUDIO_HOST", "0.0.0.0")
    
    # API Gateway Configuration
    API_GATEWAY_HOST: str = os.getenv("API_GATEWAY_HOST", "0.0.0.0")
    API_GATEWAY_PORT: int = int(os.getenv("API_GATEWAY_PORT", "8000"))
    GATEWAY_URL: str = os.getenv("GATEWAY_URL", "http://localhost:8000")
    
    # Database Configuration
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "/data/vector")
    GRAPH_DB_PATH: str = os.getenv("GRAPH_DB_PATH", "/data/graph.db")
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "/data/checkpoints.db")
    
    # Vault Configuration
    OBSIDIAN_VAULT_PATH: str = os.getenv("OBSIDIAN_VAULT_PATH", "D:/Nomade Milionario")
    VAULT_NAME: str = os.getenv("VAULT_NAME", "Nomade Milionario")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Development Configuration
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def obsidian_base_url(self) -> str:
        """Get the base URL for Obsidian Local REST API"""
        return f"{self.OBSIDIAN_PROTOCOL}://{self.OBSIDIAN_HOST}:{self.OBSIDIAN_PORT}"
    
    @property
    def langgraph_server_url(self) -> str:
        """Get the LangGraph server URL"""
        return f"http://{self.LANGGRAPH_HOST}:{self.LANGGRAPH_PORT}"
    
    @property
    def langgraph_studio_url(self) -> str:
        """Get the LangGraph Studio URL"""
        return f"http://{self.LANGGRAPH_STUDIO_HOST}:{self.LANGGRAPH_STUDIO_PORT}"
    
    @property
    def api_gateway_url(self) -> str:
        """Get the API Gateway URL"""
        return f"http://{self.API_GATEWAY_HOST}:{self.API_GATEWAY_PORT}"

# Global configuration instance
config = EnvironmentConfig()
