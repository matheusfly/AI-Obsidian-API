"""
Scrapfly-based Scraper for Motia Documentation Scraper
Professional scraping with anti-bot protection
"""

import asyncio
import time
from typing import Dict, Any, Optional
import structlog

from .base_scraper import BaseScraper

logger = structlog.get_logger("scrapfly-scraper")

class ScrapflyScraper(BaseScraper):
    """Scrapfly-based scraper with anti-bot protection"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, 
                 api_key: Optional[str] = None, region: str = "us-east-1"):
        super().__init__("scrapfly", timeout, max_retries)
        self.api_key = api_key
        self.region = region
        self.client = None
    
    async def _get_client(self):
        """Get or create Scrapfly client"""
        if self.client is None:
            try:
                from scrapfly import ScrapflyClient, ScrapeConfig
                self.ScrapflyClient = ScrapflyClient
                self.ScrapeConfig = ScrapeConfig
                
                if self.api_key:
                    self.client = ScrapflyClient(key=self.api_key)
                else:
                    # Use free tier or demo mode
                    self.client = ScrapflyClient()
                
                logger.info("Scrapfly client initialized", region=self.region)
                
            except ImportError:
                logger.error("Scrapfly not installed. Install with: pip install scrapfly-sdk")
                raise Exception("Scrapfly not available")
            except Exception as e:
                logger.error("Failed to initialize Scrapfly client", error=str(e))
                raise
    
    async def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape URL using Scrapfly"""
        await self._get_client()
        
        try:
            logger.info("Scraping with Scrapfly", url=url, scraper=self.name)
            
            # Prepare scrape configuration
            config = self.ScrapeConfig(
                url=url,
                render_js=True,  # Enable JavaScript rendering
                country="US",
                region=self.region,
                timeout=self.timeout * 1000,  # Convert to milliseconds
                headers={
                    "User-Agent": "MotiaDocsScraper/1.0 (Educational Research)"
                }
            )
            
            # Add custom options
            if "wait_for_element" in kwargs:
                config.wait_for_selector = kwargs["wait_for_element"]
            
            if "wait_time" in kwargs:
                config.wait = kwargs["wait_time"] * 1000  # Convert to milliseconds
            
            if "take_screenshot" in kwargs and kwargs["take_screenshot"]:
                config.screenshot = True
            
            # Perform scraping
            result = await self.client.scrape(config)
            
            # Extract content
            html = result.content
            content = html
            
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
            
            # Get Scrapfly-specific data
            scrapfly_data = {
                "region": result.region,
                "country": result.country,
                "render_js": result.render_js,
                "screenshot": result.screenshot,
                "cost": result.cost,
                "remaining_credits": result.remaining_credits
            }
            
            # Get response info
            response_info = {
                "status_code": result.status_code,
                "headers": dict(result.headers),
                "url": result.url,
                "final_url": result.final_url
            }
            
            result_data = {
                "url": url,
                "final_url": result.final_url,
                "status_code": result.status_code,
                "headers": dict(result.headers),
                "content": content,
                "html": html,
                "text": text,
                "links": links,
                "metadata": metadata,
                "structured_data": structured_data,
                "content_length": len(content),
                "text_length": len(text),
                "links_count": len(links),
                "scrapfly_data": scrapfly_data,
                "response_info": response_info,
                "scraper": "scrapfly"
            }
            
            logger.info("Scrapfly scraping successful", 
                       url=url, 
                       final_url=result.final_url,
                       content_length=len(content),
                       cost=result.cost,
                       scraper=self.name)
            
            return result_data
            
        except Exception as e:
            logger.error("Scrapfly scraping failed", url=url, error=str(e), scraper=self.name)
            raise
    
    async def close(self):
        """Close Scrapfly client"""
        if self.client:
            # Scrapfly client doesn't need explicit closing
            self.client = None
            logger.info("Scrapfly client closed", scraper=self.name)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()