"""
Configuration settings for the Flyde documentation scraper.
"""
import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Flyde Docs Scraper"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database
    database_url: str = Field(default="sqlite:///./data/flyde_docs.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Scraping Configuration
    base_url: str = "https://flyde.dev"
    docs_url: str = "https://flyde.dev/docs"
    github_url: str = "https://github.com/flydelabs/flyde"
    
    # Scraping Settings
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    request_delay: float = Field(default=1.0, env="REQUEST_DELAY")
    timeout: int = Field(default=30, env="TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # Rate Limiting
    requests_per_minute: int = Field(default=60, env="REQUESTS_PER_MINUTE")
    
    # User Agents
    user_agents: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
    
    # Scrapfly Configuration
    scrapfly_api_key: Optional[str] = Field(default=None, env="SCRAPFLY_API_KEY")
    scrapfly_account: Optional[str] = Field(default=None, env="SCRAPFLY_ACCOUNT")
    
    # Sentry Configuration
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    
    # MCP Configuration
    mcp_servers: Dict[str, str] = {
        "context7": "http://localhost:3000",
        "playwright": "http://localhost:3001",
        "sentry": "http://localhost:3002"
    }
    
    # Data Storage
    data_dir: str = Field(default="./data", env="DATA_DIR")
    cache_dir: str = Field(default="./data/cache", env="CACHE_DIR")
    logs_dir: str = Field(default="./logs", env="LOGS_DIR")
    
    # Content Types to Scrape
    content_types: List[str] = [
        "text/html",
        "application/json",
        "text/markdown",
        "text/plain"
    ]
    
    # File Extensions to Include
    file_extensions: List[str] = [
        ".html", ".htm", ".md", ".txt", ".json", ".xml", ".yaml", ".yml"
    ]
    
    # Exclude Patterns
    exclude_patterns: List[str] = [
        "/api/",
        "/admin/",
        "/private/",
        "*.pdf",
        "*.zip",
        "*.tar.gz"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(settings.cache_dir, exist_ok=True)
os.makedirs(settings.logs_dir, exist_ok=True)