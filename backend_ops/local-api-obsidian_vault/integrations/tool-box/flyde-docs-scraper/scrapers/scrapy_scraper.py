"""
Scrapy-based scraper for Flyde documentation.
"""
import asyncio
from typing import Dict, List, Optional, Any
from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import structlog

from .base_scraper import BaseScraper, ScrapingResult
from config.settings import settings
from config.logging import get_logger


logger = get_logger(__name__)


class FlydeDocsSpider(Spider):
    """Scrapy spider for Flyde documentation."""
    
    name = 'flyde_docs'
    allowed_domains = ['flyde.dev']
    start_urls = [settings.docs_url]
    
    def __init__(self, target_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_urls = target_urls or []
        self.results = []
    
    def start_requests(self):
        """Generate initial requests."""
        if self.target_urls:
            for url in self.target_urls:
                yield Request(url=url, callback=self.parse)
        else:
            for url in self.start_urls:
                yield Request(url=url, callback=self.parse)
    
    def parse(self, response):
        """Parse response and extract data."""
        try:
            # Extract page content
            content = response.text
            
            # Extract metadata
            metadata = {
                'title': response.css('title::text').get(),
                'url': response.url,
                'status': response.status,
                'headers': dict(response.headers),
                'links': response.css('a::attr(href)').getall(),
                'images': response.css('img::attr(src)').getall(),
            }
            
            # Create result
            result = ScrapingResult(
                url=response.url,
                content=content,
                status_code=response.status,
                headers=dict(response.headers),
                metadata=metadata
            )
            
            self.results.append(result)
            
            # Follow links if not targeting specific URLs
            if not self.target_urls:
                for link in response.css('a::attr(href)').getall():
                    if link and self._should_follow_link(link):
                        yield response.follow(link, self.parse)
        
        except Exception as e:
            logger.error("Failed to parse response", url=response.url, error=str(e))
    
    def _should_follow_link(self, link: str) -> bool:
        """Check if link should be followed."""
        # Basic filtering
        if not link or link.startswith('#'):
            return False
        
        # Check if it's a relative link or same domain
        if link.startswith('/') or link.startswith(settings.base_url):
            return True
        
        return False


class ScrapyScraper(BaseScraper):
    """Scrapy-powered scraper for Flyde documentation."""
    
    def __init__(self):
        super().__init__("scrapy")
        self.process = None
        self._setup_process()
    
    def _setup_process(self):
        """Setup Scrapy crawler process."""
        try:
            settings_dict = {
                'USER_AGENT': settings.user_agents[0],
                'ROBOTSTXT_OBEY': True,
                'DOWNLOAD_DELAY': settings.request_delay,
                'CONCURRENT_REQUESTS': settings.max_concurrent_requests,
                'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
                'AUTOTHROTTLE_ENABLED': True,
                'AUTOTHROTTLE_START_DELAY': 1,
                'AUTOTHROTTLE_MAX_DELAY': 60,
                'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
                'AUTOTHROTTLE_DEBUG': False,
                'COOKIES_ENABLED': False,
                'TELNETCONSOLE_ENABLED': False,
                'LOG_LEVEL': 'INFO',
            }
            
            self.process = CrawlerProcess(settings_dict)
            self.logger.info("Scrapy process setup successfully")
        
        except Exception as e:
            self.logger.error("Failed to setup Scrapy process", error=str(e))
    
    async def scrape_url(self, url: str, **kwargs) -> ScrapingResult:
        """Scrape a single URL using Scrapy."""
        return await self.scrape_multiple([url])
    
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrape multiple URLs using Scrapy."""
        if not self.process:
            return [
                ScrapingResult(url=url, content="", error="Scrapy process not initialized")
                for url in urls
            ]
        
        self.session_count += len(urls)
        
        try:
            # Create spider instance
            spider = FlydeDocsSpider(target_urls=urls)
            
            # Run the spider
            self.process.crawl(spider)
            self.process.start()
            
            # Process results
            results = []
            for result in spider.results:
                if result.is_success():
                    self.success_count += 1
                else:
                    self.error_count += 1
                results.append(result)
            
            return results
        
        except Exception as e:
            self.logger.error("Scrapy scraping failed", error=str(e))
            return [
                ScrapingResult(url=url, content="", error=f"Scrapy exception: {str(e)}")
                for url in urls
            ]
    
    def stop(self):
        """Stop the Scrapy process."""
        if self.process:
            self.process.stop()