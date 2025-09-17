package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/datamaster/mcp-server/internal/config"
	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"go.uber.org/zap"
)

func main() {
	fmt.Println("🔍 Real Vault Integration Test")
	fmt.Println("==============================")
	fmt.Println("Testing with 1000+ files from real Obsidian vault")
	fmt.Println("Vault Path: D:\\Nomade Milionario")
	fmt.Println()

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

	ctx := context.Background()
	testCount := 0
	successCount := 0

	// Test 1: List Files
	fmt.Println("1. Testing List Files...")
	testCount++
	result := advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
	if result.Success {
		fmt.Printf("✅ SUCCESS: Found %d files\n", len(result.Data.([]interface{})))
		successCount++
		
		// Show sample files
		if data, ok := result.Data.([]interface{}); ok {
			fmt.Println("   Sample files:")
			for i, file := range data {
				if i < 10 { // Show first 10 files
					if fileMap, ok := file.(map[string]interface{}); ok {
						name := fileMap["name"]
						fileType := fileMap["type"]
						fmt.Printf("   - %s [%s]\n", name, fileType)
					}
				}
			}
			if len(data) > 10 {
				fmt.Printf("   ... and %d more files\n", len(data)-10)
			}
		}
	} else {
		fmt.Printf("❌ FAILED: %s\n", result.Error)
	}

	// Test 2: Search for "AGENTS"
	fmt.Println("\n2. Testing Search for 'AGENTS'...")
	testCount++
	searchResult := advancedTools.SearchVault(ctx, map[string]interface{}{
		"query": "AGENTS",
		"limit": 5,
	})
	if searchResult.Success {
		fmt.Printf("✅ SUCCESS: Found %d results\n", len(searchResult.Data.([]interface{})))
		successCount++
		
		// Show search results
		if data, ok := searchResult.Data.([]interface{}); ok {
			fmt.Println("   Search results:")
			for _, result := range data {
				if resultMap, ok := result.(map[string]interface{}); ok {
					path := resultMap["path"]
					score := resultMap["score"]
					fmt.Printf("   - %s (score: %.2f)\n", path, score)
				}
			}
		}
	} else {
		fmt.Printf("❌ FAILED: %s\n", searchResult.Error)
	}

	// Test 3: Search for "Rust"
	fmt.Println("\n3. Testing Search for 'Rust'...")
	testCount++
	rustResult := advancedTools.SearchVault(ctx, map[string]interface{}{
		"query": "Rust",
		"limit": 5,
	})
	if rustResult.Success {
		fmt.Printf("✅ SUCCESS: Found %d results\n", len(rustResult.Data.([]interface{})))
		successCount++
	} else {
		fmt.Printf("❌ FAILED: %s\n", rustResult.Error)
	}

	// Test 4: Search for "nomade"
	fmt.Println("\n4. Testing Search for 'nomade'...")
	testCount++
	nomadeResult := advancedTools.SearchVault(ctx, map[string]interface{}{
		"query": "nomade",
		"limit": 5,
	})
	if nomadeResult.Success {
		fmt.Printf("✅ SUCCESS: Found %d results\n", len(nomadeResult.Data.([]interface{})))
		successCount++
	} else {
		fmt.Printf("❌ FAILED: %s\n", nomadeResult.Error)
	}

	// Test 5: Semantic Search
	fmt.Println("\n5. Testing Semantic Search...")
	testCount++
	semanticResult := advancedTools.SemanticSearch(ctx, map[string]interface{}{
		"query": "artificial intelligence",
		"top_k": 3,
	})
	if semanticResult.Success {
		fmt.Printf("✅ SUCCESS: Semantic search completed\n")
		successCount++
	} else {
		fmt.Printf("❌ FAILED: %s\n", semanticResult.Error)
	}

	// Test 6: Analyze Links
	fmt.Println("\n6. Testing Analyze Links...")
	testCount++
	linksResult := advancedTools.AnalyzeLinks(ctx, map[string]interface{}{})
	if linksResult.Success {
		fmt.Printf("✅ SUCCESS: Link analysis completed\n")
		successCount++
	} else {
		fmt.Printf("❌ FAILED: %s\n", linksResult.Error)
	}

	// Summary
	fmt.Println("\n📊 INTEGRATION TEST SUMMARY")
	fmt.Println("===========================")
	fmt.Printf("Total Tests: %d\n", testCount)
	fmt.Printf("Successful: %d\n", successCount)
	fmt.Printf("Failed: %d\n", testCount-successCount)
	fmt.Printf("Success Rate: %.1f%%\n", float64(successCount)/float64(testCount)*100)

	if successCount == testCount {
		fmt.Println("\n🎉 PERFECT! All tests passed with real vault data!")
		fmt.Println("✅ MCP Server is successfully integrated with real Obsidian vault!")
	} else if successCount > 0 {
		fmt.Println("\n✅ PARTIAL SUCCESS! Some tests passed with real data.")
		fmt.Println("⚠️ Check the failed tests above for details.")
	} else {
		fmt.Println("\n❌ FAILED! No tests passed with real data.")
		fmt.Println("🔧 Check the server configuration and API connection.")
	}

	fmt.Println("\n🚀 Real Vault Integration Test Complete!")
}
