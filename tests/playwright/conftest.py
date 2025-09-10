"""
Playwright test configuration and fixtures
"""
import pytest
import asyncio
import subprocess
import time
import requests
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import AsyncGenerator, Generator
import os
import json


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def services_config():
    """Configuration for services to test"""
    return {
        "mcp_server": {
            "url": "http://localhost:8002",
            "health_endpoint": "/health",
            "timeout": 30
        },
        "api_gateway": {
            "url": "http://localhost:8001",
            "health_endpoint": "/health",
            "timeout": 30
        },
        "chromadb": {
            "url": "http://localhost:8000",
            "health_endpoint": "/api/v1/heartbeat",
            "timeout": 30
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "timeout": 30
        },
        "obsidian": {
            "url": "http://localhost:27123",
            "vault_endpoint": "/vault",
            "timeout": 10
        }
    }


@pytest.fixture(scope="session")
def wait_for_services(services_config):
    """Wait for all services to be ready before running tests"""
    def _wait_for_service(service_name, config):
        max_attempts = config.get("timeout", 30)
        attempt = 0
        
        while attempt < max_attempts:
            try:
                if service_name == "redis":
                    # Test Redis connection
                    import redis
                    r = redis.Redis(host=config["host"], port=config["port"])
                    r.ping()
                    return True
                else:
                    # Test HTTP services
                    response = requests.get(
                        f"{config['url']}{config['health_endpoint']}", 
                        timeout=5
                    )
                    if response.status_code == 200:
                        return True
            except Exception as e:
                print(f"Service {service_name} not ready: {e}")
                time.sleep(1)
                attempt += 1
        
        return False
    
    # Wait for all services
    for service_name, config in services_config.items():
        if not _wait_for_service(service_name, config):
            pytest.skip(f"Service {service_name} is not available")
    
    return True


@pytest.fixture(scope="session")
async def browser() -> AsyncGenerator[Browser, None]:
    """Create a browser instance for testing"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--allow-running-insecure-content"
            ]
        )
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Create a browser context for testing"""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Create a page for testing"""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture
def test_data():
    """Test data for various scenarios"""
    return {
        "vault_name": "Nomade Milionario",
        "test_file": "test-obsidian-file.md",
        "test_content": "# Test File\n\nThis is a test file for Obsidian integration.",
        "search_query": "test",
        "file_path": "test-folder/test-file.md"
    }


@pytest.fixture(scope="session")
def docker_services():
    """Manage Docker services for testing"""
    def start_services():
        """Start required Docker services"""
        services = ["redis", "chromadb", "mcp-server"]
        for service in services:
            try:
                # Check if service is already running
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"name={service}", "--format", "{{.Names}}"],
                    capture_output=True,
                    text=True
                )
                if service not in result.stdout:
                    # Start service
                    if service == "redis":
                        subprocess.run([
                            "docker", "run", "-d", "--name", "redis", 
                            "-p", "6379:6379", "redis:7-alpine"
                        ])
                    elif service == "chromadb":
                        subprocess.run([
                            "docker", "run", "-d", "--name", "chromadb",
                            "-p", "8000:8000", "-v", f"{os.getcwd()}/data/vector:/chroma/chroma",
                            "chromadb/chroma:latest"
                        ])
                    elif service == "mcp-server":
                        subprocess.run([
                            "docker", "run", "-d", "--name", "mcp-server",
                            "-p", "8002:8002", "-v", "D:/Nomade Milionario:/vault:rw",
                            "-e", "OBSIDIAN_VAULT_PATH=/vault",
                            "data-vault-mcp-server"
                        ])
            except Exception as e:
                print(f"Failed to start {service}: {e}")
    
    def stop_services():
        """Stop Docker services"""
        services = ["redis", "chromadb", "mcp-server"]
        for service in services:
            try:
                subprocess.run(["docker", "stop", service], capture_output=True)
                subprocess.run(["docker", "rm", service], capture_output=True)
            except Exception as e:
                print(f"Failed to stop {service}: {e}")
    
    # Start services
    start_services()
    
    yield
    
    # Cleanup
    stop_services()


@pytest.fixture
def api_client():
    """HTTP client for API testing"""
    import httpx
    return httpx.AsyncClient(timeout=30.0)


@pytest.fixture
def test_report_dir():
    """Directory for test reports"""
    report_dir = "test-reports"
    os.makedirs(report_dir, exist_ok=True)
    return report_dir
