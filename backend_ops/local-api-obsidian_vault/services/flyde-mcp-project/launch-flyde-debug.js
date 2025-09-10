#!/usr/bin/env node

/**
 * Launch Flyde UI with Active MCP Debugging
 * 
 * This script launches the Flyde UI with comprehensive MCP debugging,
 * Playwright testing, and real-time monitoring capabilities.
 */

import { spawn } from 'child_process';
import { chromium } from 'playwright';
import { SentryMCPMonitor } from './src/sentry-monitor.js';
import fs from 'fs';
import path from 'path';

class FlydeUIDebugLauncher {
  constructor() {
    this.sentry = new SentryMCPMonitor();
    this.browser = null;
    this.page = null;
    this.serverProcess = null;
    this.debugProcess = null;
    this.testResults = {
      passed: 0,
      failed: 0,
      total: 0,
      errors: []
    };
  }

  async launch() {
    console.log('🚀 Launching Flyde UI with Active MCP Debugging...');
    console.log('==================================================');
    
    this.sentry.logInfo('flyde_ui_debug_launch', {
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    });

    try {
      // Step 1: Start MCP Debug Monitor
      await this.startMCPDebugMonitor();
      
      // Step 2: Start Flyde Web Server
      await this.startFlydeWebServer();
      
      // Step 3: Wait for server to be ready
      await this.waitForServerReady();
      
      // Step 4: Launch Playwright Browser
      await this.launchPlaywrightBrowser();
      
      // Step 5: Run Comprehensive Tests
      await this.runComprehensiveTests();
      
      // Step 6: Start Interactive Mode
      await this.startInteractiveMode();
      
    } catch (error) {
      console.error('❌ Launch failed:', error.message);
      this.sentry.logError('flyde_ui_launch_error', error);
      await this.cleanup();
      process.exit(1);
    }
  }

  async startMCPDebugMonitor() {
    console.log('🔍 Starting MCP Debug Monitor...');
    
    return new Promise((resolve, reject) => {
      this.debugProcess = spawn('node', ['mcp-debug-monitor.js'], {
        stdio: 'pipe',
        cwd: process.cwd()
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

  async startFlydeWebServer() {
    console.log('🌐 Starting Flyde Web Server...');
    
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
          stdio: 'pipe',
          cwd: process.cwd()
        });
        
        this.serverProcess.stdout.on('data', (data) => {
          const output = data.toString();
          console.log(`[SERVER] ${output.trim()}`);
          
          if (output.includes('Server running at')) {
            console.log(`✅ Flyde Web Server started on port ${port}`);
            this.serverPort = port;
            resolve();
          }
        });
        
        this.serverProcess.stderr.on('data', (data) => {
          const error = data.toString();
          if (error.includes('Port') && error.includes('already in use')) {
            console.log(`❌ Port ${port} is busy, trying next...`);
            this.serverProcess.kill();
            currentPort++;
            setTimeout(tryNextPort, 1000);
          } else {
            console.error(`[SERVER ERROR] ${error.trim()}`);
          }
        });
        
        this.serverProcess.on('error', (err) => {
          console.error('Failed to start server:', err);
          currentPort++;
          setTimeout(tryNextPort, 1000);
        });
        
        // Timeout after 10 seconds
        setTimeout(() => {
          if (!this.serverPort) {
            this.serverProcess.kill();
            currentPort++;
            setTimeout(tryNextPort, 1000);
          }
        }, 10000);
      };
      
      tryNextPort();
    });
  }

  async waitForServerReady() {
    console.log('⏳ Waiting for server to be ready...');
    
    const maxAttempts = 30;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        const response = await fetch(`http://localhost:${this.serverPort}/api/metrics`);
        if (response.ok) {
          console.log('✅ Server is ready!');
          this.sentry.logInfo('server_ready', {
            port: this.serverPort,
            attempts: attempts + 1
          });
          return;
        }
      } catch (error) {
        // Server not ready yet
      }
      
      attempts++;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error('Server failed to start within timeout');
  }

  async launchPlaywrightBrowser() {
    console.log('🎭 Launching Playwright Browser...');
    
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
      this.sentry.logError('browser_page_error', error);
      this.testResults.errors.push({
        type: 'page_error',
        message: error.message,
        stack: error.stack
      });
    });
    
    console.log('✅ Playwright Browser launched');
  }

  async runComprehensiveTests() {
    console.log('🧪 Running Comprehensive Tests...');
    
    const tests = [
      { name: 'Page Load Test', fn: () => this.testPageLoad() },
      { name: 'MCP Examples Test', fn: () => this.testMCPExamples() },
      { name: 'Sentry Integration Test', fn: () => this.testSentryIntegration() },
      { name: 'File System API Test', fn: () => this.testFileSystemAPI() },
      { name: 'Web Crawling API Test', fn: () => this.testWebCrawlingAPI() },
      { name: 'Performance Test', fn: () => this.testPerformance() }
    ];
    
    for (const test of tests) {
      await this.runTest(test.name, test.fn);
    }
    
    console.log('\n📊 Test Results Summary:');
    console.log(`✅ Passed: ${this.testResults.passed}`);
    console.log(`❌ Failed: ${this.testResults.failed}`);
    console.log(`📈 Success Rate: ${Math.round((this.testResults.passed / this.testResults.total) * 100)}%`);
  }

  async runTest(testName, testFunction) {
    console.log(`\n🧪 Running test: ${testName}`);
    this.testResults.total++;
    
    try {
      await testFunction();
      console.log(`✅ Test passed: ${testName}`);
      this.testResults.passed++;
      this.sentry.logInfo('test_passed', { testName });
    } catch (error) {
      console.error(`❌ Test failed: ${testName}`);
      console.error(`   Error: ${error.message}`);
      this.testResults.failed++;
      this.testResults.errors.push({
        test: testName,
        message: error.message,
        stack: error.stack
      });
      this.sentry.logError('test_failed', error, { testName });
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
    
    // Test clicking on Hello World card
    const helloWorldCard = await this.page.$('#example-hello-world');
    if (!helloWorldCard) {
      throw new Error('Hello World card not found');
    }
    
    await helloWorldCard.click();
    console.log('✅ Clicked Hello World card');
    
    // Wait for execution to start
    await this.page.waitForSelector('.example-card.running', { timeout: 5000 });
    console.log('✅ Card shows running state');
    
    // Wait for execution to complete
    await this.page.waitForSelector('.example-card.success', { timeout: 15000 });
    console.log('✅ Card shows success state');
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

  async testFileSystemAPI() {
    console.log('📁 Testing File System API...');
    
    const response = await fetch(`http://localhost:${this.serverPort}/api/filesystem`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        operation: 'list',
        path: 'examples'
      })
    });
    
    const result = await response.json();
    
    if (!result.success) {
      throw new Error(`File system API failed: ${result.error}`);
    }
    
    console.log('✅ File System API working');
  }

  async testWebCrawlingAPI() {
    console.log('🕷️ Testing Web Crawling API...');
    
    const response = await fetch(`http://localhost:${this.serverPort}/api/crawl`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: 'https://httpbin.org/json'
      })
    });
    
    const result = await response.json();
    
    if (!result.success) {
      throw new Error(`Web crawling API failed: ${result.error}`);
    }
    
    console.log('✅ Web Crawling API working');
  }

  async testPerformance() {
    console.log('📈 Testing Performance...');
    
    const startTime = Date.now();
    
    // Test multiple operations
    const operations = [
      fetch(`http://localhost:${this.serverPort}/api/metrics`),
      fetch(`http://localhost:${this.serverPort}/api/system`),
      fetch(`http://localhost:${this.serverPort}/api/sentry-events`)
    ];
    
    await Promise.all(operations);
    
    const duration = Date.now() - startTime;
    
    if (duration > 5000) {
      throw new Error(`Performance test failed: ${duration}ms (too slow)`);
    }
    
    console.log(`✅ Performance test passed: ${duration}ms`);
  }

  async startInteractiveMode() {
    console.log('\n🎮 Starting Interactive Mode...');
    console.log('================================');
    console.log(`🌐 Flyde UI: http://localhost:${this.serverPort}`);
    console.log('🔍 MCP Debug Monitor: Active');
    console.log('🎭 Playwright Browser: Open');
    console.log('📊 Test Results: Available');
    console.log('================================');
    console.log('\n🎯 Interactive Commands:');
    console.log('  - Press Ctrl+C to stop');
    console.log('  - Check browser for UI interactions');
    console.log('  - Monitor console for debug output');
    console.log('  - Check test results above');
    
    this.sentry.logInfo('interactive_mode_started', {
      serverPort: this.serverPort,
      testResults: this.testResults
    });
    
    // Keep the process running
    process.on('SIGINT', async () => {
      console.log('\n🛑 Shutting down...');
      await this.cleanup();
      process.exit(0);
    });
    
    // Keep alive
    while (true) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  async cleanup() {
    console.log('🧹 Cleaning up...');
    
    if (this.browser) {
      await this.browser.close();
    }
    
    if (this.serverProcess) {
      this.serverProcess.kill();
    }
    
    if (this.debugProcess) {
      this.debugProcess.kill();
    }
    
    this.sentry.logInfo('cleanup_complete', {
      timestamp: new Date().toISOString()
    });
  }
}

// Launch the Flyde UI with debugging
const launcher = new FlydeUIDebugLauncher();
launcher.launch().catch(console.error);