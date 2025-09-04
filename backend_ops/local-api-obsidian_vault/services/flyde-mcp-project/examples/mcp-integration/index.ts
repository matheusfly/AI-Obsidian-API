import { runFlow } from '@flyde/loader';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * MCP Integration Example
 * 
 * This example demonstrates:
 * - Web crawling with MCP tools
 * - Data processing and analysis
 * - Browser automation
 * - File operations
 * - Result aggregation
 */

async function runMCPIntegration() {
  console.log('🔗 Starting MCP Integration Example');
  console.log('==================================');
  console.log('This example demonstrates how to integrate MCP tools with Flyde flows');
  console.log('for enhanced AI agent capabilities and web automation.\n');
  
  try {
    const startTime = Date.now();
    
    // Execute the MCP integration flow
    const result = await runFlow(
      path.join(__dirname, 'mcp-integration.flyde'),
      {}
    );
    
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    console.log('✅ MCP Integration completed successfully!');
    console.log('📊 Results:');
    console.log('─'.repeat(50));
    console.log(`⏱️  Processing Time: ${processingTime}ms`);
    console.log(`🔗 Operations: ${result.results.summary.totalOperations}`);
    console.log(`✅ Success Rate: ${result.results.summary.successCount}/${result.results.summary.totalOperations}`);
    
    console.log('\n📋 Detailed Results:');
    console.log('─'.repeat(50));
    console.log('🌐 Web Crawl:', result.results.webCrawl.status);
    console.log('📊 Data Analysis:', result.results.dataAnalysis.operation);
    console.log('🤖 Browser Action:', result.results.browserAction.action);
    console.log('📁 File Operation:', result.results.fileOperation.operation);
    
    console.log('\n🎉 MCP Integration example completed!');
    console.log('This demonstrates the power of combining Flyde visual flows');
    console.log('with MCP tools for sophisticated AI agent workflows.');
    
  } catch (error) {
    console.error('❌ Error running MCP integration:', error);
  }
}

// Run the example
runMCPIntegration();