package main

import (
	"crypto/tls"
	"log"
	"net/http"
	"time"

	"github.com/datamaster/mcp-server/internal/config"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/server"
	"github.com/datamaster/mcp-server/internal/tools"
	"github.com/datamaster/mcp-server/pkg/obsidian"
	"github.com/gin-gonic/gin"
)

func main() {
	cfg, err := config.LoadConfig("./configs/config.yaml")
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	obsidianClient := obsidian.NewClient(cfg.API.BaseURL, cfg.API.Token, &http.Client{
		Timeout: 10 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true}, // Bypass SSL for local Obsidian API
		},
	})

	ollamaClient := ollama.NewClient(cfg.Ollama.Host, cfg.Ollama.Model)

	toolRegistry := tools.NewRegistryWithConfig(obsidianClient, ollamaClient, cfg.API.BaseURL, cfg.API.Token)
	toolRegistry.RegisterDefaultTools() // Register predefined tools

	mcpServer := server.NewServer(cfg, obsidianClient, ollamaClient, toolRegistry)

	router := gin.Default()
	mcpServer.SetupRoutes(router)

	log.Printf("MCP Server starting on port %s", cfg.Server.Port)
	if err := router.Run(":" + cfg.Server.Port); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
