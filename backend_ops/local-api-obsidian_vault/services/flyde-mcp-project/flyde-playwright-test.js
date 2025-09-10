#!/usr/bin/env node

/**
 * Flyde UI Playwright Test Suite
 * 
 * Comprehensive testing of the Flyde UI with MCP debugging,
 * Sentry integration, and real-time monitoring.
 */

import { chromium } from 'playwright';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class FlydePlaywrightTestSuite {
  constructor() {
    this.browser = null;
    this.page = null;
    this.serverProcess = null;
    this.debugProcess = null;
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

  async startServer() {
    console.log('🚀 Starting Flyde Web Server...');
    
    return new Promise((resolve, reject) => {
      // Try different ports
      const ports = [3000, 3001, 3002, 3003];
      let currentPort = 0;
      
      const tryNextPort = () => {
        if (currentPort >= ports.length) {
          reject(new Error('All ports are busy'));
          return;
        }
        
        const port = ports[currentPort];
        console.log(`🌐 Trying port ${port}...`);
        
        this.serverProcess = spawn('node', ['mcp-web-server.js'], {
          env: { ...process.env, PORT: port.toString() },
          cwd: path.join(__dirname)
        });
        
        this.serverProcess.stdout.on('data', (data) => {
          const output = data.toString();
          if (output.includes('Server running at')) {
            console.log(`✅ Server started on port ${port}`);
            this.serverPort = port;
            resolve(port);
          }
        });
        
        this.serverProcess.stderr.on('data', (data) => {
          const error = data.toString();
          if (error.includes('Port') && error.includes('already in use')) {
            console.log(`❌ Port ${port} is busy, trying next...`);
            this.serverProcess.kill();
            currentPort++;
            setTimeout(tryNextPort, 1000);
          }
        });
        
        this.serverProcess.on('error', (err) => {
          console.error('Failed to start server:', err);
          currentPort++;
          setTimeout(tryNextPort, 1000);
        });
        
        // Timeout after 15 seconds
        setTimeout(() => {
          if (!this.serverPort) {
            this.serverProcess.kill();
            currentPort++;
            setTimeout(tryNextPort, 1000);
          }
        }, 15000);
      };
      
      tryNextPort();
    });
  }

  async startDebugMonitor() {
    console.log('🔍 Starting MCP Debug Monitor...');
    
    return new Promise((resolve, reject) => {
      this.debugProcess = spawn('node', ['mcp-debug-monitor.js'], {
        cwd: path.join(__dirname)
      });
      
      this.debugProcess.stdout.on('data', (data) => {
        console.log(`[DEBUG] ${data.toString().trim()}`);
      });
      
      this.debugProcess.stderr.on('data', (data) => {
        console.log(`[DEBUG ERROR] ${data.toString().trim()}`);
      });
      
      this.debugProcess.on('error', (error) => {
        console.error('Failed to start debug monitor:', error);
        reject(error);
      });
      
      // Wait a moment for debug monitor to start
      setTimeout(() => {
        console.log('✅ MCP Debug Monitor started');
        resolve();
      }, 2000);
    });
  }

  async setupBrowser() {
    console.log('🎭 Setting up Playwright Browser...');
    
    this.browser = await chromium.launch({ 
      headless: false, // Show browser for debugging
      slowMo: 1000, // Slow down actions for better visibility
      devtools: true // Open DevTools for debugging
    });
    
    const context = await this.browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    
    this.page = await context.newPage();
    
    // Set up console logging
    this.page.on('console', msg => {
      console.log(`🖥️ Browser Console [${msg.type()}]:`, msg.text());
    });
    
    // Set up error handling
    this.page.on('pageerror', error => {
      console.error('🚨 Page Error:', error.message);
      this.testResults.errors.push({
        type: 'page_error',
        message: error.message,
        stack: error.stack
      });
    });
    
    console.log('✅ Browser setup complete');
  }

  async runTest(testName, testFunction) {
    console.log(`\n🧪 Running test: ${testName}`);
    this.testResults.total++;
    
    try {
      const startTime = Date.now();
      await testFunction();
      const duration = Date.now() - startTime;
      
      console.log(`✅ Test passed: ${testName} (${duration}ms)`);
      this.testResults.passed++;
      this.testResults.performance.push({
        test: testName,
        duration,
        success: true
      });
      
    } catch (error) {
      console.error(`❌ Test failed: ${testName}`);
      console.error(`   Error: ${error.message}`);
      this.testResults.failed++;
      this.testResults.errors.push({
        test: testName,
        message: error.message,
        stack: error.stack
      });
    }
  }

  async testPageLoad() {
    const url = `http://localhost:${this.serverPort}`;
    console.log(`📄 Loading page: ${url}`);
    
    await this.page.goto(url, { waitUntil: 'networkidle' });
    
    // Check if page loaded successfully
    const title = await this.page.title();
    if (!title.includes('MCP Playground')) {
      throw new Error(`Unexpected page title: ${title}`);
    }
    
    // Check if main elements are present
    const header = await this.page.textContent('h1');
    if (!header.includes('MCP Playground')) {
      throw new Error('Main header not found');
    }
    
    console.log('✅ Page loaded successfully');
  }

  async testMCPExamples() {
    console.log('🎮 Testing MCP Examples...');
    
    // Wait for example cards to load
    await this.page.waitForSelector('.example-card', { timeout: 10000 });
    
    // Test all example cards
    const examples = [
      { id: 'hello-world', name: 'Hello World MCP' },
      { id: 'ai-agent', name: 'AI Agent MCP' },
      { id: 'data-pipeline', name: 'Data Pipeline MCP' },
      { id: 'web-scraper', name: 'Web Scraper MCP' }
    ];
    
    for (const example of examples) {
      console.log(`  Testing ${example.name}...`);
      
      const card = await this.page.$(`#example-${example.id}`);
      if (!card) {
        throw new Error(`${example.name} card not found`);
      }
      
      await card.click();
      console.log(`  ✅ Clicked ${example.name} card`);
      
      // Wait for execution to start
      await this.page.waitForSelector(`#example-${example.id}.running`, { timeout: 5000 });
      console.log(`  ✅ ${example.name} shows running state`);
      
      // Wait for execution to complete
      await this.page.waitForSelector(`#example-${example.id}.success`, { timeout: 15000 });
      console.log(`  ✅ ${example.name} shows success state`);
      
      // Record MCP operation
      this.testResults.mcpOperations.push({
        type: 'mcp_example',
        example: example.name,
        success: true,
        timestamp: new Date().toISOString()
      });
    }
  }

  async testSentryIntegration() {
    console.log('🔍 Testing Sentry Integration...');
    
    // Check console for Sentry MCP logs
    const consoleLogs = [];
    this.page.on('console', msg => {
      if (msg.text().includes('[SENTRY MCP]')) {
        consoleLogs.push(msg.text());
      }
    });
    
    // Trigger an example to generate Sentry logs
    const aiAgentCard = await this.page.$('#example-ai-agent');
    await aiAgentCard.click();
    
    // Wait for completion
    await this.page.waitForSelector('#example-ai-agent.success', { timeout: 15000 });
    
    // Check if Sentry logs were generated
    if (consoleLogs.length === 0) {
      throw new Error('No Sentry MCP logs found');
    }
    
    console.log(`✅ Found ${consoleLogs.length} Sentry MCP logs`);
  }

  async testOutputPanel() {
    console.log('📊 Testing Output Panel...');
    
    // Check if output panel exists
    const outputPanel = await this.page.$('#output');
    if (!outputPanel) {
      throw new Error('Output panel not found');
    }
    
    // Check if output content is present
    const outputContent = await this.page.textContent('#output');
    if (!outputContent.includes('Starting:')) {
      throw new Error('Expected output content not found');
    }
    
    console.log('✅ Output panel working correctly');
  }

  async testMetrics() {
    console.log('📈 Testing Metrics...');
    
    // Check if metrics are present
    const totalExamples = await this.page.textContent('#totalExamples');
    if (totalExamples === '0') {
      throw new Error('Metrics not updating');
    }
    
    const successRate = await this.page.textContent('#successRate');
    if (!successRate.includes('%')) {
      throw new Error('Success rate not in expected format');
    }
    
    console.log('✅ Metrics updating correctly');
  }

  async testControls() {
    console.log('🎛️ Testing Control Buttons...');
    
    // Test Run All button
    const runAllButton = await this.page.$('button[onclick="runAllExamples()"]');
    if (!runAllButton) {
      throw new Error('Run All button not found');
    }
    
    await runAllButton.click();
    console.log('✅ Clicked Run All button');
    
    // Wait for all examples to complete
    await this.page.waitForFunction(() => {
      const runningCards = document.querySelectorAll('.example-card.running');
      return runningCards.length === 0;
    }, { timeout: 30000 });
    
    console.log('✅ All examples completed');
  }

  async testAPIs() {
    console.log('🔌 Testing APIs...');
    
    // Test metrics API
    const metricsResponse = await fetch(`http://localhost:${this.serverPort}/api/metrics`);
    const metricsData = await metricsResponse.json();
    
    if (!metricsData.success) {
      throw new Error('Metrics API failed');
    }
    
    console.log('✅ Metrics API working');
    
    // Test system API
    const systemResponse = await fetch(`http://localhost:${this.serverPort}/api/system`);
    const systemData = await systemResponse.json();
    
    if (!systemData.success) {
      throw new Error('System API failed');
    }
    
    console.log('✅ System API working');
    
    // Test Sentry events API
    const sentryResponse = await fetch(`http://localhost:${this.serverPort}/api/sentry-events`);
    const sentryData = await sentryResponse.json();
    
    if (!sentryData.success) {
      throw new Error('Sentry events API failed');
    }
    
    console.log('✅ Sentry events API working');
  }

  async testPerformance() {
    console.log('⚡ Testing Performance...');
    
    const startTime = Date.now();
    
    // Test multiple operations
    const operations = [
      this.page.goto(`http://localhost:${this.serverPort}`),
      fetch(`http://localhost:${this.serverPort}/api/metrics`),
      fetch(`http://localhost:${this.serverPort}/api/system`)
    ];
    
    await Promise.all(operations);
    
    const duration = Date.now() - startTime;
    
    if (duration > 10000) {
      throw new Error(`Performance test failed: ${duration}ms (too slow)`);
    }
    
    console.log(`✅ Performance test passed: ${duration}ms`);
  }

  async runAllTests() {
    console.log('🧪 Starting Flyde UI Playwright Test Suite');
    console.log('==========================================');
    
    try {
      await this.startDebugMonitor();
      await this.startServer();
      await this.setupBrowser();
      
      await this.runTest('Page Load', () => this.testPageLoad());
      await this.runTest('MCP Examples', () => this.testMCPExamples());
      await this.runTest('Sentry Integration', () => this.testSentryIntegration());
      await this.runTest('Output Panel', () => this.testOutputPanel());
      await this.runTest('Metrics', () => this.testMetrics());
      await this.runTest('Controls', () => this.testControls());
      await this.runTest('APIs', () => this.testAPIs());
      await this.runTest('Performance', () => this.testPerformance());
      
    } catch (error) {
      console.error('🚨 Test suite failed:', error.message);
      this.testResults.errors.push({
        type: 'suite_failure',
        message: error.message,
        stack: error.stack
      });
    } finally {
      await this.cleanup();
    }
    
    this.printResults();
  }

  async cleanup() {
    console.log('\n🧹 Cleaning up...');
    
    if (this.browser) {
      await this.browser.close();
    }
    
    if (this.serverProcess) {
      this.serverProcess.kill();
    }
    
    if (this.debugProcess) {
      this.debugProcess.kill();
    }
  }

  printResults() {
    const totalDuration = Date.now() - this.startTime;
    const successRate = this.testResults.total > 0 
      ? Math.round((this.testResults.passed / this.testResults.total) * 100)
      : 0;
    
    console.log('\n📊 FLYDE UI TEST RESULTS');
    console.log('========================');
    console.log(`Total Tests: ${this.testResults.total}`);
    console.log(`Passed: ${this.testResults.passed} ✅`);
    console.log(`Failed: ${this.testResults.failed} ❌`);
    console.log(`Success Rate: ${successRate}%`);
    console.log(`Total Duration: ${Math.round(totalDuration / 1000)}s`);
    console.log(`MCP Operations: ${this.testResults.mcpOperations.length}`);
    
    if (this.testResults.errors.length > 0) {
      console.log('\n🚨 ERRORS FOUND:');
      this.testResults.errors.forEach((error, index) => {
        console.log(`${index + 1}. ${error.test || error.type}: ${error.message}`);
      });
    }
    
    if (this.testResults.performance.length > 0) {
      console.log('\n⚡ PERFORMANCE METRICS:');
      this.testResults.performance.forEach(perf => {
        console.log(`  ${perf.test}: ${perf.duration}ms`);
      });
    }
    
    console.log('\n🎉 Flyde UI Playwright Test Suite completed!');
  }
}

// Run the test suite
const testSuite = new FlydePlaywrightTestSuite();
testSuite.runAllTests().catch(console.error);