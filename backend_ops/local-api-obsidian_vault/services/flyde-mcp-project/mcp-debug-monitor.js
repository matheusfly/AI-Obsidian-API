#!/usr/bin/env node

/**
 * MCP Debug Monitor - Real-time Debugging and Output Collection
 * 
 * This system provides comprehensive debugging capabilities using MCP tools:
 * - Real-time process monitoring
 * - File system watching and analysis
 * - Network request monitoring
 * - Memory usage tracking
 * - Error detection and reporting
 * - Performance metrics collection
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { SentryMCPMonitor } from './src/sentry-monitor.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class MCPDebugMonitor {
  constructor() {
    this.sentry = new SentryMCPMonitor();
    this.watchers = new Map();
    this.metrics = {
      startTime: Date.now(),
      operations: [],
      errors: [],
      performance: [],
      memory: [],
      network: []
    };
    this.isRunning = false;
  }

  async start() {
    console.log('🐛 Starting MCP Debug Monitor...');
    console.log('================================');
    
    this.isRunning = true;
    this.sentry.logInfo('debug_monitor_start', {
      timestamp: new Date().toISOString(),
      pid: process.pid
    });
    
    // Start all monitoring systems
    await Promise.all([
      this.startProcessMonitoring(),
      this.startFileSystemMonitoring(),
      this.startMemoryMonitoring(),
      this.startNetworkMonitoring(),
      this.startErrorMonitoring(),
      this.startPerformanceMonitoring()
    ]);
    
    console.log('✅ MCP Debug Monitor started successfully!');
    console.log('📊 All monitoring systems active');
    console.log('🔍 Real-time debugging enabled');
    console.log('📈 Performance tracking active');
    console.log('🚨 Error detection enabled');
    console.log('💾 Memory monitoring active');
    console.log('🌐 Network monitoring active');
    console.log('📁 File system watching active');
    
    // Keep the process running
    this.keepAlive();
  }

  async startProcessMonitoring() {
    console.log('  🔍 Starting process monitoring...');
    
    const monitorProcess = () => {
      const processInfo = {
        timestamp: new Date().toISOString(),
        pid: process.pid,
        platform: process.platform,
        nodeVersion: process.version,
        memoryUsage: process.memoryUsage(),
        uptime: process.uptime(),
        cpuUsage: process.cpuUsage()
      };
      
      this.metrics.operations.push({
        type: 'process_monitor',
        data: processInfo,
        timestamp: processInfo.timestamp
      });
      
      this.sentry.logInfo('process_monitor_tick', processInfo);
    };
    
    // Monitor every 5 seconds
    const interval = setInterval(monitorProcess, 5000);
    
    // Store interval for cleanup
    this.watchers.set('process_monitor', interval);
    
    console.log('  ✅ Process monitoring started');
  }

  async startFileSystemMonitoring() {
    console.log('  📁 Starting file system monitoring...');
    
    const watchDirectories = ['src', 'examples', 'tests'];
    
    for (const dir of watchDirectories) {
      if (fs.existsSync(dir)) {
        const watcher = fs.watch(dir, { recursive: true }, (eventType, filename) => {
          const filePath = path.join(dir, filename);
          const event = {
            timestamp: new Date().toISOString(),
            type: 'filesystem_event',
            eventType,
            filename,
            filePath,
            directory: dir
          };
          
          this.metrics.operations.push(event);
          this.sentry.logInfo('filesystem_event', event);
          
          console.log(`  📁 File system event: ${eventType} - ${filePath}`);
        });
        
        this.watchers.set(`fs_watch_${dir}`, watcher);
        console.log(`  ✅ Watching directory: ${dir}`);
      }
    }
  }

  async startMemoryMonitoring() {
    console.log('  💾 Starting memory monitoring...');
    
    const monitorMemory = () => {
      const memoryInfo = process.memoryUsage();
      const memoryEvent = {
        timestamp: new Date().toISOString(),
        type: 'memory_monitor',
        heapUsed: memoryInfo.heapUsed,
        heapTotal: memoryInfo.heapTotal,
        external: memoryInfo.external,
        rss: memoryInfo.rss,
        heapUsedMB: Math.round(memoryInfo.heapUsed / 1024 / 1024),
        heapTotalMB: Math.round(memoryInfo.heapTotal / 1024 / 1024),
        rssMB: Math.round(memoryInfo.rss / 1024 / 1024)
      };
      
      this.metrics.memory.push(memoryEvent);
      this.sentry.logInfo('memory_monitor_tick', memoryEvent);
      
      // Alert if memory usage is high
      if (memoryInfo.heapUsed / memoryInfo.heapTotal > 0.8) {
        this.sentry.logError('high_memory_usage', new Error('High memory usage detected'), memoryEvent);
        console.log(`  ⚠️ High memory usage: ${memoryEvent.heapUsedMB}MB / ${memoryEvent.heapTotalMB}MB`);
      }
    };
    
    // Monitor every 10 seconds
    const interval = setInterval(monitorMemory, 10000);
    this.watchers.set('memory_monitor', interval);
    
    console.log('  ✅ Memory monitoring started');
  }

  async startNetworkMonitoring() {
    console.log('  🌐 Starting network monitoring...');
    
    // Monitor network requests
    const originalFetch = global.fetch;
    global.fetch = async (...args) => {
      const startTime = Date.now();
      const url = args[0];
      
      try {
        const response = await originalFetch(...args);
        const duration = Date.now() - startTime;
        
        const networkEvent = {
          timestamp: new Date().toISOString(),
          type: 'network_request',
          url,
          method: 'GET',
          status: response.status,
          duration,
          success: response.ok
        };
        
        this.metrics.network.push(networkEvent);
        this.sentry.logInfo('network_request', networkEvent);
        
        console.log(`  🌐 Network request: ${url} (${response.status}) - ${duration}ms`);
        
        return response;
      } catch (error) {
        const duration = Date.now() - startTime;
        
        const networkEvent = {
          timestamp: new Date().toISOString(),
          type: 'network_error',
          url,
          error: error.message,
          duration,
          success: false
        };
        
        this.metrics.network.push(networkEvent);
        this.sentry.logError('network_request_error', error, networkEvent);
        
        console.log(`  ❌ Network error: ${url} - ${error.message}`);
        throw error;
      }
    };
    
    console.log('  ✅ Network monitoring started');
  }

  async startErrorMonitoring() {
    console.log('  🚨 Starting error monitoring...');
    
    // Monitor uncaught exceptions
    process.on('uncaughtException', (error) => {
      const errorEvent = {
        timestamp: new Date().toISOString(),
        type: 'uncaught_exception',
        error: error.message,
        stack: error.stack,
        pid: process.pid
      };
      
      this.metrics.errors.push(errorEvent);
      this.sentry.logError('uncaught_exception', error, errorEvent);
      
      console.log(`  🚨 Uncaught exception: ${error.message}`);
    });
    
    // Monitor unhandled promise rejections
    process.on('unhandledRejection', (reason, promise) => {
      const errorEvent = {
        timestamp: new Date().toISOString(),
        type: 'unhandled_rejection',
        reason: reason.toString(),
        promise: promise.toString(),
        pid: process.pid
      };
      
      this.metrics.errors.push(errorEvent);
      this.sentry.logError('unhandled_rejection', new Error(reason), errorEvent);
      
      console.log(`  🚨 Unhandled rejection: ${reason}`);
    });
    
    console.log('  ✅ Error monitoring started');
  }

  async startPerformanceMonitoring() {
    console.log('  📈 Starting performance monitoring...');
    
    const monitorPerformance = () => {
      const performanceEvent = {
        timestamp: new Date().toISOString(),
        type: 'performance_monitor',
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        cpuUsage: process.cpuUsage(),
        loadAverage: process.platform !== 'win32' ? require('os').loadavg() : [0, 0, 0]
      };
      
      this.metrics.performance.push(performanceEvent);
      this.sentry.logPerformance('performance_monitor_tick', 0, performanceEvent);
    };
    
    // Monitor every 30 seconds
    const interval = setInterval(monitorPerformance, 30000);
    this.watchers.set('performance_monitor', interval);
    
    console.log('  ✅ Performance monitoring started');
  }

  async generateDebugReport() {
    console.log('\n📊 Generating Debug Report...');
    
    const report = {
      timestamp: new Date().toISOString(),
      duration: Date.now() - this.metrics.startTime,
      summary: {
        totalOperations: this.metrics.operations.length,
        totalErrors: this.metrics.errors.length,
        memorySamples: this.metrics.memory.length,
        networkRequests: this.metrics.network.length,
        performanceSamples: this.metrics.performance.length
      },
      metrics: this.metrics,
      sentryEvents: this.sentry.getEvents(),
      sentryReport: this.sentry.generateReport()
    };
    
    // Save report
    const reportPath = 'debug-report.json';
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`📄 Debug report saved: ${reportPath}`);
    console.log(`📊 Total operations: ${report.summary.totalOperations}`);
    console.log(`🚨 Total errors: ${report.summary.totalErrors}`);
    console.log(`💾 Memory samples: ${report.summary.memorySamples}`);
    console.log(`🌐 Network requests: ${report.summary.networkRequests}`);
    
    return report;
  }

  async keepAlive() {
    console.log('\n🔄 Debug Monitor running... Press Ctrl+C to stop');
    
    // Generate periodic reports
    setInterval(async () => {
      await this.generateDebugReport();
    }, 60000); // Every minute
    
    // Keep the process alive
    while (this.isRunning) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  async stop() {
    console.log('\n🛑 Stopping MCP Debug Monitor...');
    
    this.isRunning = false;
    
    // Clean up watchers
    for (const [name, watcher] of this.watchers) {
      if (watcher.close) {
        watcher.close();
      } else if (watcher.clearInterval) {
        clearInterval(watcher);
      }
      console.log(`  🧹 Cleaned up: ${name}`);
    }
    
    // Generate final report
    await this.generateDebugReport();
    
    this.sentry.logInfo('debug_monitor_stop', {
      timestamp: new Date().toISOString(),
      duration: Date.now() - this.metrics.startTime
    });
    
    console.log('✅ MCP Debug Monitor stopped');
  }
}

// Create and start the debug monitor
const debugMonitor = new MCPDebugMonitor();

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Received SIGINT, shutting down...');
  await debugMonitor.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\n🛑 Received SIGTERM, shutting down...');
  await debugMonitor.stop();
  process.exit(0);
});

// Start the debug monitor
debugMonitor.start().catch(console.error);