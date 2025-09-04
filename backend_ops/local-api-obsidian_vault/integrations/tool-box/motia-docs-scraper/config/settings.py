"""
Motia Documentation Scraper Configuration
Advanced settings with MCP integration and performance optimization
"""

from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with MCP and performance enhancements"""
    
    # Application
    app_name: str = "Motia Documentation Scraper"
    version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8001
    
    # Scraping Configuration
    max_concurrent_requests: int = 20
    request_delay: float = 0.5
    timeout: int = 30
    max_retries: int = 5
    requests_per_minute: int = 120
    user_agent: str = "MotiaDocsScraper/1.0 (Educational Research)"
    
    # Target URLs - Motia
    motia_urls: List[str] = [
        "https://www.motia.dev/docs",
        "https://www.motia.dev/docs/getting-started/quick-start",
        "https://www.motia.dev/docs/concepts/steps/defining-steps",
        "https://www.motia.dev/manifesto",
        "https://github.com/MotiaDev/motia",
        "https://github.com/MotiaDev/motia-examples"
    ]
    
    # Target URLs - ChartDB
    chartdb_urls: List[str] = [
        "https://chartdb.io/",
        "https://www.chartdb.io/?ref=github_readme",
        "https://chartdb.io/templates?ref=github_readme",
        "https://github.com/chartdb/chartdb"
    ]
    
    # Target URLs - JSON Crack
    jsoncrack_urls: List[str] = [
        "https://jsoncrack.com/",
        "https://github.com/AykutSarac/jsoncrack.com"
    ]
    
    # Combined target URLs
    target_urls: List[str] = motia_urls + chartdb_urls + jsoncrack_urls
    
    # Database Configuration
    database_url: str = "postgresql://admin:password@localhost:5433/motia_docs"
    redis_url: str = "redis://localhost:6379/0"
    
    # Yugabyte Specific
    yugabyte_host: str = "localhost"
    yugabyte_port: int = 5433
    yugabyte_db: str = "motia_docs"
    yugabyte_user: str = "admin"
    yugabyte_password: str = "password"
    yugabyte_ssl_mode: str = "prefer"
    
    # MCP Integration
    mcp_enabled: bool = True
    mcp_server_url: str = "http://localhost:3000"
    mcp_api_key: Optional[str] = None
    mcp_timeout: int = 30
    mcp_retry_attempts: int = 3
    
    # Context7 Integration
    context7_enabled: bool = True
    context7_api_key: Optional[str] = None
    context7_endpoint: str = "https://api.context7.com/v1"
    context7_model: str = "gpt-4"
    context7_max_tokens: int = 4000
    
    # Performance Optimization
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    enable_compression: bool = True
    max_content_size: int = 10 * 1024 * 1024  # 10MB
    enable_parallel_processing: bool = True
    max_workers: int = 8
    
    # Monitoring & Logging
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Scraping Engines
    default_scraper: str = "scrapfly"
    enable_playwright: bool = True
    enable_scrapy: bool = True
    enable_selenium: bool = False
    
    # Playwright Configuration
    playwright_headless: bool = True
    playwright_browser: str = "chromium"
    playwright_viewport: Dict[str, int] = {"width": 1920, "height": 1080}
    playwright_timeout: int = 30000
    
    # Scrapfly Configuration
    scrapfly_api_key: Optional[str] = None
    scrapfly_region: str = "us-east-1"
    scrapfly_rendering: str = "js"
    
    # Data Storage
    data_dir: str = "data"
    cache_dir: str = "data/cache"
    logs_dir: str = "logs"
    output_format: str = "json"
    enable_compression: bool = True
    
    # Knowledge Management
    enable_knowledge_graph: bool = True
    enable_semantic_search: bool = True
    enable_version_control: bool = True
    knowledge_retention_days: int = 365
    
    # Security
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    enable_csrf_protection: bool = True
    
    # Advanced Features
    enable_ai_processing: bool = True
    enable_content_analysis: bool = True
    enable_link_extraction: bool = True
    enable_metadata_extraction: bool = True
    enable_screenshot_capture: bool = False
    
    # Tool-specific configurations
    enable_chartdb_scraping: bool = True
    enable_jsoncrack_scraping: bool = True
    enable_motia_scraping: bool = True
    
    # ChartDB specific settings
    chartdb_screenshot_enabled: bool = True
    chartdb_extract_diagrams: bool = True
    chartdb_extract_templates: bool = True
    
    # JSON Crack specific settings
    jsoncrack_extract_examples: bool = True
    jsoncrack_extract_features: bool = True
    jsoncrack_screenshot_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Ensure directories exist
def ensure_directories():
    """Create necessary directories"""
    directories = [
        settings.data_dir,
        settings.cache_dir,
        settings.logs_dir,
        "data/scraped",
        "data/processed",
        "data/knowledge",
        "data/motia",
        "data/chartdb",
        "data/jsoncrack",
        "flows",
        "tests",
        "mcp_servers",
        "scrapers",
        "web_ui"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Initialize directories
ensure_directories()

# MCP Configuration
MCP_CONFIG = {
    "servers": [
        {
            "name": "motia-scraper",
            "command": "python",
            "args": ["mcp_servers/scraper_mcp_server.py"],
            "env": {
                "MOTIA_SCRAPER_CONFIG": "config/settings.py"
            }
        },
        {
            "name": "context7-mcp",
            "command": "python",
            "args": ["mcp_servers/context7_mcp_server.py"],
            "env": {
                "CONTEXT7_API_KEY": settings.context7_api_key
            }
        },
        {
            "name": "yugabyte-mcp",
            "command": "python",
            "args": ["mcp_servers/yugabyte_mcp_server.py"],
            "env": {
                "YUGABYTE_URL": settings.database_url
            }
        },
        {
            "name": "chartdb-mcp",
            "command": "python",
            "args": ["mcp_servers/chartdb_mcp_server.py"],
            "env": {
                "CHARTDB_CONFIG": "config/settings.py"
            }
        },
        {
            "name": "jsoncrack-mcp",
            "command": "python",
            "args": ["mcp_servers/jsoncrack_mcp_server.py"],
            "env": {
                "JSONCRACK_CONFIG": "config/settings.py"
            }
        }
    ],
    "timeout": settings.mcp_timeout,
    "retry_attempts": settings.mcp_retry_attempts
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "max_concurrent_requests": settings.max_concurrent_requests,
    "request_delay": settings.request_delay,
    "timeout": settings.timeout,
    "max_retries": settings.max_retries,
    "requests_per_minute": settings.requests_per_minute,
    "enable_caching": settings.enable_caching,
    "cache_ttl": settings.cache_ttl,
    "enable_compression": settings.enable_compression,
    "max_content_size": settings.max_content_size,
    "enable_parallel_processing": settings.enable_parallel_processing,
    "max_workers": settings.max_workers
}

# Scraping Engine Configuration
SCRAPING_ENGINES = {
    "scrapfly": {
        "enabled": True,
        "api_key": settings.scrapfly_api_key,
        "region": settings.scrapfly_region,
        "rendering": settings.scrapfly_rendering,
        "timeout": settings.timeout
    },
    "playwright": {
        "enabled": settings.enable_playwright,
        "headless": settings.playwright_headless,
        "browser": settings.playwright_browser,
        "viewport": settings.playwright_viewport,
        "timeout": settings.playwright_timeout
    },
    "scrapy": {
        "enabled": settings.enable_scrapy,
        "concurrent_requests": settings.max_concurrent_requests,
        "download_delay": settings.request_delay,
        "timeout": settings.timeout
    },
    "selenium": {
        "enabled": settings.enable_selenium,
        "headless": True,
        "browser": "chrome",
        "timeout": settings.timeout
    }
}

# Knowledge Management Configuration
KNOWLEDGE_CONFIG = {
    "enable_knowledge_graph": settings.enable_knowledge_graph,
    "enable_semantic_search": settings.enable_semantic_search,
    "enable_version_control": settings.enable_version_control,
    "retention_days": settings.knowledge_retention_days,
    "context7_enabled": settings.context7_enabled,
    "context7_api_key": settings.context7_api_key,
    "context7_endpoint": settings.context7_endpoint,
    "context7_model": settings.context7_model,
    "context7_max_tokens": settings.context7_max_tokens
}

# Tool-specific configurations
TOOL_CONFIGS = {
    "motia": {
        "enabled": settings.enable_motia_scraping,
        "urls": settings.motia_urls,
        "scraper_type": "playwright",
        "extract_features": ["documentation", "api_reference", "examples", "tutorials"],
        "screenshot_enabled": False
    },
    "chartdb": {
        "enabled": settings.enable_chartdb_scraping,
        "urls": settings.chartdb_urls,
        "scraper_type": "playwright",
        "extract_features": ["diagrams", "templates", "features", "documentation"],
        "screenshot_enabled": settings.chartdb_screenshot_enabled,
        "extract_diagrams": settings.chartdb_extract_diagrams,
        "extract_templates": settings.chartdb_extract_templates
    },
    "jsoncrack": {
        "enabled": settings.enable_jsoncrack_scraping,
        "urls": settings.jsoncrack_urls,
        "scraper_type": "playwright",
        "extract_features": ["examples", "features", "documentation", "interactive_demos"],
        "screenshot_enabled": settings.jsoncrack_screenshot_enabled,
        "extract_examples": settings.jsoncrack_extract_examples,
        "extract_features": settings.jsoncrack_extract_features
    }
}