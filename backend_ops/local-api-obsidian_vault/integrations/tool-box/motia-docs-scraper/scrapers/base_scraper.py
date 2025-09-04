"""
Base Scraper Class for Motia Documentation Scraper
Advanced base class with performance monitoring and error handling
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger("base-scraper")

class BaseScraper(ABC):
    """Base class for all scrapers with common functionality"""
    
    def __init__(self, name: str, timeout: int = 30, max_retries: int = 3):
        self.name = name
        self.timeout = timeout
        self.max_retries = max_retries
        self.stats = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_time": 0,
            "average_response_time": 0,
            "last_request_time": None
        }
    
    @abstractmethod
    async def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape a URL and return results"""
        pass
    
    async def scrape_with_retry(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape with retry logic and performance monitoring"""
        start_time = time.time()
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info("Scraping attempt", 
                           url=url, 
                           attempt=attempt + 1, 
                           max_retries=self.max_retries + 1,
                           scraper=self.name)
                
                result = await self.scrape(url, **kwargs)
                
                # Update stats
                self._update_stats(True, time.time() - start_time)
                
                logger.info("Scraping successful", 
                           url=url, 
                           attempt=attempt + 1,
                           response_time=time.time() - start_time,
                           scraper=self.name)
                
                return result
                
            except Exception as e:
                logger.warning("Scraping attempt failed", 
                              url=url, 
                              attempt=attempt + 1, 
                              error=str(e),
                              scraper=self.name)
                
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info("Retrying after delay", 
                               url=url, 
                               wait_time=wait_time,
                               scraper=self.name)
                    await asyncio.sleep(wait_time)
                else:
                    # Final attempt failed
                    self._update_stats(False, time.time() - start_time)
                    raise e
    
    def _update_stats(self, success: bool, response_time: float):
        """Update scraper statistics"""
        self.stats["requests_made"] += 1
        self.stats["total_time"] += response_time
        self.stats["last_request_time"] = datetime.now().isoformat()
        
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        
        # Calculate average response time
        if self.stats["requests_made"] > 0:
            self.stats["average_response_time"] = self.stats["total_time"] / self.stats["requests_made"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics"""
        success_rate = 0
        if self.stats["requests_made"] > 0:
            success_rate = (self.stats["successful_requests"] / self.stats["requests_made"]) * 100
        
        return {
            "scraper_name": self.name,
            "requests_made": self.stats["requests_made"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": success_rate,
            "average_response_time": self.stats["average_response_time"],
            "total_time": self.stats["total_time"],
            "last_request_time": self.stats["last_request_time"]
        }
    
    def extract_text(self, html: str) -> str:
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
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML"""
        import re
        from urllib.parse import urljoin, urlparse
        
        # Find all href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(href_pattern, html, re.IGNORECASE)
        
        # Also find src attributes for images, etc.
        src_pattern = r'src=["\']([^"\']+)["\']'
        src_links = re.findall(src_pattern, html, re.IGNORECASE)
        
        all_links = links + src_links
        
        # Convert relative URLs to absolute
        absolute_links = []
        for link in all_links:
            if link.startswith(('http://', 'https://')):
                absolute_links.append(link)
            elif link.startswith('/'):
                absolute_links.append(urljoin(base_url, link))
            elif link.startswith('#'):
                # Skip anchor links
                continue
            else:
                absolute_links.append(urljoin(base_url, link))
        
        # Remove duplicates and filter out invalid URLs
        unique_links = []
        seen = set()
        for link in absolute_links:
            if link not in seen and self._is_valid_url(link):
                unique_links.append(link)
                seen.add(link)
        
        return unique_links
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    def extract_metadata(self, html: str) -> Dict[str, Any]:
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
        
        # Extract meta keywords
        keywords_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if keywords_match:
            metadata["keywords"] = keywords_match.group(1).strip()
        
        # Extract canonical URL
        canonical_match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if canonical_match:
            metadata["canonical_url"] = canonical_match.group(1).strip()
        
        # Extract Open Graph tags
        og_tags = {}
        og_matches = re.findall(r'<meta[^>]*property=["\']og:([^"\']*)["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        for prop, content in og_matches:
            og_tags[prop] = content.strip()
        if og_tags:
            metadata["open_graph"] = og_tags
        
        # Extract Twitter Card tags
        twitter_tags = {}
        twitter_matches = re.findall(r'<meta[^>]*name=["\']twitter:([^"\']*)["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        for prop, content in twitter_matches:
            twitter_tags[prop] = content.strip()
        if twitter_tags:
            metadata["twitter_card"] = twitter_tags
        
        return metadata
    
    def extract_structured_data(self, html: str) -> List[Dict[str, Any]]:
        """Extract structured data (JSON-LD, microdata, etc.)"""
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
        
        # Extract microdata (simplified)
        microdata_pattern = r'<[^>]*itemscope[^>]*>(.*?)</[^>]*>'
        microdata_matches = re.findall(microdata_pattern, html, re.IGNORECASE | re.DOTALL)
        
        for match in microdata_matches:
            # This is a simplified extraction - in practice, you'd want more sophisticated parsing
            structured_data.append({
                "type": "microdata",
                "data": match.strip()
            })
        
        return structured_data