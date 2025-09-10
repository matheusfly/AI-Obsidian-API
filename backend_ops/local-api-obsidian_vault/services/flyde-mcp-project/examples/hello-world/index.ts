import { runFlow } from '@flyde/loader';
import path from 'path';

/**
 * Hello World Flyde Example
 * 
 * This example demonstrates:
 * - Basic flow execution
 * - Input/output handling
 * - Simple data processing
 * - Visual flow integration
 */

async function runHelloWorld() {
  console.log('🚀 Starting Hello World Flyde Example');
  console.log('=====================================');
  
  try {
    // Execute the hello world flow
    const result = await runFlow(
      path.join(__dirname, 'hello-world.flyde'),
      { 
        message: 'Hello from TypeScript!' 
      }
    );
    
    console.log('✅ Flow executed successfully!');
    console.log('📤 Result:', result.result);
    
  } catch (error) {
    console.error('❌ Error executing flow:', error);
  }
}

// Run the example
runHelloWorld();