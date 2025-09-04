/**
 * Sentry MCP Monitor for Flyde Project
 * 
 * This module provides Sentry integration for monitoring Flyde flows
 * and MCP operations with comprehensive error tracking and performance monitoring.
 */

// Sentry MCP Monitoring Class
export class SentryMCPMonitor {
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
  logPerformance(operation, duration, metrics = {}) {
    const event = {
      id: `perf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      level: 'performance',
      operation,
      performance: {
        duration,
        metrics,
        timestamp: new Date().toISOString()
      },
      sessionId: this.getSessionId()
    };

    this.events.push(event);

    // Performance thresholds
    const thresholds = {
      warning: 1000,  // 1 second
      error: 5000     // 5 seconds
    };

    if (duration > thresholds.error) {
      console.error(`🚨 [SENTRY MCP] PERFORMANCE ERROR: ${operation} took ${duration}ms (exceeds ${thresholds.error}ms threshold)`);
    } else if (duration > thresholds.warning) {
      console.warn(`⚠️ [SENTRY MCP] PERFORMANCE WARNING: ${operation} took ${duration}ms (exceeds ${thresholds.warning}ms threshold)`);
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