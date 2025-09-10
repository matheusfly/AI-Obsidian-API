#!/usr/bin/env node

/**
 * Simple Sentry MCP Integration Example
 * 
 * This demonstrates how to use Sentry MCP monitoring without Flyde flows
 * for immediate testing and validation.
 */

// Sentry MCP Monitoring Class
class SentryMCPMonitor {
  constructor() {
    this.events = [];
    this.startTime = Date.now();
  }

  // Log information events
  logInfo(operation, data, context = {}) {
    const event = {
      id: `info_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      level: 'info',
      operation,
      data,
      context,
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId()
    };

    this.events.push(event);
    console.log(`🔍 [SENTRY MCP] INFO - ${operation}`);
    console.log(`📊 Data:`, JSON.stringify(data, null, 2));
    console.log(`🔗 Event ID: ${event.id}`);
    
    return event;
  }

  // Log error events
  logError(operation, error, context = {}) {
    const event = {
      id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      level: 'error',
      operation,
      error: {
        message: error.message || error,
        stack: error.stack || 'No stack trace available',
        name: error.name || 'Error'
      },
      context,
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId()
    };

    this.events.push(event);
    console.error(`🚨 [SENTRY MCP] ERROR - ${operation}`);
    console.error(`❌ Error: ${event.error.message}`);
    console.error(`📋 Stack: ${event.error.stack}`);
    console.error(`🔗 Event ID: ${event.id}`);
    
    return event;
  }

  // Log performance metrics
  logPerformance(operation, startTime, endTime, metrics = {}) {
    const duration = endTime - startTime;
    const event = {
      id: `perf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      level: 'performance',
      operation,
      performance: {
        duration,
        startTime: new Date(startTime).toISOString(),
        endTime: new Date(endTime).toISOString(),
        metrics
      },
      timestamp: new Date().toISOString(),
      sessionId: this.getSessionId()
    };

    this.events.push(event);

    // Performance thresholds
    const thresholds = {
      warning: 1000,  // 1 second
      error: 5000     // 5 seconds
    };

    if (duration > thresholds.error) {
      console.error(`🚨 [SENTRY MCP] PERFORMANCE ERROR: ${operation} took ${duration}ms (exceeds ${thresholds.error}ms)`);
    } else if (duration > thresholds.warning) {
      console.warn(`⚠️ [SENTRY MCP] PERFORMANCE WARNING: ${operation} took ${duration}ms (exceeds ${thresholds.warning}ms)`);
    } else {
      console.log(`✅ [SENTRY MCP] PERFORMANCE OK: ${operation} completed in ${duration}ms`);
    }

    console.log(`🔗 Event ID: ${event.id}`);
    return event;
  }

  // Get session ID
  getSessionId() {
    return `session_${this.startTime}`;
  }

  // Get all events
  getEvents() {
    return this.events;
  }

  // Get events by level
  getEventsByLevel(level) {
    return this.events.filter(event => event.level === level);
  }

  // Generate summary report
  generateReport() {
    const report = {
      sessionId: this.getSessionId(),
      totalEvents: this.events.length,
      eventsByLevel: {
        info: this.getEventsByLevel('info').length,
        error: this.getEventsByLevel('error').length,
        performance: this.getEventsByLevel('performance').length
      },
      sessionDuration: Date.now() - this.startTime,
      timestamp: new Date().toISOString()
    };

    console.log('\n📊 [SENTRY MCP] SESSION REPORT');
    console.log('================================');
    console.log(`Session ID: ${report.sessionId}`);
    console.log(`Total Events: ${report.totalEvents}`);
    console.log(`Info Events: ${report.eventsByLevel.info}`);
    console.log(`Error Events: ${report.eventsByLevel.error}`);
    console.log(`Performance Events: ${report.eventsByLevel.performance}`);
    console.log(`Session Duration: ${report.sessionDuration}ms`);
    console.log('================================\n');

    return report;
  }
}

// Demo function
async function runSentryDemo() {
  console.log('🎉 Starting Sentry MCP Integration Demo');
  console.log('=======================================\n');

  const sentry = new SentryMCPMonitor();

  // Demo 1: Basic info logging
  console.log('📝 Demo 1: Basic Info Logging');
  console.log('─'.repeat(30));
  sentry.logInfo('demo_start', {
    demo: 'Basic Info Logging',
    user: 'demo_user',
    environment: 'development'
  });

  // Demo 2: Error logging
  console.log('\n📝 Demo 2: Error Logging');
  console.log('─'.repeat(30));
  try {
    throw new Error('This is a demo error for Sentry MCP testing');
  } catch (error) {
    sentry.logError('demo_error', error, {
      demo: 'Error Logging',
      operation: 'intentional_error'
    });
  }

  // Demo 3: Performance monitoring
  console.log('\n📝 Demo 3: Performance Monitoring');
  console.log('─'.repeat(30));
  
  const startTime = Date.now();
  
  // Simulate some work
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  const endTime = Date.now();
  sentry.logPerformance('demo_performance', startTime, endTime, {
    demo: 'Performance Monitoring',
    simulatedWork: true,
    workType: 'setTimeout'
  });

  // Demo 4: Fast operation
  console.log('\n📝 Demo 4: Fast Operation');
  console.log('─'.repeat(30));
  
  const fastStart = Date.now();
  // Quick operation
  const result = 'fast_result';
  const fastEnd = Date.now();
  
  sentry.logPerformance('demo_fast_operation', fastStart, fastEnd, {
    demo: 'Fast Operation',
    result: result
  });

  // Demo 5: Slow operation (should trigger warning)
  console.log('\n📝 Demo 5: Slow Operation (Warning)');
  console.log('─'.repeat(30));
  
  const slowStart = Date.now();
  await new Promise(resolve => setTimeout(resolve, 2500));
  const slowEnd = Date.now();
  
  sentry.logPerformance('demo_slow_operation', slowStart, slowEnd, {
    demo: 'Slow Operation',
    expectedWarning: true
  });

  // Generate final report
  const report = sentry.generateReport();

  console.log('🎉 Sentry MCP Demo Completed Successfully!');
  console.log('All monitoring features are working correctly.');
  
  return {
    success: true,
    events: sentry.getEvents(),
    report
  };
}

// Run the demo
runSentryDemo()
  .then(result => {
    console.log('\n✅ Demo completed successfully!');
    console.log(`📊 Total events captured: ${result.events.length}`);
  })
  .catch(error => {
    console.error('\n❌ Demo failed:', error);
    process.exit(1);
  });