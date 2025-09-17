package main

import (
	"context"
	"flag"
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
	// Parse command line flags
	mockMode := flag.Bool("mock", false, "Run in mock mode (no external dependencies)")
	port := flag.String("port", "3010", "Server port")
	configPath := flag.String("config", "configs/config.yaml", "Configuration file path")
	flag.Parse()

	fmt.Printf("🚀 Debug Server Mode Detection\n")
	fmt.Printf("==============================\n")
	fmt.Printf("Mock Mode Flag: %v\n", *mockMode)
	fmt.Printf("Port: %s\n", *port)
	fmt.Printf("Config Path: %s\n", *configPath)

	// Initialize logger
	logger, err := zap.NewDevelopment()
	if err != nil {
		log.Fatal("Failed to create logger:", err)
	}
	defer logger.Sync()

	// Load configuration
	cfg, err := config.LoadConfig(*configPath)
	if err != nil {
		logger.Fatal("Failed to load config", zap.Error(err))
	}

	fmt.Printf("Config API Base URL: %s\n", cfg.API.BaseURL)
	fmt.Printf("Config API Token: %s...\n", cfg.API.Token[:20])

	// Create HTTP client (real or mock)
	var httpClient client.HTTPClient
	if *mockMode {
		fmt.Println("🔧 Creating MOCK HTTP client")
		logger.Info("Using mock HTTP client")
		httpClient = client.NewMockClient(logger)
	} else {
		fmt.Println("🔧 Creating REAL HTTP client")
		logger.Info("Using real HTTP client", zap.String("base_url", cfg.API.BaseURL))
		clientCfg := &client.Config{
			BaseURL:     cfg.API.BaseURL,
			Token:       cfg.API.Token,
			Timeout:     10 * time.Second,
			RateLimit:   10,
			CacheTTL:    5 * time.Minute,
			EnableCache: true,
		}
		httpClient = client.NewClient(clientCfg, logger)
	}

	// Create Ollama client (only in real mode)
	var ollamaClient *ollama.Client
	if !*mockMode {
		fmt.Println("🔧 Creating REAL Ollama client")
		ollamaClient = ollama.NewClient(cfg.Ollama.Host, cfg.Ollama.Model)
	} else {
		fmt.Println("🔧 Skipping Ollama client (mock mode)")
	}

	// Create advanced tools
	advancedTools := tools.NewAdvancedTools(httpClient, ollamaClient, logger)

	// Test the tools
	fmt.Println("\n🧪 Testing Tools...")
	ctx := context.Background()
	result := advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
	fmt.Printf("List Files Result: Success=%v, Message=%s\n", result.Success, result.Message)
	if result.Success {
		if data, ok := result.Data.([]interface{}); ok {
			fmt.Printf("Found %d files\n", len(data))
			if len(data) > 0 {
				if fileMap, ok := data[0].(map[string]interface{}); ok {
					name := fileMap["name"]
					fmt.Printf("First file: %s\n", name)
				}
			}
		}
	}

	fmt.Println("\n✅ Debug Complete!")
}
