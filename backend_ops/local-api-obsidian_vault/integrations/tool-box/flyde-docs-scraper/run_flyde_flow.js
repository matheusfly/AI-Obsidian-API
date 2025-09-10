/**
 * Run the Flyde hello-world flow
 * This script demonstrates how to execute the visual flow
 */

const { runFlow } = require('@flyde/loader');
const path = require('path');

async function runHelloWorldFlow() {
    console.log('🚀 Running Flyde Hello World Flow...');
    console.log('Target URL: https://flyde.dev/playground/blog-generator');
    console.log('');

    try {
        // Run the flow
        const result = await runFlow(
            path.join(__dirname, './flows/hello-world.flyde'),
            {
                // The flow will use its internal trigger
            }
        );

        console.log('✅ Flow completed successfully!');
        console.log('📊 Results:');
        console.log(JSON.stringify(result, null, 2));

        // Check if we have output
        if (result.output) {
            console.log('');
            console.log('🎉 Hello World Summary:');
            console.log(`Message: ${result.output.message}`);
            console.log(`Filename: ${result.output.filename}`);
            console.log(`URL: ${result.output.url}`);
            console.log(`Scraper: ${result.output.scraper}`);
            console.log(`Content Length: ${result.output.statistics.content_length}`);
            console.log(`Text Length: ${result.output.statistics.text_length}`);
            console.log(`Links Found: ${result.output.statistics.links_count}`);
        }

    } catch (error) {
        console.error('❌ Flow execution failed:', error.message);
        console.error(error.stack);
    }
}

// Run the flow
runHelloWorldFlow();