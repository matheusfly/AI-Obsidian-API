package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"go.uber.org/zap"
)

func main() {
	// Initialize logger
	logger, err := zap.NewDevelopment()
	if err != nil {
		log.Fatal("Failed to create logger:", err)
	}
	defer logger.Sync()

	// Test both HTTP and HTTPS ports
	ports := []string{"27123", "27124"}
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	for _, port := range ports {
		fmt.Printf("\n=== Testing port %s ===\n", port)
		
		// Create client config
		cfg := &client.Config{
			BaseURL:     fmt.Sprintf("http://localhost:%s", port),
			Token:       apiKey,
			Timeout:     10 * time.Second,
			RateLimit:   10,
			CacheTTL:    5 * time.Minute,
			EnableCache: false,
		}

		// Create client
		httpClient := client.NewClient(cfg, logger)

		// Test basic connection
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		// Test root endpoint
		var rootResponse map[string]interface{}
		if err := httpClient.Get(ctx, "/", &rootResponse); err != nil {
			fmt.Printf("❌ Root endpoint failed: %v\n", err)
		} else {
			fmt.Printf("✅ Root endpoint success: %+v\n", rootResponse)
		}

		// Test vault listing
		var vaultFiles []map[string]interface{}
		if err := httpClient.Get(ctx, "/vault/", &vaultFiles); err != nil {
			fmt.Printf("❌ Vault listing failed: %v\n", err)
		} else {
			fmt.Printf("✅ Vault listing success: found %d items\n", len(vaultFiles))
			if len(vaultFiles) > 0 {
				fmt.Printf("   First item: %+v\n", vaultFiles[0])
			}
		}

		// Test search
		searchResults, err := httpClient.Search(ctx, "test", 5)
		if err != nil {
			fmt.Printf("❌ Search failed: %v\n", err)
		} else {
			fmt.Printf("✅ Search success: found %d results\n", len(searchResults))
		}
	}

	fmt.Println("\n=== Connection test completed ===")
}
