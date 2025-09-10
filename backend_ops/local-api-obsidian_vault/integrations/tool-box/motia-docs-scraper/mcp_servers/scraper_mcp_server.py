#!/usr/bin/env python3
"""
Motia Documentation Scraper MCP Server
Advanced MCP integration with performance monitoring and active debugging
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
import aiofiles
from pathlib import Path

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("motia-scraper-mcp")

class MotiaScraperMCPServer:
    """Advanced MCP server for Motia documentation scraping"""
    
    def __init__(self):
        self.server = Server("motia-scraper")
        self.setup_handlers()
        self.scraping_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "start_time": datetime.now(),
            "active_scrapers": {}
        }
        
    def setup_handlers(self):
        """Setup MCP handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available scraping tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="scrape_url",
                        description="Scrape a single URL with advanced options",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to scrape"
                                },
                                "scraper_type": {
                                    "type": "string",
                                    "enum": ["scrapfly", "playwright", "scrapy", "requests"],
                                    "description": "Scraping engine to use"
                                },
                                "extract_links": {
                                    "type": "boolean",
                                    "description": "Extract all links from the page"
                                },
                                "extract_text": {
                                    "type": "boolean",
                                    "description": "Extract clean text content"
                                },
                                "take_screenshot": {
                                    "type": "boolean",
                                    "description": "Take a screenshot of the page"
                                },
                                "wait_for_element": {
                                    "type": "string",
                                    "description": "CSS selector to wait for before scraping"
                                }
                            },
                            "required": ["url"]
                        }
                    ),
                    Tool(
                        name="scrape_multiple_urls",
                        description="Scrape multiple URLs with parallel processing",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "urls": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of URLs to scrape"
                                },
                                "scraper_type": {
                                    "type": "string",
                                    "enum": ["scrapfly", "playwright", "scrapy", "requests"],
                                    "description": "Scraping engine to use"
                                },
                                "max_concurrent": {
                                    "type": "integer",
                                    "description": "Maximum concurrent requests"
                                },
                                "delay_between_requests": {
                                    "type": "number",
                                    "description": "Delay between requests in seconds"
                                }
                            },
                            "required": ["urls"]
                        }
                    ),
                    Tool(
                        name="crawl_documentation_site",
                        description="Crawl entire documentation site with pagination",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "base_url": {
                                    "type": "string",
                                    "description": "Base URL of the documentation site"
                                },
                                "max_depth": {
                                    "type": "integer",
                                    "description": "Maximum crawl depth"
                                },
                                "follow_external_links": {
                                    "type": "boolean",
                                    "description": "Whether to follow external links"
                                },
                                "content_filters": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "CSS selectors to filter content"
                                }
                            },
                            "required": ["base_url"]
                        }
                    ),
                    Tool(
                        name="analyze_content",
                        description="Analyze scraped content with AI",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "Content to analyze"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "enum": ["summary", "extract_keywords", "extract_entities", "classify", "sentiment"],
                                    "description": "Type of analysis to perform"
                                },
                                "context": {
                                    "type": "string",
                                    "description": "Additional context for analysis"
                                }
                            },
                            "required": ["content", "analysis_type"]
                        }
                    ),
                    Tool(
                        name="get_scraping_stats",
                        description="Get current scraping statistics and performance metrics",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "detailed": {
                                    "type": "boolean",
                                    "description": "Include detailed statistics"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="optimize_scraping",
                        description="Optimize scraping performance based on current metrics",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "target_throughput": {
                                    "type": "integer",
                                    "description": "Target requests per minute"
                                },
                                "max_errors": {
                                    "type": "integer",
                                    "description": "Maximum acceptable error rate"
                                }
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "scrape_url":
                    return await self.scrape_url(arguments)
                elif name == "scrape_multiple_urls":
                    return await self.scrape_multiple_urls(arguments)
                elif name == "crawl_documentation_site":
                    return await self.crawl_documentation_site(arguments)
                elif name == "analyze_content":
                    return await self.analyze_content(arguments)
                elif name == "get_scraping_stats":
                    return await self.get_scraping_stats(arguments)
                elif name == "optimize_scraping":
                    return await self.optimize_scraping(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def scrape_url(self, args: Dict[str, Any]) -> CallToolResult:
        """Scrape a single URL with advanced options"""
        url = args["url"]
        scraper_type = args.get("scraper_type", "requests")
        extract_links = args.get("extract_links", True)
        extract_text = args.get("extract_text", True)
        take_screenshot = args.get("take_screenshot", False)
        wait_for_element = args.get("wait_for_element")
        
        logger.info(f"Scraping URL: {url} with {scraper_type}")
        
        try:
            # Update stats
            self.scraping_stats["total_requests"] += 1
            
            # Perform scraping based on type
            if scraper_type == "requests":
                result = await self._scrape_with_requests(url)
            elif scraper_type == "playwright":
                result = await self._scrape_with_playwright(url, wait_for_element, take_screenshot)
            elif scraper_type == "scrapfly":
                result = await self._scrape_with_scrapfly(url)
            else:
                result = await self._scrape_with_requests(url)
            
            # Process content
            if extract_text and "html" in result:
                result["text"] = self._extract_text(result["html"])
            
            if extract_links and "html" in result:
                result["links"] = self._extract_links(result["html"], url)
            
            # Add metadata
            result["metadata"] = {
                "scraper_type": scraper_type,
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "status_code": result.get("status_code", 200)
            }
            
            # Save result
            await self._save_result(result, url)
            
            self.scraping_stats["successful_requests"] += 1
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Successfully scraped {url}\nContent length: {len(result.get('html', ''))}\nText length: {len(result.get('text', ''))}\nLinks found: {len(result.get('links', []))}"
                )]
            )
            
        except Exception as e:
            self.scraping_stats["failed_requests"] += 1
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to scrape {url}: {str(e)}")],
                isError=True
            )
    
    async def scrape_multiple_urls(self, args: Dict[str, Any]) -> CallToolResult:
        """Scrape multiple URLs with parallel processing"""
        urls = args["urls"]
        scraper_type = args.get("scraper_type", "requests")
        max_concurrent = args.get("max_concurrent", 5)
        delay = args.get("delay_between_requests", 1.0)
        
        logger.info(f"Scraping {len(urls)} URLs with {scraper_type}")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                await asyncio.sleep(delay)
                return await self.scrape_url({
                    "url": url,
                    "scraper_type": scraper_type,
                    "extract_links": True,
                    "extract_text": True
                })
        
        # Execute parallel scraping
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Completed scraping {len(urls)} URLs\nSuccessful: {successful}\nFailed: {failed}"
            )]
        )
    
    async def crawl_documentation_site(self, args: Dict[str, Any]) -> CallToolResult:
        """Crawl entire documentation site with pagination"""
        base_url = args["base_url"]
        max_depth = args.get("max_depth", 3)
        follow_external = args.get("follow_external_links", False)
        content_filters = args.get("content_filters", [])
        
        logger.info(f"Starting crawl of {base_url} with max depth {max_depth}")
        
        visited_urls = set()
        urls_to_visit = [base_url]
        crawled_pages = []
        
        for depth in range(max_depth):
            if not urls_to_visit:
                break
                
            current_batch = urls_to_visit.copy()
            urls_to_visit.clear()
            
            # Scrape current batch
            for url in current_batch:
                if url in visited_urls:
                    continue
                    
                visited_urls.add(url)
                
                try:
                    result = await self.scrape_url({
                        "url": url,
                        "scraper_type": "playwright",
                        "extract_links": True,
                        "extract_text": True
                    })
                    
                    crawled_pages.append({
                        "url": url,
                        "depth": depth,
                        "content_length": len(result.content[0].text) if result.content else 0
                    })
                    
                    # Extract new URLs to visit
                    if result.content:
                        # This would need to be implemented to extract links from content
                        pass
                        
                except Exception as e:
                    logger.error(f"Failed to crawl {url}: {str(e)}")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Crawled {len(crawled_pages)} pages from {base_url}\nMax depth reached: {max_depth}"
            )]
        )
    
    async def analyze_content(self, args: Dict[str, Any]) -> CallToolResult:
        """Analyze scraped content with AI"""
        content = args["content"]
        analysis_type = args["analysis_type"]
        context = args.get("context", "")
        
        logger.info(f"Analyzing content with {analysis_type}")
        
        # This would integrate with Context7 or other AI services
        # For now, return basic analysis
        analysis_result = {
            "type": analysis_type,
            "content_length": len(content),
            "word_count": len(content.split()),
            "analysis": f"Basic {analysis_type} analysis of {len(content)} characters"
        }
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Analysis Result:\n{json.dumps(analysis_result, indent=2)}"
            )]
        )
    
    async def get_scraping_stats(self, args: Dict[str, Any]) -> CallToolResult:
        """Get current scraping statistics"""
        detailed = args.get("detailed", False)
        
        current_time = datetime.now()
        runtime = (current_time - self.scraping_stats["start_time"]).total_seconds()
        
        stats = {
            "total_requests": self.scraping_stats["total_requests"],
            "successful_requests": self.scraping_stats["successful_requests"],
            "failed_requests": self.scraping_stats["failed_requests"],
            "success_rate": (self.scraping_stats["successful_requests"] / max(1, self.scraping_stats["total_requests"])) * 100,
            "runtime_seconds": runtime,
            "requests_per_minute": (self.scraping_stats["total_requests"] / max(1, runtime)) * 60
        }
        
        if detailed:
            stats.update({
                "active_scrapers": self.scraping_stats["active_scrapers"],
                "start_time": self.scraping_stats["start_time"].isoformat(),
                "current_time": current_time.isoformat()
            })
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Scraping Statistics:\n{json.dumps(stats, indent=2)}"
            )]
        )
    
    async def optimize_scraping(self, args: Dict[str, Any]) -> CallToolResult:
        """Optimize scraping performance"""
        target_throughput = args.get("target_throughput", 60)
        max_errors = args.get("max_errors", 5)
        
        current_rpm = (self.scraping_stats["total_requests"] / max(1, (datetime.now() - self.scraping_stats["start_time"]).total_seconds())) * 60
        current_error_rate = (self.scraping_stats["failed_requests"] / max(1, self.scraping_stats["total_requests"])) * 100
        
        optimizations = []
        
        if current_rpm < target_throughput:
            optimizations.append(f"Increase concurrency to reach {target_throughput} RPM")
        
        if current_error_rate > max_errors:
            optimizations.append(f"Reduce request rate to lower error rate below {max_errors}%")
        
        if not optimizations:
            optimizations.append("Performance is optimal")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Optimization Recommendations:\n" + "\n".join(f"- {opt}" for opt in optimizations)
            )]
        )
    
    async def _scrape_with_requests(self, url: str) -> Dict[str, Any]:
        """Scrape using requests library"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            return {
                "html": response.text,
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
    
    async def _scrape_with_playwright(self, url: str, wait_for: Optional[str] = None, screenshot: bool = False) -> Dict[str, Any]:
        """Scrape using Playwright (placeholder)"""
        # This would use Playwright for JavaScript rendering
        return await self._scrape_with_requests(url)
    
    async def _scrape_with_scrapfly(self, url: str) -> Dict[str, Any]:
        """Scrape using Scrapfly (placeholder)"""
        # This would use Scrapfly API
        return await self._scrape_with_requests(url)
    
    def _extract_text(self, html: str) -> str:
        """Extract clean text from HTML"""
        # Basic text extraction (would use BeautifulSoup in real implementation)
        import re
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML"""
        import re
        from urllib.parse import urljoin, urlparse
        
        # Find all href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(href_pattern, html)
        
        # Convert relative URLs to absolute
        absolute_links = []
        for link in links:
            if link.startswith('http'):
                absolute_links.append(link)
            else:
                absolute_links.append(urljoin(base_url, link))
        
        return absolute_links
    
    async def _save_result(self, result: Dict[str, Any], url: str) -> None:
        """Save scraping result to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scrape_result_{timestamp}.json"
        filepath = Path("data") / filename
        
        # Ensure data directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(result, indent=2, ensure_ascii=False))

async def main():
    """Main entry point"""
    server_instance = MotiaScraperMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="motia-scraper",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())