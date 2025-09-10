"""
Main entry point for the Flyde documentation scraper.
"""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import structlog

from config.settings import settings
from config.logging import configure_logging, get_logger
from scrapers.scrapfly_scraper import ScrapflyScraper
from scrapers.playwright_scraper import PlaywrightScraper
from scrapers.scrapy_scraper import ScrapyScraper


# Configure logging
configure_logging()
logger = get_logger(__name__)


class FlydeDocsScraper:
    """Main orchestrator for Flyde documentation scraping."""
    
    def __init__(self):
        self.scrapers = {
            "scrapfly": ScrapflyScraper(),
            "playwright": PlaywrightScraper(),
            "scrapy": ScrapyScraper()
        }
        self.data_dir = Path(settings.data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize Sentry if configured
        if settings.sentry_dsn:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.sentry_environment,
                traces_sample_rate=1.0,
            )
            logger.info("Sentry initialized")
    
    async def scrape_flyde_docs(self, scraper_name: str = "scrapfly") -> Dict[str, Any]:
        """Scrape the main Flyde documentation site."""
        logger.info("Starting Flyde documentation scraping", scraper=scraper_name)
        
        if scraper_name not in self.scrapers:
            raise ValueError(f"Unknown scraper: {scraper_name}")
        
        scraper = self.scrapers[scraper_name]
        
        # Start with the main docs page
        main_docs_result = await scraper.scrape_url(settings.docs_url)
        
        if not main_docs_result.is_success():
            logger.error("Failed to scrape main docs page", error=main_docs_result.error)
            return {"error": main_docs_result.error}
        
        # Extract links from the main page
        links = scraper.extract_links(main_docs_result.content, settings.docs_url)
        logger.info("Extracted links from main page", count=len(links))
        
        # Scrape all discovered pages
        results = await scraper.scrape_multiple(links)
        
        # Process and save results
        processed_results = []
        for result in results:
            if result.is_success():
                processed_result = self._process_result(result)
                processed_results.append(processed_result)
            else:
                logger.warning("Failed to scrape page", url=result.url, error=result.error)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f"flyde_docs_{scraper_name}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "scraper": scraper_name,
                    "timestamp": timestamp,
                    "total_pages": len(results),
                    "successful_pages": len(processed_results),
                    "failed_pages": len(results) - len(processed_results)
                },
                "results": processed_results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info("Scraping completed", 
                  output_file=str(output_file),
                  total_pages=len(results),
                  successful_pages=len(processed_results))
        
        return {
            "output_file": str(output_file),
            "total_pages": len(results),
            "successful_pages": len(processed_results),
            "failed_pages": len(results) - len(processed_results)
        }
    
    def _process_result(self, result) -> Dict[str, Any]:
        """Process a scraping result."""
        # Extract clean text
        text_content = result.content
        if result.content.startswith('<'):
            # It's HTML, extract text
            text_content = self.scrapers["scrapfly"].extract_text_content(result.content)
        
        # Extract metadata
        metadata = {}
        if result.content.startswith('<'):
            metadata = self.scrapers["scrapfly"].extract_metadata(result.content, result.url)
        
        return {
            "url": result.url,
            "title": metadata.get("title", ""),
            "description": metadata.get("description", ""),
            "text_content": text_content,
            "html_content": result.content if result.content.startswith('<') else "",
            "metadata": metadata,
            "scraping_metadata": {
                "status_code": result.status_code,
                "timestamp": result.timestamp,
                "headers": result.headers
            }
        }
    
    async def hello_world_example(self) -> Dict[str, Any]:
        """Run a hello world example scraping."""
        logger.info("Running hello world example")
        
        # Test URL - the Flyde playground
        test_url = "https://flyde.dev/playground/blog-generator"
        
        # Try each scraper
        results = {}
        for scraper_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Testing {scraper_name} scraper")
                result = await scraper.scrape_url(test_url)
                results[scraper_name] = {
                    "success": result.is_success(),
                    "status_code": result.status_code,
                    "content_length": len(result.content),
                    "error": result.error
                }
                
                if result.is_success():
                    # Extract some basic info
                    text_content = scraper.extract_text_content(result.content)
                    results[scraper_name]["text_preview"] = text_content[:200] + "..." if len(text_content) > 200 else text_content
                
            except Exception as e:
                logger.error(f"Error testing {scraper_name}", error=str(e))
                results[scraper_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f"hello_world_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_url": test_url,
                "timestamp": timestamp,
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info("Hello world example completed", output_file=str(output_file))
        
        return {
            "test_url": test_url,
            "output_file": str(output_file),
            "results": results
        }
    
    async def run_comprehensive_scraping(self) -> Dict[str, Any]:
        """Run comprehensive scraping of all Flyde documentation."""
        logger.info("Starting comprehensive Flyde documentation scraping")
        
        start_time = time.time()
        
        # Define target URLs
        target_urls = [
            settings.docs_url,
            "https://flyde.dev/docs/introduction",
            "https://flyde.dev/docs/core-concepts",
            "https://flyde.dev/docs/built-in-nodes",
            "https://flyde.dev/docs/integrate-flows",
            "https://flyde.dev/docs/custom-nodes",
            "https://flyde.dev/docs/testing-deployment-troubleshooting",
            "https://flyde.dev/docs/advanced-concepts",
            "https://flyde.dev/docs/third-party-nodes",
            "https://flyde.dev/docs/faq",
            "https://flyde.dev/playground",
            "https://flyde.dev/playground/blog-generator",
            "https://github.com/flydelabs/flyde",
            "https://github.com/flydelabs/flyde/blob/main/README.md"
        ]
        
        all_results = {}
        
        # Test each scraper
        for scraper_name in self.scrapers.keys():
            logger.info(f"Testing {scraper_name} scraper")
            
            try:
                scraper = self.scrapers[scraper_name]
                results = await scraper.scrape_multiple(target_urls)
                
                all_results[scraper_name] = {
                    "total_urls": len(target_urls),
                    "successful": len([r for r in results if r.is_success()]),
                    "failed": len([r for r in results if not r.is_success()]),
                    "results": [r.to_dict() for r in results]
                }
                
            except Exception as e:
                logger.error(f"Error with {scraper_name} scraper", error=str(e))
                all_results[scraper_name] = {
                    "error": str(e)
                }
        
        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f"comprehensive_scraping_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "timestamp": timestamp,
                    "duration_seconds": time.time() - start_time,
                    "target_urls": target_urls
                },
                "results": all_results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info("Comprehensive scraping completed", 
                  output_file=str(output_file),
                  duration_seconds=time.time() - start_time)
        
        return {
            "output_file": str(output_file),
            "duration_seconds": time.time() - start_time,
            "results": all_results
        }


async def main():
    """Main entry point."""
    scraper = FlydeDocsScraper()
    
    # Run hello world example
    print("🚀 Running Hello World Example...")
    hello_world_result = await scraper.hello_world_example()
    print(f"✅ Hello World completed! Results saved to: {hello_world_result['output_file']}")
    
    # Run comprehensive scraping
    print("\n📚 Running Comprehensive Scraping...")
    comprehensive_result = await scraper.run_comprehensive_scraping()
    print(f"✅ Comprehensive scraping completed! Results saved to: {comprehensive_result['output_file']}")
    
    # Print summary
    print("\n📊 Summary:")
    for scraper_name, result in comprehensive_result['results'].items():
        if 'error' not in result:
            success_rate = (result['successful'] / result['total_urls']) * 100
            print(f"  {scraper_name}: {result['successful']}/{result['total_urls']} ({success_rate:.1f}%)")
        else:
            print(f"  {scraper_name}: Error - {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())