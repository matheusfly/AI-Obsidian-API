package server

import (
	"context"
	"encoding/json"
	"net/http"
	"time"

	"github.com/datamaster/mcp-server/internal/config"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"github.com/datamaster/mcp-server/pkg/obsidian"
	"github.com/gin-gonic/gin"
)

// Server represents the MCP server instance
type Server struct {
	config         *config.Config
	obsidianClient *obsidian.Client
	ollamaClient   *ollama.Client
	toolRegistry   *tools.Registry
}

// NewServer creates a new MCP server instance
func NewServer(cfg *config.Config, oc *obsidian.Client, olc *ollama.Client, tr *tools.Registry) *Server {
	return &Server{
		config:         cfg,
		obsidianClient: oc,
		ollamaClient:   olc,
		toolRegistry:   tr,
	}
}

// SetupRoutes configures the Gin router with API endpoints
func (s *Server) SetupRoutes(router *gin.Engine) {
	router.GET("/health", s.healthCheck)
	router.GET("/tools/list", s.listTools)
	router.POST("/tools/execute", s.executeTool)
	router.POST("/mcp", s.handleMCPRequest) // Add proper MCP JSON-RPC endpoint
	// Add WebSocket endpoint later for interactive sessions
}

// healthCheck handles the /health endpoint
func (s *Server) healthCheck(c *gin.Context) {
	// Simple health check - just return healthy status
	// The server is running if we can reach this endpoint
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"message":   "MCP Server with real data integration is operational",
		"mode":      "real-data",
		"timestamp": time.Now().Format(time.RFC3339),
	})
}

// listTools handles the /tools/list endpoint
func (s *Server) listTools(c *gin.Context) {
	c.JSON(http.StatusOK, s.toolRegistry.ListTools())
}

// executeTool handles the /tools/execute endpoint
func (s *Server) executeTool(c *gin.Context) {
	var toolCall mcp.ToolCall
	if err := c.ShouldBindJSON(&toolCall); err != nil {
		c.JSON(http.StatusBadRequest, mcp.ToolResult{Success: false, Error: err.Error()})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second) // Longer timeout for tool execution
	defer cancel()

	result := s.toolRegistry.ExecuteTool(ctx, toolCall)
	if result.Success {
		c.JSON(http.StatusOK, result)
	} else {
		c.JSON(http.StatusInternalServerError, result) // Or 400 if it's a bad parameter error
	}
}

// MCPRequest represents a JSON-RPC request
type MCPRequest struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      int         `json:"id"`
	Method  string      `json:"method"`
	Params  interface{} `json:"params"`
}

// MCPResponse represents a JSON-RPC response
type MCPResponse struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      int         `json:"id"`
	Result  interface{} `json:"result"`
	Error   *MCPError   `json:"error,omitempty"`
}

// MCPError represents an MCP error
type MCPError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

// handleMCPRequest handles JSON-RPC requests to the MCP server
func (s *Server) handleMCPRequest(c *gin.Context) {
	var request MCPRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, MCPResponse{
			JSONRPC: "2.0",
			ID:      request.ID,
			Error: &MCPError{
				Code:    -32700,
				Message: "Parse error",
			},
		})
		return
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 60*time.Second)
	defer cancel()

	var response MCPResponse
	response.JSONRPC = "2.0"
	response.ID = request.ID

	switch request.Method {
	case "initialize":
		response.Result = map[string]interface{}{
			"protocolVersion": "2024-11-05",
			"capabilities": map[string]interface{}{
				"tools": map[string]interface{}{
					"listChanged": true,
				},
			},
			"serverInfo": map[string]interface{}{
				"name":    "obsidian-vault-mcp-server",
				"version": "1.0.0",
			},
		}

	case "tools/list":
		tools := s.toolRegistry.ListTools()
		response.Result = map[string]interface{}{
			"tools": tools,
		}

	case "tools/call":
		if params, ok := request.Params.(map[string]interface{}); ok {
			if toolName, ok := params["name"].(string); ok {
				if arguments, ok := params["arguments"].(map[string]interface{}); ok {
					toolCall := mcp.ToolCall{
						ToolName:   toolName,
						Parameters: arguments,
					}
					result := s.toolRegistry.ExecuteTool(ctx, toolCall)
					if result.Success {
						response.Result = result.Data
					} else {
						response.Error = &MCPError{
							Code:    -32000,
							Message: result.Error,
						}
					}
				} else {
					response.Error = &MCPError{
						Code:    -32602,
						Message: "Invalid params: missing arguments",
					}
				}
			} else {
				response.Error = &MCPError{
					Code:    -32602,
					Message: "Invalid params: missing tool name",
				}
			}
		} else {
			response.Error = &MCPError{
				Code:    -32602,
				Message: "Invalid params",
			}
		}

	default:
		response.Error = &MCPError{
			Code:    -32601,
			Message: "Method not found",
		}
	}

	c.JSON(http.StatusOK, response)
}
