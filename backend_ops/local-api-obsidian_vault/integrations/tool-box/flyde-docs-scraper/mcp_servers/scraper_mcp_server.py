"""
MCP server for the Flyde documentation scraper.
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from mcp import ServerSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
import structlog

from config.settings import settings
from config.logging import get_logger
from scrapers.scrapfly_scraper import ScrapflyScraper
from scrapers.playwright_scraper import PlaywrightScraper
from scrapers.scrapy_scraper import ScrapyScraper


logger = get_logger(__name__)


class ScraperMCPServer:
    """MCP server for Flyde documentation scraping."""
    
    def __init__(self):
        self.server = Server("flyde-scraper-mcp")
        self.scrapers = {
            "scrapfly": ScrapflyScraper(),
            "playwright": PlaywrightScraper(),
            "scrapy": ScrapyScraper()
        }
        self._setup_server()
    
    def _setup_server(self):
        """Setup MCP server with tools."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Dict[str, Any]]:
            """List available tools."""
            return [
                {
                    "name": "scrape_url",
                    "description": "Scrape a single URL using specified scraper",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to scrape"},
                            "scraper": {
                                "type": "string", 
                                "enum": ["scrapfly", "playwright", "scrapy"],
                                "description": "Scraper to use"
                            },
                            "options": {
                                "type": "object",
                                "description": "Additional scraping options"
                            }
                        },
                        "required": ["url", "scraper"]
                    }
                },
                {
                    "name": "scrape_multiple",
                    "description": "Scrape multiple URLs using specified scraper",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "URLs to scrape"
                            },
                            "scraper": {
                                "type": "string",
                                "enum": ["scrapfly", "playwright", "scrapy"],
                                "description": "Scraper to use"
                            },
                            "options": {
                                "type": "object",
                                "description": "Additional scraping options"
                            }
                        },
                        "required": ["urls", "scraper"]
                    }
                },
                {
                    "name": "extract_links",
                    "description": "Extract links from HTML content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "HTML content"},
                            "base_url": {"type": "string", "description": "Base URL for relative links"}
                        },
                        "required": ["content", "base_url"]
                    }
                },
                {
                    "name": "extract_text",
                    "description": "Extract clean text from HTML content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "HTML content"}
                        },
                        "required": ["content"]
                    }
                },
                {
                    "name": "get_scraper_stats",
                    "description": "Get statistics for all scrapers",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Call a specific tool."""
            try:
                if name == "scrape_url":
                    return await self._scrape_url(arguments)
                elif name == "scrape_multiple":
                    return await self._scrape_multiple(arguments)
                elif name == "extract_links":
                    return await self._extract_links(arguments)
                elif name == "extract_text":
                    return await self._extract_text(arguments)
                elif name == "get_scraper_stats":
                    return await self._get_scraper_stats(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            
            except Exception as e:
                logger.error("Tool call failed", tool=name, error=str(e))
                return [{
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }]
    
    async def _scrape_url(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape a single URL."""
        url = args["url"]
        scraper_name = args["scraper"]
        options = args.get("options", {})
        
        if scraper_name not in self.scrapers:
            raise ValueError(f"Unknown scraper: {scraper_name}")
        
        scraper = self.scrapers[scraper_name]
        result = await scraper.scrape_url(url, **options)
        
        return [{
            "type": "text",
            "text": json.dumps(result.to_dict(), indent=2)
        }]
    
    async def _scrape_multiple(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs."""
        urls = args["urls"]
        scraper_name = args["scraper"]
        options = args.get("options", {})
        
        if scraper_name not in self.scrapers:
            raise ValueError(f"Unknown scraper: {scraper_name}")
        
        scraper = self.scrapers[scraper_name]
        results = await scraper.scrape_multiple(urls, **options)
        
        return [{
            "type": "text",
            "text": json.dumps([r.to_dict() for r in results], indent=2)
        }]
    
    async def _extract_links(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract links from HTML content."""
        content = args["content"]
        base_url = args["base_url"]
        
        # Use any scraper to extract links (they all have the same method)
        scraper = self.scrapers["scrapfly"]
        links = scraper.extract_links(content, base_url)
        
        return [{
            "type": "text",
            "text": json.dumps({"links": links}, indent=2)
        }]
    
    async def _extract_text(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract clean text from HTML content."""
        content = args["content"]
        
        # Use any scraper to extract text
        scraper = self.scrapers["scrapfly"]
        text = scraper.extract_text_content(content)
        
        return [{
            "type": "text",
            "text": json.dumps({"text": text}, indent=2)
        }]
    
    async def _get_scraper_stats(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get statistics for all scrapers."""
        stats = {}
        for name, scraper in self.scrapers.items():
            stats[name] = {
                "sessions": scraper.session_count,
                "successes": scraper.success_count,
                "errors": scraper.error_count,
                "success_rate": scraper.success_count / max(1, scraper.session_count) * 100
            }
        
        return [{
            "type": "text",
            "text": json.dumps(stats, indent=2)
        }]
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            async with ServerSession(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="flyde-scraper-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            ) as session:
                await self.server.run(session)


async def main():
    """Main entry point."""
    server = ScraperMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())