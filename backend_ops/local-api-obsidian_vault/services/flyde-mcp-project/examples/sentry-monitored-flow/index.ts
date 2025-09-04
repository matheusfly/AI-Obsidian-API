import { runFlow } from '@flyde/loader';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Sentry-Monitored Flow Example
 * 
 * This example demonstrates:
 * - Sentry MCP integration for error tracking
 * - Performance monitoring and alerting
 * - Flow execution logging
 * - Error handling and reporting
 */

async function runSentryMonitoredFlow() {
  console.log('🔍 Starting Sentry-Monitored Flow Example');
  console.log('=========================================');
  console.log('This example demonstrates Sentry MCP integration with Flyde flows');
  console.log('for comprehensive error tracking and performance monitoring.\n');
  
  const testMessages = [
    'Hello Sentry Monitoring!',
    'Test performance monitoring',
    '', // This should trigger an error
    'Another test message for monitoring'
  ];
  
  for (const message of testMessages) {
    console.log(`\n📨 Testing with message: "${message}"`);
    console.log('─'.repeat(50));
    
    try {
      const startTime = Date.now();
      
      // Execute the Sentry-monitored flow
      const result = await runFlow(
        path.resolve(__dirname, 'sentry-monitored.flyde'),
        { message }
      );
      
      const endTime = Date.now();
      const totalDuration = endTime - startTime;
      
      console.log('✅ Flow executed successfully!');
      console.log('📊 Results:');
      console.log('─'.repeat(30));
      console.log(`⏱️  Total Duration: ${totalDuration}ms`);
      console.log(`🔍 Sentry Event ID: ${result.result.sentryEventId}`);
      console.log(`📊 Flow Duration: ${result.result.metrics.totalDuration}ms`);
      console.log(`📝 Input Length: ${result.result.metrics.inputLength}`);
      console.log(`📊 Word Count: ${result.result.metrics.wordCount}`);
      console.log(`🎯 Output: ${result.result.output}`);
      
      // Performance analysis
      if (totalDuration > 5000) {
        console.warn('⚠️ PERFORMANCE WARNING: Flow took longer than 5 seconds');
      } else if (totalDuration > 1000) {
        console.warn('⚠️ PERFORMANCE NOTICE: Flow took longer than 1 second');
      } else {
        console.log('✅ Performance OK');
      }
      
    } catch (error) {
      console.error('❌ Flow execution failed:', error.message);
      
      // Check if we have an error report from the flow
      if (error.message.includes('Input cannot be empty')) {
        console.log('🔍 This was an expected error for empty input testing');
      }
    }
    
    // Add delay between tests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('\n🎉 Sentry-monitored flow example completed!');
  console.log('📊 Check the logs above for detailed Sentry monitoring information');
  console.log('This demonstrates how Sentry MCP can enhance Flyde flow monitoring');
}

// Run the example
runSentryMonitoredFlow();