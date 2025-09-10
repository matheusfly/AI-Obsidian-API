// Performance Optimization Tests Suite - System Performance Monitoring and Optimization
// Tests system performance and identifies optimization opportunities
const { test, expect } = require('@playwright/test');

test.describe('Performance Optimization Tests Suite - System Performance Monitoring and Optimization', () => {
  test('Run Performance Optimization Tests - System Performance Analysis and Optimization', async ({ page }) => {
    console.log('🧪 Running Performance Optimization Tests - Analyzing system performance...');
    
    try {
      // Test MCP server response time with multiple samples
      const responseTimes = [];
      const sampleCount = 5;
      
      for (let i = 0; i < sampleCount; i++) {
        const startTime = Date.now();
        const response = await page.request.get('http://127.0.0.1:8001/health');
        const responseTime = Date.now() - startTime;
        
        expect(response.status()).toBe(200);
        responseTimes.push(responseTime);
        
        // Add small delay between requests to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      // Calculate statistics
      const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
      const minResponseTime = Math.min(...responseTimes);
      const maxResponseTime = Math.max(...responseTimes);
      
      console.log(`📊 Performance Analysis:`);
      console.log(`  - Sample Count: ${sampleCount}`);
      console.log(`  - Average Response Time: ${avgResponseTime.toFixed(2)}ms`);
      console.log(`  - Min Response Time: ${minResponseTime}ms`);
      console.log(`  - Max Response Time: ${maxResponseTime}ms`);
      console.log(`  - All Response Times: [${responseTimes.join(', ')}]ms`);
      
      // Performance thresholds
      const excellentThreshold = 50;  // < 50ms is excellent
      const goodThreshold = 100;      // < 100ms is good
      const acceptableThreshold = 200; // < 200ms is acceptable
      
      let performanceGrade;
      if (avgResponseTime < excellentThreshold) {
        performanceGrade = 'EXCELLENT';
      } else if (avgResponseTime < goodThreshold) {
        performanceGrade = 'GOOD';
      } else if (avgResponseTime < acceptableThreshold) {
        performanceGrade = 'ACCEPTABLE';
      } else {
        performanceGrade = 'NEEDS_OPTIMIZATION';
      }
      
      console.log(`  - Performance Grade: ${performanceGrade}`);
      
      // Verify performance is within acceptable limits
      expect(avgResponseTime).toBeLessThan(acceptableThreshold);
      expect(maxResponseTime).toBeLessThan(acceptableThreshold * 2);
      
      // Test concurrent requests performance
      console.log('🧪 Testing concurrent request performance...');
      const concurrentStartTime = Date.now();
      const concurrentPromises = [];
      
      for (let i = 0; i < 3; i++) {
        concurrentPromises.push(page.request.get('http://127.0.0.1:8001/health'));
      }
      
      const concurrentResponses = await Promise.all(concurrentPromises);
      const concurrentTime = Date.now() - concurrentStartTime;
      
      concurrentResponses.forEach(response => {
        expect(response.status()).toBe(200);
      });
      
      console.log(`  - Concurrent Requests (3): ${concurrentTime}ms`);
      expect(concurrentTime).toBeLessThan(1000); // Should complete within 1 second
      
      console.log(`✅ Performance Optimization Tests completed: ${performanceGrade} performance`);
      console.log(`📊 Performance Optimization Tests - System performance analysis successful`);
      
    } catch (error) {
      console.log(`❌ Performance Optimization Tests failed: ${error.message}`);
      throw error;
    }
  });
});
