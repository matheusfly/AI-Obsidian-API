package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/datamaster/mcp-server/internal/config"
	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"go.uber.org/zap"
)

func main() {
	fmt.Println("🚀 Starting MCP Server in REAL MODE")
	fmt.Println("===================================")

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

	// Create REAL HTTP client
	clientCfg := &client.Config{
		BaseURL:     cfg.API.BaseURL,
		Token:       cfg.API.Token,
		Timeout:     10 * time.Second,
		RateLimit:   10,
		CacheTTL:    5 * time.Minute,
		EnableCache: true,
	}
	httpClient := client.NewClient(clientCfg, logger)
	logger.Info("Using REAL HTTP client", zap.String("base_url", cfg.API.BaseURL))

	// Create REAL Ollama client
	ollamaClient := ollama.NewClient(cfg.Ollama.Host, cfg.Ollama.Model)
	logger.Info("Using REAL Ollama client", zap.String("host", cfg.Ollama.Host), zap.String("model", cfg.Ollama.Model))

	// Create advanced tools
	advancedTools := tools.NewAdvancedTools(httpClient, ollamaClient, logger)

	// Test the connection
	fmt.Println("\n🧪 Testing Real Connection...")
	ctx := context.Background()
	result := advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
	if result.Success {
		fmt.Printf("✅ Real connection working! Found %d files\n", len(result.Data.([]interface{})))
	} else {
		fmt.Printf("❌ Real connection failed: %s\n", result.Error)
	}

	// Setup HTTP handlers
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		response := map[string]interface{}{
			"status":    "healthy",
			"message":   "MCP Server is running in REAL MODE",
			"timestamp": time.Now(),
			"mode":      "real",
			"mock_mode": false,
		}
		json.NewEncoder(w).Encode(response)
	})

	http.HandleFunc("/tools", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		tools := advancedTools.GetToolDefinitions()
		response := map[string]interface{}{
			"tools": tools,
			"count": len(tools),
		}
		json.NewEncoder(w).Encode(response)
	})

	http.HandleFunc("/tools/execute", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		var request struct {
			Tool   string                 `json:"tool"`
			Params map[string]interface{} `json:"params"`
		}

		if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
			http.Error(w, "Invalid JSON", http.StatusBadRequest)
			return
		}

		logger.Info("Executing tool", zap.String("tool", request.Tool), zap.Any("params", request.Params))

		// Execute tool based on name
		var result mcp.ToolResult

		switch request.Tool {
		case "list_files_in_vault":
			result = advancedTools.ListFilesInVault(ctx, request.Params)
		case "read_note":
			result = advancedTools.ReadNote(ctx, request.Params)
		case "search_vault":
			result = advancedTools.SearchVault(ctx, request.Params)
		case "semantic_search":
			result = advancedTools.SemanticSearch(ctx, request.Params)
		case "create_note":
			result = advancedTools.CreateNote(ctx, request.Params)
		case "bulk_tag":
			result = advancedTools.BulkTag(ctx, request.Params)
		case "analyze_links":
			result = advancedTools.AnalyzeLinks(ctx, request.Params)
		default:
			result = mcp.ToolResult{
				Success: false,
				Error:   fmt.Sprintf("Unknown tool: %s", request.Tool),
			}
		}

		logger.Info("Tool execution completed", 
			zap.String("tool", request.Tool), 
			zap.Bool("success", result.Success),
			zap.String("error", result.Error))

		w.Header().Set("Content-Type", "application/json")
		status := http.StatusOK
		if !result.Success {
			status = http.StatusBadRequest
		}
		w.WriteHeader(status)
		json.NewEncoder(w).Encode(result)
	})

	// Start server
	port := "3011"
	fmt.Printf("\n🚀 Starting server on port %s...\n", port)
	fmt.Printf("✅ Health check: http://localhost:%s/health\n", port)
	fmt.Printf("✅ Tools list: http://localhost:%s/tools\n", port)
	fmt.Printf("✅ Real Obsidian vault: %s\n", cfg.Vault.Path)
	
	logger.Info("Starting server", zap.String("port", port))
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		logger.Fatal("Failed to start server", zap.Error(err))
	}
}
