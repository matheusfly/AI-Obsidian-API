const { test, expect } = require('@playwright/test');

test('MCP Integration Server health check', async ({ request }) => {
  const response = await request.get('http://127.0.0.1:8001/health');
  expect(response.status()).toBe(200);
});

test('LangGraph Studio health check', async ({ request }) => {
  const response = await request.get('http://127.0.0.1:2024/ok');
  expect(response.status()).toBe(200);
});

test('MCP Debug Dashboard accessibility', async ({ page }) => {
  await page.goto('http://127.0.0.1:8003/');
  await expect(page).toHaveTitle(/MCP Debug Dashboard/);
});
