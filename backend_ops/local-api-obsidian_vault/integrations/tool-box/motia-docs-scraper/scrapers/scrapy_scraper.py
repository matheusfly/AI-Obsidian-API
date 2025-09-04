"""
Scrapy-based Scraper for Motia Documentation Scraper
High-performance scraping with built-in features
"""

import asyncio
import time
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import structlog

from .base_scraper import BaseScraper

logger = structlog.get_logger("scrapy-scraper")

class ScrapyScraper(BaseScraper):
    """Scrapy-based scraper for high-performance scraping"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, 
                 concurrent_requests: int = 16):
        super().__init__("scrapy", timeout, max_retries)
        self.concurrent_requests = concurrent_requests
        self.spider = None
        self.crawler = None
    
    async def _get_spider(self):
        """Get or create Scrapy spider"""
        if self.spider is None:
            try:
                from scrapy import Spider
                from scrapy.crawler import CrawlerProcess
                from scrapy.utils.project import get_project_settings
                
                # Create custom spider class
                class MotiaDocsSpider(Spider):
                    name = 'motia_docs'
                    custom_settings = {
                        'CONCURRENT_REQUESTS': self.concurrent_requests,
                        'DOWNLOAD_DELAY': 1,
                        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
                        'USER_AGENT': 'MotiaDocsScraper/1.0 (Educational Research)',
                        'ROBOTSTXT_OBEY': False,
                        'DOWNLOAD_TIMEOUT': self.timeout,
                        'RETRY_TIMES': self.max_retries,
                        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
                        'AUTOTHROTTLE_ENABLED': True,
                        'AUTOTHROTTLE_START_DELAY': 1,
                        'AUTOTHROTTLE_MAX_DELAY': 10,
                        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
                        'AUTOTHROTTLE_DEBUG': False,
                        'COOKIES_ENABLED': True,
                        'TELNETCONSOLE_ENABLED': False,
                        'LOG_LEVEL': 'WARNING'
                    }
                    
                    def __init__(self, target_url=None, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.target_url = target_url
                        self.results = []
                    
                    def start_requests(self):
                        if self.target_url:
                            yield self.make_requests_from_url(self.target_url)
                    
                    def parse(self, response):
                        # Extract content
                        html = response.text
                        content = html
                        
                        # Extract text
                        text = self.extract_text(html)
                        
                        # Extract links
                        links = self.extract_links(html, response.url)
                        
                        # Extract metadata
                        metadata = self.extract_metadata(html)
                        
                        # Extract structured data
                        structured_data = self.extract_structured_data(html)
                        
                        result = {
                            'url': response.url,
                            'status_code': response.status,
                            'headers': dict(response.headers),
                            'content': content,
                            'html': html,
                            'text': text,
                            'links': links,
                            'metadata': metadata,
                            'structured_data': structured_data,
                            'content_length': len(content),
                            'text_length': len(text),
                            'links_count': len(links),
                            'scraper': 'scrapy'
                        }
                        
                        self.results.append(result)
                        return result
                    
                    def extract_text(self, html):
                        """Extract clean text from HTML"""
                        import re
                        # Remove script and style elements
                        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
                        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
                        html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)
                        # Remove HTML comments
                        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
                        # Remove HTML tags
                        text = re.sub(r'<[^>]+>', ' ', html)
                        # Decode HTML entities
                        import html
                        text = html.unescape(text)
                        # Clean up whitespace
                        text = re.sub(r'\s+', ' ', text).strip()
                        return text
                    
                    def extract_links(self, html, base_url):
                        """Extract links from HTML"""
                        import re
                        from urllib.parse import urljoin, urlparse
                        
                        # Find all href attributes
                        href_pattern = r'href=["\']([^"\']+)["\']'
                        links = re.findall(href_pattern, html, re.IGNORECASE)
                        
                        # Convert relative URLs to absolute
                        absolute_links = []
                        for link in links:
                            if link.startswith(('http://', 'https://')):
                                absolute_links.append(link)
                            elif link.startswith('/'):
                                absolute_links.append(urljoin(base_url, link))
                            elif link.startswith('#'):
                                continue
                            else:
                                absolute_links.append(urljoin(base_url, link))
                        
                        # Remove duplicates
                        return list(set(absolute_links))
                    
                    def extract_metadata(self, html):
                        """Extract metadata from HTML"""
                        import re
                        
                        metadata = {}
                        
                        # Extract title
                        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
                        if title_match:
                            metadata["title"] = title_match.group(1).strip()
                        
                        # Extract meta description
                        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
                        if desc_match:
                            metadata["description"] = desc_match.group(1).strip()
                        
                        return metadata
                    
                    def extract_structured_data(self, html):
                        """Extract structured data from HTML"""
                        import re
                        import json
                        
                        structured_data = []
                        
                        # Extract JSON-LD
                        json_ld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
                        json_ld_matches = re.findall(json_ld_pattern, html, re.IGNORECASE | re.DOTALL)
                        
                        for match in json_ld_matches:
                            try:
                                data = json.loads(match.strip())
                                structured_data.append({
                                    "type": "json-ld",
                                    "data": data
                                })
                            except json.JSONDecodeError:
                                continue
                        
                        return structured_data
                
                self.MotiaDocsSpider = MotiaDocsSpider
                logger.info("Scrapy spider created", scraper=self.name)
                
            except ImportError:
                logger.error("Scrapy not installed. Install with: pip install scrapy")
                raise Exception("Scrapy not available")
            except Exception as e:
                logger.error("Failed to create Scrapy spider", error=str(e))
                raise
    
    async def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape URL using Scrapy"""
        await self._get_spider()
        
        try:
            logger.info("Scraping with Scrapy", url=url, scraper=self.name)
            
            # Create spider instance
            spider = self.MotiaDocsSpider(target_url=url)
            
            # Create crawler process
            from scrapy.crawler import CrawlerProcess
            from scrapy.utils.project import get_project_settings
            
            # Get settings
            settings = get_project_settings()
            settings.update({
                'CONCURRENT_REQUESTS': self.concurrent_requests,
                'DOWNLOAD_DELAY': 1,
                'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
                'USER_AGENT': 'MotiaDocsScraper/1.0 (Educational Research)',
                'ROBOTSTXT_OBEY': False,
                'DOWNLOAD_TIMEOUT': self.timeout,
                'RETRY_TIMES': self.max_retries,
                'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
                'AUTOTHROTTLE_ENABLED': True,
                'AUTOTHROTTLE_START_DELAY': 1,
                'AUTOTHROTTLE_MAX_DELAY': 10,
                'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
                'AUTOTHROTTLE_DEBUG': False,
                'COOKIES_ENABLED': True,
                'TELNETCONSOLE_ENABLED': False,
                'LOG_LEVEL': 'WARNING'
            })
            
            # Create crawler process
            process = CrawlerProcess(settings)
            
            # Add spider to process
            process.crawl(self.MotiaDocsSpider, target_url=url)
            
            # Start crawling
            process.start()
            
            # Get results from spider
            results = spider.results
            
            if not results:
                raise Exception("No results from Scrapy spider")
            
            result = results[0]  # Get first result
            
            logger.info("Scrapy scraping successful", 
                       url=url, 
                       content_length=len(result.get('content', '')),
                       scraper=self.name)
            
            return result
            
        except Exception as e:
            logger.error("Scrapy scraping failed", url=url, error=str(e), scraper=self.name)
            raise
    
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Scrape multiple URLs with Scrapy"""
        await self._get_spider()
        
        try:
            logger.info("Scraping multiple URLs with Scrapy", url_count=len(urls), scraper=self.name)
            
            # Create spider instance
            spider = self.MotiaDocsSpider()
            
            # Create crawler process
            from scrapy.crawler import CrawlerProcess
            from scrapy.utils.project import get_project_settings
            
            # Get settings
            settings = get_project_settings()
            settings.update({
                'CONCURRENT_REQUESTS': self.concurrent_requests,
                'DOWNLOAD_DELAY': 1,
                'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
                'USER_AGENT': 'MotiaDocsScraper/1.0 (Educational Research)',
                'ROBOTSTXT_OBEY': False,
                'DOWNLOAD_TIMEOUT': self.timeout,
                'RETRY_TIMES': self.max_retries,
                'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
                'AUTOTHROTTLE_ENABLED': True,
                'AUTOTHROTTLE_START_DELAY': 1,
                'AUTOTHROTTLE_MAX_DELAY': 10,
                'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
                'AUTOTHROTTLE_DEBUG': False,
                'COOKIES_ENABLED': True,
                'TELNETCONSOLE_ENABLED': False,
                'LOG_LEVEL': 'WARNING'
            })
            
            # Create crawler process
            process = CrawlerProcess(settings)
            
            # Add spider to process
            process.crawl(self.MotiaDocsSpider, start_urls=urls)
            
            # Start crawling
            process.start()
            
            # Get results from spider
            results = spider.results
            
            logger.info("Scrapy multiple scraping successful", 
                       url_count=len(urls),
                       result_count=len(results),
                       scraper=self.name)
            
            return results
            
        except Exception as e:
            logger.error("Scrapy multiple scraping failed", error=str(e), scraper=self.name)
            raise
    
    async def close(self):
        """Close Scrapy resources"""
        # Scrapy doesn't need explicit closing
        logger.info("Scrapy resources closed", scraper=self.name)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()