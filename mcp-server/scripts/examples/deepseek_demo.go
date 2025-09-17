package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/config"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"go.uber.org/zap"
)

func main() {
	fmt.Println("🚀 DeepSeek-R1:8B MCP Server Demo")
	fmt.Println("=================================")

	// Load configuration
	cfg, err := config.LoadConfig("./configs/config.yaml")
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Initialize logger
	logger, err := zap.NewDevelopment()
	if err != nil {
		log.Fatalf("Failed to create logger: %v", err)
	}
	defer logger.Sync()

	fmt.Printf("📁 Vault Path: %s\n", cfg.Vault.Path)
	fmt.Printf("🔗 API URL: %s\n", cfg.API.BaseURL)
	fmt.Printf("🤖 Ollama Model: %s\n", cfg.Ollama.Model)
	fmt.Printf("🌐 Server Port: %s\n", cfg.Server.Port)
	fmt.Println()

	// Initialize HTTP client
	clientConfig := &client.Config{
		BaseURL:     cfg.API.BaseURL,
		Token:       cfg.API.Token,
		Timeout:     30 * time.Second,
		RateLimit:   10,
		CacheTTL:    5 * time.Minute,
		EnableCache: cfg.Vault.EnableCache,
	}

	obsidianClient := client.NewClient(clientConfig, logger)

	// Initialize Ollama client
	ollamaClient := ollama.NewClient(cfg.Ollama.Host, cfg.Ollama.Model)

	// Initialize advanced tools
	advancedTools := tools.NewAdvancedTools(obsidianClient, ollamaClient, logger)

	ctx := context.Background()

	// Demo 1: List files in vault
	fmt.Println("📋 Demo 1: Listing files in vault")
	fmt.Println("--------------------------------")
	result := advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
	if result.Success {
		files, ok := result.Data.([]map[string]interface{})
		if ok {
			fmt.Printf("✅ Found %d files\n", len(files))
			for i, file := range files {
				if i >= 5 { // Show only first 5
					fmt.Printf("   ... and %d more files\n", len(files)-5)
					break
				}
				name := file["name"]
				path := file["path"]
				fmt.Printf("   📄 %s (%s)\n", name, path)
			}
		}
	} else {
		fmt.Printf("❌ Failed to list files: %s\n", result.Error)
	}
	fmt.Println()

	// Demo 2: Search vault
	fmt.Println("🔍 Demo 2: Searching vault")
	fmt.Println("--------------------------")
	result = advancedTools.SearchVault(ctx, map[string]interface{}{
		"query": "milionario",
		"limit": 3,
	})
	if result.Success {
		results, ok := result.Data.([]map[string]interface{})
		if ok {
			fmt.Printf("✅ Found %d results for 'milionario'\n", len(results))
			for i, searchResult := range results {
				if i >= 3 {
					break
				}
				path := searchResult["path"]
				fmt.Printf("   📄 %s\n", path)
			}
		}
	} else {
		fmt.Printf("❌ Search failed: %s\n", result.Error)
	}
	fmt.Println()

	// Demo 3: Test Ollama connectivity
	fmt.Println("🤖 Demo 3: Testing DeepSeek-R1:8B connectivity")
	fmt.Println("----------------------------------------------")
	start := time.Now()
	response, err := ollamaClient.GenerateCompletion(ctx, "Hello! Can you tell me about knowledge management?")
	duration := time.Since(start)

	if err != nil {
		fmt.Printf("❌ Ollama connection failed: %v\n", err)
	} else {
		fmt.Printf("✅ Ollama response received in %v\n", duration)
		fmt.Printf("📝 Response preview: %.100s...\n", response)
	}
	fmt.Println()

	// Demo 4: Semantic search
	fmt.Println("🧠 Demo 4: Semantic search with DeepSeek-R1:8B")
	fmt.Println("----------------------------------------------")
	result = advancedTools.SemanticSearch(ctx, map[string]interface{}{
		"query": "business strategies",
		"top_k": 2,
	})
	if result.Success {
		data, ok := result.Data.(map[string]interface{})
		if ok {
			query := data["query"]
			embedding := data["embedding"]
			results := data["results"]

			fmt.Printf("✅ Semantic search completed\n")
			fmt.Printf("   Query: %s\n", query)
			fmt.Printf("   Embedding length: %d characters\n", len(embedding.(string)))

			if resultsSlice, ok := results.([]map[string]interface{}); ok {
				fmt.Printf("   Results: %d found\n", len(resultsSlice))
			}
		}
	} else {
		fmt.Printf("❌ Semantic search failed: %s\n", result.Error)
	}
	fmt.Println()

	// Demo 5: Tool definitions
	fmt.Println("🛠️  Demo 5: Available MCP tools")
	fmt.Println("-------------------------------")
	toolDefinitions := advancedTools.GetToolDefinitions()
	fmt.Printf("✅ Available tools: %d\n", len(toolDefinitions))
	for _, tool := range toolDefinitions {
		fmt.Printf("   🔧 %s: %s\n", tool.Name, tool.Description)
	}
	fmt.Println()

	// Demo 6: Performance test
	fmt.Println("⚡ Demo 6: Performance test")
	fmt.Println("--------------------------")
	operations := []struct {
		name string
		fn   func() mcp.ToolResult
	}{
		{"ListFiles", func() mcp.ToolResult {
			return advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
		}},
		{"Search", func() mcp.ToolResult {
			return advancedTools.SearchVault(ctx, map[string]interface{}{
				"query": "test",
				"limit": 5,
			})
		}},
	}

	for _, op := range operations {
		start := time.Now()
		result := op.fn()
		duration := time.Since(start)

		if result.Success {
			fmt.Printf("   ✅ %s: %v\n", op.name, duration)
		} else {
			fmt.Printf("   ❌ %s: %v (failed: %s)\n", op.name, duration, result.Error)
		}
	}
	fmt.Println()

	// Demo 7: Cache statistics
	fmt.Println("💾 Demo 7: Cache statistics")
	fmt.Println("--------------------------")
	cacheStats := obsidianClient.GetCacheStats()
	fmt.Printf("✅ Cache enabled: %v\n", cacheStats["enabled"])
	if enabled, ok := cacheStats["enabled"].(bool); ok && enabled {
		fmt.Printf("   Items cached: %v\n", cacheStats["items"])
		fmt.Printf("   TTL: %v\n", cacheStats["ttl"])
	}
	fmt.Println()

	fmt.Println("🎉 Demo completed successfully!")
	fmt.Println()
	fmt.Println("📋 Next steps:")
	fmt.Println("   1. Start the MCP server: go run ./cmd/server/main.go")
	fmt.Println("   2. Configure MCPHost with configs/mcphost.json")
	fmt.Println("   3. Test with DeepSeek-R1:8B via Ollama")
	fmt.Println("   4. Run integration tests: go test ./tests/...")
	fmt.Println()
	fmt.Println("🔗 Useful commands:")
	fmt.Println("   • List tools: curl http://localhost:3010/tools/list")
	fmt.Println("   • Health check: curl http://localhost:3010/health")
	fmt.Println("   • Execute tool: curl -X POST http://localhost:3010/tools/execute \\")
	fmt.Println("     -H 'Content-Type: application/json' \\")
	fmt.Println("     -d '{\"tool_name\": \"search_vault\", \"parameters\": {\"query\": \"test\"}}'")
}

