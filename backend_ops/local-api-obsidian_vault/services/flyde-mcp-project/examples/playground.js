#!/usr/bin/env node

/**
 * Flyde MCP Playground
 * 
 * Interactive playground for exploring Flyde examples
 * Run with: npm run playground
 */

import { runFlow } from '@flyde/loader';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Available examples
const examples = {
  'hello-world': {
    name: 'Hello World',
    description: 'Basic introduction to Flyde concepts',
    file: 'hello-world/hello-world.flyde',
    inputs: { message: 'Hello from Playground!' }
  },
  'ai-agent': {
    name: 'AI Agent',
    description: 'Complete AI agent workflow',
    file: 'ai-agent/ai-agent.flyde',
    inputs: { message: 'Tell me about visual programming' }
  },
  'data-pipeline': {
    name: 'Data Pipeline',
    description: 'ETL pipeline with data processing',
    file: 'data-pipeline/data-pipeline.flyde',
    inputs: {}
  }
};

async function runExample(exampleKey) {
  const example = examples[exampleKey];
  if (!example) {
    console.log('❌ Example not found:', exampleKey);
    return;
  }

  console.log(`\n🚀 Running: ${example.name}`);
  console.log('─'.repeat(50));
  console.log(`📝 Description: ${example.description}`);
  console.log(`📁 File: ${example.file}`);
  console.log(`📥 Inputs:`, example.inputs);
  console.log('─'.repeat(50));

  try {
    const startTime = Date.now();
    
    const flowPath = path.resolve(__dirname, example.file);
    console.log('🔍 Debug - Flow path:', flowPath);
    console.log('🔍 Debug - File exists:', fs.existsSync(flowPath));
    
    // Workaround for Flyde loader path duplication bug
    const result = await runFlow(flowPath, example.inputs);
    
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    console.log('✅ Example completed successfully!');
    console.log(`⏱️  Processing Time: ${processingTime}ms`);
    console.log('📤 Output:', JSON.stringify(result, null, 2));
    
  } catch (error) {
    console.error('❌ Error running example:', error.message);
  }
}

async function showMenu() {
  console.log('\n🎮 Flyde MCP Playground');
  console.log('========================');
  console.log('Available examples:');
  
  Object.entries(examples).forEach(([key, example], index) => {
    console.log(`${index + 1}. ${example.name} (${key})`);
    console.log(`   ${example.description}`);
  });
  
  console.log('\nCommands:');
  console.log('  all     - Run all examples');
  console.log('  <key>   - Run specific example');
  console.log('  help    - Show this menu');
  console.log('  exit    - Exit playground');
}

async function main() {
  console.log('🎉 Welcome to Flyde MCP Playground!');
  console.log('This playground demonstrates visual programming with Flyde');
  console.log('and MCP (Model Context Protocol) integration.\n');
  
  await showMenu();
  
  // For now, run all examples automatically
  console.log('\n🔄 Running all examples...\n');
  
  for (const [key, example] of Object.entries(examples)) {
    await runExample(key);
    console.log('\n' + '='.repeat(60) + '\n');
  }
  
  console.log('🎉 All examples completed!');
  console.log('Thanks for exploring Flyde with MCP! 🚀');
}

// Run the playground
main().catch(console.error);