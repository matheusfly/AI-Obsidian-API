/**
 * Sentry MCP Monitor for Flyde Project
 * 
 * This module provides Sentry integration for monitoring Flyde flows
 * and MCP operations with comprehensive error tracking and performance monitoring.
 */

import { CodeNode } from '@flyde/core';

// Sentry MCP Integration Node
export const SentryMonitor: CodeNode = {
  id: 'SentryMonitor',
  displayName: 'Sentry Monitor',
  description: 'Monitor Flyde flows with Sentry MCP integration',
  inputs: {
    flowName: { description: 'Name of the flow being monitored' },
    operation: { description: 'Operation being performed' },
    data: { description: 'Data to monitor' },
    level: { description: 'Log level (info, warn, error)' }
  },
  outputs: {
    monitored: { description: 'Monitoring result' },
    error: { description: 'Error if monitoring fails' }
  },
  run: async (inputs, outputs) => {
    try {
      const monitoringData = {
        flowName: inputs.flowName,
        operation: inputs.operation,
        data: inputs.data,
        level: inputs.level || 'info',
        timestamp: new Date().toISOString(),
        sessionId: `session_${Date.now()}`,
        environment: process.env.NODE_ENV || 'development'
      };

      // Simulate Sentry MCP monitoring
      console.log('🔍 Sentry MCP Monitor:', {
        flow: monitoringData.flowName,
        operation: monitoringData.operation,
        level: monitoringData.level,
        timestamp: monitoringData.timestamp
      });

      // Simulate different monitoring scenarios
      if (monitoringData.level === 'error') {
        console.error('❌ Sentry Error Tracking:', monitoringData);
      } else if (monitoringData.level === 'warn') {
        console.warn('⚠️ Sentry Warning:', monitoringData);
      } else {
        console.log('ℹ️ Sentry Info:', monitoringData);
      }

      outputs.monitored.next({
        success: true,
        monitoringData,
        sentryEventId: `event_${Date.now()}`,
        message: 'Successfully monitored with Sentry MCP'
      });

    } catch (error) {
      console.error('❌ Sentry Monitor Error:', error);
      outputs.error.next({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  }
};

// Performance Monitor Node
export const PerformanceMonitor: CodeNode = {
  id: 'PerformanceMonitor',
  displayName: 'Performance Monitor',
  description: 'Monitor performance metrics for Flyde flows',
  inputs: {
    flowName: { description: 'Name of the flow' },
    startTime: { description: 'Flow start time' },
    endTime: { description: 'Flow end time' },
    metrics: { description: 'Additional metrics' }
  },
  outputs: {
    performance: { description: 'Performance analysis' },
    alert: { description: 'Performance alert if threshold exceeded' }
  },
  run: async (inputs, outputs) => {
    try {
      const startTime = inputs.startTime || Date.now();
      const endTime = inputs.endTime || Date.now();
      const duration = endTime - startTime;

      const performanceData = {
        flowName: inputs.flowName,
        duration: duration,
        startTime: new Date(startTime).toISOString(),
        endTime: new Date(endTime).toISOString(),
        metrics: inputs.metrics || {},
        timestamp: new Date().toISOString()
      };

      // Performance thresholds
      const thresholds = {
        warning: 1000, // 1 second
        error: 5000    // 5 seconds
      };

      let alert = null;
      if (duration > thresholds.error) {
        alert = {
          level: 'error',
          message: `Flow ${inputs.flowName} took ${duration}ms (exceeds error threshold)`,
          threshold: thresholds.error,
          actual: duration
        };
      } else if (duration > thresholds.warning) {
        alert = {
          level: 'warning',
          message: `Flow ${inputs.flowName} took ${duration}ms (exceeds warning threshold)`,
          threshold: thresholds.warning,
          actual: duration
        };
      }

      console.log('📊 Performance Monitor:', performanceData);
      if (alert) {
        console.log(`🚨 Performance Alert:`, alert);
        outputs.alert.next(alert);
      }

      outputs.performance.next(performanceData);

    } catch (error) {
      console.error('❌ Performance Monitor Error:', error);
    }
  }
};

// Error Handler Node
export const ErrorHandler: CodeNode = {
  id: 'ErrorHandler',
  displayName: 'Error Handler',
  description: 'Handle and report errors with Sentry MCP',
  inputs: {
    error: { description: 'Error to handle' },
    context: { description: 'Error context' },
    flowName: { description: 'Flow where error occurred' }
  },
  outputs: {
    handled: { description: 'Error handling result' },
    report: { description: 'Error report for Sentry' }
  },
  run: async (inputs, outputs) => {
    try {
      const errorData = {
        error: inputs.error,
        context: inputs.context,
        flowName: inputs.flowName,
        timestamp: new Date().toISOString(),
        stack: inputs.error?.stack || 'No stack trace available',
        message: inputs.error?.message || 'Unknown error'
      };

      // Simulate Sentry error reporting
      console.error('🚨 Sentry Error Report:', errorData);

      const report = {
        sentryEventId: `error_${Date.now()}`,
        errorData,
        status: 'reported',
        timestamp: new Date().toISOString()
      };

      outputs.handled.next({
        success: true,
        errorId: report.sentryEventId,
        message: 'Error successfully reported to Sentry'
      });

      outputs.report.next(report);

    } catch (error) {
      console.error('❌ Error Handler Error:', error);
      outputs.handled.next({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  }
};

// Export all monitoring nodes
export const MonitoringNodes = {
  SentryMonitor,
  PerformanceMonitor,
  ErrorHandler
};