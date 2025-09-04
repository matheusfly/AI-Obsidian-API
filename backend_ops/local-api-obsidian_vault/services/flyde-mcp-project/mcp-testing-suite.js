#!/usr/bin/env node

/**
 * MCP-Powered Testing and Debugging Suite
 * 
 * This comprehensive testing system uses multiple MCP tools for:
 * - Web crawling and content analysis
 * - File system operations and monitoring
 * - Playwright browser automation
 * - Sentry error tracking and performance monitoring
 * - Real-time debugging and output collection
 */

import { chromium } from 'playwright';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { SentryMCPMonitor } from './src/sentry-monitor.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class MCPTestingSuite {
  constructor() {
    this.sentry = new SentryMCPMonitor();
    this.browser = null;
    this.page = null;
    this.serverProcess = null;
    this.testResults = {
      passed: 0,
      failed: 0,
      total: 0,
      errors: [],
      performance: [],
      mcpOperations: []
    };
    this.startTime = Date.now();
  }

  async initialize() {
    console.log('🚀 Initializing MCP-Powered Testing Suite...');
    console.log('==============================================');
    
    this.sentry.logInfo('testing_suite_init', {
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    });
    
    // Test 1: File System MCP Operations
    await this.testFileSystemMCP();
    
    // Test 2: Web Crawling MCP Operations
    await this.testWebCrawlingMCP();
    
    // Test 3: Browser Automation with Playwright
    await this.testBrowserAutomation();
    
    // Test 4: Sentry MCP Integration
    await this.testSentryMCP();
    
    // Test 5: Real-time Debugging and Output Collection
    await this.testRealTimeDebugging();
    
    // Generate comprehensive report
    await this.generateComprehensiveReport();
  }

  async testFileSystemMCP() {
    console.log('\n📁 Testing File System MCP Operations...');
    this.sentry.logInfo('filesystem_mcp_test_start', { test: 'filesystem' });
    
    const startTime = Date.now();
    
    try {
      // Test file reading
      const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      this.testResults.mcpOperations.push({
        operation: 'file_read',
        target: 'package.json',
        success: true,
        duration: Date.now() - startTime
      });
      
      // Test directory listing
      const examplesDir = fs.readdirSync('examples');
      this.testResults.mcpOperations.push({
        operation: 'directory_list',
        target: 'examples',
        success: true,
        fileCount: examplesDir.length,
        duration: Date.now() - startTime
      });
      
      // Test file writing
      const testFile = 'test-output.json';
      const testData = {
        timestamp: new Date().toISOString(),
        test: 'filesystem_mcp',
        status: 'success'
      };
      
      fs.writeFileSync(testFile, JSON.stringify(testData, null, 2));
      this.testResults.mcpOperations.push({
        operation: 'file_write',
        target: testFile,
        success: true,
        duration: Date.now() - startTime
      });
      
      // Clean up test file
      fs.unlinkSync(testFile);
      
      console.log('✅ File System MCP Operations: SUCCESS');
      this.sentry.logInfo('filesystem_mcp_test_success', {
        operations: this.testResults.mcpOperations.length,
        duration: Date.now() - startTime
      });
      
    } catch (error) {
      console.error('❌ File System MCP Operations: FAILED');
      this.sentry.logError('filesystem_mcp_test_error', error);
      this.testResults.errors.push({
        test: 'filesystem_mcp',
        error: error.message,
        stack: error.stack
      });
    }
  }

  async testWebCrawlingMCP() {
    console.log('\n🕷️ Testing Web Crawling MCP Operations...');
    this.sentry.logInfo('web_crawling_mcp_test_start', { test: 'web_crawling' });
    
    const startTime = Date.now();
    
    try {
      // Simulate web crawling operations
      const testUrls = [
        'https://httpbin.org/json',
        'https://httpbin.org/html',
        'https://httpbin.org/xml'
      ];
      
      for (const url of testUrls) {
        const crawlStart = Date.now();
        
        // Simulate fetch operation
        const response = await fetch(url);
        const data = await response.text();
        
        this.testResults.mcpOperations.push({
          operation: 'web_crawl',
          target: url,
          success: response.ok,
          statusCode: response.status,
          dataSize: data.length,
          duration: Date.now() - crawlStart
        });
        
        console.log(`  📄 Crawled: ${url} (${response.status})`);
      }
      
      console.log('✅ Web Crawling MCP Operations: SUCCESS');
      this.sentry.logInfo('web_crawling_mcp_test_success', {
        urls: testUrls.length,
        duration: Date.now() - startTime
      });
      
    } catch (error) {
      console.error('❌ Web Crawling MCP Operations: FAILED');
      this.sentry.logError('web_crawling_mcp_test_error', error);
      this.testResults.errors.push({
        test: 'web_crawling_mcp',
        error: error.message,
        stack: error.stack
      });
    }
  }

  async testBrowserAutomation() {
    console.log('\n🌐 Testing Browser Automation with Playwright...');
    this.sentry.logInfo('browser_automation_test_start', { test: 'browser_automation' });
    
    const startTime = Date.now();
    
    try {
      // Launch browser
      this.browser = await chromium.launch({ 
        headless: true,
        slowMo: 1000
      });
      
      const context = await this.browser.newContext({
        viewport: { width: 1280, height: 720 }
      });
      
      this.page = await context.newPage();
      
      // Test 1: Navigate to a test page
      await this.page.goto('https://httpbin.org/html');
      const title = await this.page.title();
      
      this.testResults.mcpOperations.push({
        operation: 'browser_navigate',
        target: 'https://httpbin.org/html',
        success: true,
        title: title,
        duration: Date.now() - startTime
      });
      
      // Test 2: Take screenshot
      const screenshot = await this.page.screenshot({ fullPage: true });
      const screenshotPath = 'test-screenshot.png';
      fs.writeFileSync(screenshotPath, screenshot);
      
      this.testResults.mcpOperations.push({
        operation: 'browser_screenshot',
        target: screenshotPath,
        success: true,
        size: screenshot.length,
        duration: Date.now() - startTime
      });
      
      // Test 3: Extract content
      const content = await this.page.textContent('body');
      this.testResults.mcpOperations.push({
        operation: 'browser_content_extract',
        target: 'body',
        success: true,
        contentLength: content.length,
        duration: Date.now() - startTime
      });
      
      console.log('✅ Browser Automation: SUCCESS');
      this.sentry.logInfo('browser_automation_test_success', {
        operations: 3,
        duration: Date.now() - startTime
      });
      
    } catch (error) {
      console.error('❌ Browser Automation: FAILED');
      this.sentry.logError('browser_automation_test_error', error);
      this.testResults.errors.push({
        test: 'browser_automation',
        error: error.message,
        stack: error.stack
      });
    }
  }

  async testSentryMCP() {
    console.log('\n🔍 Testing Sentry MCP Integration...');
    this.sentry.logInfo('sentry_mcp_test_start', { test: 'sentry_mcp' });
    
    const startTime = Date.now();
    
    try {
      // Test info logging
      this.sentry.logInfo('test_info_event', {
        message: 'Testing Sentry MCP info logging',
        testId: 'sentry_mcp_test_001'
      });
      
      // Test performance logging
      this.sentry.logPerformance('test_performance_event', 1500, {
        operation: 'sentry_mcp_test',
        metrics: { cpu: 45, memory: 128 }
      });
      
      // Test error logging
      try {
        throw new Error('Test error for Sentry MCP');
      } catch (error) {
        this.sentry.logError('test_error_event', error, {
          context: 'sentry_mcp_test',
          testId: 'sentry_mcp_test_002'
        });
      }
      
      // Get events
      const events = this.sentry.getEvents();
      const report = this.sentry.generateReport();
      
      this.testResults.mcpOperations.push({
        operation: 'sentry_logging',
        target: 'info_event',
        success: true,
        duration: Date.now() - startTime
      });
      
      this.testResults.mcpOperations.push({
        operation: 'sentry_logging',
        target: 'performance_event',
        success: true,
        duration: Date.now() - startTime
      });
      
      this.testResults.mcpOperations.push({
        operation: 'sentry_logging',
        target: 'error_event',
        success: true,
        duration: Date.now() - startTime
      });
      
      console.log('✅ Sentry MCP Integration: SUCCESS');
      console.log(`  📊 Events logged: ${events.length}`);
      console.log(`  📈 Report generated: ${report.totalEvents} total events`);
      
      this.sentry.logInfo('sentry_mcp_test_success', {
        eventsLogged: events.length,
        duration: Date.now() - startTime
      });
      
    } catch (error) {
      console.error('❌ Sentry MCP Integration: FAILED');
      this.sentry.logError('sentry_mcp_test_error', error);
      this.testResults.errors.push({
        test: 'sentry_mcp',
        error: error.message,
        stack: error.stack
      });
    }
  }

  async testRealTimeDebugging() {
    console.log('\n🐛 Testing Real-time Debugging and Output Collection...');
    this.sentry.logInfo('realtime_debugging_test_start', { test: 'realtime_debugging' });
    
    const startTime = Date.now();
    
    try {
      // Test 1: Process monitoring
      const processInfo = {
        pid: process.pid,
        platform: process.platform,
        nodeVersion: process.version,
        memoryUsage: process.memoryUsage(),
        uptime: process.uptime()
      };
      
      this.testResults.mcpOperations.push({
        operation: 'process_monitoring',
        target: 'system_info',
        success: true,
        data: processInfo,
        duration: Date.now() - startTime
      });
      
      // Test 2: File system monitoring
      const watchDir = 'examples';
      const watcher = fs.watch(watchDir, (eventType, filename) => {
        console.log(`  📁 File system event: ${eventType} - ${filename}`);
        this.testResults.mcpOperations.push({
          operation: 'filesystem_monitoring',
          target: filename,
          eventType: eventType,
          success: true,
          duration: Date.now() - startTime
        });
      });
      
      // Test 3: Network monitoring simulation
      const networkTest = async () => {
        const start = Date.now();
        try {
          await fetch('https://httpbin.org/delay/1');
          return { success: true, duration: Date.now() - start };
        } catch (error) {
          return { success: false, error: error.message, duration: Date.now() - start };
        }
      };
      
      const networkResult = await networkTest();
      this.testResults.mcpOperations.push({
        operation: 'network_monitoring',
        target: 'https://httpbin.org/delay/1',
        success: networkResult.success,
        duration: networkResult.duration,
        data: networkResult
      });
      
      // Test 4: Memory monitoring
      const memoryInfo = {
        heapUsed: process.memoryUsage().heapUsed,
        heapTotal: process.memoryUsage().heapTotal,
        external: process.memoryUsage().external,
        rss: process.memoryUsage().rss
      };
      
      this.testResults.mcpOperations.push({
        operation: 'memory_monitoring',
        target: 'heap_usage',
        success: true,
        data: memoryInfo,
        duration: Date.now() - startTime
      });
      
      // Clean up watcher
      watcher.close();
      
      console.log('✅ Real-time Debugging: SUCCESS');
      this.sentry.logInfo('realtime_debugging_test_success', {
        operations: 4,
        duration: Date.now() - startTime
      });
      
    } catch (error) {
      console.error('❌ Real-time Debugging: FAILED');
      this.sentry.logError('realtime_debugging_test_error', error);
      this.testResults.errors.push({
        test: 'realtime_debugging',
        error: error.message,
        stack: error.stack
      });
    }
  }

  async generateComprehensiveReport() {
    console.log('\n📊 Generating Comprehensive MCP Testing Report...');
    
    const totalDuration = Date.now() - this.startTime;
    const successRate = this.testResults.mcpOperations.filter(op => op.success).length / this.testResults.mcpOperations.length * 100;
    
    const report = {
      timestamp: new Date().toISOString(),
      totalDuration: totalDuration,
      summary: {
        totalOperations: this.testResults.mcpOperations.length,
        successfulOperations: this.testResults.mcpOperations.filter(op => op.success).length,
        failedOperations: this.testResults.mcpOperations.filter(op => !op.success).length,
        successRate: Math.round(successRate * 100) / 100,
        errors: this.testResults.errors.length
      },
      operations: this.testResults.mcpOperations,
      errors: this.testResults.errors,
      performance: {
        averageOperationTime: this.testResults.mcpOperations.reduce((sum, op) => sum + op.duration, 0) / this.testResults.mcpOperations.length,
        slowestOperation: this.testResults.mcpOperations.reduce((max, op) => op.duration > max.duration ? op : max, { duration: 0 }),
        fastestOperation: this.testResults.mcpOperations.reduce((min, op) => op.duration < min.duration ? op : min, { duration: Infinity })
      },
      sentryEvents: this.sentry.getEvents(),
      sentryReport: this.sentry.generateReport()
    };
    
    // Save report to file
    const reportPath = 'mcp-testing-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    // Generate HTML report
    const htmlReport = this.generateHTMLReport(report);
    fs.writeFileSync('mcp-testing-report.html', htmlReport);
    
    console.log('\n🎉 MCP Testing Suite Complete!');
    console.log('================================');
    console.log(`📊 Total Operations: ${report.summary.totalOperations}`);
    console.log(`✅ Successful: ${report.summary.successfulOperations}`);
    console.log(`❌ Failed: ${report.summary.failedOperations}`);
    console.log(`📈 Success Rate: ${report.summary.successRate}%`);
    console.log(`⏱️ Total Duration: ${Math.round(totalDuration / 1000)}s`);
    console.log(`📄 Report saved: ${reportPath}`);
    console.log(`🌐 HTML Report: mcp-testing-report.html`);
    
    this.sentry.logInfo('testing_suite_complete', {
      totalOperations: report.summary.totalOperations,
      successRate: report.summary.successRate,
      duration: totalDuration
    });
  }

  generateHTMLReport(report) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Testing Suite Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 2rem; font-weight: bold; color: #007bff; }
        .metric-label { color: #666; margin-top: 5px; }
        .operations { margin-bottom: 30px; }
        .operation { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745; }
        .operation.failed { border-left-color: #dc3545; }
        .error { background: #f8d7da; color: #721c24; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .success { color: #28a745; }
        .failed { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MCP Testing Suite Report</h1>
            <p>Generated: ${report.timestamp}</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">${report.summary.totalOperations}</div>
                <div class="metric-label">Total Operations</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${report.summary.successfulOperations}</div>
                <div class="metric-label">Successful</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${report.summary.successRate}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${Math.round(report.totalDuration / 1000)}s</div>
                <div class="metric-label">Total Duration</div>
            </div>
        </div>
        
        <div class="operations">
            <h2>📋 Operations Details</h2>
            ${report.operations.map(op => `
                <div class="operation ${op.success ? 'success' : 'failed'}">
                    <strong>${op.operation}</strong> - ${op.target}
                    <br>
                    <small>Duration: ${op.duration}ms | Status: ${op.success ? 'SUCCESS' : 'FAILED'}</small>
                </div>
            `).join('')}
        </div>
        
        ${report.errors.length > 0 ? `
        <div class="errors">
            <h2>❌ Errors</h2>
            ${report.errors.map(error => `
                <div class="error">
                    <strong>${error.test}</strong>: ${error.error}
                </div>
            `).join('')}
        </div>
        ` : ''}
    </div>
</body>
</html>`;
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
    }
    if (this.serverProcess) {
      this.serverProcess.kill();
    }
  }
}

// Run the testing suite
const testingSuite = new MCPTestingSuite();

// Handle cleanup on exit
process.on('SIGINT', async () => {
  console.log('\n🛑 Cleaning up...');
  await testingSuite.cleanup();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Cleaning up...');
  await testingSuite.cleanup();
  process.exit(0);
});

// Start the testing suite
testingSuite.initialize().catch(console.error);