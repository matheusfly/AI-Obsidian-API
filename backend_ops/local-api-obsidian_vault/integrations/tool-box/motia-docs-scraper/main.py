#!/usr/bin/env python3
"""
Motia Documentation Scraper - Main Orchestrator
Advanced scraping with MCP integration, performance monitoring, and active debugging
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiofiles
import httpx
from asyncio_throttle import Throttler
import structlog

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings, PERFORMANCE_CONFIG, SCRAPING_ENGINES
from scrapers.base_scraper import BaseScraper
from scrapers.scrapfly_scraper import ScrapflyScraper
from scrapers.playwright_scraper import PlaywrightScraper
from scrapers.scrapy_scraper import ScrapyScraper

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("motia-scraper")

class MotiaDocsScraper:
    """Advanced Motia documentation scraper with MCP integration"""
    
    def __init__(self):
        self.scrapers = {}
        self.throttler = Throttler(rate_limit=PERFORMANCE_CONFIG["requests_per_minute"], period=60)
        self.stats = {
            "start_time": datetime.now(),
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_content_length": 0,
            "scraped_urls": set(),
            "errors": []
        }
        self.setup_scrapers()
        
    def setup_scrapers(self):
        """Initialize scraping engines"""
        try:
            if SCRAPING_ENGINES["scrapfly"]["enabled"]:
                self.scrapers["scrapfly"] = ScrapflyScraper()
                logger.info("Scrapfly scraper initialized")
                
            if SCRAPING_ENGINES["playwright"]["enabled"]:
                self.scrapers["playwright"] = PlaywrightScraper()
                logger.info("Playwright scraper initialized")
                
            if SCRAPING_ENGINES["scrapy"]["enabled"]:
                self.scrapers["scrapy"] = ScrapyScraper()
                logger.info("Scrapy scraper initialized")
                
            # Always have requests as fallback
            from scrapers.requests_scraper import RequestsScraper
            self.scrapers["requests"] = RequestsScraper()
            logger.info("Requests scraper initialized")
            
        except Exception as e:
            logger.error("Failed to initialize scrapers", error=str(e))
            raise
    
    async def scrape_url(self, url: str, scraper_type: str = "scrapfly", **kwargs) -> Dict[str, Any]:
        """Scrape a single URL with advanced options"""
        logger.info("Starting URL scrape", url=url, scraper_type=scraper_type)
        
        # Check if already scraped
        if url in self.stats["scraped_urls"]:
            logger.info("URL already scraped, skipping", url=url)
            return {"status": "already_scraped", "url": url}
        
        # Apply throttling
        async with self.throttler:
            try:
                self.stats["total_requests"] += 1
                
                # Get scraper
                scraper = self.scrapers.get(scraper_type, self.scrapers["requests"])
                
                # Perform scraping
                start_time = time.time()
                result = await scraper.scrape(url, **kwargs)
                scrape_time = time.time() - start_time
                
                # Add metadata
                result.update({
                    "metadata": {
                        "scraper_type": scraper_type,
                        "scrape_time": scrape_time,
                        "timestamp": datetime.now().isoformat(),
                        "url": url
                    }
                })
                
                # Update stats
                self.stats["successful_requests"] += 1
                self.stats["total_content_length"] += len(result.get("content", ""))
                self.stats["scraped_urls"].add(url)
                
                logger.info("URL scraped successfully", 
                           url=url, 
                           content_length=len(result.get("content", "")),
                           scrape_time=scrape_time)
                
                return result
                
            except Exception as e:
                self.stats["failed_requests"] += 1
                self.stats["errors"].append({
                    "url": url,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.error("Failed to scrape URL", url=url, error=str(e))
                return {"error": str(e), "url": url}
    
    async def scrape_multiple_urls(self, urls: List[str], scraper_type: str = "scrapfly", 
                                 max_concurrent: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Scrape multiple URLs with parallel processing"""
        logger.info("Starting multiple URL scrape", 
                   url_count=len(urls), 
                   scraper_type=scraper_type,
                   max_concurrent=max_concurrent)
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_url(url, scraper_type, **kwargs)
        
        # Execute parallel scraping
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "url": urls[i],
                    "error": str(result),
                    "status": "failed"
                })
            else:
                processed_results.append(result)
        
        logger.info("Multiple URL scrape completed", 
                   total_urls=len(urls),
                   successful=sum(1 for r in processed_results if "error" not in r),
                   failed=sum(1 for r in processed_results if "error" in r))
        
        return processed_results
    
    async def crawl_documentation_site(self, base_url: str, max_depth: int = 3, 
                                     follow_external: bool = False, **kwargs) -> Dict[str, Any]:
        """Crawl entire documentation site with pagination"""
        logger.info("Starting documentation site crawl", 
                   base_url=base_url, 
                   max_depth=max_depth,
                   follow_external=follow_external)
        
        visited_urls = set()
        urls_to_visit = [base_url]
        crawled_pages = []
        all_links = set()
        
        for depth in range(max_depth):
            if not urls_to_visit:
                break
            
            logger.info("Crawling depth", depth=depth, urls_count=len(urls_to_visit))
            
            current_batch = urls_to_visit.copy()
            urls_to_visit.clear()
            
            # Scrape current batch
            batch_results = await self.scrape_multiple_urls(
                current_batch, 
                max_concurrent=PERFORMANCE_CONFIG["max_concurrent_requests"],
                **kwargs
            )
            
            for i, result in enumerate(batch_results):
                url = current_batch[i]
                
                if "error" in result:
                    continue
                
                crawled_pages.append({
                    "url": url,
                    "depth": depth,
                    "content_length": len(result.get("content", "")),
                    "title": result.get("title", ""),
                    "links_found": len(result.get("links", []))
                })
                
                # Extract new URLs to visit
                if "links" in result:
                    for link in result["links"]:
                        if link not in visited_urls:
                            # Check if it's internal or external
                            is_internal = link.startswith(base_url) or link.startswith("/")
                            
                            if is_internal or follow_external:
                                all_links.add(link)
                                if link not in visited_urls and link not in urls_to_visit:
                                    urls_to_visit.append(link)
            
            # Mark current batch as visited
            visited_urls.update(current_batch)
            
            # Add delay between depths
            if urls_to_visit:
                await asyncio.sleep(PERFORMANCE_CONFIG["request_delay"])
        
        crawl_result = {
            "base_url": base_url,
            "max_depth": max_depth,
            "total_pages_crawled": len(crawled_pages),
            "total_links_found": len(all_links),
            "crawled_pages": crawled_pages,
            "all_links": list(all_links),
            "crawl_stats": self.get_stats()
        }
        
        logger.info("Documentation site crawl completed", 
                   pages_crawled=len(crawled_pages),
                   links_found=len(all_links))
        
        return crawl_result
    
    async def process_motia_docs(self) -> Dict[str, Any]:
        """Process all Motia documentation URLs"""
        logger.info("Starting Motia documentation processing")
        
        # Define target URLs with metadata
        target_urls = [
            {
                "url": "https://www.motia.dev/docs",
                "type": "main_docs",
                "priority": "high"
            },
            {
                "url": "https://www.motia.dev/docs/getting-started/quick-start",
                "type": "tutorial",
                "priority": "high"
            },
            {
                "url": "https://www.motia.dev/docs/concepts/steps/defining-steps",
                "type": "concept",
                "priority": "high"
            },
            {
                "url": "https://www.motia.dev/manifesto",
                "type": "manifesto",
                "priority": "medium"
            },
            {
                "url": "https://github.com/MotiaDev/motia",
                "type": "github_repo",
                "priority": "high"
            },
            {
                "url": "https://github.com/MotiaDev/motia-examples",
                "type": "examples",
                "priority": "medium"
            }
        ]
        
        # Process URLs
        results = []
        for url_info in target_urls:
            logger.info("Processing URL", url=url_info["url"], type=url_info["type"])
            
            result = await self.scrape_url(
                url_info["url"],
                scraper_type="playwright",  # Use Playwright for better JS rendering
                extract_links=True,
                extract_text=True,
                take_screenshot=False
            )
            
            result["url_info"] = url_info
            results.append(result)
            
            # Add delay between requests
            await asyncio.sleep(PERFORMANCE_CONFIG["request_delay"])
        
        # Save results
        await self.save_results(results, "motia_docs_complete")
        
        # Generate summary
        summary = self.generate_summary(results)
        
        logger.info("Motia documentation processing completed", 
                   total_urls=len(target_urls),
                   successful=sum(1 for r in results if "error" not in r))
        
        return {
            "results": results,
            "summary": summary,
            "stats": self.get_stats()
        }
    
    async def save_results(self, results: List[Dict[str, Any]], filename_prefix: str) -> str:
        """Save results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = Path(settings.data_dir) / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare data for saving
        save_data = {
            "metadata": {
                "timestamp": timestamp,
                "total_results": len(results),
                "scraper_stats": self.get_stats()
            },
            "results": results
        }
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(save_data, indent=2, ensure_ascii=False))
        
        logger.info("Results saved", filepath=str(filepath))
        return str(filepath)
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of scraping results"""
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]
        
        total_content_length = sum(len(r.get("content", "")) for r in successful)
        total_links = sum(len(r.get("links", [])) for r in successful)
        
        return {
            "total_urls": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": (len(successful) / len(results)) * 100 if results else 0,
            "total_content_length": total_content_length,
            "total_links_found": total_links,
            "average_content_length": total_content_length / len(successful) if successful else 0,
            "urls_by_type": self._group_urls_by_type(successful)
        }
    
    def _group_urls_by_type(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group URLs by type"""
        type_counts = {}
        for result in results:
            url_info = result.get("url_info", {})
            url_type = url_info.get("type", "unknown")
            type_counts[url_type] = type_counts.get(url_type, 0) + 1
        return type_counts
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current scraping statistics"""
        current_time = datetime.now()
        runtime = (current_time - self.stats["start_time"]).total_seconds()
        
        return {
            "runtime_seconds": runtime,
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": (self.stats["successful_requests"] / max(1, self.stats["total_requests"])) * 100,
            "requests_per_minute": (self.stats["total_requests"] / max(1, runtime)) * 60,
            "total_content_length": self.stats["total_content_length"],
            "unique_urls_scraped": len(self.stats["scraped_urls"]),
            "error_count": len(self.stats["errors"]),
            "start_time": self.stats["start_time"].isoformat(),
            "current_time": current_time.isoformat()
        }
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimize scraping performance based on current metrics"""
        stats = self.get_stats()
        
        optimizations = []
        
        # Check success rate
        if stats["success_rate"] < 90:
            optimizations.append("Reduce request rate to improve success rate")
        
        # Check throughput
        if stats["requests_per_minute"] < 30:
            optimizations.append("Increase concurrency to improve throughput")
        
        # Check error rate
        if stats["error_count"] > stats["total_requests"] * 0.1:
            optimizations.append("Add more retry logic and error handling")
        
        if not optimizations:
            optimizations.append("Performance is optimal")
        
        return {
            "current_metrics": stats,
            "optimizations": optimizations,
            "recommendations": self._generate_recommendations(stats)
        }
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if stats["success_rate"] < 95:
            recommendations.append("Consider using different scraping engines for different sites")
        
        if stats["requests_per_minute"] < 50:
            recommendations.append("Increase max_concurrent_requests setting")
        
        if stats["error_count"] > 0:
            recommendations.append("Implement exponential backoff for failed requests")
        
        return recommendations

async def main():
    """Main entry point"""
    scraper = MotiaDocsScraper()
    
    try:
        logger.info("Starting Motia Documentation Scraper")
        
        # Process all Motia documentation
        results = await scraper.process_motia_docs()
        
        # Print summary
        print("\n" + "="*80)
        print("MOTIA DOCUMENTATION SCRAPING COMPLETED")
        print("="*80)
        print(f"Total URLs processed: {results['summary']['total_urls']}")
        print(f"Successful: {results['summary']['successful']}")
        print(f"Failed: {results['summary']['failed']}")
        print(f"Success rate: {results['summary']['success_rate']:.1f}%")
        print(f"Total content length: {results['summary']['total_content_length']:,} characters")
        print(f"Total links found: {results['summary']['total_links_found']}")
        print(f"Average content length: {results['summary']['average_content_length']:.0f} characters")
        print("\nURLs by type:")
        for url_type, count in results['summary']['urls_by_type'].items():
            print(f"  {url_type}: {count}")
        
        # Performance optimization
        optimization = await scraper.optimize_performance()
        print(f"\nPerformance optimizations:")
        for opt in optimization['optimizations']:
            print(f"  - {opt}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error("Fatal error in main", error=str(e))
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())