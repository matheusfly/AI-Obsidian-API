#!/usr/bin/env node

/**
 * Flyde MCP Project - Main Entry Point
 * 
 * This is the main entry point for the Flyde MCP project.
 * It demonstrates various Flyde examples and MCP integrations.
 */

import { runFlow } from '@flyde/loader';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Example configurations
const examples = [
  {
    name: 'Hello World',
    description: 'Basic Flyde introduction',
    flowPath: path.join(__dirname, '../examples/hello-world/hello-world.flyde'),
    inputs: { message: 'Hello from Flyde MCP!' }
  },
  {
    name: 'AI Agent',
    description: 'AI agent workflow example',
    flowPath: path.join(__dirname, '../examples/ai-agent/ai-agent.flyde'),
    inputs: { message: 'Explain visual programming benefits' }
  },
  {
    name: 'Data Pipeline',
    description: 'ETL data processing pipeline',
    flowPath: path.join(__dirname, '../examples/data-pipeline/data-pipeline.flyde'),
    inputs: {}
  }
];

async function runExample(example: typeof examples[0]) {
  console.log(`\n🚀 Running: ${example.name}`);
  console.log('─'.repeat(50));
  console.log(`📝 Description: ${example.description}`);
  console.log(`📁 Flow: ${example.flowPath}`);
  console.log(`📥 Inputs:`, example.inputs);
  console.log('─'.repeat(50));

  try {
    const startTime = Date.now();
    
    const result = await runFlow(example.flowPath, example.inputs);
    
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    console.log('✅ Example completed successfully!');
    console.log(`⏱️  Processing Time: ${processingTime}ms`);
    console.log('📤 Output:', JSON.stringify(result, null, 2));
    
  } catch (error) {
    console.error('❌ Error running example:', error);
  }
}

async function main() {
  console.log('🎉 Welcome to Flyde MCP Project!');
  console.log('================================');
  console.log('This project demonstrates visual programming with Flyde');
  console.log('and MCP (Model Context Protocol) integration.\n');
  
  console.log('📚 Available Examples:');
  examples.forEach((example, index) => {
    console.log(`${index + 1}. ${example.name}`);
    console.log(`   ${example.description}`);
  });
  
  console.log('\n🔄 Running all examples...\n');
  
  for (const example of examples) {
    await runExample(example);
    console.log('\n' + '='.repeat(60) + '\n');
  }
  
  console.log('🎉 All examples completed!');
  console.log('Thanks for exploring Flyde with MCP! 🚀');
  console.log('\n📖 Next Steps:');
  console.log('- Explore the examples/ directory');
  console.log('- Try modifying the flows');
  console.log('- Create your own custom nodes');
  console.log('- Integrate with your projects');
}

// Run the main function
main().catch(console.error);