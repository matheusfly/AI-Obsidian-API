package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/config"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func main() {
	// Parse command line flags
	mockMode := flag.Bool("mock", false, "Run in mock mode (no external dependencies)")
	port := flag.String("port", "3010", "Server port")
	configPath := flag.String("config", "configs/config.yaml", "Configuration file path")
	flag.Parse()

	fmt.Printf("🚀 Starting MCP Server (Mock Mode: %v)\n", *mockMode)
	fmt.Println("=====================================")

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

	// Override port if specified
	if *port != "3010" {
		cfg.Server.Port = *port
	}

	// Create HTTP client (real or mock)
	var httpClient client.HTTPClient
	if *mockMode {
		logger.Info("Using mock HTTP client")
		httpClient = client.NewMockClient(logger)
	} else {
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
		ollamaClient = ollama.NewClient(cfg.Ollama.Host, cfg.Ollama.Model)
	}

	// Create advanced tools
	advancedTools := tools.NewAdvancedTools(httpClient, ollamaClient, logger)

	// Setup Gin router
	gin.SetMode(gin.ReleaseMode)
	r := gin.New()
	r.Use(gin.Logger())
	r.Use(gin.Recovery())

	// Health check endpoint
	r.GET("/health", func(c *gin.Context) {
		mode := "real"
		if *mockMode {
			mode = "mock"
		}
		c.JSON(http.StatusOK, gin.H{
			"status":    "healthy",
			"message":   "MCP Server is running",
			"timestamp": time.Now(),
			"mode":      mode,
			"mock_mode": *mockMode,
		})
	})

	// MCP endpoints
	r.GET("/tools", func(c *gin.Context) {
		tools := advancedTools.GetToolDefinitions()
		c.JSON(http.StatusOK, gin.H{
			"tools": tools,
			"count": len(tools),
		})
	})

	r.POST("/tools/execute", func(c *gin.Context) {
		var request struct {
			Tool   string                 `json:"tool"`
			Params map[string]interface{} `json:"params"`
		}

		if err := c.ShouldBindJSON(&request); err != nil {
			logger.Error("Invalid request format", zap.Error(err))
			c.JSON(http.StatusBadRequest, gin.H{
				"success": false,
				"error":   "Invalid request format",
			})
			return
		}

		logger.Info("Executing tool", zap.String("tool", request.Tool), zap.Any("params", request.Params))

		// Execute tool based on name
		ctx := context.Background()
		var result mcp.ToolResult

		// Add panic recovery for tool execution
		defer func() {
			if r := recover(); r != nil {
				logger.Error("Tool execution panicked", zap.String("tool", request.Tool), zap.Any("panic", r))
				result = mcp.ToolResult{
					Success: false,
					Error:   fmt.Sprintf("Tool execution panicked: %v", r),
				}
			}
		}()

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

		status := http.StatusOK
		if !result.Success {
			status = http.StatusBadRequest
		}

		c.JSON(status, result)
	})

	// Demo endpoint
	r.GET("/demo", func(c *gin.Context) {
		ctx := context.Background()

		// Test all tools
		demoResults := make(map[string]interface{})

		// List files
		listResult := advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
		demoResults["list_files"] = listResult

		// Search
		searchResult := advancedTools.SearchVault(ctx, map[string]interface{}{
			"query": "test",
			"limit": 5,
		})
		demoResults["search"] = searchResult

		// Semantic search
		semanticResult := advancedTools.SemanticSearch(ctx, map[string]interface{}{
			"query": "demo",
			"top_k": 3,
		})
		demoResults["semantic_search"] = semanticResult

		c.JSON(http.StatusOK, gin.H{
			"message":   "MCP Server Demo",
			"mode":      "mock",
			"mock_mode": *mockMode,
			"results":   demoResults,
		})
	})

	// Start server
	server := &http.Server{
		Addr:    ":" + cfg.Server.Port,
		Handler: r,
	}

	// Graceful shutdown
	go func() {
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Failed to start server", zap.Error(err))
		}
	}()

	logger.Info("MCP Server started",
		zap.String("port", cfg.Server.Port),
		zap.Bool("mock_mode", *mockMode),
		zap.String("config", *configPath),
	)

	fmt.Printf("✅ MCP Server running on port %s\n", cfg.Server.Port)
	fmt.Printf("🌐 Health check: http://localhost:%s/health\n", cfg.Server.Port)
	fmt.Printf("🔧 Tools: http://localhost:%s/tools\n", cfg.Server.Port)
	fmt.Printf("🎯 Demo: http://localhost:%s/demo\n", cfg.Server.Port)
	fmt.Printf("📝 Execute tool: POST http://localhost:%s/tools/execute\n", cfg.Server.Port)
	fmt.Println("\nPress Ctrl+C to stop the server")

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	// Graceful shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		logger.Fatal("Server forced to shutdown", zap.Error(err))
	}

	logger.Info("Server exited")
}
