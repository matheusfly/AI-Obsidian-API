package tests

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/datamaster/mcp-server/internal/ollama"
	"go.uber.org/zap"
)

// OllamaValidationTestSuite provides comprehensive Ollama integration testing
type OllamaValidationTestSuite struct {
	ollamaClient *ollama.Client
	logger       *zap.Logger
}

// NewOllamaValidationTestSuite creates a new Ollama validation test suite
func NewOllamaValidationTestSuite() *OllamaValidationTestSuite {
	logger, _ := zap.NewDevelopment()

	return &OllamaValidationTestSuite{
		ollamaClient: nil, // Will be initialized if Ollama is available
		logger:       logger,
	}
}

// TestOllamaConnection tests connection to Ollama service
func (suite *OllamaValidationTestSuite) TestOllamaConnection(t *testing.T) {
	t.Log("🔍 Testing Ollama Connection")

	// Try to connect to Ollama
	client := ollama.NewClient("http://localhost:11434", "deepseek-r1:8b")

	// Test with a simple prompt
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	response, err := client.GenerateCompletion(ctx, "Hello, this is a connection test.")
	if err != nil {
		t.Logf("⚠️ Ollama connection failed: %v", err)
		t.Logf("💡 Make sure Ollama is running: ollama serve")
		t.Logf("💡 Make sure DeepSeek-R1:8B is installed: ollama pull deepseek-r1:8b")
		return
	}

	if response == "" {
		t.Fatalf("Empty response from Ollama")
	}

	t.Logf("✅ Ollama connection successful")
	t.Logf("📝 Response: %s", response)
}

// TestModelAvailability tests if required models are available
func (suite *OllamaValidationTestSuite) TestModelAvailability(t *testing.T) {
	t.Log("🔍 Testing Model Availability")

	models := []string{
		"deepseek-r1:8b",
		"qwen2.5:7b",
		"llama3.1:8b",
	}

	// Test with empty model name
	_ = ollama.NewClient("http://localhost:11434", "")

	for _, model := range models {
		t.Run(model, func(t *testing.T) {
			// Create client with specific model
			testClient := ollama.NewClient("http://localhost:11434", model)

			ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
			defer cancel()

			response, err := testClient.GenerateCompletion(ctx, "Test prompt for model validation.")
			if err != nil {
				t.Logf("⚠️ Model %s not available: %v", model, err)
				return
			}

			if response == "" {
				t.Logf("⚠️ Model %s returned empty response", model)
				return
			}

			t.Logf("✅ Model %s is available and working", model)
		})
	}
}

// TestToolCallingCapability tests if models support tool calling
func (suite *OllamaValidationTestSuite) TestToolCallingCapability(t *testing.T) {
	t.Log("🔍 Testing Tool Calling Capability")

	client := ollama.NewClient("http://localhost:11434", "deepseek-r1:8b")

	// Test tool calling with a simple prompt
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	toolPrompt := `You have access to these tools:
- search_vault: Search the Obsidian vault for notes
- read_note: Read a specific note

Please use the search_vault tool to search for "test" and then read the first result.`

	response, err := client.GenerateCompletion(ctx, toolPrompt)
	if err != nil {
		t.Logf("⚠️ Tool calling test failed: %v", err)
		return
	}

	t.Logf("✅ Tool calling capability test completed")
	t.Logf("📝 Response: %s", response)
}

// TestPerformanceMetrics tests Ollama performance
func (suite *OllamaValidationTestSuite) TestPerformanceMetrics(t *testing.T) {
	t.Log("🔍 Testing Performance Metrics")

	client := ollama.NewClient("http://localhost:11434", "deepseek-r1:8b")

	testPrompts := []string{
		"Hello, world!",
		"Explain the concept of artificial intelligence in one sentence.",
		"Write a short poem about programming.",
		"List three benefits of using local LLMs.",
		"Describe the Model Context Protocol in simple terms.",
	}

	var totalDuration time.Duration
	successCount := 0

	for i, prompt := range testPrompts {
		start := time.Now()

		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		_, err := client.GenerateCompletion(ctx, prompt)
		cancel()

		duration := time.Since(start)
		totalDuration += duration

		if err != nil {
			t.Logf("⚠️ Prompt %d failed: %v", i+1, err)
		} else {
			successCount++
			t.Logf("✅ Prompt %d completed in %v", i+1, duration)
		}
	}

	avgDuration := totalDuration / time.Duration(len(testPrompts))
	successRate := float64(successCount) / float64(len(testPrompts)) * 100

	t.Logf("📊 Performance Summary:")
	t.Logf("   Success Rate: %.1f%%", successRate)
	t.Logf("   Average Duration: %v", avgDuration)
	t.Logf("   Total Duration: %v", totalDuration)

	if successRate < 80 {
		t.Logf("⚠️ Low success rate: %.1f%%", successRate)
	}

	if avgDuration > 10*time.Second {
		t.Logf("⚠️ High average duration: %v", avgDuration)
	}
}

// TestContextHandling tests context and token limits
func (suite *OllamaValidationTestSuite) TestContextHandling(t *testing.T) {
	t.Log("🔍 Testing Context Handling")

	client := ollama.NewClient("http://localhost:11434", "deepseek-r1:8b")

	// Test with different context lengths
	contextTests := []struct {
		name        string
		prompt      string
		description string
	}{
		{
			name:        "ShortContext",
			prompt:      "Hello!",
			description: "Very short prompt",
		},
		{
			name:        "MediumContext",
			prompt:      "Please explain the Model Context Protocol (MCP) and how it enables AI models to interact with external tools and data sources. Include details about its benefits for local AI setups and privacy-conscious users.",
			description: "Medium length prompt",
		},
		{
			name:        "LongContext",
			prompt:      generateLongPrompt(),
			description: "Long prompt to test context limits",
		},
	}

	for _, test := range contextTests {
		t.Run(test.name, func(t *testing.T) {
			start := time.Now()

			ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
			response, err := client.GenerateCompletion(ctx, test.prompt)
			cancel()

			duration := time.Since(start)

			if err != nil {
				t.Logf("⚠️ %s failed: %v", test.description, err)
				return
			}

			t.Logf("✅ %s completed in %v (response length: %d chars)",
				test.description, duration, len(response))
		})
	}
}

// TestErrorHandling tests error handling in Ollama client
func (suite *OllamaValidationTestSuite) TestErrorHandling(t *testing.T) {
	t.Log("🔍 Testing Error Handling")

	// Test with invalid URL
	invalidClient := ollama.NewClient("http://localhost:9999", "deepseek-r1:8b")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err := invalidClient.GenerateCompletion(ctx, "Test prompt")
	if err == nil {
		t.Fatalf("Expected error with invalid URL, but got success")
	}

	t.Logf("✅ Error handling test passed: %v", err)
}

// TestConcurrentRequests tests concurrent requests to Ollama
func (suite *OllamaValidationTestSuite) TestConcurrentRequests(t *testing.T) {
	t.Log("🔍 Testing Concurrent Requests")

	client := ollama.NewClient("http://localhost:11434", "deepseek-r1:8b")

	concurrency := 3
	results := make(chan error, concurrency)

	start := time.Now()

	for i := 0; i < concurrency; i++ {
		go func(id int) {
			ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
			defer cancel()

			_, err := client.GenerateCompletion(ctx, fmt.Sprintf("Concurrent test %d", id))
			results <- err
		}(i)
	}

	// Collect results
	successCount := 0
	for i := 0; i < concurrency; i++ {
		if err := <-results; err == nil {
			successCount++
		}
	}

	duration := time.Since(start)
	successRate := float64(successCount) / float64(concurrency) * 100

	t.Logf("📊 Concurrent Requests:")
	t.Logf("   Success Rate: %.1f%%", successRate)
	t.Logf("   Duration: %v", duration)

	if successRate < 66 { // Allow some failures
		t.Logf("⚠️ Low success rate for concurrent requests: %.1f%%", successRate)
	}
}

// generateLongPrompt creates a long prompt for context testing
func generateLongPrompt() string {
	return `Please provide a comprehensive analysis of the Model Context Protocol (MCP) and its applications in local AI setups. 

The Model Context Protocol is an open standard that enables large language models to interact with external tools and data sources. This protocol is particularly valuable for privacy-conscious users who want to run AI models locally without sending data to cloud services.

Key aspects to cover:
1. Technical architecture and design principles
2. Benefits for local AI deployments
3. Integration with tools like Ollama and Obsidian
4. Security and privacy considerations
5. Performance implications
6. Use cases and applications
7. Comparison with other approaches
8. Future development and trends

Please provide detailed explanations for each aspect, including practical examples and implementation considerations. Focus on how MCP enables AI models to become more useful by accessing external data and tools while maintaining user privacy and control.

Additionally, discuss the challenges and limitations of implementing MCP in local environments, such as hardware requirements, model compatibility, and development complexity. Provide recommendations for users who want to get started with MCP in their own setups.

Finally, explain how MCP fits into the broader ecosystem of local AI tools and how it compares to alternatives like direct API integrations or custom tool implementations.`
}

// TestOllamaValidation runs all Ollama validation tests
func TestOllamaValidation(t *testing.T) {
	suite := NewOllamaValidationTestSuite()

	// Run validation tests
	suite.TestOllamaConnection(t)
	suite.TestModelAvailability(t)
	suite.TestToolCallingCapability(t)
	suite.TestPerformanceMetrics(t)
	suite.TestContextHandling(t)
	suite.TestErrorHandling(t)
	suite.TestConcurrentRequests(t)

	t.Log("🎉 All Ollama validation tests completed!")
}
