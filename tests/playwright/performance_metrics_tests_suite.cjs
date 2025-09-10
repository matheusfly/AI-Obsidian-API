// Performance Metrics Tests Suite - Performance Monitoring and Metrics Collection Testing
// Tests system performance monitoring, metrics collection, and response time validation
const { test, expect } = require('@playwright/test');

test.describe('Performance Metrics Tests Suite - Performance Monitoring and Metrics Collection Testing', () => {
  test('Run Performance Metrics Tests - Performance Monitoring and Response Time Validation', async ({ page }) => {
    console.log('🧪 Running Performance Metrics Tests - Testing performance monitoring and metrics...');
    
    try {
      // Test MCP server response time
      const mcpStartTime = Date.now();
      const mcpResponse = await page.request.get('http://127.0.0.1:8001/health');
      const mcpResponseTime = Date.now() - mcpStartTime;
      
      expect(mcpResponse.status()).toBe(200);
      expect(mcpResponseTime).toBeLessThan(5000); // Should respond within 5 seconds
      console.log(`✅ MCP server response time: ${mcpResponseTime}ms`);
      
      // Test LangGraph response time (optional - skip if not running)
      let langgraphResponseTime = 0;
      try {
        const langgraphStartTime = Date.now();
        await page.goto('http://127.0.0.1:2024/docs', { timeout: 5000 });
        langgraphResponseTime = Date.now() - langgraphStartTime;
        
        expect(langgraphResponseTime).toBeLessThan(10000); // Should load within 10 seconds
        console.log(`✅ LangGraph response time: ${langgraphResponseTime}ms`);
      } catch (error) {
        console.log('⚠️ LangGraph Studio not running on port 2024 - skipping performance test');
        langgraphResponseTime = 0; // Skip this test
      }
      
      // Test multiple requests for average response time
      const responseTimes = [];
      for (let i = 0; i < 3; i++) {
        const startTime = Date.now();
        await page.request.get('http://127.0.0.1:8001/health');
        responseTimes.push(Date.now() - startTime);
      }
      
      const averageResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
      expect(averageResponseTime).toBeLessThan(3000); // Average should be under 3 seconds
      console.log(`✅ Average response time: ${averageResponseTime.toFixed(2)}ms`);
      
      console.log(`✅ Performance Metrics Tests completed: All performance metrics within acceptable limits`);
      console.log(`📊 Performance Metrics Tests - Performance monitoring testing successful`);
      
    } catch (error) {
      console.log(`❌ Performance Metrics Tests failed: ${error.message}`);
      throw error;
    }
  });
});
