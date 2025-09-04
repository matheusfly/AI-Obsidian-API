"""
ChartDB Comprehensive Documentation Scraper
Advanced scraper with full pagination coverage and custom features
"""

import asyncio
import aiohttp
import json
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
import logging

from config.settings import settings, URL_PATTERNS, PAGINATION_PATTERNS, CONTENT_PATTERNS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedContent:
    """Data class for scraped content"""
    url: str
    title: str
    content: str
    content_type: str
    metadata: Dict[str, Any]
    diagrams: List[Dict[str, Any]]
    templates: List[Dict[str, Any]]
    code_blocks: List[Dict[str, Any]]
    links: List[str]
    timestamp: datetime

class ChartDBScraper:
    """Advanced ChartDB documentation scraper with comprehensive pagination"""
    
    def __init__(self):
        self.session = None
        self.scraped_urls = set()
        self.scraped_content = []
        self.pagination_cache = {}
        self.diagram_cache = {}
        self.template_cache = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=settings.max_concurrent_requests)
        timeout = aiohttp.ClientTimeout(total=settings.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def scrape_all(self) -> List[ScrapedContent]:
        """Scrape all ChartDB documentation with full pagination"""
        logger.info("Starting comprehensive ChartDB documentation scraping")
        
        all_content = []
        
        # Scrape main site with pagination
        main_content = await self._scrape_section_with_pagination("main_site")
        all_content.extend(main_content)
        
        # Scrape documentation with pagination
        docs_content = await self._scrape_section_with_pagination("documentation")
        all_content.extend(docs_content)
        
        # Scrape API documentation
        api_content = await self._scrape_api_documentation()
        all_content.extend(api_content)
        
        # Scrape GitHub content
        github_content = await self._scrape_github_content()
        all_content.extend(github_content)
        
        # Extract diagrams from all content
        await self._extract_all_diagrams(all_content)
        
        # Extract templates from all content
        await self._extract_all_templates(all_content)
        
        # Process and enhance content
        enhanced_content = await self._enhance_content(all_content)
        
        self.scraped_content = enhanced_content
        logger.info(f"Scraping completed. Total pages: {len(enhanced_content)}")
        
        return enhanced_content
    
    async def _scrape_section_with_pagination(self, section: str) -> List[ScrapedContent]:
        """Scrape a section with comprehensive pagination handling"""
        logger.info(f"Scraping section: {section}")
        
        urls = URL_PATTERNS.get(section, [])
        content = []
        
        for base_url in urls:
            try:
                # Initial page scraping
                page_content = await self._scrape_page(base_url)
                if page_content:
                    content.append(page_content)
                
                # Handle pagination
                paginated_content = await self._handle_pagination(base_url)
                content.extend(paginated_content)
                
                # Handle load more buttons
                load_more_content = await self._handle_load_more(base_url)
                content.extend(load_more_content)
                
                # Handle infinite scroll
                infinite_content = await self._handle_infinite_scroll(base_url)
                content.extend(infinite_content)
                
                # Respect rate limiting
                await asyncio.sleep(settings.page_delay)
                
            except Exception as e:
                logger.error(f"Error scraping {base_url}: {e}")
                continue
        
        return content
    
    async def _scrape_page(self, url: str) -> Optional[ScrapedContent]:
        """Scrape a single page"""
        if url in self.scraped_urls:
            return None
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract basic content
                    title = self._extract_title(soup)
                    content = self._extract_content(soup)
                    content_type = self._determine_content_type(url, soup)
                    
                    # Extract specific elements
                    diagrams = self._extract_diagrams(soup, url)
                    templates = self._extract_templates(soup, url)
                    code_blocks = self._extract_code_blocks(soup)
                    links = self._extract_links(soup, url)
                    
                    # Create metadata
                    metadata = {
                        'url': url,
                        'title': title,
                        'content_type': content_type,
                        'response_status': response.status,
                        'content_length': len(content),
                        'diagram_count': len(diagrams),
                        'template_count': len(templates),
                        'code_block_count': len(code_blocks),
                        'link_count': len(links),
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    scraped_content = ScrapedContent(
                        url=url,
                        title=title,
                        content=content,
                        content_type=content_type,
                        metadata=metadata,
                        diagrams=diagrams,
                        templates=templates,
                        code_blocks=code_blocks,
                        links=links,
                        timestamp=datetime.now()
                    )
                    
                    self.scraped_urls.add(url)
                    return scraped_content
                    
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            return None
    
    async def _handle_pagination(self, base_url: str) -> List[ScrapedContent]:
        """Handle standard pagination"""
        content = []
        current_page = 1
        max_pages = settings.max_pages_per_section
        
        while current_page <= max_pages:
            try:
                # Construct paginated URL
                paginated_url = self._construct_paginated_url(base_url, current_page)
                
                # Scrape the page
                page_content = await self._scrape_page(paginated_url)
                if not page_content:
                    break
                
                content.append(page_content)
                
                # Check if there's a next page
                has_next = await self._has_next_page(page_content)
                if not has_next:
                    break
                
                current_page += 1
                await asyncio.sleep(settings.page_delay)
                
            except Exception as e:
                logger.error(f"Error handling pagination for {base_url}: {e}")
                break
        
        return content
    
    async def _handle_load_more(self, base_url: str) -> List[ScrapedContent]:
        """Handle load more buttons and AJAX pagination"""
        content = []
        
        try:
            # Get initial page
            page_content = await self._scrape_page(base_url)
            if not page_content:
                return content
            
            content.append(page_content)
            
            # Look for load more buttons
            soup = BeautifulSoup(page_content.content, 'html.parser')
            load_more_selectors = PAGINATION_PATTERNS["load_more"]["load_more"]
            
            load_more_buttons = soup.select(load_more_selectors)
            
            for button in load_more_buttons:
                try:
                    # Extract load more URL or data attributes
                    load_url = self._extract_load_more_url(button, base_url)
                    if load_url:
                        # Scrape the loaded content
                        loaded_content = await self._scrape_page(load_url)
                        if loaded_content:
                            content.append(loaded_content)
                            
                except Exception as e:
                    logger.error(f"Error handling load more button: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error handling load more for {base_url}: {e}")
        
        return content
    
    async def _handle_infinite_scroll(self, base_url: str) -> List[ScrapedContent]:
        """Handle infinite scroll pagination"""
        content = []
        
        try:
            # This would require browser automation (Playwright/Selenium)
            # For now, we'll simulate by checking for common infinite scroll patterns
            page_content = await self._scrape_page(base_url)
            if not page_content:
                return content
            
            content.append(page_content)
            
            # Look for infinite scroll indicators
            soup = BeautifulSoup(page_content.content, 'html.parser')
            infinite_scroll_selectors = PAGINATION_PATTERNS["load_more"]["infinite_scroll"]
            
            infinite_elements = soup.select(infinite_scroll_selectors)
            
            if infinite_elements:
                # Simulate scrolling by checking for data attributes
                for element in infinite_elements:
                    scroll_url = element.get('data-url') or element.get('data-load-url')
                    if scroll_url:
                        scroll_url = urljoin(base_url, scroll_url)
                        scroll_content = await self._scrape_page(scroll_url)
                        if scroll_content:
                            content.append(scroll_content)
                            
        except Exception as e:
            logger.error(f"Error handling infinite scroll for {base_url}: {e}")
        
        return content
    
    async def _scrape_api_documentation(self) -> List[ScrapedContent]:
        """Scrape API documentation with pagination"""
        content = []
        
        for endpoint in settings.api_endpoints.values():
            api_url = f"{settings.api_base_url}{endpoint}"
            
            try:
                # Scrape API endpoint documentation
                page_content = await self._scrape_page(api_url)
                if page_content:
                    content.append(page_content)
                
                # Handle API pagination if present
                paginated_content = await self._handle_api_pagination(api_url)
                content.extend(paginated_content)
                
            except Exception as e:
                logger.error(f"Error scraping API endpoint {api_url}: {e}")
                continue
        
        return content
    
    async def _handle_api_pagination(self, api_url: str) -> List[ScrapedContent]:
        """Handle API-specific pagination"""
        content = []
        page = 1
        per_page = 50  # Common API pagination size
        
        while page <= settings.max_pages_per_section:
            try:
                # Construct paginated API URL
                paginated_url = f"{api_url}?page={page}&per_page={per_page}"
                
                async with self.session.get(paginated_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if there's more data
                        if not data or len(data) == 0:
                            break
                        
                        # Create content from API response
                        api_content = self._create_content_from_api_response(
                            paginated_url, data, page
                        )
                        content.append(api_content)
                        
                        # Check for next page indicator
                        if 'next' not in data or not data['next']:
                            break
                        
                        page += 1
                        await asyncio.sleep(settings.page_delay)
                    else:
                        break
                        
            except Exception as e:
                logger.error(f"Error handling API pagination for {api_url}: {e}")
                break
        
        return content
    
    async def _scrape_github_content(self) -> List[ScrapedContent]:
        """Scrape GitHub repository content"""
        content = []
        
        for repo in settings.github_repos:
            github_url = f"https://github.com/{repo}"
            
            try:
                # Scrape main repository page
                page_content = await self._scrape_page(github_url)
                if page_content:
                    content.append(page_content)
                
                # Scrape repository contents
                repo_content = await self._scrape_github_repository(repo)
                content.extend(repo_content)
                
            except Exception as e:
                logger.error(f"Error scraping GitHub repo {repo}: {e}")
                continue
        
        return content
    
    async def _scrape_github_repository(self, repo: str) -> List[ScrapedContent]:
        """Scrape GitHub repository contents with pagination"""
        content = []
        
        # Common GitHub paths to scrape
        paths = [
            "/tree/main/docs",
            "/tree/main/examples", 
            "/tree/main/templates",
            "/tree/main/src",
            "/wiki"
        ]
        
        for path in paths:
            repo_url = f"https://github.com/{repo}{path}"
            
            try:
                page_content = await self._scrape_page(repo_url)
                if page_content:
                    content.append(page_content)
                
                # Handle GitHub pagination
                paginated_content = await self._handle_github_pagination(repo_url)
                content.extend(paginated_content)
                
            except Exception as e:
                logger.error(f"Error scraping GitHub path {repo_url}: {e}")
                continue
        
        return content
    
    async def _handle_github_pagination(self, github_url: str) -> List[ScrapedContent]:
        """Handle GitHub-specific pagination"""
        content = []
        page = 1
        
        while page <= settings.max_pages_per_section:
            try:
                paginated_url = f"{github_url}?page={page}"
                page_content = await self._scrape_page(paginated_url)
                
                if not page_content:
                    break
                
                content.append(page_content)
                
                # Check if there are more pages (GitHub specific)
                soup = BeautifulSoup(page_content.content, 'html.parser')
                next_button = soup.select_one('.paginate-container .next_page')
                
                if not next_button or 'disabled' in next_button.get('class', []):
                    break
                
                page += 1
                await asyncio.sleep(settings.page_delay)
                
            except Exception as e:
                logger.error(f"Error handling GitHub pagination for {github_url}: {e}")
                break
        
        return content
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_selectors = [
            'h1', 'title', '.page-title', '.doc-title',
            '.content-title', '.main-title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "Untitled"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        content_selectors = [
            'main', '.main-content', '.content', '.documentation',
            '.doc-content', '.page-content', 'article'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text(strip=True)
        
        return ""
    
    def _determine_content_type(self, url: str, soup: BeautifulSoup) -> str:
        """Determine the type of content"""
        if 'api' in url.lower():
            return 'api_documentation'
        elif 'docs' in url.lower() or 'documentation' in url.lower():
            return 'documentation'
        elif 'template' in url.lower():
            return 'template'
        elif 'example' in url.lower():
            return 'example'
        elif 'github.com' in url:
            return 'github_repository'
        else:
            return 'general'
    
    def _extract_diagrams(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract diagrams from page"""
        diagrams = []
        
        for pattern_name, pattern_data in CONTENT_PATTERNS["diagrams"].items():
            selectors = pattern_data["selectors"]
            attributes = pattern_data["attributes"]
            formats = pattern_data["formats"]
            
            for selector in selectors:
                elements = soup.select(selector)
                
                for element in elements:
                    diagram_data = {
                        'type': pattern_name,
                        'selector': selector,
                        'tag': element.name,
                        'attributes': {}
                    }
                    
                    # Extract attributes
                    for attr in attributes:
                        value = element.get(attr)
                        if value:
                            diagram_data['attributes'][attr] = value
                    
                    # Check if it's a diagram format
                    src = element.get('src', '')
                    if any(fmt in src.lower() for fmt in formats):
                        diagram_data['is_diagram'] = True
                        diagram_data['url'] = urljoin(base_url, src)
                    
                    diagrams.append(diagram_data)
        
        return diagrams
    
    def _extract_templates(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract templates from page"""
        templates = []
        
        for pattern_name, pattern_data in CONTENT_PATTERNS["templates"].items():
            selectors = pattern_data["selectors"]
            metadata_fields = pattern_data["metadata"]
            download_links = pattern_data["download_links"]
            
            for selector in selectors:
                elements = soup.select(selector)
                
                for element in elements:
                    template_data = {
                        'type': pattern_name,
                        'selector': selector,
                        'tag': element.name,
                        'metadata': {},
                        'download_links': []
                    }
                    
                    # Extract metadata
                    for field in metadata_fields:
                        if field in ['title', 'description']:
                            text_element = element.find(field) or element
                            value = text_element.get_text(strip=True)
                            if value:
                                template_data['metadata'][field] = value
                        else:
                            value = element.get(field)
                            if value:
                                template_data['metadata'][field] = value
                    
                    # Extract download links
                    for link_attr in download_links:
                        link_value = element.get(link_attr)
                        if link_value:
                            full_url = urljoin(base_url, link_value)
                            template_data['download_links'].append(full_url)
                    
                    templates.append(template_data)
        
        return templates
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract code blocks from page"""
        code_blocks = []
        
        for pattern_name, pattern_data in CONTENT_PATTERNS["code_blocks"].items():
            selectors = pattern_data["selectors"]
            languages = pattern_data["languages"]
            
            for selector in selectors:
                elements = soup.select(selector)
                
                for element in elements:
                    code_data = {
                        'type': pattern_name,
                        'selector': selector,
                        'tag': element.name,
                        'content': element.get_text(strip=True),
                        'language': 'unknown'
                    }
                    
                    # Try to determine language
                    class_list = element.get('class', [])
                    for lang in languages:
                        if any(lang in cls.lower() for cls in class_list):
                            code_data['language'] = lang
                            break
                    
                    # Check parent elements for language hints
                    parent = element.parent
                    while parent and code_data['language'] == 'unknown':
                        parent_classes = parent.get('class', [])
                        for lang in languages:
                            if any(lang in cls.lower() for cls in parent_classes):
                                code_data['language'] = lang
                                break
                        parent = parent.parent
                    
                    code_blocks.append(code_data)
        
        return code_blocks
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            links.append(full_url)
        
        return links
    
    def _construct_paginated_url(self, base_url: str, page: int) -> str:
        """Construct paginated URL"""
        if '?' in base_url:
            return f"{base_url}&page={page}"
        else:
            return f"{base_url}?page={page}"
    
    async def _has_next_page(self, content: ScrapedContent) -> bool:
        """Check if there's a next page"""
        soup = BeautifulSoup(content.content, 'html.parser')
        
        # Check for next page indicators
        next_selectors = PAGINATION_PATTERNS["standard"]["next_page"]
        next_elements = soup.select(next_selectors)
        
        return len(next_elements) > 0
    
    def _extract_load_more_url(self, button, base_url: str) -> Optional[str]:
        """Extract URL from load more button"""
        # Check various attributes for load more URL
        url_attrs = ['data-url', 'data-load-url', 'href', 'data-href']
        
        for attr in url_attrs:
            url = button.get(attr)
            if url:
                return urljoin(base_url, url)
        
        return None
    
    def _create_content_from_api_response(self, url: str, data: Any, page: int) -> ScrapedContent:
        """Create ScrapedContent from API response"""
        title = f"API Response - Page {page}"
        content = json.dumps(data, indent=2)
        
        metadata = {
            'url': url,
            'title': title,
            'content_type': 'api_response',
            'page': page,
            'data_type': type(data).__name__,
            'data_length': len(str(data)),
            'scraped_at': datetime.now().isoformat()
        }
        
        return ScrapedContent(
            url=url,
            title=title,
            content=content,
            content_type='api_response',
            metadata=metadata,
            diagrams=[],
            templates=[],
            code_blocks=[],
            links=[],
            timestamp=datetime.now()
        )
    
    async def _extract_all_diagrams(self, content_list: List[ScrapedContent]):
        """Extract and process all diagrams from content"""
        for content in content_list:
            for diagram in content.diagrams:
                if diagram.get('is_diagram'):
                    diagram_url = diagram['attributes'].get('src')
                    if diagram_url:
                        # Download and process diagram
                        await self._process_diagram(diagram_url, diagram)
    
    async def _extract_all_templates(self, content_list: List[ScrapedContent]):
        """Extract and process all templates from content"""
        for content in content_list:
            for template in content.templates:
                for download_link in template['download_links']:
                    # Download and process template
                    await self._process_template(download_link, template)
    
    async def _process_diagram(self, diagram_url: str, diagram_data: Dict[str, Any]):
        """Process and store diagram"""
        try:
            async with self.session.get(diagram_url) as response:
                if response.status == 200:
                    diagram_content = await response.read()
                    
                    # Store diagram
                    diagram_id = f"diagram_{int(time.time())}"
                    self.diagram_cache[diagram_id] = {
                        'url': diagram_url,
                        'content': diagram_content,
                        'metadata': diagram_data,
                        'processed_at': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Error processing diagram {diagram_url}: {e}")
    
    async def _process_template(self, template_url: str, template_data: Dict[str, Any]):
        """Process and store template"""
        try:
            async with self.session.get(template_url) as response:
                if response.status == 200:
                    template_content = await response.read()
                    
                    # Store template
                    template_id = f"template_{int(time.time())}"
                    self.template_cache[template_id] = {
                        'url': template_url,
                        'content': template_content,
                        'metadata': template_data,
                        'processed_at': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Error processing template {template_url}: {e}")
    
    async def _enhance_content(self, content_list: List[ScrapedContent]) -> List[ScrapedContent]:
        """Enhance content with additional processing"""
        enhanced_content = []
        
        for content in content_list:
            # Add AI processing if enabled
            if settings.enable_ai_processing:
                content = await self._ai_enhance_content(content)
            
            # Add semantic search indexing
            if settings.enable_semantic_search:
                content = await self._add_semantic_indexing(content)
            
            # Add auto-categorization
            if settings.enable_auto_categorization:
                content = await self._auto_categorize_content(content)
            
            enhanced_content.append(content)
        
        return enhanced_content
    
    async def _ai_enhance_content(self, content: ScrapedContent) -> ScrapedContent:
        """Enhance content with AI processing"""
        # This would integrate with AI services for content enhancement
        # For now, we'll add basic enhancements
        content.metadata['ai_processed'] = True
        content.metadata['enhancement_timestamp'] = datetime.now().isoformat()
        
        return content
    
    async def _add_semantic_indexing(self, content: ScrapedContent) -> ScrapedContent:
        """Add semantic search indexing"""
        # This would integrate with semantic search services
        content.metadata['semantic_indexed'] = True
        content.metadata['indexing_timestamp'] = datetime.now().isoformat()
        
        return content
    
    async def _auto_categorize_content(self, content: ScrapedContent) -> ScrapedContent:
        """Auto-categorize content based on analysis"""
        # Basic categorization logic
        categories = []
        
        if 'api' in content.content.lower():
            categories.append('api')
        if 'diagram' in content.content.lower():
            categories.append('diagram')
        if 'template' in content.content.lower():
            categories.append('template')
        if 'tutorial' in content.content.lower():
            categories.append('tutorial')
        
        content.metadata['auto_categories'] = categories
        content.metadata['categorization_timestamp'] = datetime.now().isoformat()
        
        return content
    
    def save_results(self, output_file: str = None):
        """Save scraping results to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/chartdb_scraping_results_{timestamp}.json"
        
        results = {
            'scraping_metadata': {
                'total_pages': len(self.scraped_content),
                'total_diagrams': len(self.diagram_cache),
                'total_templates': len(self.template_cache),
                'scraping_completed_at': datetime.now().isoformat(),
                'settings_used': settings.dict()
            },
            'scraped_content': [
                {
                    'url': content.url,
                    'title': content.title,
                    'content_type': content.content_type,
                    'metadata': content.metadata,
                    'diagrams': content.diagrams,
                    'templates': content.templates,
                    'code_blocks': content.code_blocks,
                    'links': content.links,
                    'timestamp': content.timestamp.isoformat()
                }
                for content in self.scraped_content
            ],
            'diagrams': self.diagram_cache,
            'templates': self.template_cache
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_file}")

# Main execution function
async def main():
    """Main execution function"""
    async with ChartDBScraper() as scraper:
        results = await scraper.scrape_all()
        scraper.save_results()
        return results

if __name__ == "__main__":
    asyncio.run(main())