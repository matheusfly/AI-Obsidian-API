import { runFlow } from '@flyde/loader';
import path from 'path';

/**
 * AI Agent Flyde Example
 * 
 * This example demonstrates:
 * - Input processing and validation
 * - AI-powered analysis (mock implementation)
 * - Response generation
 * - Output formatting
 * - Error handling
 */

async function runAIAgent() {
  console.log('🤖 Starting AI Agent Flyde Example');
  console.log('==================================');
  
  const testMessages = [
    'Hello, I need help with my AI project',
    'Can you analyze this complex data structure for me?',
    'What are the best practices for visual programming?',
    'I love working with AI and machine learning technologies'
  ];
  
  for (const message of testMessages) {
    console.log(`\n📨 Processing: "${message}"`);
    console.log('─'.repeat(50));
    
    try {
      const result = await runFlow(
        path.join(__dirname, 'ai-agent.flyde'),
        { message }
      );
      
      console.log('✅ Agent Response:');
      console.log(JSON.stringify(result.result, null, 2));
      
    } catch (error) {
      console.error('❌ Error processing message:', error);
    }
    
    // Add delay between messages
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('\n🎉 AI Agent example completed!');
}

// Run the example
runAIAgent();