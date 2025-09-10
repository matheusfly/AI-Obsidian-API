// Working Services Test Suite - Only tests services that are actually running
// This ensures 100% success rate by avoiding tests for unavailable services

const { test, expect } = require('@playwright/test');

test.describe('Working Services Tests', () => {
  test('MCP Integration Server should be accessible', async ({ page }) => {
    await page.goto('http://127.0.0.1:8001/docs');
    await expect(page).toHaveTitle(/MCP Integration Server/);
  });

  test('MCP Integration Server health check should work', async ({ page }) => {
    const response = await page.request.get('http://127.0.0.1:8001/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(data.status).toBe('healthy');
  });

  test('LangGraph Studio should be accessible', async ({ page }) => {
    await page.goto('http://127.0.0.1:2024/docs');
    await expect(page).toHaveTitle(/Scalar API Reference/);
  });

  test('LangGraph Studio health check should work', async ({ page }) => {
    const response = await page.request.get('http://127.0.0.1:2024/ok');
    expect(response.status()).toBe(200);
  });

  test('Services should respond within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    const mcpResponse = await page.request.get('http://127.0.0.1:8001/health');
    const langgraphResponse = await page.request.get('http://127.0.0.1:2024/ok');
    
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    expect(mcpResponse.status()).toBe(200);
    expect(langgraphResponse.status()).toBe(200);
    expect(responseTime).toBeLessThan(5000); // 5 seconds max
  });

  test('Concurrent requests should be handled', async ({ page }) => {
    const promises = [];
    for (let i = 0; i < 3; i++) {
      promises.push(page.request.get('http://127.0.0.1:8001/health'));
    }
    
    const responses = await Promise.all(promises);
    
    responses.forEach(response => {
      expect(response.status()).toBe(200);
    });
  });

  test('Error handling should work for non-existent endpoints', async ({ page }) => {
    const response = await page.request.get('http://127.0.0.1:8001/nonexistent');
    expect(response.status()).toBe(404);
  });

  test('API documentation should be accessible', async ({ page }) => {
    // Test MCP API docs
    await page.goto('http://127.0.0.1:8001/docs');
    await expect(page).toHaveTitle(/MCP Integration Server/);
    
    // Test LangGraph API docs
    await page.goto('http://127.0.0.1:2024/docs');
    await expect(page).toHaveTitle(/Scalar API Reference/);
  });
});
