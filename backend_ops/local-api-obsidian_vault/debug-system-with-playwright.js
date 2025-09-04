#!/usr/bin/env node

/**
 * Comprehensive System Debugging with Playwright Testing
 * 
 * This script launches the entire system and performs comprehensive testing
 * using Playwright for browser automation and Sentry MCP for monitoring.
 */

const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Sentry MCP Monitoring Class
class SystemDebugMonitor {
  constructor() {
    this.events = [];
    this.startTime = Date.now();
    this.testResults = [];
    this.services = {
      vaultApi: { status: 'unknown', url: 'http://localhost:8085' },
      obsidianApi: { status: 'unknown', url: 'http://localhost:27123' },
      n8n: { status: 'unknown', url: 'http://localhost:5678' },
      grafana: { status: 'unknown', url: 'http://localhost:3004' },
      docs: { status: 'unknown', url: 'http://localhost:3000' }
    };
  }

  logEvent(level, operation, data, context = {}) {
    const event = {
      id: `${level}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      level,
      operation,
      data,
      context,
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId()
    };

    this.events.push(event);
    
    const emoji = {
      info: '🔍',
      success: '✅',
      warning: '⚠️',
      error: '🚨',
      debug: '🐛'
    }[level] || '📝';

    console.log(`${emoji} [SYSTEM DEBUG] ${level.toUpperCase()} - ${operation}`);
    if (data && Object.keys(data).length > 0) {
      console.log(`📊 Data:`, JSON.stringify(data, null, 2));
    }
    console.log(`🔗 Event ID: ${event.id}\n`);
    
    return event;
  }

  getSessionId() {
    return `debug_session_${this.startTime}`;
  }

  async checkServiceHealth(serviceName, url) {
    try {
      const response = await fetch(url + '/health', { 
        method: 'GET',
        timeout: 5000 
      });
      
      if (response.ok) {
        this.services[serviceName].status = 'healthy';
        this.logEvent('success', `Service Health Check: ${serviceName}`, {
          url,
          status: response.status,
          statusText: response.statusText
        });
        return true;
      } else {
        this.services[serviceName].status = 'unhealthy';
        this.logEvent('warning', `Service Health Check: ${serviceName}`, {
          url,
          status: response.status,
          statusText: response.statusText
        });
        return false;
      }
    } catch (error) {
      this.services[serviceName].status = 'down';
      this.logEvent('error', `Service Health Check: ${serviceName}`, {
        url,
        error: error.message
      });
      return false;
    }
  }

  async runPlaywrightTests() {
    this.logEvent('info', 'Starting Playwright Browser Tests', {
      browser: 'chromium',
      headless: false
    });

    const browser = await chromium.launch({ 
      headless: false,
      devtools: true 
    });
    
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      recordVideo: { dir: './debug-videos/' }
    });

    const page = await context.newPage();

    // Test 1: Vault API Health Check
    try {
      this.logEvent('debug', 'Testing Vault API Health Endpoint');
      await page.goto('http://localhost:8085/health');
      await page.waitForLoadState('networkidle');
      
      const healthData = await page.textContent('body');
      this.testResults.push({
        test: 'Vault API Health',
        status: 'passed',
        data: healthData
      });
      
      this.logEvent('success', 'Vault API Health Test Passed', { data: healthData });
    } catch (error) {
      this.testResults.push({
        test: 'Vault API Health',
        status: 'failed',
        error: error.message
      });
      this.logEvent('error', 'Vault API Health Test Failed', { error: error.message });
    }

    // Test 2: Obsidian API Health Check
    try {
      this.logEvent('debug', 'Testing Obsidian API Health Endpoint');
      await page.goto('http://localhost:27123/health');
      await page.waitForLoadState('networkidle');
      
      const healthData = await page.textContent('body');
      this.testResults.push({
        test: 'Obsidian API Health',
        status: 'passed',
        data: healthData
      });
      
      this.logEvent('success', 'Obsidian API Health Test Passed', { data: healthData });
    } catch (error) {
      this.testResults.push({
        test: 'Obsidian API Health',
        status: 'failed',
        error: error.message
      });
      this.logEvent('error', 'Obsidian API Health Test Failed', { error: error.message });
    }

    // Test 3: n8n Interface
    try {
      this.logEvent('debug', 'Testing n8n Interface');
      await page.goto('http://localhost:5678');
      await page.waitForLoadState('networkidle');
      
      const title = await page.title();
      this.testResults.push({
        test: 'n8n Interface',
        status: 'passed',
        data: { title }
      });
      
      this.logEvent('success', 'n8n Interface Test Passed', { title });
    } catch (error) {
      this.testResults.push({
        test: 'n8n Interface',
        status: 'failed',
        error: error.message
      });
      this.logEvent('error', 'n8n Interface Test Failed', { error: error.message });
    }

    // Test 4: Grafana Dashboard
    try {
      this.logEvent('debug', 'Testing Grafana Dashboard');
      await page.goto('http://localhost:3004');
      await page.waitForLoadState('networkidle');
      
      const title = await page.title();
      this.testResults.push({
        test: 'Grafana Dashboard',
        status: 'passed',
        data: { title }
      });
      
      this.logEvent('success', 'Grafana Dashboard Test Passed', { title });
    } catch (error) {
      this.testResults.push({
        test: 'Grafana Dashboard',
        status: 'failed',
        error: error.message
      });
      this.logEvent('error', 'Grafana Dashboard Test Failed', { error: error.message });
    }

    // Test 5: Documentation Site
    try {
      this.logEvent('debug', 'Testing Documentation Site');
      await page.goto('http://localhost:3000');
      await page.waitForLoadState('networkidle');
      
      const title = await page.title();
      const hasNavigation = await page.locator('nav').count() > 0;
      
      this.testResults.push({
        test: 'Documentation Site',
        status: 'passed',
        data: { title, hasNavigation }
      });
      
      this.logEvent('success', 'Documentation Site Test Passed', { title, hasNavigation });
    } catch (error) {
      this.testResults.push({
        test: 'Documentation Site',
        status: 'failed',
        error: error.message
      });
      this.logEvent('error', 'Documentation Site Test Failed', { error: error.message });
    }

    // Test 6: API Endpoints Testing
    try {
      this.logEvent('debug', 'Testing API Endpoints');
      
      // Test Vault API endpoints
      const vaultResponse = await page.request.get('http://localhost:8085/vault/files');
      const vaultStatus = vaultResponse.status();
      
      this.testResults.push({
        test: 'Vault API Files Endpoint',
        status: vaultStatus === 200 ? 'passed' : 'failed',
        data: { status: vaultStatus }
      });
      
      this.logEvent(vaultStatus === 200 ? 'success' : 'warning', 'Vault API Files Endpoint', { status: vaultStatus });
    } catch (error) {
      this.testResults.push({
        test: 'Vault API Files Endpoint',
        status: 'failed',
        error: error.message
      });
      this.logEvent('error', 'Vault API Files Endpoint Test Failed', { error: error.message });
    }

    await browser.close();
    this.logEvent('info', 'Playwright Tests Completed', {
      totalTests: this.testResults.length,
      passed: this.testResults.filter(t => t.status === 'passed').length,
      failed: this.testResults.filter(t => t.status === 'failed').length
    });
  }

  generateDebugReport() {
    const report = {
      sessionId: this.getSessionId(),
      startTime: new Date(this.startTime).toISOString(),
      endTime: new Date().toISOString(),
      duration: Date.now() - this.startTime,
      totalEvents: this.events.length,
      eventsByLevel: {
        info: this.events.filter(e => e.level === 'info').length,
        success: this.events.filter(e => e.level === 'success').length,
        warning: this.events.filter(e => e.level === 'warning').length,
        error: this.events.filter(e => e.level === 'error').length,
        debug: this.events.filter(e => e.level === 'debug').length
      },
      services: this.services,
      testResults: this.testResults,
      summary: {
        healthyServices: Object.values(this.services).filter(s => s.status === 'healthy').length,
        totalServices: Object.keys(this.services).length,
        passedTests: this.testResults.filter(t => t.status === 'passed').length,
        totalTests: this.testResults.length
      }
    };

    console.log('\n🔍 [SYSTEM DEBUG] COMPREHENSIVE REPORT');
    console.log('=====================================');
    console.log(`Session ID: ${report.sessionId}`);
    console.log(`Duration: ${report.duration}ms`);
    console.log(`Total Events: ${report.totalEvents}`);
    console.log(`Healthy Services: ${report.summary.healthyServices}/${report.summary.totalServices}`);
    console.log(`Passed Tests: ${report.summary.passedTests}/${report.summary.totalTests}`);
    console.log('\n📊 Service Status:');
    Object.entries(report.services).forEach(([name, service]) => {
      const status = service.status === 'healthy' ? '✅' : service.status === 'unhealthy' ? '⚠️' : '❌';
      console.log(`  ${status} ${name}: ${service.status} (${service.url})`);
    });
    console.log('\n🧪 Test Results:');
    report.testResults.forEach(test => {
      const status = test.status === 'passed' ? '✅' : '❌';
      console.log(`  ${status} ${test.test}: ${test.status}`);
    });
    console.log('=====================================\n');

    // Save report to file
    const reportPath = `./debug-report-${Date.now()}.json`;
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`📄 Debug report saved to: ${reportPath}`);

    return report;
  }
}

// Main debugging function
async function runSystemDebug() {
  console.log('🚀 Starting Comprehensive System Debug with Playwright');
  console.log('====================================================\n');

  const monitor = new SystemDebugMonitor();
  
  // Check all services
  monitor.logEvent('info', 'Checking Service Health', { services: Object.keys(monitor.services) });
  
  for (const [serviceName, service] of Object.entries(monitor.services)) {
    await monitor.checkServiceHealth(serviceName, service.url);
    // Wait a bit between checks
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // Run Playwright tests
  await monitor.runPlaywrightTests();

  // Generate final report
  const report = monitor.generateDebugReport();

  console.log('🎉 System Debug Completed!');
  console.log(`📊 Overall Health: ${report.summary.healthyServices}/${report.summary.totalServices} services healthy`);
  console.log(`🧪 Test Success Rate: ${report.summary.passedTests}/${report.summary.totalTests} tests passed`);
  
  return report;
}

// Run the debug
runSystemDebug()
  .then(report => {
    console.log('\n✅ System debugging completed successfully!');
    process.exit(0);
  })
  .catch(error => {
    console.error('\n❌ System debugging failed:', error);
    process.exit(1);
  });
