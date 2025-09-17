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
	"go.uber.org/zap"
)

func main() {
	fmt.Println("🔍 Testing Real Obsidian API Direct Integration")
	fmt.Println("==============================================")

	// Initialize logger
	logger, err := zap.NewDevelopment()
	if err != nil {
		log.Fatal("Failed to create logger:", err)
	}
	defer logger.Sync()

	// Load configuration
	cfg, err := config.LoadConfig("configs/config.yaml")
	if err != nil {
		logger.Fatal("Failed to load config", zap.Error(err))
	}

	fmt.Printf("API Base URL: %s\n", cfg.API.BaseURL)
	fmt.Printf("API Token: %s...\n", cfg.API.Token[:20])

	// Create real HTTP client
	clientCfg := &client.Config{
		BaseURL:     cfg.API.BaseURL,
		Token:       cfg.API.Token,
		Timeout:     10 * time.Second,
		RateLimit:   10,
		CacheTTL:    5 * time.Minute,
		EnableCache: true,
	}
	httpClient := client.NewClient(clientCfg, logger)

	// Create Ollama client
	ollamaClient := ollama.NewClient(cfg.Ollama.Host, cfg.Ollama.Model)

	// Create advanced tools
	advancedTools := tools.NewAdvancedTools(httpClient, ollamaClient, logger)

	// Test 1: List Files
	fmt.Println("\n1. Testing List Files...")
	ctx := context.Background()
	result := advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
	fmt.Printf("Success: %v\n", result.Success)
	if result.Success {
		fmt.Printf("Message: %s\n", result.Message)
		if data, ok := result.Data.([]interface{}); ok {
			fmt.Printf("Found %d files:\n", len(data))
			for i, file := range data {
				if i < 10 { // Show first 10 files
					if fileMap, ok := file.(map[string]interface{}); ok {
						name := fileMap["name"]
						path := fileMap["path"]
						fileType := fileMap["type"]
						fmt.Printf("  - %s (%s) [%s]\n", name, path, fileType)
					}
				}
			}
			if len(data) > 10 {
				fmt.Printf("  ... and %d more files\n", len(data)-10)
			}
		}
	} else {
		fmt.Printf("Error: %s\n", result.Error)
	}

	// Test 2: Search Vault
	fmt.Println("\n2. Testing Search Vault...")
	searchResult := advancedTools.SearchVault(ctx, map[string]interface{}{
		"query": "AGENTS",
		"limit": 5,
	})
	fmt.Printf("Success: %v\n", searchResult.Success)
	if searchResult.Success {
		fmt.Printf("Message: %s\n", searchResult.Message)
		if data, ok := searchResult.Data.([]interface{}); ok {
			fmt.Printf("Found %d search results:\n", len(data))
			for i, result := range data {
				if i < 5 { // Show first 5 results
					if resultMap, ok := result.(map[string]interface{}); ok {
						path := resultMap["path"]
						score := resultMap["score"]
						fmt.Printf("  - %s (score: %.2f)\n", path, score)
					}
				}
			}
		}
	} else {
		fmt.Printf("Error: %s\n", searchResult.Error)
	}

	fmt.Println("\n✅ Real API Direct Integration Test Complete!")
}
