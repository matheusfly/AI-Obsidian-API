"""
Playwright-based Scraper for Motia Documentation Scraper
Advanced browser automation with JavaScript rendering
"""

import asyncio
import time
from typing import Dict, Any, Optional
from pathlib import Path
import structlog

from .base_scraper import BaseScraper

logger = structlog.get_logger("playwright-scraper")

class PlaywrightScraper(BaseScraper):
    """Playwright-based scraper with JavaScript rendering"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, 
                 headless: bool = True, browser: str = "chromium"):
        super().__init__("playwright", timeout, max_retries)
        self.headless = headless
        self.browser = browser
        self.browser_instance = None
        self.context = None
        self.page = None
    
    async def _get_browser(self):
        """Get or create browser instance"""
        if self.browser_instance is None:
            try:
                from playwright.async_api import async_playwright
                self.playwright = await async_playwright().start()
                
                # Launch browser
                if self.browser == "chromium":
                    self.browser_instance = await self.playwright.chromium.launch(
                        headless=self.headless,
                        args=[
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-gpu",
                            "--disable-web-security",
                            "--disable-features=VizDisplayCompositor"
                        ]
                    )
                elif self.browser == "firefox":
                    self.browser_instance = await self.playwright.firefox.launch(
                        headless=self.headless
                    )
                elif self.browser == "webkit":
                    self.browser_instance = await self.playwright.webkit.launch(
                        headless=self.headless
                    )
                else:
                    raise ValueError(f"Unsupported browser: {self.browser}")
                
                logger.info("Browser launched", browser=self.browser, headless=self.headless)
                
            except ImportError:
                logger.error("Playwright not installed. Install with: pip install playwright")
                raise Exception("Playwright not available")
            except Exception as e:
                logger.error("Failed to launch browser", error=str(e))
                raise
    
    async def _get_page(self):
        """Get or create page instance"""
        if self.page is None:
            await self._get_browser()
            
            # Create context
            self.context = await self.browser_instance.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="MotiaDocsScraper/1.0 (Educational Research)",
                ignore_https_errors=True
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set up page event handlers
            self.page.on("response", self._handle_response)
            self.page.on("request", self._handle_request)
            
            logger.info("Page created", browser=self.browser)
    
    async def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape URL using Playwright"""
        await self._get_page()
        
        try:
            logger.info("Navigating to URL", url=url, scraper=self.name)
            
            # Navigate to URL
            response = await self.page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
            
            # Wait for specific element if requested
            wait_for_element = kwargs.get("wait_for_element")
            if wait_for_element:
                logger.info("Waiting for element", selector=wait_for_element)
                await self.page.wait_for_selector(wait_for_element, timeout=10000)
            
            # Wait for additional time if requested
            wait_time = kwargs.get("wait_time", 0)
            if wait_time > 0:
                logger.info("Waiting additional time", seconds=wait_time)
                await asyncio.sleep(wait_time)
            
            # Take screenshot if requested
            screenshot_path = None
            if kwargs.get("take_screenshot", False):
                screenshot_path = await self._take_screenshot(url)
            
            # Get page content
            html = await self.page.content()
            
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
            
            # Get page title
            title = await self.page.title()
            
            # Get page URL (in case of redirects)
            final_url = self.page.url
            
            # Get console logs
            console_logs = await self.page.evaluate("() => window.console.logs || []")
            
            # Get performance metrics
            performance_metrics = await self.page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        loadTime: navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0,
                        domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart : 0,
                        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
                    };
                }
            """)
            
            result = {
                "url": url,
                "final_url": final_url,
                "status_code": response.status if response else 200,
                "title": title,
                "content": html,
                "html": html,
                "text": text,
                "links": links,
                "metadata": metadata,
                "structured_data": structured_data,
                "content_length": len(html),
                "text_length": len(text),
                "links_count": len(links),
                "screenshot_path": screenshot_path,
                "console_logs": console_logs,
                "performance_metrics": performance_metrics,
                "browser": self.browser,
                "headless": self.headless
            }
            
            logger.info("Playwright scraping successful", 
                       url=url, 
                       final_url=final_url,
                       content_length=len(html),
                       scraper=self.name)
            
            return result
            
        except Exception as e:
            logger.error("Playwright scraping failed", url=url, error=str(e), scraper=self.name)
            raise
    
    async def _take_screenshot(self, url: str) -> str:
        """Take screenshot of the page"""
        try:
            # Create screenshots directory
            screenshots_dir = Path("data/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshots_dir / filename
            
            # Take screenshot
            await self.page.screenshot(path=str(filepath), full_page=True)
            
            logger.info("Screenshot taken", filepath=str(filepath))
            return str(filepath)
            
        except Exception as e:
            logger.error("Failed to take screenshot", error=str(e))
            return None
    
    async def _handle_response(self, response):
        """Handle response events"""
        logger.debug("Response received", 
                    url=response.url, 
                    status=response.status,
                    scraper=self.name)
    
    async def _handle_request(self, request):
        """Handle request events"""
        logger.debug("Request made", 
                    url=request.url, 
                    method=request.method,
                    scraper=self.name)
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser_instance:
                await self.browser_instance.close()
                self.browser_instance = None
            
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            logger.info("Browser closed", scraper=self.name)
            
        except Exception as e:
            logger.error("Error closing browser", error=str(e), scraper=self.name)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()