#!/usr/bin/env node

/**
 * Sentry-Monitored Flyde MCP Playground
 * 
 * Interactive playground with Sentry MCP monitoring for enhanced error tracking
 * and performance monitoring of Flyde flows.
 */

import { runFlow } from '@flyde/loader';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Sentry MCP monitoring functions
class SentryMonitor {
  static async logInfo(flowName, operation, data) {
    console.log(`🔍 [SENTRY] INFO - Flow: ${flowName}, Operation: ${operation}`);
    console.log(`📊 Data:`, data);
  }

  static async logError(flowName, operation, error) {
    console.error(`🚨 [SENTRY] ERROR - Flow: ${flowName}, Operation: ${operation}`);
    console.error(`❌ Error:`, error.message);
    console.error(`📋 Stack:`, error.stack);
  }

  static async logPerformance(flowName, startTime, endTime) {
    const duration = endTime - startTime;
    console.log(`📊 [SENTRY] PERFORMANCE - Flow: ${flowName}, Duration: ${duration}ms`);
    
    if (duration > 5000) {
      console.warn(`⚠️ [SENTRY] WARNING - Flow ${flowName} took ${duration}ms (exceeds 5s threshold)`);
    }
  }
}

// Available examples with Sentry monitoring
const examples = {
  'hello-world': {
    name: 'Hello World',
    description: 'Basic introduction to Flyde concepts',
    file: 'hello-world/hello-world.flyde',
    inputs: { message: 'Hello from Sentry-Monitored Playground!' }
  },
  'ai-agent': {
    name: 'AI Agent',
    description: 'Complete AI agent workflow',
    file: 'ai-agent/ai-agent.flyde',
    inputs: { message: 'Tell me about visual programming with monitoring' }
  },
  'data-pipeline': {
    name: 'Data Pipeline',
    description: 'ETL pipeline with data processing',
    file: 'data-pipeline/data-pipeline.flyde',
    inputs: {}
  },
  'mcp-integration': {
    name: 'MCP Integration',
    description: 'MCP tools integration with monitoring',
    file: 'mcp-integration/mcp-integration.flyde',
    inputs: {}
  }
};

async function runExampleWithSentry(exampleKey) {
  const example = examples[exampleKey];
  if (!example) {
    console.log('❌ Example not found:', exampleKey);
    return;
  }

  console.log(`\n🚀 Running: ${example.name} (with Sentry monitoring)`);
  console.log('─'.repeat(60));
  console.log(`📝 Description: ${example.description}`);
  console.log(`📁 File: ${example.file}`);
  console.log(`📥 Inputs:`, example.inputs);
  console.log('─'.repeat(60));

  const startTime = Date.now();
  
  try {
    // Log start of flow execution
    await SentryMonitor.logInfo(example.name, 'flow_start', {
      file: example.file,
      inputs: example.inputs,
      timestamp: new Date().toISOString()
    });

    const result = await runFlow(
      path.resolve(__dirname, example.file),
      example.inputs
    );
    
    const endTime = Date.now();
    
    // Log performance metrics
    await SentryMonitor.logPerformance(example.name, startTime, endTime);
    
    // Log successful completion
    await SentryMonitor.logInfo(example.name, 'flow_complete', {
      duration: endTime - startTime,
      result: result,
      timestamp: new Date().toISOString()
    });
    
    console.log('✅ Example completed successfully!');
    console.log(`⏱️  Processing Time: ${endTime - startTime}ms`);
    console.log('📤 Output:', JSON.stringify(result, null, 2));
    
  } catch (error) {
    const endTime = Date.now();
    
    // Log error with Sentry
    await SentryMonitor.logError(example.name, 'flow_error', error);
    
    // Log performance even for failed flows
    await SentryMonitor.logPerformance(example.name, startTime, endTime);
    
    console.error('❌ Error running example:', error.message);
  }
}

async function showMenu() {
  console.log('\n🎮 Sentry-Monitored Flyde MCP Playground');
  console.log('==========================================');
  console.log('Available examples (with Sentry monitoring):');
  
  Object.entries(examples).forEach(([key, example], index) => {
    console.log(`${index + 1}. ${example.name} (${key})`);
    console.log(`   ${example.description}`);
  });
  
  console.log('\n🔍 Sentry Monitoring Features:');
  console.log('  - Real-time error tracking');
  console.log('  - Performance monitoring');
  console.log('  - Flow execution logging');
  console.log('  - Automatic alerting');
  
  console.log('\nCommands:');
  console.log('  all     - Run all examples with monitoring');
  console.log('  <key>   - Run specific example with monitoring');
  console.log('  help    - Show this menu');
  console.log('  exit    - Exit playground');
}

async function main() {
  console.log('🎉 Welcome to Sentry-Monitored Flyde MCP Playground!');
  console.log('====================================================');
  console.log('This playground demonstrates visual programming with Flyde');
  console.log('and MCP (Model Context Protocol) integration with comprehensive');
  console.log('Sentry monitoring for error tracking and performance analysis.\n');
  
  await showMenu();
  
  // Run all examples with Sentry monitoring
  console.log('\n🔄 Running all examples with Sentry monitoring...\n');
  
  for (const [key, example] of Object.entries(examples)) {
    await runExampleWithSentry(key);
    console.log('\n' + '='.repeat(70) + '\n');
  }
  
  console.log('🎉 All examples completed with Sentry monitoring!');
  console.log('📊 Check the logs above for detailed monitoring information');
  console.log('Thanks for exploring Flyde with MCP and Sentry! 🚀');
}

// Run the Sentry-monitored playground
main().catch(async (error) => {
  await SentryMonitor.logError('playground', 'main_error', error);
  console.error('Fatal error in playground:', error);
  process.exit(1);
});