#!/usr/bin/env node

/**
 * MCP Web Server - Comprehensive MCP-Powered Web Interface
 * 
 * This server provides a complete web interface for MCP operations with:
 * - Real-time monitoring dashboard
 * - Interactive MCP playground
 * - Sentry integration
 * - File system operations
 * - Web crawling capabilities
 * - Performance metrics
 * - Debug tools
 */

import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { SentryMCPMonitor } from './src/sentry-monitor.js';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize Sentry monitoring
const sentry = new SentryMCPMonitor();

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'examples', 'web-ui')));

// Global metrics
const metrics = {
  startTime: Date.now(),
  requests: 0,
  errors: 0,
  operations: []
};

// Log server startup
sentry.logInfo('mcp_web_server_start', {
  port: PORT,
  timestamp: new Date().toISOString()
});

// Routes
app.get('/', (req, res) => {
  const startTime = Date.now();
  metrics.requests++;
  
  try {
    sentry.logInfo('page_request', {
      url: req.url,
      userAgent: req.get('User-Agent'),
      ip: req.ip
    });
    
    res.sendFile(path.join(__dirname, 'examples', 'web-ui', 'sentry-integrated.html'));
    
    const duration = Date.now() - startTime;
    sentry.logPerformance('page_serve', duration, {
      url: req.url,
      statusCode: 200
    });
    
  } catch (error) {
    metrics.errors++;
    sentry.logError('page_serve_error', error, {
      url: req.url,
      method: req.method
    });
    res.status(500).send('Internal Server Error');
  }
});

// API endpoint for running MCP examples
app.post('/api/run-example', async (req, res) => {
  const startTime = Date.now();
  const { exampleId, exampleName } = req.body;
  
  try {
    sentry.logInfo('mcp_example_start', {
      exampleId,
      exampleName,
      timestamp: new Date().toISOString()
    });
    
    // Simulate MCP example execution
    const result = await simulateMCPExample(exampleId, exampleName);
    
    const duration = Date.now() - startTime;
    sentry.logPerformance('mcp_example_execution', duration, {
      exampleId,
      exampleName,
      success: true
    });
    
    sentry.logInfo('mcp_example_complete', {
      exampleId,
      exampleName,
      duration,
      success: true
    });
    
    metrics.operations.push({
      type: 'mcp_example',
      exampleId,
      exampleName,
      duration,
      success: true,
      timestamp: new Date().toISOString()
    });
    
    res.json({
      success: true,
      result,
      duration,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    const duration = Date.now() - startTime;
    metrics.errors++;
    
    sentry.logError('mcp_example_error', error, {
      exampleId,
      exampleName,
      duration
    });
    
    metrics.operations.push({
      type: 'mcp_example',
      exampleId,
      exampleName,
      duration,
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
    
    res.status(500).json({
      success: false,
      error: error.message,
      duration,
      timestamp: new Date().toISOString()
    });
  }
});

// API endpoint for file system operations
app.post('/api/filesystem', async (req, res) => {
  const startTime = Date.now();
  const { operation, path: filePath, content } = req.body;
  
  try {
    sentry.logInfo('filesystem_operation', {
      operation,
      path: filePath,
      timestamp: new Date().toISOString()
    });
    
    let result;
    
    switch (operation) {
      case 'read':
        result = fs.readFileSync(filePath, 'utf8');
        break;
      case 'write':
        fs.writeFileSync(filePath, content);
        result = { success: true };
        break;
      case 'list':
        result = fs.readdirSync(filePath);
        break;
      case 'exists':
        result = fs.existsSync(filePath);
        break;
      case 'stats':
        result = fs.statSync(filePath);
        break;
      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
    
    const duration = Date.now() - startTime;
    sentry.logPerformance('filesystem_operation', duration, {
      operation,
      path: filePath,
      success: true
    });
    
    metrics.operations.push({
      type: 'filesystem',
      operation,
      path: filePath,
      duration,
      success: true,
      timestamp: new Date().toISOString()
    });
    
    res.json({
      success: true,
      result,
      duration,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    const duration = Date.now() - startTime;
    metrics.errors++;
    
    sentry.logError('filesystem_operation_error', error, {
      operation,
      path: filePath
    });
    
    res.status(500).json({
      success: false,
      error: error.message,
      duration,
      timestamp: new Date().toISOString()
    });
  }
});

// API endpoint for web crawling
app.post('/api/crawl', async (req, res) => {
  const startTime = Date.now();
  const { url, options = {} } = req.body;
  
  try {
    sentry.logInfo('web_crawl_start', {
      url,
      options,
      timestamp: new Date().toISOString()
    });
    
    const response = await fetch(url, options);
    const data = await response.text();
    
    const duration = Date.now() - startTime;
    sentry.logPerformance('web_crawl', duration, {
      url,
      status: response.status,
      success: response.ok
    });
    
    metrics.operations.push({
      type: 'web_crawl',
      url,
      status: response.status,
      duration,
      success: response.ok,
      timestamp: new Date().toISOString()
    });
    
    res.json({
      success: true,
      result: {
        url,
        status: response.status,
        headers: Object.fromEntries(response.headers),
        data: data.substring(0, 1000), // Limit data size
        size: data.length
      },
      duration,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    const duration = Date.now() - startTime;
    metrics.errors++;
    
    sentry.logError('web_crawl_error', error, {
      url
    });
    
    res.status(500).json({
      success: false,
      error: error.message,
      duration,
      timestamp: new Date().toISOString()
    });
  }
});

// API endpoint for getting metrics
app.get('/api/metrics', (req, res) => {
  try {
    const uptime = Date.now() - metrics.startTime;
    const sentryEvents = sentry.getEvents();
    const sentryReport = sentry.generateReport();
    
    const response = {
      success: true,
      metrics: {
        uptime,
        requests: metrics.requests,
        errors: metrics.errors,
        operations: metrics.operations.length,
        successRate: metrics.requests > 0 ? Math.round((metrics.requests - metrics.errors) / metrics.requests * 100) : 100,
        memoryUsage: process.memoryUsage(),
        sentryEvents: sentryEvents.length,
        sentryReport
      },
      timestamp: new Date().toISOString()
    };
    
    res.json(response);
    
  } catch (error) {
    sentry.logError('metrics_fetch_error', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// API endpoint for getting Sentry events
app.get('/api/sentry-events', (req, res) => {
  try {
    const events = sentry.getEvents();
    const report = sentry.generateReport();
    
    res.json({
      success: true,
      events,
      report,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    sentry.logError('sentry_events_fetch_error', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// API endpoint for system information
app.get('/api/system', (req, res) => {
  try {
    const systemInfo = {
      platform: process.platform,
      nodeVersion: process.version,
      pid: process.pid,
      uptime: process.uptime(),
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
      env: process.env.NODE_ENV || 'development'
    };
    
    res.json({
      success: true,
      system: systemInfo,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    sentry.logError('system_info_error', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Simulate MCP example execution
async function simulateMCPExample(exampleId, exampleName) {
  const examples = {
    'hello-world': {
      name: 'Hello World MCP',
      description: 'Basic MCP example with greeting',
      steps: [
        'Initializing MCP connection...',
        'Loading Hello World flow...',
        'Executing greeting logic...',
        'Processing output...',
        'Sending response...'
      ],
      duration: 2000
    },
    'ai-agent': {
      name: 'AI Agent MCP',
      description: 'AI-powered agent simulation',
      steps: [
        'Connecting to AI service...',
        'Loading agent configuration...',
        'Processing user input...',
        'Generating AI response...',
        'Formatting output...'
      ],
      duration: 3000
    },
    'data-pipeline': {
      name: 'Data Pipeline MCP',
      description: 'Data processing pipeline',
      steps: [
        'Initializing data sources...',
        'Loading pipeline configuration...',
        'Processing data chunks...',
        'Transforming data...',
        'Saving results...'
      ],
      duration: 4000
    },
    'web-scraper': {
      name: 'Web Scraper MCP',
      description: 'Web scraping automation',
      steps: [
        'Connecting to target website...',
        'Loading scraping rules...',
        'Extracting data...',
        'Processing content...',
        'Saving scraped data...'
      ],
      duration: 3500
    }
  };
  
  const example = examples[exampleId];
  if (!example) {
    throw new Error(`Unknown example: ${exampleId}`);
  }
  
  // Simulate execution steps
  const results = [];
  for (let i = 0; i < example.steps.length; i++) {
    const step = example.steps[i];
    results.push({
      step: i + 1,
      message: step,
      timestamp: new Date().toISOString(),
      status: 'running'
    });
    
    // Simulate step execution time
    await new Promise(resolve => setTimeout(resolve, example.duration / example.steps.length));
    
    results[i].status = 'completed';
  }
  
  return {
    exampleId,
    exampleName: example.name,
    description: example.description,
    steps: results,
    totalDuration: example.duration,
    success: true
  };
}

// Error handling middleware
app.use((error, req, res, next) => {
  metrics.errors++;
  sentry.logError('server_error', error, {
    url: req.url,
    method: req.method,
    headers: req.headers
  });
  
  res.status(500).json({
    success: false,
    error: 'Internal Server Error',
    message: error.message
  });
});

// Start server
app.listen(PORT, () => {
  console.log('🚀 MCP Web Server Started!');
  console.log('==========================');
  console.log(`🌐 Server running at: http://localhost:${PORT}`);
  console.log('🔍 Sentry MCP monitoring: ACTIVE');
  console.log('📊 Metrics endpoint: /api/metrics');
  console.log('🎮 Interactive UI: Ready');
  console.log('📁 File system API: /api/filesystem');
  console.log('🕷️ Web crawling API: /api/crawl');
  console.log('🔍 Sentry events API: /api/sentry-events');
  console.log('💻 System info API: /api/system');
  console.log('==========================');
  
  sentry.logInfo('mcp_web_server_ready', {
    port: PORT,
    url: `http://localhost:${PORT}`,
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down MCP Web Server...');
  sentry.logInfo('mcp_web_server_shutdown', {
    reason: 'SIGINT',
    timestamp: new Date().toISOString()
  });
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down MCP Web Server...');
  sentry.logInfo('mcp_web_server_shutdown', {
    reason: 'SIGTERM',
    timestamp: new Date().toISOString()
  });
  process.exit(0);
});