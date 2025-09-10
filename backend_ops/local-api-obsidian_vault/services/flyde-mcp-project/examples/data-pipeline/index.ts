import { runFlow } from '@flyde/loader';
import path from 'path';

/**
 * Data Pipeline Flyde Example
 * 
 * This example demonstrates:
 * - ETL (Extract, Transform, Load) pipeline
 * - Data validation and error handling
 * - Data transformation and enrichment
 * - Aggregation and summarization
 * - Export and reporting
 */

async function runDataPipeline() {
  console.log('🔄 Starting Data Pipeline Flyde Example');
  console.log('======================================');
  
  try {
    const startTime = Date.now();
    
    // Execute the data pipeline flow
    const result = await runFlow(
      path.join(__dirname, 'data-pipeline.flyde'),
      {}
    );
    
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    console.log('\n✅ Pipeline executed successfully!');
    console.log('📊 Results:');
    console.log('─'.repeat(40));
    console.log(`⏱️  Processing Time: ${processingTime}ms`);
    console.log(`📈 Records Processed: ${result.result.recordCount}`);
    console.log(`📁 Export Format: ${result.result.format}`);
    console.log(`💾 Destination: ${result.result.destination}`);
    
    console.log('\n📋 Summary Statistics:');
    console.log('─'.repeat(40));
    console.log(`👥 Total Records: ${result.result.summary.totalRecords}`);
    console.log(`📊 Age Groups:`, result.result.summary.ageGroups);
    console.log(`📧 Email Domains: ${result.result.summary.domains.join(', ')}`);
    console.log(`📊 Average Age: ${result.result.summary.averageAge.toFixed(1)}`);
    
    console.log('\n🎉 Data pipeline example completed!');
    
  } catch (error) {
    console.error('❌ Error executing pipeline:', error);
  }
}

// Run the example
runDataPipeline();