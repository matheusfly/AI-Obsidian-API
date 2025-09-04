#!/usr/bin/env python3
"""
Comprehensive Documentation Fetcher
Complete context window builder with full pagination coverage for all tools
"""

import asyncio
import aiohttp
import json
import re
import time
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DocumentationPage:
    """Data class for documentation pages"""
    tool: str
    url: str
    title: str
    content: str
    content_type: str
    page_type: str
    metadata: Dict[str, Any]
    links: List[str]
    code_blocks: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    api_endpoints: List[Dict[str, Any]]
    examples: List[Dict[str, Any]]
    timestamp: datetime
    depth: int = 0
    parent_url: Optional[str] = None

class ComprehensiveDocsFetcher:
    """Comprehensive documentation fetcher with full pagination coverage"""
    
    def __init__(self):
        self.session = None
        self.scraped_urls: Set[str] = set()
        self.documentation_pages: List[DocumentationPage] = []
        self.pagination_cache: Dict[str, List[str]] = {}
        self.max_depth = 5
        self.max_pages_per_section = 200
        
        # Tool configurations
        self.tools_config = {
            'motia': {
                'name': 'Motia',
                'base_urls': [
                    'https://www.motia.dev/',
                    'https://www.motia.dev/docs',
                    'https://github.com/MotiaDev/motia'
                ],
                'docs_patterns': [
                    r'/docs/',
                    r'/documentation/',
                    r'/guide/',
                    r'/tutorial/',
                    r'/api/',
                    r'/reference/'
                ],
                'github_patterns': [
                    r'/docs/',
                    r'/examples/',
                    r'/src/',
                    r'/lib/',
                    r'/README',
                    r'\.md$'
                ]
            },
            'flyde': {
                'name': 'Flyde',
                'base_urls': [
                    'https://flyde.dev/',
                    'https://flyde.dev/docs',
                    'https://github.com/flydelabs/flyde'
                ],
                'docs_patterns': [
                    r'/docs/',
                    r'/playground/',
                    r'/examples/',
                    r'/guide/',
                    r'/tutorial/',
                    r'/api/'
                ],
                'github_patterns': [
                    r'/docs/',
                    r'/examples/',
                    r'/src/',
                    r'/packages/',
                    r'/README',
                    r'\.flyde$',
                    r'\.md$'
                ]
            },
            'chartdb': {
                'name': 'ChartDB',
                'base_urls': [
                    'https://chartdb.io/',
                    'https://docs.chartdb.io/',
                    'https://api.chartdb.io/',
                    'https://github.com/chartdb/chartdb'
                ],
                'docs_patterns': [
                    r'/docs/',
                    r'/documentation/',
                    r'/api/',
                    r'/templates/',
                    r'/examples/',
                    r'/guide/'
                ],
                'github_patterns': [
                    r'/docs/',
                    r'/examples/',
                    r'/src/',
                    r'/templates/',
                    r'/README',
                    r'\.md$'
                ]
            },
            'jsoncrack': {
                'name': 'JSON Crack',
                'base_urls': [
                    'https://jsoncrack.com/',
                    'https://github.com/AykutSarac/jsoncrack.com'
                ],
                'docs_patterns': [
                    r'/docs/',
                    r'/documentation/',
                    r'/editor/',
                    r'/examples/',
                    r'/api/',
                    r'/guide/'
                ],
                'github_patterns': [
                    r'/docs/',
                    r'/examples/',
                    r'/src/',
                    r'/components/',
                    r'/README',
                    r'\.md$'
                ]
            }
        }
        
        # Pagination patterns
        self.pagination_patterns = {
            'next_page': [
                'a[rel="next"]',
                '.pagination .next',
                '.page-next',
                '.next-page',
                'a[aria-label="Next"]',
                'a[title="Next"]'
            ],
            'page_numbers': [
                '.pagination a',
                '.page-numbers a',
                '.pager a',
                '.page-links a',
                'nav a[href*="page"]'
            ],
            'load_more': [
                '.load-more',
                '.show-more',
                '[data-load-more]',
                '.load-more-btn',
                'button[data-load]'
            ],
            'infinite_scroll': [
                '[data-infinite-scroll]',
                '.infinite-scroll',
                '.lazy-load',
                '[data-lazy]'
            ]
        }
        
        # Content extraction patterns
        self.content_patterns = {
            'code_blocks': [
                'pre code',
                '.code-block',
                '.highlight',
                '.syntax-highlight',
                '.code-example',
                'code'
            ],
            'api_endpoints': [
                '.endpoint',
                '.api-endpoint',
                '.method',
                '.http-method',
                '[data-endpoint]'
            ],
            'examples': [
                '.example',
                '.demo',
                '.sample',
                '.code-example',
                '.usage-example'
            ],
            'images': [
                'img[src*="diagram"]',
                'img[src*="screenshot"]',
                'img[src*="example"]',
                'img[alt*="diagram"]',
                'img[alt*="example"]'
            ]
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=50)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_all_documentation(self) -> List[DocumentationPage]:
        """Fetch all documentation with complete pagination coverage"""
        logger.info("🚀 Starting comprehensive documentation fetching...")
        
        all_pages = []
        
        # Fetch each tool's documentation
        for tool_id, config in self.tools_config.items():
            logger.info(f"🔧 Fetching {config['name']} documentation...")
            
            tool_pages = await self._fetch_tool_documentation(tool_id, config)
            all_pages.extend(tool_pages)
            
            logger.info(f"✅ {config['name']}: {len(tool_pages)} pages fetched")
        
        self.documentation_pages = all_pages
        logger.info(f"🎉 Total documentation pages fetched: {len(all_pages)}")
        
        return all_pages
    
    async def _fetch_tool_documentation(self, tool_id: str, config: Dict[str, Any]) -> List[DocumentationPage]:
        """Fetch documentation for a specific tool"""
        pages = []
        
        for base_url in config['base_urls']:
            try:
                # Fetch base page
                base_page = await self._fetch_page(base_url, tool_id, 0)
                if base_page:
                    pages.append(base_page)
                
                # Handle pagination for main site
                if 'github.com' not in base_url:
                    paginated_pages = await self._handle_comprehensive_pagination(base_url, tool_id, config)
                    pages.extend(paginated_pages)
                
                # Handle GitHub-specific pagination
                else:
                    github_pages = await self._handle_github_pagination(base_url, tool_id, config)
                    pages.extend(github_pages)
                
                # Respect rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching {base_url}: {e}")
                continue
        
        return pages
    
    async def _fetch_page(self, url: str, tool_id: str, depth: int, parent_url: str = None) -> Optional[DocumentationPage]:
        """Fetch a single page with comprehensive content extraction"""
        if url in self.scraped_urls or depth > self.max_depth:
            return None
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract comprehensive content
                    title = self._extract_title(soup)
                    content = self._extract_content(soup)
                    content_type = self._determine_content_type(url, soup)
                    page_type = self._determine_page_type(url, soup, tool_id)
                    
                    # Extract specific elements
                    code_blocks = self._extract_code_blocks(soup)
                    api_endpoints = self._extract_api_endpoints(soup)
                    examples = self._extract_examples(soup)
                    images = self._extract_images(soup, url)
                    links = self._extract_links(soup, url)
                    
                    # Create comprehensive metadata
                    metadata = {
                        'url': url,
                        'title': title,
                        'content_type': content_type,
                        'page_type': page_type,
                        'response_status': response.status,
                        'content_length': len(response.content),
                        'text_length': len(content),
                        'code_blocks_count': len(code_blocks),
                        'api_endpoints_count': len(api_endpoints),
                        'examples_count': len(examples),
                        'images_count': len(images),
                        'links_count': len(links),
                        'depth': depth,
                        'parent_url': parent_url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    page = DocumentationPage(
                        tool=tool_id,
                        url=url,
                        title=title,
                        content=content,
                        content_type=content_type,
                        page_type=page_type,
                        metadata=metadata,
                        links=links,
                        code_blocks=code_blocks,
                        images=images,
                        api_endpoints=api_endpoints,
                        examples=examples,
                        timestamp=datetime.now(),
                        depth=depth,
                        parent_url=parent_url
                    )
                    
                    self.scraped_urls.add(url)
                    return page
                    
        except Exception as e:
            logger.error(f"Error fetching page {url}: {e}")
            return None
    
    async def _handle_comprehensive_pagination(self, base_url: str, tool_id: str, config: Dict[str, Any]) -> List[DocumentationPage]:
        """Handle comprehensive pagination for all types"""
        pages = []
        
        # Standard pagination
        standard_pages = await self._handle_standard_pagination(base_url, tool_id)
        pages.extend(standard_pages)
        
        # Load more pagination
        load_more_pages = await self._handle_load_more_pagination(base_url, tool_id)
        pages.extend(load_more_pages)
        
        # Infinite scroll pagination
        infinite_pages = await self._handle_infinite_scroll_pagination(base_url, tool_id)
        pages.extend(infinite_pages)
        
        # API pagination
        api_pages = await self._handle_api_pagination(base_url, tool_id)
        pages.extend(api_pages)
        
        # Documentation section pagination
        docs_pages = await self._handle_docs_section_pagination(base_url, tool_id, config)
        pages.extend(docs_pages)
        
        return pages
    
    async def _handle_standard_pagination(self, base_url: str, tool_id: str) -> List[DocumentationPage]:
        """Handle standard next/previous pagination"""
        pages = []
        current_page = 1
        max_pages = self.max_pages_per_section
        
        while current_page <= max_pages:
            try:
                # Construct paginated URL
                paginated_url = self._construct_paginated_url(base_url, current_page)
                
                # Fetch the page
                page = await self._fetch_page(paginated_url, tool_id, 1, base_url)
                if not page:
                    break
                
                pages.append(page)
                
                # Check if there's a next page
                has_next = await self._has_next_page(page)
                if not has_next:
                    break
                
                current_page += 1
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error in standard pagination for {base_url}: {e}")
                break
        
        return pages
    
    async def _handle_load_more_pagination(self, base_url: str, tool_id: str) -> List[DocumentationPage]:
        """Handle load more button pagination"""
        pages = []
        
        try:
            # Get initial page
            page = await self._fetch_page(base_url, tool_id, 1)
            if not page:
                return pages
            
            pages.append(page)
            
            # Look for load more buttons
            soup = BeautifulSoup(page.content, 'html.parser')
            
            for selector in self.pagination_patterns['load_more']:
                load_more_buttons = soup.select(selector)
                
                for button in load_more_buttons:
                    try:
                        # Extract load more URL
                        load_url = self._extract_load_more_url(button, base_url)
                        if load_url:
                            load_page = await self._fetch_page(load_url, tool_id, 1, base_url)
                            if load_page:
                                pages.append(load_page)
                                
                    except Exception as e:
                        logger.error(f"Error handling load more button: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error in load more pagination for {base_url}: {e}")
        
        return pages
    
    async def _handle_infinite_scroll_pagination(self, base_url: str, tool_id: str) -> List[DocumentationPage]:
        """Handle infinite scroll pagination"""
        pages = []
        
        try:
            # This would require browser automation for true infinite scroll
            # For now, we'll check for data attributes that indicate infinite scroll
            page = await self._fetch_page(base_url, tool_id, 1)
            if not page:
                return pages
            
            pages.append(page)
            
            soup = BeautifulSoup(page.content, 'html.parser')
            
            for selector in self.pagination_patterns['infinite_scroll']:
                infinite_elements = soup.select(selector)
                
                for element in infinite_elements:
                    scroll_url = element.get('data-url') or element.get('data-load-url')
                    if scroll_url:
                        scroll_url = urljoin(base_url, scroll_url)
                        scroll_page = await self._fetch_page(scroll_url, tool_id, 1, base_url)
                        if scroll_page:
                            pages.append(scroll_page)
                            
        except Exception as e:
            logger.error(f"Error in infinite scroll pagination for {base_url}: {e}")
        
        return pages
    
    async def _handle_api_pagination(self, base_url: str, tool_id: str) -> List[DocumentationPage]:
        """Handle API-specific pagination"""
        pages = []
        
        # Common API endpoints to check
        api_endpoints = [
            '/api/',
            '/api/v1/',
            '/api/docs/',
            '/swagger/',
            '/openapi/',
            '/redoc/'
        ]
        
        for endpoint in api_endpoints:
            api_url = urljoin(base_url, endpoint)
            
            try:
                page = await self._fetch_page(api_url, tool_id, 1, base_url)
                if page:
                    pages.append(page)
                
                # Handle API pagination
                api_pages = await self._handle_api_endpoint_pagination(api_url, tool_id)
                pages.extend(api_pages)
                
            except Exception as e:
                logger.error(f"Error fetching API endpoint {api_url}: {e}")
                continue
        
        return pages
    
    async def _handle_api_endpoint_pagination(self, api_url: str, tool_id: str) -> List[DocumentationPage]:
        """Handle pagination for specific API endpoints"""
        pages = []
        page = 1
        per_page = 50
        
        while page <= self.max_pages_per_section:
            try:
                # Construct paginated API URL
                paginated_url = f"{api_url}?page={page}&per_page={per_page}"
                
                async with self.session.get(paginated_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if there's more data
                        if not data or len(data) == 0:
                            break
                        
                        # Create page from API response
                        api_page = self._create_page_from_api_response(paginated_url, data, tool_id, page)
                        pages.append(api_page)
                        
                        # Check for next page indicator
                        if 'next' not in data or not data['next']:
                            break
                        
                        page += 1
                        await asyncio.sleep(0.5)
                    else:
                        break
                        
            except Exception as e:
                logger.error(f"Error in API pagination for {api_url}: {e}")
                break
        
        return pages
    
    async def _handle_docs_section_pagination(self, base_url: str, tool_id: str, config: Dict[str, Any]) -> List[DocumentationPage]:
        """Handle pagination for documentation sections"""
        pages = []
        
        # Find all documentation links
        try:
            page = await self._fetch_page(base_url, tool_id, 1)
            if not page:
                return pages
            
            soup = BeautifulSoup(page.content, 'html.parser')
            
            # Find documentation links
            doc_links = []
            for pattern in config['docs_patterns']:
                links = soup.find_all('a', href=re.compile(pattern))
                doc_links.extend([urljoin(base_url, link['href']) for link in links])
            
            # Fetch each documentation page
            for doc_url in doc_links[:50]:  # Limit to prevent too many requests
                try:
                    doc_page = await self._fetch_page(doc_url, tool_id, 2, base_url)
                    if doc_page:
                        pages.append(doc_page)
                    
                    # Handle pagination within documentation sections
                    section_pages = await self._handle_standard_pagination(doc_url, tool_id)
                    pages.extend(section_pages)
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error fetching doc page {doc_url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in docs section pagination for {base_url}: {e}")
        
        return pages
    
    async def _handle_github_pagination(self, github_url: str, tool_id: str, config: Dict[str, Any]) -> List[DocumentationPage]:
        """Handle GitHub-specific pagination"""
        pages = []
        
        try:
            # Fetch main repository page
            page = await self._fetch_page(github_url, tool_id, 1)
            if page:
                pages.append(page)
            
            # Find GitHub content links
            soup = BeautifulSoup(page.content, 'html.parser')
            
            # Find relevant GitHub links
            github_links = []
            for pattern in config['github_patterns']:
                links = soup.find_all('a', href=re.compile(pattern))
                github_links.extend([urljoin(github_url, link['href']) for link in links])
            
            # Fetch each GitHub page
            for github_link in github_links[:100]:  # Limit to prevent too many requests
                try:
                    github_page = await self._fetch_page(github_link, tool_id, 2, github_url)
                    if github_page:
                        pages.append(github_page)
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error fetching GitHub page {github_link}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in GitHub pagination for {github_url}: {e}")
        
        return pages
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_selectors = [
            'h1', 'title', '.page-title', '.doc-title',
            '.content-title', '.main-title', '.article-title'
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
            '.doc-content', '.page-content', 'article', '.post-content',
            '.entry-content', '.markdown-body'
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
        elif 'github.com' in url:
            return 'github_repository'
        elif 'playground' in url.lower() or 'demo' in url.lower():
            return 'interactive_demo'
        elif 'tutorial' in url.lower() or 'guide' in url.lower():
            return 'tutorial'
        else:
            return 'general'
    
    def _determine_page_type(self, url: str, soup: BeautifulSoup, tool_id: str) -> str:
        """Determine the specific page type"""
        if 'api' in url.lower():
            return 'api_reference'
        elif 'docs' in url.lower():
            return 'documentation'
        elif 'tutorial' in url.lower():
            return 'tutorial'
        elif 'example' in url.lower():
            return 'example'
        elif 'playground' in url.lower():
            return 'playground'
        elif 'github.com' in url:
            return 'github_content'
        else:
            return 'general'
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract code blocks from page"""
        code_blocks = []
        
        for selector in self.content_patterns['code_blocks']:
            elements = soup.select(selector)
            
            for element in elements:
                code_data = {
                    'selector': selector,
                    'content': element.get_text(strip=True),
                    'language': 'unknown',
                    'tag': element.name
                }
                
                # Try to determine language
                class_list = element.get('class', [])
                for cls in class_list:
                    if 'language-' in cls or 'lang-' in cls:
                        code_data['language'] = cls.split('-')[-1]
                        break
                
                code_blocks.append(code_data)
        
        return code_blocks
    
    def _extract_api_endpoints(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract API endpoints from page"""
        api_endpoints = []
        
        for selector in self.content_patterns['api_endpoints']:
            elements = soup.select(selector)
            
            for element in elements:
                endpoint_data = {
                    'selector': selector,
                    'content': element.get_text(strip=True),
                    'tag': element.name,
                    'attributes': dict(element.attrs)
                }
                
                api_endpoints.append(endpoint_data)
        
        return api_endpoints
    
    def _extract_examples(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract examples from page"""
        examples = []
        
        for selector in self.content_patterns['examples']:
            elements = soup.select(selector)
            
            for element in elements:
                example_data = {
                    'selector': selector,
                    'content': element.get_text(strip=True),
                    'tag': element.name,
                    'attributes': dict(element.attrs)
                }
                
                examples.append(example_data)
        
        return examples
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract images from page"""
        images = []
        
        for selector in self.content_patterns['images']:
            elements = soup.select(selector)
            
            for element in elements:
                src = element.get('src')
                if src:
                    full_url = urljoin(base_url, src)
                    image_data = {
                        'selector': selector,
                        'src': full_url,
                        'alt': element.get('alt', ''),
                        'title': element.get('title', ''),
                        'tag': element.name
                    }
                    
                    images.append(image_data)
        
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') or href.startswith('/'):
                full_url = urljoin(base_url, href)
                links.append(full_url)
        
        return links
    
    def _construct_paginated_url(self, base_url: str, page: int) -> str:
        """Construct paginated URL"""
        if '?' in base_url:
            return f"{base_url}&page={page}"
        else:
            return f"{base_url}?page={page}"
    
    async def _has_next_page(self, page: DocumentationPage) -> bool:
        """Check if there's a next page"""
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Check for next page indicators
        for selector in self.pagination_patterns['next_page']:
            next_elements = soup.select(selector)
            if next_elements:
                return True
        
        return False
    
    def _extract_load_more_url(self, button, base_url: str) -> Optional[str]:
        """Extract URL from load more button"""
        url_attrs = ['data-url', 'data-load-url', 'href', 'data-href']
        
        for attr in url_attrs:
            url = button.get(attr)
            if url:
                return urljoin(base_url, url)
        
        return None
    
    def _create_page_from_api_response(self, url: str, data: Any, tool_id: str, page: int) -> DocumentationPage:
        """Create DocumentationPage from API response"""
        title = f"API Response - Page {page}"
        content = json.dumps(data, indent=2)
        
        metadata = {
            'url': url,
            'title': title,
            'content_type': 'api_response',
            'page_type': 'api_data',
            'page': page,
            'data_type': type(data).__name__,
            'data_length': len(str(data)),
            'scraped_at': datetime.now().isoformat()
        }
        
        return DocumentationPage(
            tool=tool_id,
            url=url,
            title=title,
            content=content,
            content_type='api_response',
            page_type='api_data',
            metadata=metadata,
            links=[],
            code_blocks=[],
            images=[],
            api_endpoints=[],
            examples=[],
            timestamp=datetime.now(),
            depth=1
        )
    
    def save_comprehensive_results(self, output_dir: str = "comprehensive_docs"):
        """Save comprehensive results to organized files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save by tool
        for tool_id in self.tools_config.keys():
            tool_pages = [p for p in self.documentation_pages if p.tool == tool_id]
            
            if tool_pages:
                tool_dir = os.path.join(output_dir, tool_id)
                os.makedirs(tool_dir, exist_ok=True)
                
                # Save as JSON
                tool_data = [asdict(page) for page in tool_pages]
                with open(os.path.join(tool_dir, f"{tool_id}_documentation.json"), 'w', encoding='utf-8') as f:
                    json.dump(tool_data, f, indent=2, ensure_ascii=False, default=str)
                
                # Save as markdown
                self._save_tool_as_markdown(tool_id, tool_pages, tool_dir)
                
                # Save code blocks separately
                self._save_code_blocks(tool_id, tool_pages, tool_dir)
                
                # Save API endpoints separately
                self._save_api_endpoints(tool_id, tool_pages, tool_dir)
        
        # Save unified summary
        self._save_unified_summary(output_dir)
        
        logger.info(f"💾 Comprehensive results saved to: {output_dir}")
    
    def _save_tool_as_markdown(self, tool_id: str, pages: List[DocumentationPage], tool_dir: str):
        """Save tool documentation as markdown"""
        md_content = f"# {self.tools_config[tool_id]['name']} Documentation\n\n"
        md_content += f"**Total Pages:** {len(pages)}\n"
        md_content += f"**Generated:** {datetime.now().isoformat()}\n\n"
        
        for page in pages:
            md_content += f"## {page.title}\n\n"
            md_content += f"**URL:** {page.url}\n"
            md_content += f"**Type:** {page.page_type}\n"
            md_content += f"**Content Length:** {len(page.content)} characters\n\n"
            md_content += f"{page.content[:1000]}...\n\n"
            md_content += "---\n\n"
        
        with open(os.path.join(tool_dir, f"{tool_id}_documentation.md"), 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def _save_code_blocks(self, tool_id: str, pages: List[DocumentationPage], tool_dir: str):
        """Save code blocks separately"""
        all_code_blocks = []
        
        for page in pages:
            for code_block in page.code_blocks:
                code_block['source_url'] = page.url
                code_block['source_title'] = page.title
                all_code_blocks.append(code_block)
        
        if all_code_blocks:
            with open(os.path.join(tool_dir, f"{tool_id}_code_blocks.json"), 'w', encoding='utf-8') as f:
                json.dump(all_code_blocks, f, indent=2, ensure_ascii=False)
    
    def _save_api_endpoints(self, tool_id: str, pages: List[DocumentationPage], tool_dir: str):
        """Save API endpoints separately"""
        all_api_endpoints = []
        
        for page in pages:
            for endpoint in page.api_endpoints:
                endpoint['source_url'] = page.url
                endpoint['source_title'] = page.title
                all_api_endpoints.append(endpoint)
        
        if all_api_endpoints:
            with open(os.path.join(tool_dir, f"{tool_id}_api_endpoints.json"), 'w', encoding='utf-8') as f:
                json.dump(all_api_endpoints, f, indent=2, ensure_ascii=False)
    
    def _save_unified_summary(self, output_dir: str):
        """Save unified summary of all documentation"""
        summary = {
            'total_pages': len(self.documentation_pages),
            'tools': {},
            'generated_at': datetime.now().isoformat()
        }
        
        for tool_id in self.tools_config.keys():
            tool_pages = [p for p in self.documentation_pages if p.tool == tool_id]
            summary['tools'][tool_id] = {
                'name': self.tools_config[tool_id]['name'],
                'pages': len(tool_pages),
                'total_content_length': sum(len(p.content) for p in tool_pages),
                'total_code_blocks': sum(len(p.code_blocks) for p in tool_pages),
                'total_api_endpoints': sum(len(p.api_endpoints) for p in tool_pages),
                'total_examples': sum(len(p.examples) for p in tool_pages)
            }
        
        with open(os.path.join(output_dir, "unified_summary.json"), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    
    def print_comprehensive_summary(self):
        """Print comprehensive summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE DOCUMENTATION FETCHING SUMMARY")
        print("="*80)
        
        total_pages = len(self.documentation_pages)
        total_content = sum(len(p.content) for p in self.documentation_pages)
        total_code_blocks = sum(len(p.code_blocks) for p in self.documentation_pages)
        total_api_endpoints = sum(len(p.api_endpoints) for p in self.documentation_pages)
        total_examples = sum(len(p.examples) for p in self.documentation_pages)
        
        print(f"\n🎯 OVERALL STATISTICS:")
        print(f"   Total Pages Fetched: {total_pages:,}")
        print(f"   Total Content Length: {total_content:,} characters")
        print(f"   Total Code Blocks: {total_code_blocks:,}")
        print(f"   Total API Endpoints: {total_api_endpoints:,}")
        print(f"   Total Examples: {total_examples:,}")
        
        print(f"\n🔧 TOOL BREAKDOWN:")
        for tool_id, config in self.tools_config.items():
            tool_pages = [p for p in self.documentation_pages if p.tool == tool_id]
            if tool_pages:
                tool_content = sum(len(p.content) for p in tool_pages)
                tool_code = sum(len(p.code_blocks) for p in tool_pages)
                tool_api = sum(len(p.api_endpoints) for p in tool_pages)
                tool_examples = sum(len(p.examples) for p in tool_pages)
                
                print(f"\n   {config['name']}:")
                print(f"      Pages: {len(tool_pages):,}")
                print(f"      Content: {tool_content:,} characters")
                print(f"      Code Blocks: {tool_code:,}")
                print(f"      API Endpoints: {tool_api:,}")
                print(f"      Examples: {tool_examples:,}")
        
        print(f"\n✅ Comprehensive documentation fetching completed!")
        print(f"📁 Results saved to: comprehensive_docs/")

# Main execution function
async def main():
    """Main execution function"""
    print("🚀 Comprehensive Documentation Fetcher")
    print("="*50)
    
    async with ComprehensiveDocsFetcher() as fetcher:
        # Fetch all documentation
        results = await fetcher.fetch_all_documentation()
        
        # Save comprehensive results
        fetcher.save_comprehensive_results()
        
        # Print summary
        fetcher.print_comprehensive_summary()
        
        return results

if __name__ == "__main__":
    asyncio.run(main())