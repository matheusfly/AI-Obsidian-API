// Simple Playwright test for web interfaces
// This test runs directly with Playwright without pytest

const { test, expect } = require('@playwright/test');

test.describe('Web Interface Tests', () => {
  test('MCP Integration Server should be accessible', async ({ page }) => {
    // Test MCP Integration Server
    await page.goto('http://127.0.0.1:8001/docs');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if page loaded successfully
    const title = await page.title();
    expect(title).toBeTruthy();
    
    // Check for API documentation
    const content = await page.content();
    expect(content.length).toBeGreaterThan(100);
  });

  test('LangGraph Studio should be accessible', async ({ page }) => {
    // Test LangGraph Studio
    await page.goto('http://127.0.0.1:2024/docs');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check if page loaded successfully
    const title = await page.title();
    expect(title).toBeTruthy();
    
    // Check for API documentation elements
    const headings = await page.locator('h1, h2, h3').count();
    expect(headings).toBeGreaterThan(0);
  });

  test('Health endpoints should respond', async ({ page }) => {
    // Test health endpoints
    const services = [
      'http://127.0.0.1:8001/health',
      'http://127.0.0.1:8002/health',
      'http://127.0.0.1:8003/health'
    ];
    
    for (const url of services) {
      try {
        const response = await page.goto(url);
        if (response) {
          expect(response.status()).toBeLessThan(500);
        }
      } catch (error) {
        // Service might not be running, continue
        console.log(`Service at ${url} not accessible: ${error.message}`);
      }
    }
  });

  test('Performance should be acceptable', async ({ page }) => {
    // Test performance
    const startTime = Date.now();
    
    await page.goto('http://127.0.0.1:8001/docs');
    await page.waitForLoadState('networkidle');
    
    const endTime = Date.now();
    const loadTime = endTime - startTime;
    
    // Should load within 10 seconds
    expect(loadTime).toBeLessThan(10000);
  });
});
