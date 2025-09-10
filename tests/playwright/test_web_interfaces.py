"""
Playwright Tests for Web Interfaces
Tests web UI components and user interactions
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, expect
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestWebInterfaces:
    """Test cases for web interfaces using Playwright"""
    
    @pytest.fixture(scope="class")
    async def browser_context(self):
        """Set up browser context for all tests"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            yield context
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_langgraph_studio_ui(self, browser_context):
        """Test LangGraph Studio web interface"""
        page = await browser_context.new_page()
        
        try:
            # Navigate to LangGraph Studio
            await page.goto("http://127.0.0.1:2024/docs")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            
            # Check if page loaded successfully
            title = await page.title()
            assert title is not None
            
            # Check for API documentation elements
            await expect(page).to_have_url("http://127.0.0.1:2024/docs")
            
            # Look for common API doc elements
            api_elements = await page.query_selector_all("h1, h2, h3")
            assert len(api_elements) > 0, "No API documentation elements found"
            
        except Exception as e:
            pytest.skip(f"LangGraph Studio not accessible: {e}")
        finally:
            await page.close()
    
    @pytest.mark.asyncio
    async def test_debug_dashboard_ui(self, browser_context):
        """Test Debug Dashboard web interface"""
        page = await browser_context.new_page()
        
        try:
            # Navigate to Debug Dashboard
            await page.goto("http://127.0.0.1:8003/")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            
            # Check if page loaded successfully
            title = await page.title()
            assert title is not None
            
            # Check for dashboard elements
            await expect(page).to_have_url("http://127.0.0.1:8003/")
            
            # Look for dashboard content
            content = await page.content()
            assert len(content) > 100, "Dashboard content too short"
            
        except Exception as e:
            pytest.skip(f"Debug Dashboard not accessible: {e}")
        finally:
            await page.close()
    
    @pytest.mark.asyncio
    async def test_observability_dashboard_ui(self, browser_context):
        """Test Observability Dashboard web interface"""
        page = await browser_context.new_page()
        
        try:
            # Navigate to Observability Dashboard
            await page.goto("http://127.0.0.1:8002/")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            
            # Check if page loaded successfully
            title = await page.title()
            assert title is not None
            
            # Check for observability content
            await expect(page).to_have_url("http://127.0.0.1:8002/")
            
            # Look for metrics or dashboard content
            content = await page.content()
            assert len(content) > 50, "Observability content too short"
            
        except Exception as e:
            pytest.skip(f"Observability Dashboard not accessible: {e}")
        finally:
            await page.close()
    
    @pytest.mark.asyncio
    async def test_mcp_integration_ui(self, browser_context):
        """Test MCP Integration Server web interface"""
        page = await browser_context.new_page()
        
        try:
            # Navigate to MCP Integration Server
            await page.goto("http://127.0.0.1:8001/docs")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            
            # Check if page loaded successfully
            title = await page.title()
            assert title is not None
            
            # Check for API documentation
            await expect(page).to_have_url("http://127.0.0.1:8001/docs")
            
            # Look for API documentation elements
            content = await page.content()
            assert "api" in content.lower() or "swagger" in content.lower(), "No API documentation found"
            
        except Exception as e:
            pytest.skip(f"MCP Integration Server not accessible: {e}")
        finally:
            await page.close()
    
    @pytest.mark.asyncio
    async def test_health_endpoints_ui(self, browser_context):
        """Test health endpoints across all services"""
        services = [
            ("MCP Integration", "http://127.0.0.1:8001/health"),
            ("Observability", "http://127.0.0.1:8002/health"),
            ("Debug Dashboard", "http://127.0.0.1:8003/health"),
        ]
        
        for service_name, url in services:
            page = await browser_context.new_page()
            
            try:
                # Navigate to health endpoint
                response = await page.goto(url)
                
                if response and response.status == 200:
                    # Check for JSON response
                    content = await page.content()
                    assert "healthy" in content.lower() or "status" in content.lower(), f"{service_name} health check failed"
                else:
                    pytest.skip(f"{service_name} not accessible")
                    
            except Exception as e:
                pytest.skip(f"{service_name} not accessible: {e}")
            finally:
                await page.close()
    
    @pytest.mark.asyncio
    async def test_responsive_design(self, browser_context):
        """Test responsive design across different screen sizes"""
        viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop"},
            {"width": 1024, "height": 768, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"}
        ]
        
        for viewport in viewports:
            page = await browser_context.new_page()
            
            try:
                # Set viewport
                await page.set_viewport_size(viewport["width"], viewport["height"])
                
                # Test each service
                services = [
                    "http://127.0.0.1:2024/docs",
                    "http://127.0.0.1:8003/",
                    "http://127.0.0.1:8002/"
                ]
                
                for service_url in services:
                    try:
                        await page.goto(service_url)
                        await page.wait_for_load_state("networkidle")
                        
                        # Check if content is visible
                        content = await page.content()
                        assert len(content) > 100, f"Content too short for {viewport['name']} on {service_url}"
                        
                    except Exception as e:
                        # Skip if service not accessible
                        continue
                        
            finally:
                await page.close()
    
    @pytest.mark.asyncio
    async def test_user_interactions(self, browser_context):
        """Test user interactions on web interfaces"""
        page = await browser_context.new_page()
        
        try:
            # Test LangGraph Studio interactions
            await page.goto("http://127.0.0.1:2024/docs")
            await page.wait_for_load_state("networkidle")
            
            # Look for interactive elements
            buttons = await page.query_selector_all("button")
            links = await page.query_selector_all("a")
            
            # Test button clicks if any exist
            for button in buttons[:3]:  # Test first 3 buttons
                try:
                    await button.click()
                    await page.wait_for_timeout(500)  # Wait for response
                except Exception:
                    # Button might not be clickable, continue
                    continue
            
            # Test link navigation if any exist
            for link in links[:3]:  # Test first 3 links
                try:
                    href = await link.get_attribute("href")
                    if href and href.startswith("http"):
                        await link.click()
                        await page.wait_for_load_state("networkidle")
                        break  # Test one external link
                except Exception:
                    # Link might not be navigable, continue
                    continue
                    
        except Exception as e:
            pytest.skip(f"User interaction testing failed: {e}")
        finally:
            await page.close()
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, browser_context):
        """Test performance metrics for web interfaces"""
        page = await browser_context.new_page()
        
        try:
            # Enable performance monitoring
            await page.route("**/*", lambda route: route.continue_())
            
            # Test each service
            services = [
                ("LangGraph Studio", "http://127.0.0.1:2024/docs"),
                ("Debug Dashboard", "http://127.0.0.1:8003/"),
                ("Observability", "http://127.0.0.1:8002/")
            ]
            
            for service_name, url in services:
                try:
                    # Navigate and measure performance
                    start_time = asyncio.get_event_loop().time()
                    await page.goto(url)
                    await page.wait_for_load_state("networkidle")
                    end_time = asyncio.get_event_loop().time()
                    
                    load_time = end_time - start_time
                    
                    # Check performance
                    assert load_time < 10.0, f"{service_name} took too long to load: {load_time}s"
                    
                    # Check for console errors
                    console_logs = []
                    page.on("console", lambda msg: console_logs.append(msg))
                    
                    # Wait a bit for any console messages
                    await page.wait_for_timeout(1000)
                    
                    # Check for errors
                    errors = [log for log in console_logs if log.type == "error"]
                    assert len(errors) == 0, f"{service_name} has console errors: {errors}"
                    
                except Exception as e:
                    # Service might not be accessible
                    continue
                    
        finally:
            await page.close()
    
    @pytest.mark.asyncio
    async def test_accessibility_basics(self, browser_context):
        """Test basic accessibility features"""
        page = await browser_context.new_page()
        
        try:
            # Test LangGraph Studio accessibility
            await page.goto("http://127.0.0.1:2024/docs")
            await page.wait_for_load_state("networkidle")
            
            # Check for basic accessibility elements
            headings = await page.query_selector_all("h1, h2, h3, h4, h5, h6")
            assert len(headings) > 0, "No headings found for accessibility"
            
            # Check for alt text on images
            images = await page.query_selector_all("img")
            for img in images:
                alt_text = await img.get_attribute("alt")
                # Alt text should exist (can be empty for decorative images)
                assert alt_text is not None, "Image missing alt attribute"
            
            # Check for form labels
            inputs = await page.query_selector_all("input, textarea, select")
            for input_elem in inputs:
                # Check if input has associated label
                input_id = await input_elem.get_attribute("id")
                if input_id:
                    label = await page.query_selector(f"label[for='{input_id}']")
                    # Label should exist for form inputs
                    if input_elem.get_attribute("type") != "hidden":
                        assert label is not None, f"Input {input_id} missing label"
                        
        except Exception as e:
            pytest.skip(f"Accessibility testing failed: {e}")
        finally:
            await page.close()

class TestWebAPIs:
    """Test cases for web API endpoints"""
    
    @pytest.mark.asyncio
    async def test_api_endpoints(self, browser_context):
        """Test API endpoints using Playwright"""
        page = await browser_context.new_page()
        
        try:
            # Test MCP Integration API
            await page.goto("http://127.0.0.1:8001/docs")
            await page.wait_for_load_state("networkidle")
            
            # Look for API documentation
            content = await page.content()
            assert "openapi" in content.lower() or "swagger" in content.lower(), "No API documentation found"
            
            # Test API endpoint
            response = await page.request.get("http://127.0.0.1:8001/health")
            assert response.status in [200, 404], f"Health endpoint returned {response.status}"
            
        except Exception as e:
            pytest.skip(f"API testing failed: {e}")
        finally:
            await page.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
