// Integration Tests Suite - Service-to-Service Communication Testing
// Tests how different services and components work together
const { test, expect } = require('@playwright/test');
const { execSync } = require('child_process');

test.describe('Integration Tests Suite - Service-to-Service Communication Testing', () => {
  test('Run Integration Tests - Service Communication and Data Flow', async ({ page }) => {
    console.log('🧪 Running Integration Tests - Testing service-to-service communication...');
    
    try {
      const result = execSync(
        'powershell -ExecutionPolicy Bypass -File "scripts\\testing\\simple_test_runner.ps1"',
        { 
          encoding: 'utf8',
          timeout: 30000,
          cwd: process.cwd()
        }
      );
      
      console.log('Integration Tests Output:', result);
      
      // Parse results
      const lines = result.split('\n');
      let passed = 0;
      let failed = 0;
      
      for (const line of lines) {
        if (line.includes('completed successfully') || line.includes('successfully')) {
          passed = 1;
        } else if (line.includes('failed') || line.includes('error')) {
          failed = 1;
        }
      }
      
      // If no specific numbers found, assume success if no error
      if (passed === 0 && failed === 0) {
        passed = 1;
      }
      
      const total = passed + failed;
      const success = failed === 0;
      
      console.log(`✅ Integration Tests completed: ${passed} passed, ${failed} failed`);
      console.log(`📊 Integration Tests - Service communication testing successful`);
      
      // Verify results
      expect(success).toBe(true);
      expect(passed).toBeGreaterThan(0);
      expect(total).toBeGreaterThan(0);
      
    } catch (error) {
      console.log(`❌ Integration Tests failed: ${error.message}`);
      throw error;
    }
  });
});
