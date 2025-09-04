"""
Playwright-based scraper for Flyde documentation.
"""
import asyncio
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Browser, Page
import structlog

from .base_scraper import BaseScraper, ScrapingResult
from config.settings import settings
from config.logging import get_logger


logger = get_logger(__name__)


class PlaywrightScraper(BaseScraper):
    """Playwright-powered scraper for Flyde documentation."""
    
    def __init__(self):
        super().__init__("playwright")
        self.browser: Optional[Browser] = None
        self.context = None
        self._initialized = False
    
    async def _initialize(self):
        """Initialize Playwright browser."""
        if self._initialized:
            return
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            self.context = await self.browser.new_context(
                user_agent=settings.user_agents[0],
                viewport={'width': 1920, 'height': 1080}
            )
            self._initialized = True
            self.logger.info("Playwright browser initialized successfully")
        except Exception as e:
            self.logger.error("Failed to initialize Playwright", error=str(e))
            raise
    
    async def _cleanup(self):
        """Clean up Playwright resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def scrape_url(self, url: str, **kwargs) -> ScrapingResult:
        """Scrape a single URL using Playwright."""
        await self._initialize()
        
        self.session_count += 1
        page = None
        
        try:
            page = await self.context.new_page()
            
            # Set timeout
            page.set_default_timeout(settings.timeout * 1000)
            
            # Navigate to URL
            response = await page.goto(url, wait_until='networkidle')
            
            if not response:
                self.error_count += 1
                return ScrapingResult(
                    url=url,
                    content="",
                    error="No response received"
                )
            
            # Wait for content to load
            await page.wait_for_load_state('domcontentloaded')
            
            # Get page content
            content = await page.content()
            
            # Extract additional metadata
            metadata = await self._extract_page_metadata(page)
            
            # Check for JavaScript errors
            js_errors = await self._get_js_errors(page)
            if js_errors:
                metadata['js_errors'] = js_errors
            
            self.success_count += 1
            return ScrapingResult(
                url=url,
                content=content,
                status_code=response.status,
                headers=dict(response.headers),
                metadata=metadata
            )
        
        except Exception as e:
            self.error_count += 1
            self.logger.error("Playwright scraping failed", url=url, error=str(e))
            return ScrapingResult(
                url=url,
                content="",
                error=f"Playwright exception: {str(e)}"
            )
        finally:
            if page:
                await page.close()
    
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrape multiple URLs using Playwright."""
        await self._initialize()
        
        results = []
        semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
        
        async def scrape_with_semaphore(url: str) -> ScrapingResult:
            async with semaphore:
                return await self.scrape_url(url)
        
        # Create tasks for all URLs
        tasks = [scrape_with_semaphore(url) for url in urls]
        
        # Execute all tasks
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                self.error_count += 1
                results.append(ScrapingResult(
                    url=urls[i],
                    content="",
                    error=f"Task exception: {str(result)}"
                ))
            else:
                results.append(result)
        
        self.session_count += len(urls)
        return results
    
    async def _extract_page_metadata(self, page: Page) -> Dict[str, Any]:
        """Extract metadata from the page."""
        metadata = {}
        
        try:
            # Get page title
            metadata['title'] = await page.title()
            
            # Get meta tags
            meta_tags = await page.query_selector_all('meta')
            for meta in meta_tags:
                name = await meta.get_attribute('name')
                property_attr = await meta.get_attribute('property')
                content = await meta.get_attribute('content')
                
                if name == 'description':
                    metadata['description'] = content
                elif name == 'keywords':
                    metadata['keywords'] = content
                elif property_attr == 'og:title':
                    metadata['og_title'] = content
                elif property_attr == 'og:description':
                    metadata['og_description'] = content
            
            # Get page dimensions
            viewport = await page.viewport_size()
            if viewport:
                metadata['viewport'] = viewport
            
            # Get page URL (in case of redirects)
            metadata['final_url'] = page.url
            
        except Exception as e:
            self.logger.error("Failed to extract page metadata", error=str(e))
        
        return metadata
    
    async def _get_js_errors(self, page: Page) -> List[str]:
        """Get JavaScript errors from the page."""
        errors = []
        
        try:
            # Listen for console errors
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            
            # Wait a bit for any errors to appear
            await asyncio.sleep(1)
            
        except Exception as e:
            self.logger.error("Failed to get JS errors", error=str(e))
        
        return errors
    
    async def scrape_with_screenshot(self, url: str, screenshot_path: str) -> ScrapingResult:
        """Scrape URL and take a screenshot."""
        await self._initialize()
        
        page = None
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until='networkidle')
            
            # Take screenshot
            await page.screenshot(path=screenshot_path, full_page=True)
            
            # Get content
            content = await page.content()
            
            return ScrapingResult(
                url=url,
                content=content,
                metadata={'screenshot_path': screenshot_path}
            )
        
        finally:
            if page:
                await page.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup()