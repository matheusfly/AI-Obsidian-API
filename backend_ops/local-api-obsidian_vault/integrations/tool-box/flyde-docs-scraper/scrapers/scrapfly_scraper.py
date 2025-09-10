"""
Scrapfly-based scraper for Flyde documentation.
"""
import asyncio
from typing import Dict, List, Optional, Any
import structlog

from scrapfly import ScrapflyClient, ScrapeConfig
from .base_scraper import BaseScraper, ScrapingResult
from config.settings import settings
from config.logging import get_logger


logger = get_logger(__name__)


class ScrapflyScraper(BaseScraper):
    """Scrapfly-powered scraper for Flyde documentation."""
    
    def __init__(self):
        super().__init__("scrapfly")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Scrapfly client."""
        if not settings.scrapfly_api_key:
            self.logger.warning("Scrapfly API key not configured")
            return
        
        try:
            self.client = ScrapflyClient(
                key=settings.scrapfly_api_key,
                account=settings.scrapfly_account
            )
            self.logger.info("Scrapfly client initialized successfully")
        except Exception as e:
            self.logger.error("Failed to initialize Scrapfly client", error=str(e))
    
    async def scrape_url(self, url: str, **kwargs) -> ScrapingResult:
        """Scrape a single URL using Scrapfly."""
        if not self.client:
            return ScrapingResult(
                url=url,
                content="",
                error="Scrapfly client not initialized"
            )
        
        self.session_count += 1
        
        try:
            # Configure scraping parameters
            config = ScrapeConfig(
                url=url,
                asp=True,  # Anti-scraping protection
                country="US",
                headers={
                    "User-Agent": settings.user_agents[0],
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                }
            )
            
            # Perform the scrape
            result = await self.client.async_scrape(config)
            
            if result.success:
                self.success_count += 1
                return ScrapingResult(
                    url=url,
                    content=result.content,
                    status_code=result.status_code,
                    headers=result.headers,
                    metadata={
                        "scrapfly_session_id": result.session_id,
                        "scrapfly_asp": result.asp,
                        "scrapfly_country": result.country
                    }
                )
            else:
                self.error_count += 1
                return ScrapingResult(
                    url=url,
                    content="",
                    status_code=result.status_code,
                    error=f"Scrapfly failed: {result.error}"
                )
        
        except Exception as e:
            self.error_count += 1
            self.logger.error("Scrapfly scraping failed", url=url, error=str(e))
            return ScrapingResult(
                url=url,
                content="",
                error=f"Scrapfly exception: {str(e)}"
            )
    
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrape multiple URLs using Scrapfly."""
        if not self.client:
            return [
                ScrapingResult(url=url, content="", error="Scrapfly client not initialized")
                for url in urls
            ]
        
        results = []
        
        # Process URLs in batches to respect rate limits
        batch_size = min(10, len(urls))
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            
            # Create scrape configurations for the batch
            configs = []
            for url in batch:
                config = ScrapeConfig(
                    url=url,
                    asp=True,
                    country="US",
                    headers={
                        "User-Agent": settings.user_agents[0],
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate",
                        "Connection": "keep-alive",
                    }
                )
                configs.append(config)
            
            try:
                # Scrape batch
                batch_results = await self.client.async_scrape_all(configs)
                
                # Process results
                for result in batch_results:
                    if result.success:
                        self.success_count += 1
                        results.append(ScrapingResult(
                            url=result.url,
                            content=result.content,
                            status_code=result.status_code,
                            headers=result.headers,
                            metadata={
                                "scrapfly_session_id": result.session_id,
                                "scrapfly_asp": result.asp,
                                "scrapfly_country": result.country
                            }
                        ))
                    else:
                        self.error_count += 1
                        results.append(ScrapingResult(
                            url=result.url,
                            content="",
                            status_code=result.status_code,
                            error=f"Scrapfly failed: {result.error}"
                        ))
                
                # Rate limiting between batches
                if i + batch_size < len(urls):
                    await asyncio.sleep(settings.request_delay)
            
            except Exception as e:
                self.logger.error("Batch scraping failed", batch_start=i, error=str(e))
                # Add error results for the batch
                for url in batch:
                    self.error_count += 1
                    results.append(ScrapingResult(
                        url=url,
                        content="",
                        error=f"Batch scraping exception: {str(e)}"
                    ))
        
        self.session_count += len(urls)
        return results
    
    async def scrape_with_retry(self, url: str, max_retries: int = None) -> ScrapingResult:
        """Scrape URL with retry logic."""
        max_retries = max_retries or settings.max_retries
        
        for attempt in range(max_retries + 1):
            result = await self.scrape_url(url)
            
            if result.is_success():
                return result
            
            if attempt < max_retries:
                delay = 2 ** attempt  # Exponential backoff
                self.logger.info(f"Retrying {url} in {delay}s (attempt {attempt + 1}/{max_retries + 1})")
                await asyncio.sleep(delay)
        
        return result