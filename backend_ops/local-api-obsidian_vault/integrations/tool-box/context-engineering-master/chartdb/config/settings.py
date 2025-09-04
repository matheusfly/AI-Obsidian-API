"""
ChartDB Documentation Scraper Configuration
Advanced settings for comprehensive documentation extraction with pagination
"""

import os
from typing import Dict, List, Any
from pydantic import BaseSettings, Field

class ChartDBSettings(BaseSettings):
    """ChartDB scraper configuration settings"""
    
    # === CORE SCRAPING SETTINGS ===
    base_urls: List[str] = Field(default=[
        "https://chartdb.io/",
        "https://docs.chartdb.io/",
        "https://api.chartdb.io/",
        "https://github.com/chartdb/chartdb"
    ])
    
    # === PAGINATION SETTINGS ===
    pagination_enabled: bool = True
    max_pages_per_section: int = 100
    page_delay: float = 1.0
    pagination_selectors: Dict[str, str] = Field(default={
        "next_page": "a[rel='next'], .pagination .next, .page-next",
        "page_numbers": ".pagination a, .page-numbers a",
        "load_more": ".load-more, .show-more, [data-load-more]",
        "infinite_scroll": "[data-infinite-scroll], .infinite-scroll"
    })
    
    # === ADVANCED SCRAPING FEATURES ===
    extract_diagrams: bool = True
    extract_templates: bool = True
    extract_api_docs: bool = True
    extract_github_content: bool = True
    extract_screenshots: bool = True
    extract_schemas: bool = True
    
    # === API INTEGRATION ===
    chartdb_api_key: str = Field(default="", env="CHARTDB_API_KEY")
    api_base_url: str = "https://api.chartdb.io/api"
    api_endpoints: Dict[str, str] = Field(default={
        "diagrams": "/diagrams",
        "templates": "/templates", 
        "schemas": "/schemas",
        "users": "/users",
        "projects": "/projects"
    })
    
    # === DATABASE SCHEMA EXTRACTION ===
    supported_databases: List[str] = Field(default=[
        "postgresql", "mysql", "sqlite", "sqlserver", 
        "mariadb", "clickhouse", "cockroachdb", "oracle",
        "mongodb", "redis", "cassandra", "dynamodb"
    ])
    
    schema_extraction_patterns: Dict[str, str] = Field(default={
        "postgresql": r"CREATE TABLE\s+(\w+)\s*\(",
        "mysql": r"CREATE TABLE\s+`?(\w+)`?\s*\(",
        "sqlite": r"CREATE TABLE\s+(\w+)\s*\(",
        "mongodb": r"db\.(\w+)\.",
        "redis": r"(\w+):\w+"
    })
    
    # === DIAGRAM EXTRACTION ===
    diagram_formats: List[str] = Field(default=["png", "svg", "pdf", "jpg"])
    diagram_selectors: Dict[str, str] = Field(default={
        "canvas": "canvas, svg",
        "images": "img[src*='diagram'], img[alt*='diagram']",
        "download_links": "a[href*='download'], a[href*='export']",
        "preview": ".diagram-preview, .schema-preview"
    })
    
    # === TEMPLATE EXTRACTION ===
    template_categories: List[str] = Field(default=[
        "database", "er-diagram", "schema", "workflow", 
        "architecture", "network", "flowchart", "mindmap"
    ])
    
    template_selectors: Dict[str, str] = Field(default={
        "template_cards": ".template-card, .template-item",
        "template_links": "a[href*='template'], a[href*='example']",
        "template_previews": ".template-preview, .example-preview",
        "template_metadata": ".template-meta, .template-info"
    })
    
    # === GITHUB INTEGRATION ===
    github_repos: List[str] = Field(default=[
        "chartdb/chartdb",
        "chartdb/templates",
        "chartdb/examples"
    ])
    
    github_content_types: List[str] = Field(default=[
        "readme", "docs", "examples", "templates", 
        "schemas", "scripts", "configs"
    ])
    
    # === PERFORMANCE SETTINGS ===
    max_concurrent_requests: int = 20
    request_delay: float = 0.5
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 2.0
    
    # === CACHING SETTINGS ===
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_storage: str = "redis"  # redis, memory, file
    
    # === OUTPUT SETTINGS ===
    output_formats: List[str] = Field(default=["json", "markdown", "html", "csv"])
    output_directory: str = "data"
    compress_output: bool = True
    include_metadata: bool = True
    
    # === MCP INTEGRATION ===
    mcp_servers: Dict[str, Dict[str, Any]] = Field(default={
        "chartdb_mcp": {
            "enabled": True,
            "port": 8003,
            "functions": [
                "scrape_chartdb",
                "extract_database_diagrams", 
                "extract_templates",
                "analyze_database_schema",
                "generate_schema_documentation"
            ]
        },
        "context7_mcp": {
            "enabled": True,
            "port": 8004,
            "functions": [
                "store_context",
                "retrieve_context",
                "search_context",
                "update_context"
            ]
        }
    })
    
    # === SENTRY INTEGRATION ===
    sentry_dsn: str = Field(default="", env="SENTRY_DSN")
    sentry_enabled: bool = True
    
    # === CONTEXT7 INTEGRATION ===
    context7_api_key: str = Field(default="", env="CONTEXT7_API_KEY")
    context7_base_url: str = "https://api.context7.io"
    
    # === YUGABYTE INTEGRATION ===
    yugabyte_connection: Dict[str, str] = Field(default={
        "host": "localhost",
        "port": "5433",
        "database": "chartdb_docs",
        "username": "yugabyte",
        "password": ""
    })
    
    # === ADVANCED FEATURES ===
    enable_ai_processing: bool = True
    enable_semantic_search: bool = True
    enable_auto_categorization: bool = True
    enable_relationship_mapping: bool = True
    
    # === CUSTOM SELECTORS ===
    custom_selectors: Dict[str, Dict[str, str]] = Field(default={
        "documentation": {
            "sections": ".doc-section, .documentation-section",
            "titles": "h1, h2, h3, .doc-title",
            "content": ".doc-content, .documentation-content",
            "code_blocks": "pre code, .code-block, .highlight"
        },
        "api_docs": {
            "endpoints": ".endpoint, .api-endpoint",
            "methods": ".method, .http-method",
            "parameters": ".parameter, .param",
            "responses": ".response, .api-response"
        },
        "templates": {
            "categories": ".category, .template-category",
            "previews": ".preview, .template-preview",
            "downloads": ".download, .template-download",
            "metadata": ".meta, .template-meta"
        }
    })
    
    # === FILTERING SETTINGS ===
    content_filters: Dict[str, List[str]] = Field(default={
        "include_keywords": [
            "database", "schema", "diagram", "template", "api",
            "documentation", "tutorial", "example", "guide"
        ],
        "exclude_keywords": [
            "advertisement", "sponsor", "promo", "marketing"
        ],
        "min_content_length": 100,
        "max_content_length": 50000
    })
    
    # === MONITORING SETTINGS ===
    enable_metrics: bool = True
    metrics_port: int = 9090
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = ChartDBSettings()

# === URL PATTERNS FOR COMPREHENSIVE COVERAGE ===
URL_PATTERNS = {
    "main_site": [
        "https://chartdb.io/",
        "https://chartdb.io/templates",
        "https://chartdb.io/examples", 
        "https://chartdb.io/docs",
        "https://chartdb.io/api",
        "https://chartdb.io/blog",
        "https://chartdb.io/help",
        "https://chartdb.io/support"
    ],
    "documentation": [
        "https://docs.chartdb.io/",
        "https://docs.chartdb.io/docs/",
        "https://docs.chartdb.io/docs/api/",
        "https://docs.chartdb.io/docs/guides/",
        "https://docs.chartdb.io/docs/tutorials/",
        "https://docs.chartdb.io/docs/examples/",
        "https://docs.chartdb.io/docs/reference/"
    ],
    "api": [
        "https://api.chartdb.io/api/",
        "https://api.chartdb.io/api/diagrams/",
        "https://api.chartdb.io/api/templates/",
        "https://api.chartdb.io/api/schemas/",
        "https://api.chartdb.io/api/users/",
        "https://api.chartdb.io/api/projects/"
    ],
    "github": [
        "https://github.com/chartdb/chartdb",
        "https://github.com/chartdb/chartdb/tree/main/docs",
        "https://github.com/chartdb/chartdb/tree/main/examples",
        "https://github.com/chartdb/chartdb/tree/main/templates",
        "https://github.com/chartdb/chartdb/tree/main/src",
        "https://github.com/chartdb/chartdb/wiki"
    ]
}

# === PAGINATION PATTERNS ===
PAGINATION_PATTERNS = {
    "standard": {
        "next_page": "a[rel='next'], .pagination .next, .page-next",
        "page_numbers": ".pagination a, .page-numbers a, .pager a",
        "previous_page": "a[rel='prev'], .pagination .prev, .page-prev"
    },
    "load_more": {
        "load_more": ".load-more, .show-more, [data-load-more]",
        "infinite_scroll": "[data-infinite-scroll], .infinite-scroll"
    },
    "api_pagination": {
        "next_url": "next",
        "page_param": "page",
        "per_page_param": "per_page",
        "total_pages": "total_pages"
    }
}

# === CONTENT EXTRACTION PATTERNS ===
CONTENT_PATTERNS = {
    "diagrams": {
        "selectors": [
            "canvas", "svg", "img[src*='diagram']",
            ".diagram-container", ".schema-diagram"
        ],
        "attributes": ["src", "data-src", "data-diagram"],
        "formats": ["png", "svg", "jpg", "pdf"]
    },
    "templates": {
        "selectors": [
            ".template-card", ".template-item", 
            "a[href*='template']", ".example-card"
        ],
        "metadata": ["title", "description", "category", "tags"],
        "download_links": ["href", "data-download"]
    },
    "code_blocks": {
        "selectors": [
            "pre code", ".code-block", ".highlight",
            ".syntax-highlight", ".code-example"
        ],
        "languages": ["sql", "javascript", "python", "json", "yaml"]
    }
}