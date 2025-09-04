#!/usr/bin/env node

/**
 * Flyde UI Status Checker
 * 
 * This script checks the status of all Flyde UI components
 * and provides comprehensive debugging information.
 */

import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

class FlydeStatusChecker {
  constructor() {
    this.status = {
      server: false,
      debugMonitor: false,
      playwright: false,
      ports: [],
      processes: [],
      errors: []
    };
  }

  async checkAll() {
    console.log('🔍 Checking Flyde UI Status...');
    console.log('==============================');
    
    await this.checkPorts();
    await this.checkProcesses();
    await this.checkServer();
    await this.checkFiles();
    await this.checkDependencies();
    
    this.printStatus();
  }

  async checkPorts() {
    console.log('🌐 Checking ports...');
    
    const ports = [3000, 3001, 3002, 3003];
    
    for (const port of ports) {
      try {
        const response = await fetch(`http://localhost:${port}/api/metrics`);
        if (response.ok) {
          this.status.ports.push(port);
          console.log(`  ✅ Port ${port}: Active`);
        }
      } catch (error) {
        console.log(`  ❌ Port ${port}: Inactive`);
      }
    }
  }

  async checkProcesses() {
    console.log('🔄 Checking processes...');
    
    try {
      const { exec } = await import('child_process');
      const { promisify } = await import('util');
      const execAsync = promisify(exec);
      
      const { stdout } = await execAsync('tasklist /fi "imagename eq node.exe"');
      
      if (stdout.includes('node.exe')) {
        console.log('  ✅ Node.js processes found');
        this.status.processes = stdout.split('\n').filter(line => line.includes('node.exe'));
      } else {
        console.log('  ❌ No Node.js processes found');
      }
    } catch (error) {
      console.log('  ❌ Error checking processes:', error.message);
    }
  }

  async checkServer() {
    console.log('🌐 Checking server status...');
    
    for (const port of this.status.ports) {
      try {
        const response = await fetch(`http://localhost:${port}/api/metrics`);
        const data = await response.json();
        
        if (data.success) {
          console.log(`  ✅ Server on port ${port}: Healthy`);
          console.log(`     - Uptime: ${Math.round(data.metrics.uptime / 1000)}s`);
          console.log(`     - Requests: ${data.metrics.requests}`);
          console.log(`     - Errors: ${data.metrics.errors}`);
          console.log(`     - Success Rate: ${data.metrics.successRate}%`);
          this.status.server = true;
        }
      } catch (error) {
        console.log(`  ❌ Server on port ${port}: Error - ${error.message}`);
      }
    }
  }

  async checkFiles() {
    console.log('📁 Checking files...');
    
    const requiredFiles = [
      'mcp-web-server.js',
      'mcp-debug-monitor.js',
      'flyde-playwright-test.js',
      'launch-flyde-debug.js',
      'src/sentry-monitor.js',
      'examples/web-ui/sentry-integrated.html'
    ];
    
    for (const file of requiredFiles) {
      if (fs.existsSync(file)) {
        console.log(`  ✅ ${file}: Found`);
      } else {
        console.log(`  ❌ ${file}: Missing`);
        this.status.errors.push(`Missing file: ${file}`);
      }
    }
  }

  async checkDependencies() {
    console.log('📦 Checking dependencies...');
    
    try {
      const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      const dependencies = Object.keys(packageJson.dependencies || {});
      
      console.log(`  📊 Dependencies: ${dependencies.length}`);
      
      // Check if Playwright is installed
      try {
        const { exec } = await import('child_process');
        const { promisify } = await import('util');
        const execAsync = promisify(exec);
        
        await execAsync('npx playwright --version');
        console.log('  ✅ Playwright: Installed');
        this.status.playwright = true;
      } catch (error) {
        console.log('  ❌ Playwright: Not installed');
        this.status.errors.push('Playwright not installed');
      }
      
    } catch (error) {
      console.log('  ❌ Error reading package.json:', error.message);
    }
  }

  printStatus() {
    console.log('\n📊 FLYDE UI STATUS SUMMARY');
    console.log('===========================');
    
    console.log(`🌐 Server Status: ${this.status.server ? '✅ Active' : '❌ Inactive'}`);
    console.log(`🔍 Debug Monitor: ${this.status.debugMonitor ? '✅ Active' : '❌ Inactive'}`);
    console.log(`🎭 Playwright: ${this.status.playwright ? '✅ Installed' : '❌ Not Installed'}`);
    console.log(`🌐 Active Ports: ${this.status.ports.length > 0 ? this.status.ports.join(', ') : 'None'}`);
    console.log(`🔄 Node Processes: ${this.status.processes.length}`);
    
    if (this.status.errors.length > 0) {
      console.log('\n🚨 ERRORS FOUND:');
      this.status.errors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error}`);
      });
    }
    
    console.log('\n🎯 RECOMMENDATIONS:');
    
    if (!this.status.server) {
      console.log('  - Start the server: npm run mcp-web');
    }
    
    if (!this.status.playwright) {
      console.log('  - Install Playwright: npx playwright install');
    }
    
    if (this.status.ports.length === 0) {
      console.log('  - Check if any ports are available');
    }
    
    console.log('\n🚀 QUICK START COMMANDS:');
    console.log('  npm run launch-flyde    # Launch with debugging');
    console.log('  npm run test-flyde      # Run Playwright tests');
    console.log('  npm run mcp-web         # Start web server');
    console.log('  npm run mcp-debug       # Start debug monitor');
    
    console.log('\n🎉 Status check complete!');
  }
}

// Run the status checker
const checker = new FlydeStatusChecker();
checker.checkAll().catch(console.error);