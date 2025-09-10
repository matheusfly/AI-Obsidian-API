// Coverage setup for Playwright tests
const fs = require('fs');
const path = require('path');

async function globalSetup(config) {
  console.log('🔧 Setting up Playwright coverage collection...');
  
  // Create coverage directory
  const coverageDir = path.join(process.cwd(), 'test-reports', 'playwright', 'coverage');
  if (!fs.existsSync(coverageDir)) {
    fs.mkdirSync(coverageDir, { recursive: true });
  }
  
  // Initialize coverage data
  const coverageData = {
    timestamp: new Date().toISOString(),
    tests: [],
    coverage: {
      lines: { total: 0, covered: 0, percentage: 0 },
      functions: { total: 0, covered: 0, percentage: 0 },
      branches: { total: 0, covered: 0, percentage: 0 },
      statements: { total: 0, covered: 0, percentage: 0 }
    },
    summary: {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      successRate: 0
    }
  };
  
  // Save initial coverage data
  fs.writeFileSync(
    path.join(coverageDir, 'coverage-data.json'),
    JSON.stringify(coverageData, null, 2)
  );
  
  console.log('✅ Coverage setup completed');
}

module.exports = globalSetup;
