package main

import (
	"context"
	"fmt"
	"log"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"go.uber.org/zap"
)

func main() {
	fmt.Println("🚀 MCP Server Mock Mode Demo")
	fmt.Println("=============================")

	// Initialize logger
	logger, err := zap.NewDevelopment()
	if err != nil {
		log.Fatal("Failed to create logger:", err)
	}
	defer logger.Sync()

	// Create mock HTTP client that simulates Obsidian API responses
	mockClient := client.NewMockClient(logger)

	// Create mock Ollama client
	mockOllamaClient := createMockOllamaClient(logger)

	// Create advanced tools
	advancedTools := tools.NewAdvancedTools(mockClient, mockOllamaClient, logger)

	// Test all tools
	ctx := context.Background()

	fmt.Println("\n📁 Testing ListFilesInVault...")
	result := advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
	fmt.Printf("Result: %+v\n", result)

	fmt.Println("\n📖 Testing ReadNote...")
	result = advancedTools.ReadNote(ctx, map[string]interface{}{
		"filename": "test-note.md",
	})
	fmt.Printf("Result: %+v\n", result)

	fmt.Println("\n🔍 Testing SearchVault...")
	result = advancedTools.SearchVault(ctx, map[string]interface{}{
		"query": "test query",
		"limit": 5,
	})
	fmt.Printf("Result: %+v\n", result)

	fmt.Println("\n🧠 Testing SemanticSearch...")
	result = advancedTools.SemanticSearch(ctx, map[string]interface{}{
		"query": "semantic test",
		"top_k": 3,
	})
	fmt.Printf("Result: %+v\n", result)

	fmt.Println("\n📝 Testing CreateNote...")
	result = advancedTools.CreateNote(ctx, map[string]interface{}{
		"path":    "new-note.md",
		"content": "# New Note\n\nThis is a test note created by the MCP server.",
	})
	fmt.Printf("Result: %+v\n", result)

	fmt.Println("\n🏷️ Testing BulkTag...")
	result = advancedTools.BulkTag(ctx, map[string]interface{}{
		"tags": []string{"test", "demo", "mcp"},
	})
	fmt.Printf("Result: %+v\n", result)

	fmt.Println("\n🔗 Testing AnalyzeLinks...")
	result = advancedTools.AnalyzeLinks(ctx, map[string]interface{}{})
	fmt.Printf("Result: %+v\n", result)

	fmt.Println("\n📋 Tool Definitions:")
	definitions := advancedTools.GetToolDefinitions()
	for i, def := range definitions {
		fmt.Printf("%d. %s: %s\n", i+1, def.Name, def.Description)
	}

	fmt.Println("\n✅ Mock mode demo completed successfully!")
}

// createMockOllamaClient creates a mock Ollama client
func createMockOllamaClient(logger *zap.Logger) *ollama.Client {
	// This would be a mock implementation
	// For now, we'll return nil and handle it in the tools
	return nil
}
