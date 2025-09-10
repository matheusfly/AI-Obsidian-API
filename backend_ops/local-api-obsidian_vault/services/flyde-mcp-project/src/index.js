#!/usr/bin/env node

/**
 * MCP Flyde Project - Main Entry Point
 * 
 * This is the main entry point for the MCP-powered Flyde project
 * with comprehensive Sentry monitoring and interactive capabilities.
 */

import { SentryMCPMonitor } from './sentry-monitor.js';

console.log('🚀 MCP Flyde Project Starting...');
console.log('================================');

// Initialize Sentry monitoring
const sentry = new SentryMCPMonitor();

// Log startup
sentry.logInfo('application_start', {
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString()
});

console.log('✅ Sentry MCP monitoring initialized');
console.log('🎮 Interactive UI available at: http://localhost:3001');
console.log('📊 Command line playground: npm run mcp-playground');
console.log('🔍 Sentry demo: npm run sentry-demo');

// Keep the process running
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down MCP Flyde Project...');
    sentry.logInfo('application_shutdown', {
        reason: 'SIGINT',
        timestamp: new Date().toISOString()
    });
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down MCP Flyde Project...');
    sentry.logInfo('application_shutdown', {
        reason: 'SIGTERM',
        timestamp: new Date().toISOString()
    });
    process.exit(0);
});

console.log('\n🎉 MCP Flyde Project is running!');
console.log('Press Ctrl+C to stop');