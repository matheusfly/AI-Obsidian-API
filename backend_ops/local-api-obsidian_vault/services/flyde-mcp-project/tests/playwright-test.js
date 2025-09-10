#!/usr/bin/env node

/**
 * Playwright Test Suite for MCP Flyde Interactive UI
 * 
 * This test suite validates the interactive web UI functionality
 * with comprehensive Sentry monitoring and error detection.
 */

import { chromium } from 'playwright';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PlaywrightTestSuite {
  constructor() {
    this.browser = null;
    this.page = null;
    this.serverProcess = null;
    this.testResults = {
      passed: 0,
      failed: 0,
      total: 0,
      errors: []
    };
  }

  async startServer() {
    console.log('🚀 Starting MCP Flyde server...');
    
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
        
        this.serverProcess = spawn('node', ['examples/web-ui/server.js'], {
          env: { ...process.env, PORT: port.toString() },
          cwd: path.join(__dirname, '..')
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
          } else {
            console.error('Server error:', error);
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

  async setupBrowser() {
    console.log('🌐 Setting up browser...');
    this.browser = await chromium.launch({ 
      headless: false, // Set to true for headless testing
      slowMo: 1000 // Slow down actions for better visibility
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
  }

  async runTest(testName, testFunction) {
    console.log(`\n🧪 Running test: ${testName}`);
    this.testResults.total++;
    
    try {
      await testFunction();
      console.log(`✅ Test passed: ${testName}`);
      this.testResults.passed++;
    } catch (error) {
      console.error(`❌ Test failed: ${testName}`);
      console.error(`   Error: ${error.message}`);
      this.testResults.failed++;
      this.testResults.errors.push({
        type: 'test_failure',
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

  async testExampleCards() {
    console.log('🎮 Testing example cards...');
    
    // Wait for example cards to load
    await this.page.waitForSelector('.example-card', { timeout: 10000 });
    
    // Check if all example cards are present
    const cards = await this.page.$$('.example-card');
    if (cards.length < 4) {
      throw new Error(`Expected 4 example cards, found ${cards.length}`);
    }
    
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

  async testOutputPanel() {
    console.log('📊 Testing output panel...');
    
    // Check if output panel exists
    const outputPanel = await this.page.$('#output');
    if (!outputPanel) {
      throw new Error('Output panel not found');
    }
    
    // Check if output content is present
    const outputContent = await this.page.textContent('#output');
    if (!outputContent.includes('Starting: Hello World MCP')) {
      throw new Error('Expected output content not found');
    }
    
    console.log('✅ Output panel working correctly');
  }

  async testMetrics() {
    console.log('📈 Testing metrics...');
    
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
    console.log('🎛️ Testing control buttons...');
    
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

  async testSentryMonitoring() {
    console.log('🔍 Testing Sentry monitoring...');
    
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

  async runAllTests() {
    console.log('🧪 Starting Playwright Test Suite for MCP Flyde UI');
    console.log('==================================================');
    
    try {
      await this.startServer();
      await this.setupBrowser();
      
      await this.runTest('Page Load', () => this.testPageLoad());
      await this.runTest('Example Cards', () => this.testExampleCards());
      await this.runTest('Output Panel', () => this.testOutputPanel());
      await this.runTest('Metrics', () => this.testMetrics());
      await this.runTest('Controls', () => this.testControls());
      await this.runTest('Sentry Monitoring', () => this.testSentryMonitoring());
      
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
  }

  printResults() {
    console.log('\n📊 TEST RESULTS');
    console.log('================');
    console.log(`Total Tests: ${this.testResults.total}`);
    console.log(`Passed: ${this.testResults.passed} ✅`);
    console.log(`Failed: ${this.testResults.failed} ❌`);
    console.log(`Success Rate: ${Math.round((this.testResults.passed / this.testResults.total) * 100)}%`);
    
    if (this.testResults.errors.length > 0) {
      console.log('\n🚨 ERRORS FOUND:');
      this.testResults.errors.forEach((error, index) => {
        console.log(`${index + 1}. ${error.type}: ${error.message}`);
      });
    }
    
    console.log('\n🎉 Test suite completed!');
  }
}

// Run the test suite
const testSuite = new PlaywrightTestSuite();
testSuite.runAllTests().catch(console.error);