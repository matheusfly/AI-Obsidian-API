package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/datamaster/mcp-server/internal/config"
	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func main() {
	// Parse command line flags
	port := flag.String("port", "3011", "Server port")
	configPath := flag.String("config", "configs/config.yaml", "Configuration file path")
	flag.Parse()

	fmt.Printf("🚀 Starting MCP Server in REAL MODE\n")
	fmt.Printf("===================================\n")
	fmt.Printf("Port: %s\n", *port)
	fmt.Printf("Config: %s\n", *configPath)

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

	// Setup Gin router
	gin.SetMode(gin.ReleaseMode)
	r := gin.New()
	r.Use(gin.Logger())
	r.Use(gin.Recovery())

	// Health check endpoint
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "healthy",
			"message":   "MCP Server is running in REAL MODE",
			"timestamp": time.Now(),
			"mode":      "real",
			"mock_mode": false,
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

	// Start server
	fmt.Printf("🚀 Starting server on port %s...\n", *port)
	fmt.Printf("✅ Health check: http://localhost:%s/health\n", *port)
	fmt.Printf("✅ Tools list: http://localhost:%s/tools\n", *port)
	fmt.Printf("✅ Real Obsidian vault: %s\n", cfg.Vault.Path)
	
	if err := r.Run(":" + *port); err != nil {
		logger.Fatal("Failed to start server", zap.Error(err))
	}
}
