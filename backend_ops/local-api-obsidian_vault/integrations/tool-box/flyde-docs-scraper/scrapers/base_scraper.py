"""
Base scraper class providing common functionality for all scraping engines.
"""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
import structlog

from config.settings import settings
from config.logging import get_logger


logger = get_logger(__name__)


class ScrapingResult:
    """Result of a scraping operation."""
    
    def __init__(
        self,
        url: str,
        content: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.url = url
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.metadata = metadata or {}
        self.error = error
        self.timestamp = time.time()
    
    def is_success(self) -> bool:
        """Check if the scraping was successful."""
        return self.error is None and self.status_code == 200
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "url": self.url,
            "content": self.content,
            "status_code": self.status_code,
            "headers": self.headers,
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp
        }


class BaseScraper(ABC):
    """Base class for all scrapers."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"scraper.{name}")
        self.session_count = 0
        self.error_count = 0
        self.success_count = 0
    
    @abstractmethod
    async def scrape_url(self, url: str, **kwargs) -> ScrapingResult:
        """Scrape a single URL."""
        pass
    
    @abstractmethod
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrape multiple URLs."""
        pass
    
    def should_scrape_url(self, url: str) -> bool:
        """Check if URL should be scraped based on configuration."""
        parsed = urlparse(url)
        
        # Check if URL is in allowed domain
        if not url.startswith(settings.base_url):
            return False
        
        # Check exclude patterns
        for pattern in settings.exclude_patterns:
            if pattern in url:
                return False
        
        # Check file extensions
        path = parsed.path.lower()
        if not any(path.endswith(ext) for ext in settings.file_extensions):
            return False
        
        return True
    
    def extract_links(self, content: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        from bs4 import BeautifulSoup
        
        links = []
        try:
            soup = BeautifulSoup(content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)
                if self.should_scrape_url(absolute_url):
                    links.append(absolute_url)
        except Exception as e:
            self.logger.error("Failed to extract links", error=str(e))
        
        return list(set(links))  # Remove duplicates
    
    def extract_text_content(self, content: str) -> str:
        """Extract clean text content from HTML."""
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            self.logger.error("Failed to extract text content", error=str(e))
            return content
    
    def extract_metadata(self, content: str, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML content."""
        from bs4 import BeautifulSoup
        
        metadata = {
            "url": url,
            "title": "",
            "description": "",
            "keywords": [],
            "author": "",
            "language": "en"
        }
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata["title"] = title_tag.get_text().strip()
            
            # Extract meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', '').lower()
                property_attr = meta.get('property', '').lower()
                content_attr = meta.get('content', '')
                
                if name == 'description' or property_attr == 'og:description':
                    metadata["description"] = content_attr
                elif name == 'keywords':
                    metadata["keywords"] = [kw.strip() for kw in content_attr.split(',')]
                elif name == 'author':
                    metadata["author"] = content_attr
                elif property_attr == 'og:title':
                    metadata["title"] = content_attr or metadata["title"]
            
            # Extract language
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                metadata["language"] = html_tag['lang']
        
        except Exception as e:
            self.logger.error("Failed to extract metadata", error=str(e))
        
        return metadata
    
    async def rate_limit(self) -> None:
        """Implement rate limiting."""
        await asyncio.sleep(settings.request_delay)
    
    def log_stats(self) -> None:
        """Log scraping statistics."""
        self.logger.info(
            "Scraping statistics",
            scraper=self.name,
            sessions=self.session_count,
            successes=self.success_count,
            errors=self.error_count,
            success_rate=self.success_count / max(1, self.session_count) * 100
        )