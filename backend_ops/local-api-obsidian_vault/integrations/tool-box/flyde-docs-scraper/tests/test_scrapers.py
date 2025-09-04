"""
Tests for the scraping engines.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from pathlib import Path

from scrapers.base_scraper import ScrapingResult
from scrapers.scrapfly_scraper import ScrapflyScraper
from scrapers.playwright_scraper import PlaywrightScraper
from scrapers.scrapy_scraper import ScrapyScraper


class TestScrapingResult:
    """Test ScrapingResult class."""
    
    def test_success_result(self):
        """Test successful scraping result."""
        result = ScrapingResult(
            url="https://example.com",
            content="<html>Test content</html>",
            status_code=200
        )
        
        assert result.is_success() is True
        assert result.url == "https://example.com"
        assert result.content == "<html>Test content</html>"
        assert result.status_code == 200
        assert result.error is None
    
    def test_error_result(self):
        """Test error scraping result."""
        result = ScrapingResult(
            url="https://example.com",
            content="",
            status_code=404,
            error="Page not found"
        )
        
        assert result.is_success() is False
        assert result.error == "Page not found"
        assert result.status_code == 404
    
    def test_to_dict(self):
        """Test result serialization."""
        result = ScrapingResult(
            url="https://example.com",
            content="Test content",
            status_code=200,
            headers={"Content-Type": "text/html"},
            metadata={"title": "Test Page"}
        )
        
        data = result.to_dict()
        assert data["url"] == "https://example.com"
        assert data["content"] == "Test content"
        assert data["status_code"] == 200
        assert data["headers"]["Content-Type"] == "text/html"
        assert data["metadata"]["title"] == "Test Page"


class TestBaseScraper:
    """Test base scraper functionality."""
    
    def test_should_scrape_url(self):
        """Test URL filtering logic."""
        scraper = ScrapflyScraper()
        
        # Valid URLs
        assert scraper.should_scrape_url("https://flyde.dev/docs") is True
        assert scraper.should_scrape_url("https://flyde.dev/docs/introduction") is True
        
        # Invalid URLs
        assert scraper.should_scrape_url("https://google.com") is False
        assert scraper.should_scrape_url("https://flyde.dev/api/private") is False
    
    def test_extract_links(self):
        """Test link extraction."""
        scraper = ScrapflyScraper()
        
        html_content = """
        <html>
            <body>
                <a href="/docs">Docs</a>
                <a href="https://flyde.dev/playground">Playground</a>
                <a href="https://google.com">External</a>
                <a href="#section">Anchor</a>
            </body>
        </html>
        """
        
        links = scraper.extract_links(html_content, "https://flyde.dev")
        
        assert "/docs" in links
        assert "https://flyde.dev/playground" in links
        assert "https://google.com" not in links  # External link
        assert "#section" not in links  # Anchor link
    
    def test_extract_text_content(self):
        """Test text content extraction."""
        scraper = ScrapflyScraper()
        
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Hello World</h1>
                <p>This is a <strong>test</strong> paragraph.</p>
                <script>console.log('test');</script>
                <style>body { color: red; }</style>
            </body>
        </html>
        """
        
        text = scraper.extract_text_content(html_content)
        
        assert "Hello World" in text
        assert "This is a test paragraph" in text
        assert "console.log" not in text  # Script removed
        assert "color: red" not in text  # Style removed
    
    def test_extract_metadata(self):
        """Test metadata extraction."""
        scraper = ScrapflyScraper()
        
        html_content = """
        <html lang="en">
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
                <meta name="keywords" content="test, example">
                <meta name="author" content="Test Author">
                <meta property="og:title" content="OG Title">
            </head>
            <body>Content</body>
        </html>
        """
        
        metadata = scraper.extract_metadata(html_content, "https://example.com")
        
        assert metadata["title"] == "Test Page"
        assert metadata["description"] == "Test description"
        assert metadata["keywords"] == ["test", "example"]
        assert metadata["author"] == "Test Author"
        assert metadata["language"] == "en"


@pytest.mark.asyncio
class TestScrapflyScraper:
    """Test Scrapfly scraper."""
    
    async def test_scraper_initialization(self):
        """Test scraper initialization."""
        scraper = ScrapflyScraper()
        assert scraper.name == "scrapfly"
        assert scraper.session_count == 0
        assert scraper.error_count == 0
        assert scraper.success_count == 0
    
    @patch('scrapers.scrapfly_scraper.ScrapflyClient')
    async def test_scrape_url_success(self, mock_client):
        """Test successful URL scraping."""
        # Mock successful response
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = "<html>Test content</html>"
        mock_result.status_code = 200
        mock_result.session_id = "test_session"
        mock_result.asp = True
        mock_result.country = "US"
        
        mock_client.return_value.async_scrape.return_value = mock_result
        
        scraper = ScrapflyScraper()
        result = await scraper.scrape_url("https://flyde.dev/docs")
        
        assert result.is_success() is True
        assert result.content == "<html>Test content</html>"
        assert result.status_code == 200
        assert result.metadata["scrapfly_session_id"] == "test_session"
    
    @patch('scrapers.scrapfly_scraper.ScrapflyClient')
    async def test_scrape_url_failure(self, mock_client):
        """Test failed URL scraping."""
        # Mock failed response
        mock_result = Mock()
        mock_result.success = False
        mock_result.status_code = 404
        mock_result.error = "Page not found"
        
        mock_client.return_value.async_scrape.return_value = mock_result
        
        scraper = ScrapflyScraper()
        result = await scraper.scrape_url("https://flyde.dev/nonexistent")
        
        assert result.is_success() is False
        assert result.error == "Scrapfly failed: Page not found"
        assert result.status_code == 404


@pytest.mark.asyncio
class TestPlaywrightScraper:
    """Test Playwright scraper."""
    
    async def test_scraper_initialization(self):
        """Test scraper initialization."""
        scraper = PlaywrightScraper()
        assert scraper.name == "playwright"
        assert scraper._initialized is False
    
    @patch('scrapers.playwright_scraper.async_playwright')
    async def test_scrape_url_success(self, mock_playwright):
        """Test successful URL scraping."""
        # Mock Playwright components
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        mock_response = Mock()
        
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "text/html"}
        
        mock_page.goto.return_value = mock_response
        mock_page.content.return_value = "<html>Test content</html>"
        mock_page.title.return_value = "Test Page"
        mock_page.url = "https://flyde.dev/docs"
        
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        mock_playwright.return_value.start.return_value.chromium.launch.return_value = mock_browser
        
        scraper = PlaywrightScraper()
        result = await scraper.scrape_url("https://flyde.dev/docs")
        
        assert result.is_success() is True
        assert result.content == "<html>Test content</html>"
        assert result.status_code == 200


class TestScrapyScraper:
    """Test Scrapy scraper."""
    
    def test_scraper_initialization(self):
        """Test scraper initialization."""
        scraper = ScrapyScraper()
        assert scraper.name == "scrapy"
        assert scraper.process is not None


@pytest.mark.asyncio
class TestIntegration:
    """Integration tests."""
    
    async def test_hello_world_example(self):
        """Test hello world example."""
        from main import FlydeDocsScraper
        
        scraper = FlydeDocsScraper()
        
        # Mock the scrapers to avoid actual network calls
        with patch.object(scraper.scrapers["scrapfly"], 'scrape_url') as mock_scrape:
            mock_result = ScrapingResult(
                url="https://flyde.dev/playground/blog-generator",
                content="<html>Test content</html>",
                status_code=200
            )
            mock_scrape.return_value = mock_result
            
            result = await scraper.hello_world_example()
            
            assert "test_url" in result
            assert "output_file" in result
            assert "results" in result
            assert result["test_url"] == "https://flyde.dev/playground/blog-generator"


if __name__ == "__main__":
    pytest.main([__file__])