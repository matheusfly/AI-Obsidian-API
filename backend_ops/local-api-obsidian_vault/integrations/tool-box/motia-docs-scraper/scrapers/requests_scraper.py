"""
Requests-based Scraper for Motia Documentation Scraper
Simple but reliable HTTP scraper with advanced features
"""

import asyncio
import httpx
import time
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import structlog

from .base_scraper import BaseScraper

logger = structlog.get_logger("requests-scraper")

class RequestsScraper(BaseScraper):
    """HTTP requests-based scraper with advanced features"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, 
                 user_agent: str = "MotiaDocsScraper/1.0 (Educational Research)"):
        super().__init__("requests", timeout, max_retries)
        self.user_agent = user_agent
        self.session = None
    
    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session"""
        if self.session is None:
            self.session = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
            )
        return self.session
    
    async def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape URL using HTTP requests"""
        session = await self._get_session()
        
        try:
            logger.info("Making HTTP request", url=url, scraper=self.name)
            
            # Prepare request parameters
            request_params = {
                "timeout": self.timeout,
                "follow_redirects": True
            }
            
            # Add custom headers if provided
            if "headers" in kwargs:
                request_params["headers"] = kwargs["headers"]
            
            # Make request
            response = await session.get(url, **request_params)
            response.raise_for_status()
            
            # Extract content
            content = response.text
            html = content
            
            # Extract text if requested
            text = ""
            if kwargs.get("extract_text", True):
                text = self.extract_text(html)
            
            # Extract links if requested
            links = []
            if kwargs.get("extract_links", True):
                links = self.extract_links(html, url)
            
            # Extract metadata
            metadata = self.extract_metadata(html)
            
            # Extract structured data
            structured_data = self.extract_structured_data(html)
            
            result = {
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": content,
                "html": html,
                "text": text,
                "links": links,
                "metadata": metadata,
                "structured_data": structured_data,
                "content_length": len(content),
                "text_length": len(text),
                "links_count": len(links)
            }
            
            logger.info("HTTP request successful", 
                       url=url, 
                       status_code=response.status_code,
                       content_length=len(content),
                       scraper=self.name)
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error("HTTP status error", 
                        url=url, 
                        status_code=e.response.status_code,
                        scraper=self.name)
            raise Exception(f"HTTP {e.response.status_code}: {e.response.reason_phrase}")
        
        except httpx.TimeoutException:
            logger.error("Request timeout", url=url, scraper=self.name)
            raise Exception(f"Request timeout after {self.timeout} seconds")
        
        except httpx.RequestError as e:
            logger.error("Request error", url=url, error=str(e), scraper=self.name)
            raise Exception(f"Request failed: {str(e)}")
        
        except Exception as e:
            logger.error("Unexpected error", url=url, error=str(e), scraper=self.name)
            raise
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()