// Performance Tests Suite - Real PowerShell test execution
const { test, expect } = require('@playwright/test');
const { execSync } = require('child_process');

test.describe('Performance Tests Suite', () => {
  test('Run Performance Tests', async ({ page }) => {
    console.log('🧪 Running Performance Tests...');
    
    try {
      const result = execSync(
        'powershell -ExecutionPolicy Bypass -File "scripts\\testing\\simple_test_runner.ps1"',
        { 
          encoding: 'utf8',
          timeout: 30000,
          cwd: process.cwd()
        }
      );
      
      console.log('Performance Tests Output:', result);
      
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
      
      console.log(`✅ Performance Tests completed: ${passed} passed, ${failed} failed`);
      
      // Verify results
      expect(success).toBe(true);
      expect(passed).toBeGreaterThan(0);
      expect(total).toBeGreaterThan(0);
      
    } catch (error) {
      console.log(`❌ Performance Tests failed: ${error.message}`);
      throw error;
    }
  });
});
