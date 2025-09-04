#!/usr/bin/env node

/**
 * Sentry-Integrated MCP Flyde Web Server
 * 
 * This server provides the interactive web UI with comprehensive
 * Sentry MCP monitoring and error tracking.
 */

import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { SentryMCPMonitor } from '../../src/sentry-monitor.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize Sentry monitoring
const sentry = new SentryMCPMonitor();

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Log server startup
sentry.logInfo('server_startup', {
    port: PORT,
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString()
});

// Routes
app.get('/', (req, res) => {
    const startTime = Date.now();
    
    try {
        sentry.logInfo('page_request', {
            url: req.url,
            userAgent: req.get('User-Agent'),
            ip: req.ip
        });
        
        res.sendFile(path.join(__dirname, 'index.html'));
        
        const duration = Date.now() - startTime;
        sentry.logPerformance('page_serve', duration, {
            url: req.url,
            statusCode: 200
        });
        
    } catch (error) {
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
        sentry.logInfo('example_start', {
            exampleId,
            exampleName,
            timestamp: new Date().toISOString()
        });
        
        // Simulate MCP example execution
        const result = await simulateMCPExample(exampleId, exampleName);
        
        const duration = Date.now() - startTime;
        sentry.logPerformance('example_execution', duration, {
            exampleId,
            exampleName,
            success: true
        });
        
        sentry.logInfo('example_complete', {
            exampleId,
            exampleName,
            duration,
            success: true
        });
        
        res.json({
            success: true,
            result,
            duration,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        const duration = Date.now() - startTime;
        
        sentry.logError('example_execution_error', error, {
            exampleId,
            exampleName,
            duration
        });
        
        res.status(500).json({
            success: false,
            error: error.message,
            duration,
            timestamp: new Date().toISOString()
        });
    }
});

// API endpoint for getting Sentry metrics
app.get('/api/sentry-metrics', (req, res) => {
    try {
        const events = sentry.getEvents();
        const report = sentry.generateReport();
        
        res.json({
            success: true,
            metrics: {
                totalEvents: events.length,
                eventsByLevel: report.eventsByLevel,
                sessionDuration: report.sessionDuration,
                recentEvents: events.slice(-10) // Last 10 events
            },
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        sentry.logError('metrics_fetch_error', error);
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
    console.log('🚀 Sentry-Integrated MCP Flyde Server Started!');
    console.log('==============================================');
    console.log(`🌐 Server running at: http://localhost:${PORT}`);
    console.log('🔍 Sentry MCP monitoring: ACTIVE');
    console.log('📊 Metrics endpoint: /api/sentry-metrics');
    console.log('🎮 Interactive UI: Ready');
    console.log('==============================================');
    
    sentry.logInfo('server_ready', {
        port: PORT,
        url: `http://localhost:${PORT}`,
        timestamp: new Date().toISOString()
    });
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down server...');
    sentry.logInfo('server_shutdown', {
        reason: 'SIGINT',
        timestamp: new Date().toISOString()
    });
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down server...');
    sentry.logInfo('server_shutdown', {
        reason: 'SIGTERM',
        timestamp: new Date().toISOString()
    });
    process.exit(0);
});