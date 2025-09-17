package main

import (
	"context"
	"fmt"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/tools"
	"go.uber.org/zap"
)

// MockOllamaClient for testing
type MockOllamaClient struct{}

func (m *MockOllamaClient) GenerateCompletion(ctx context.Context, prompt string) (string, error) {
	return "mock completion", nil
}

func (m *MockOllamaClient) ChatCompletion(ctx context.Context, messages []map[string]interface{}) (map[string]interface{}, error) {
	return map[string]interface{}{"response": "mock chat response"}, nil
}

func (m *MockOllamaClient) GenerateEmbedding(ctx context.Context, text string) ([]float64, error) {
	return []float64{0.1, 0.2, 0.3, 0.4, 0.5}, nil
}

func main() {
	// Create logger
	logger, _ := zap.NewDevelopment()

	// Create mock HTTP client
	mockHTTP := client.NewMockClient(logger)

	// Create mock Ollama client
	mockOllama := &MockOllamaClient{}

	// Create advanced tools
	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	// Test semantic search
	ctx := context.Background()
	params := map[string]interface{}{
		"query": "test query",
		"top_k": 3,
	}

	fmt.Println("Testing semantic search...")
	result := advancedTools.SemanticSearch(ctx, params)

	fmt.Printf("Success: %v\n", result.Success)
	if result.Error != "" {
		fmt.Printf("Error: %s\n", result.Error)
	}
	if result.Data != nil {
		fmt.Printf("Data: %+v\n", result.Data)
	}
}
